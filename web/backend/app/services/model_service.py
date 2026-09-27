import datetime
import logging
import pickle
import keras
import numpy as np
from typing import List, Tuple
from app.config import ASSETS_DIR
from app.services.stock_service import StockService
from app.models.entities import StockPrice
from app.models.schemas import (
    PredictRequest,
    PredictResponse,
    PredictionItem,
)

logger = logging.getLogger(__name__)

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
            raise FileNotFoundError(f"Scaler {clean_ticker}_scaler.pkl was not found.")

        with open(scaler_file_path, "rb") as scaler_file_object:
            return pickle.load(scaler_file_object)

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
        req_start = datetime.date.fromisoformat(parameters.start_date)
        req_end = datetime.date.fromisoformat(parameters.end_date)

        model = cls.get_model(ticker, model_name)
        scaler = cls.get_scaler(ticker)

        window_size = int(model.input_shape[1])
        feature_dim = 1
        if len(model.input_shape) > 2:
            feature_dim = int(model.input_shape[2])

        await StockService.ensure_stock_cached(ticker)

        all_records = await StockPrice.find(
            StockPrice.metadata.ticker == ticker
        ).sort("+timestamp").to_list()

        if not all_records or len(all_records) < window_size:
            raise ValueError(
                f"Insufficient historical data for {ticker} (minimum {window_size} records required)."
            )

        last_hist_date = all_records[-1].timestamp.date()

        if req_end > last_hist_date:
            forecast_start = last_hist_date + datetime.timedelta(days=1)
            all_forecast_days = cls.get_business_days(forecast_start, req_end)
            
            if not all_forecast_days:
                raise ValueError(f"No trading days available for forecasting up to {parameters.end_date}.")

            close_prices = []
            for record in all_records:
                close_prices.append(record.close)

            recent_window_slice = close_prices[-window_size:]
            recent_window = [float(price) for price in recent_window_slice]

            predicted_prices = []
            for _ in range(len(all_forecast_days)):
                current_window = recent_window[-window_size:]
                window_slice = np.array(current_window, dtype=np.float32).reshape(-1, 1)
                
                scaled_window = scaler.transform(window_slice)
                model_input = scaled_window.reshape(1, window_size, feature_dim)
                
                scaled_output = model.predict(model_input, verbose=0)
                inversed_output = scaler.inverse_transform(scaled_output)
                
                predicted_price_value = float(inversed_output.flatten()[0])

                predicted_prices.append(predicted_price_value)
                recent_window.append(predicted_price_value)

            prediction_items = []
            for b_day, price_val in zip(all_forecast_days, predicted_prices):
                if req_start <= b_day <= req_end:
                    date_string = b_day.strftime("%Y-%m-%d")
                    rounded_price = round(price_val, 2)
                    item = PredictionItem(
                        date=date_string,
                        predicted_price=rounded_price,
                    )
                    prediction_items.append(item)

            if not prediction_items:
                raise ValueError(
                    f"No trading days found in the range {parameters.start_date} to {parameters.end_date}."
                )
        else:
            records_before = []
            for record in all_records:
                record_date = record.timestamp.date()
                if record_date < req_start:
                    records_before.append(record)

            if len(records_before) < window_size:
                raise ValueError(
                    f"Historical data before {parameters.start_date} is less than {window_size} trading days."
                )

            all_forecast_days = cls.get_business_days(req_start, req_end)
            if not all_forecast_days:
                raise ValueError(
                    f"No trading days found in the range {parameters.start_date} to {parameters.end_date}."
                )

            close_prices = []
            for record in records_before:
                close_prices.append(record.close)

            recent_window_slice = close_prices[-window_size:]
            recent_window = [float(price) for price in recent_window_slice]

            prediction_items = []
            for b_day in all_forecast_days:
                current_window = recent_window[-window_size:]
                window_slice = np.array(current_window, dtype=np.float32).reshape(-1, 1)
                
                scaled_window = scaler.transform(window_slice)
                model_input = scaled_window.reshape(1, window_size, feature_dim)
                
                scaled_output = model.predict(model_input, verbose=0)
                inversed_output = scaler.inverse_transform(scaled_output)
                
                predicted_price_value = float(inversed_output.flatten()[0])

                recent_window.append(predicted_price_value)
                
                date_string = b_day.strftime("%Y-%m-%d")
                rounded_price = round(predicted_price_value, 2)
                item = PredictionItem(
                    date=date_string,
                    predicted_price=rounded_price,
                )
                prediction_items.append(item)

        logger.info(f"Forecast {ticker} ({model_name}): {len(prediction_items)} points")
        return PredictResponse(
            ticker=ticker,
            model=model_name,
            predictions=prediction_items,
        )
