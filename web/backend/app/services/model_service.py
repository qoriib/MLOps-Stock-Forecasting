import datetime
import pickle
from typing import List, Tuple

import numpy as np
import keras

from app.config import ASSETS_DIR
from app.models.schemas import (
    PredictRequest,
    PredictResponse,
    PredictionItem,
)
from app.models.entities import StockPrice
from app.services.stock_service import StockService

model_cache_storage = {}


class ModelService:
    @staticmethod
    def get_available_assets() -> Tuple[List[str], List[str]]:
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

        return sorted_tickers, sorted_models

    @staticmethod
    def get_scaler(ticker: str):
        clean_ticker = ticker.strip().upper()
        scaler_file_path = ASSETS_DIR / f"{clean_ticker}_scaler.pkl"
        if not scaler_file_path.exists():
            raise FileNotFoundError(f"Scaler {clean_ticker}_scaler.pkl tidak ditemukan.")

        with open(scaler_file_path, "rb") as scaler_file_object:
            return pickle.load(scaler_file_object)

    @staticmethod
    def get_forecast_model(ticker: str, model: str):
        clean_ticker = ticker.strip().upper()
        clean_model = model.strip().upper()
        cache_lookup_key = f"{clean_ticker}_{clean_model}"

        if cache_lookup_key in model_cache_storage:
            return model_cache_storage[cache_lookup_key]

        model_path = ASSETS_DIR / f"{cache_lookup_key}.keras"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file {cache_lookup_key}.keras tidak ditemukan.")

        loaded_model = keras.models.load_model(model_path)
        model_cache_storage[cache_lookup_key] = loaded_model
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
        req_start = datetime.date.fromisoformat(parameters.start_date)
        req_end = datetime.date.fromisoformat(parameters.end_date)

        model = cls.get_forecast_model(ticker, model_name)
        scaler = cls.get_scaler(ticker)

        window_size = int(model.input_shape[1])
        feature_dim = int(model.input_shape[2]) if len(model.input_shape) > 2 else 1

        await StockService.ensure_stock_cached(ticker)

        all_records = await StockPrice.find(
            StockPrice.metadata.ticker == ticker
        ).sort("+timestamp").to_list()

        if not all_records or len(all_records) < window_size:
            raise ValueError(
                f"Data historis untuk {ticker} tidak mencukupi (minimal {window_size} data)."
            )

        last_hist_date = all_records[-1].timestamp.date()

        if req_end > last_hist_date:
            forecast_start = last_hist_date + datetime.timedelta(days=1)
            all_forecast_days = cls.get_business_days(forecast_start, req_end)
            if not all_forecast_days:
                raise ValueError(f"Tidak ada hari bursa yang dapat diramal hingga {parameters.end_date}.")

            close_prices = [record.close for record in all_records]
            recent_window = list(np.array(close_prices[-window_size:], dtype=np.float32))

            predicted_prices = []
            for _ in range(len(all_forecast_days)):
                window_slice = np.array(recent_window[-window_size:], dtype=np.float32).reshape(-1, 1)
                scaled_window = scaler.transform(window_slice)
                model_input = scaled_window.reshape(1, window_size, feature_dim)
                scaled_output = model.predict(model_input, verbose=0)
                inversed_output = scaler.inverse_transform(scaled_output)
                predicted_price_value = float(inversed_output.flatten()[0])

                predicted_prices.append(predicted_price_value)
                recent_window.append(predicted_price_value)

            prediction_items = [
                PredictionItem(
                    date=b_day.strftime("%Y-%m-%d"),
                    predicted_price=round(price_val, 2),
                )
                for b_day, price_val in zip(all_forecast_days, predicted_prices)
                if req_start <= b_day <= req_end
            ]

            if not prediction_items:
                raise ValueError(
                    f"Tidak ada hari bursa dalam rentang {parameters.start_date} hingga {parameters.end_date}."
                )
        else:
            records_before = [r for r in all_records if r.timestamp.date() < req_start]
            if len(records_before) < window_size:
                raise ValueError(
                    f"Data historis sebelum {parameters.start_date} kurang dari {window_size} hari."
                )

            all_forecast_days = cls.get_business_days(req_start, req_end)
            if not all_forecast_days:
                raise ValueError(
                    f"Tidak ada hari bursa dalam rentang {parameters.start_date} hingga {parameters.end_date}."
                )

            close_prices = [r.close for r in records_before]
            recent_window = list(np.array(close_prices[-window_size:], dtype=np.float32))

            prediction_items = []
            for b_day in all_forecast_days:
                window_slice = np.array(recent_window[-window_size:], dtype=np.float32).reshape(-1, 1)
                scaled_window = scaler.transform(window_slice)
                model_input = scaled_window.reshape(1, window_size, feature_dim)
                scaled_output = model.predict(model_input, verbose=0)
                inversed_output = scaler.inverse_transform(scaled_output)
                predicted_price_value = float(inversed_output.flatten()[0])

                recent_window.append(predicted_price_value)
                prediction_items.append(
                    PredictionItem(
                        date=b_day.strftime("%Y-%m-%d"),
                        predicted_price=round(predicted_price_value, 2),
                    )
                )

        return PredictResponse(
            ticker=ticker,
            model=model_name,
            predictions=prediction_items,
        )
