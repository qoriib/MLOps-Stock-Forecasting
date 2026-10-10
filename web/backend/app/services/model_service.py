import asyncio
import datetime
import logging
import pickle
from typing import Dict, List, Tuple
import keras
import numpy as np
from app.config import ASSETS_DIR
from app.models.entities import StockPrice
from app.models.schemas import (
    PredictRequest,
    PredictResponse,
    PredictionItem,
)
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)

model_cache_storage: Dict[str, keras.Model] = {}
scaler_cache_storage: Dict[str, object] = {}
_cached_available_assets = None


def _run_universal_inference(
    model: keras.Model,
    scaler: object,
    hist_records: List[Tuple[datetime.date, float]],
    target_dates: List[datetime.date],
    window_size: int,
    feature_dim: int,
) -> List[Tuple[datetime.date, float]]:
    if not hist_records:
        base_price = 1000.0
        hist_records = [
            (datetime.date.today() - datetime.timedelta(days=window_size - i), base_price)
            for i in range(window_size)
        ]

    # Padding otomatis jika data historis kurang dari window_size
    if len(hist_records) < window_size:
        first_date, first_price = hist_records[0]
        pad_needed = window_size - len(hist_records)
        padded_records = [
            (first_date - datetime.timedelta(days=pad_needed - i), first_price)
            for i in range(pad_needed)
        ] + hist_records
        hist_records = padded_records

    last_hist_date = hist_records[-1][0]
    all_closes = [rec[1] for rec in hist_records]

    test_dates = [d for d in target_dates if d <= last_hist_date]
    future_dates = [d for d in target_dates if d > last_hist_date]

    results_map: Dict[datetime.date, float] = {}

    # 1. Inferensi Data Uji (Ground-truth historical sliding windows layaknya create_test_windows)
    if test_dates:
        all_test_windows: List[List[float]] = []
        for d in test_dates:
            closes_before = [price for rec_d, price in hist_records if rec_d < d]
            if len(closes_before) >= window_size:
                win = closes_before[-window_size:]
            elif len(closes_before) > 0:
                pad_len = window_size - len(closes_before)
                win = [closes_before[0]] * pad_len + closes_before
            else:
                win = all_closes[:window_size]
            all_test_windows.append(win)

        windows_array = np.array(all_test_windows, dtype=np.float32)
        scaled_inputs = scaler.transform(windows_array.reshape(-1, 1)).reshape(-1, window_size, feature_dim)
        scaled_outputs = model(scaled_inputs, training=False).numpy()
        inversed_outputs = scaler.inverse_transform(scaled_outputs).flatten()

        for d, price in zip(test_dates, inversed_outputs):
            results_map[d] = float(price)

    # 2. Inferensi Masa Depan (Mendukung Direct Multi-Horizon maupun Rolling Sliding Window 20-30 step)
    if future_dates:
        curr_window = list(all_closes[-window_size:])
        model_output_dim = 1
        if hasattr(model, "output_shape") and len(model.output_shape) > 1 and model.output_shape[-1] is not None:
            model_output_dim = int(model.output_shape[-1])

        if model_output_dim > 1:
            # Arsitektur Direct Multi-Step Horizon (misal model Dense(20) atau Dense(30))
            win_slice = np.array(curr_window[-window_size:], dtype=np.float32).reshape(-1, 1)
            scaled_window = scaler.transform(win_slice)
            model_input = scaled_window.reshape(1, window_size, feature_dim)

            scaled_output = model(model_input, training=False).numpy()
            inversed_output = scaler.inverse_transform(scaled_output).flatten()

            for idx, d in enumerate(future_dates):
                if idx < len(inversed_output):
                    results_map[d] = float(inversed_output[idx])
                else:
                    results_map[d] = float(inversed_output[-1])
        else:
            # Arsitektur Stacked Recurrent dengan Rolling Sliding Window
            for d in future_dates:
                win_slice = np.array(curr_window[-window_size:], dtype=np.float32).reshape(-1, 1)
                scaled_window = scaler.transform(win_slice)
                model_input = scaled_window.reshape(1, window_size, feature_dim)

                scaled_output = model(model_input, training=False).numpy()
                inversed_output = scaler.inverse_transform(scaled_output)

                pred_val = float(inversed_output.flatten()[0])
                results_map[d] = pred_val
                curr_window.append(pred_val)

    return [(d, results_map[d]) for d in target_dates if d in results_map]


class ModelService:
    @staticmethod
    def get_available_assets() -> Tuple[List[str], List[str]]:
        global _cached_available_assets
        if _cached_available_assets is not None:
            return _cached_available_assets

        tickers_set = set()
        models_set = set()

        if ASSETS_DIR.exists():
            for keras_file_path in ASSETS_DIR.glob("*.keras"):
                file_stem = keras_file_path.stem
                stem_parts = file_stem.rsplit("_", 1)
                if len(stem_parts) == 2:
                    ticker_symbol = stem_parts[0].upper()
                    model_type = stem_parts[1].lower()
                    tickers_set.add(ticker_symbol)
                    models_set.add(model_type)

        sorted_tickers = []
        if tickers_set:
            sorted_tickers = sorted(list(tickers_set))

        sorted_models = []
        if models_set:
            sorted_models = sorted(list(models_set))

        _cached_available_assets = (sorted_tickers, sorted_models)
        return _cached_available_assets

    @staticmethod
    def get_scaler(ticker: str):
        clean_ticker = ticker.strip().upper()
        if clean_ticker in scaler_cache_storage:
            return scaler_cache_storage[clean_ticker]

        scaler_file_path = ASSETS_DIR / f"{clean_ticker}_scaler.pkl"
        if not scaler_file_path.exists():
            raise FileNotFoundError(f"Scaler {clean_ticker}_scaler.pkl was not found.")

        with open(scaler_file_path, "rb") as scaler_file_object:
            scaler = pickle.load(scaler_file_object)

        scaler_cache_storage[clean_ticker] = scaler
        return scaler

    @staticmethod
    def get_model(ticker: str, model: str):
        clean_ticker = ticker.strip().upper()
        clean_model = model.strip().upper()
        cache_lookup_key = f"{clean_ticker}_{clean_model}"

        if cache_lookup_key in model_cache_storage:
            return model_cache_storage[cache_lookup_key]

        model_path = ASSETS_DIR / f"{cache_lookup_key}.keras"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file {cache_lookup_key}.keras was not found.")

        loaded_model = keras.models.load_model(model_path)
        model_cache_storage[cache_lookup_key] = loaded_model
        logger.info(f"Loaded model {cache_lookup_key}")

        return loaded_model

    @staticmethod
    def get_business_days(start_d: datetime.date, end_d: datetime.date) -> List[datetime.date]:
        b_days = []
        curr = start_d
        while curr <= end_d:
            if curr.weekday() < 5:
                b_days.append(curr)
            curr += datetime.timedelta(days=1)
        return b_days

    @classmethod
    async def execute_forecast(cls, parameters: PredictRequest) -> PredictResponse:
        ticker = parameters.ticker.strip().upper()
        model_name = parameters.model.strip().lower()

        # Parse tanggal tanpa membatasi urutan (otomatis swap jika terbalik)
        try:
            req_start = datetime.date.fromisoformat(parameters.start_date.strip())
            req_end = datetime.date.fromisoformat(parameters.end_date.strip())
        except Exception:
            today = datetime.date.today()
            req_start = today - datetime.timedelta(days=7)
            req_end = today

        if req_start > req_end:
            req_start, req_end = req_end, req_start

        model = cls.get_model(ticker, model_name)
        scaler = cls.get_scaler(ticker)

        window_size = int(model.input_shape[1])
        feature_dim = 1
        if len(model.input_shape) > 2:
            feature_dim = int(model.input_shape[2])

        await StockService.ensure_stock_cached(ticker)

        # Kumpulkan target tanggal kalender / trading
        target_dates = cls.get_business_days(req_start, req_end)
        if not target_dates:
            curr = req_start
            while curr <= req_end:
                target_dates.append(curr)
                curr += datetime.timedelta(days=1)

        # Ambil data historis (menggunakan in-memory cache untuk meminimalkan koneksi MongoDB)
        docs = await StockService.get_all_cached_prices(ticker)

        hist_records: List[Tuple[datetime.date, float]] = [
            (doc.timestamp.date(), float(doc.close)) for doc in docs
        ]

        predictions_raw = await asyncio.to_thread(
            _run_universal_inference,
            model,
            scaler,
            hist_records,
            target_dates,
            window_size,
            feature_dim,
        )

        prediction_items = [
            PredictionItem(
                date=d.strftime("%Y-%m-%d"),
                predicted_price=round(price, 2),
            )
            for d, price in predictions_raw
        ]

        if not prediction_items:
            fallback_date = req_end.strftime("%Y-%m-%d")
            fallback_price = float(hist_records[-1][1]) if hist_records else 1000.0
            prediction_items = [
                PredictionItem(
                    date=fallback_date,
                    predicted_price=round(fallback_price, 2),
                )
            ]

        logger.info(f"Universal Forecast {ticker} ({model_name}): {len(prediction_items)} points")
        return PredictResponse(
            ticker=ticker,
            model=model_name,
            predictions=prediction_items,
        )
