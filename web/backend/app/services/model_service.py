import datetime
import math
import pickle
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd
import keras

from app.config import ASSETS_DIR
from app.models.schemas import (
    HistoricalItem,
    PredictRequest,
    PredictResponse,
    PredictionItem,
    ScalerMeta,
)
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
    def get_forecast_model(ticker: str, model_type: str):
        clean_ticker = ticker.strip().upper()
        clean_model_type = model_type.strip().upper()
        cache_lookup_key = f"{clean_ticker}_{clean_model_type}"

        if cache_lookup_key in model_cache_storage:
            return model_cache_storage[cache_lookup_key]

        model_path = ASSETS_DIR / f"{cache_lookup_key}.keras"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file {cache_lookup_key}.keras tidak ditemukan.")

        loaded_model = keras.models.load_model(model_path)
        model_cache_storage[cache_lookup_key] = loaded_model
        return loaded_model

    @staticmethod
    def generate_future_business_dates(last_date_string: str, steps_count: int) -> List[str]:
        future_date_list = []
        current_date = datetime.datetime.strptime(last_date_string, "%Y-%m-%d")

        while len(future_date_list) < steps_count:
            current_date += datetime.timedelta(days=1)
            weekday_number = current_date.weekday()
            if weekday_number < 5:
                formatted_date = current_date.strftime("%Y-%m-%d")
                future_date_list.append(formatted_date)

        return future_date_list

    @classmethod
    def execute_forecast(cls, parameters: PredictRequest) -> PredictResponse:
        ticker = parameters.ticker.strip().upper()
        model_type = parameters.model_type.strip().lower()
        steps_count = parameters.steps
        history_limit = parameters.history_limit
        window_size = 30

        history_response = StockService.get_stock_history(
            ticker=ticker,
            start_date=parameters.start_date,
            end_date=parameters.end_date,
        )
        if not history_response or not history_response.data:
            raise ValueError(f"Data historis pasar untuk {ticker} tidak ditemukan.")

        historical_records = history_response.data
        total_historical_records = len(historical_records)
        if total_historical_records < window_size:
            raise ValueError(
                f"Jumlah data ({total_historical_records}) kurang dari window size minimal ({window_size})."
            )

        model = cls.get_forecast_model(ticker, model_type)
        scaler = cls.get_scaler(ticker)

        close_prices = []
        for record in historical_records:
            close_prices.append(record.close)

        close_prices_array = np.array(close_prices, dtype=np.float32)
        recent_window = list(close_prices_array[-window_size:])

        predicted_prices = []
        for step_iteration in range(steps_count):
            window_slice = np.array(recent_window[-window_size:], dtype=np.float32).reshape(-1, 1)
            scaled_window = scaler.transform(window_slice)
            model_input = scaled_window.reshape(1, window_size, 1)
            scaled_output = model.predict(model_input, verbose=0)
            inversed_output = scaler.inverse_transform(scaled_output)
            predicted_price_value = float(inversed_output.flatten()[0])

            predicted_prices.append(predicted_price_value)
            recent_window.append(predicted_price_value)

        last_historical_prices = close_prices_array[-60:]
        if len(last_historical_prices) > 1:
            price_differences = np.diff(last_historical_prices)
            standard_error = float(np.sqrt(np.mean(price_differences ** 2)))
        else:
            standard_error = 50.0

        last_date = historical_records[-1].date
        future_dates = cls.generate_future_business_dates(last_date, steps_count)

        prediction_items = []
        for step_index, future_date in enumerate(future_dates):
            price_value = round(float(predicted_prices[step_index]), 2)
            expansion_factor = math.sqrt(1.0 + 0.04 * step_index)
            margin = 1.96 * standard_error * expansion_factor
            lower_value = round(max(0.0, price_value - margin), 2)
            upper_value = round(price_value + margin, 2)

            prediction_item = PredictionItem(
                date=future_date,
                predicted_price=price_value,
                lower_bound=lower_value,
                upper_bound=upper_value,
            )
            prediction_items.append(prediction_item)

        scaler_meta = None
        if hasattr(scaler, "data_min_"):
            scaler_meta = ScalerMeta(
                scaler_type="MinMaxScaler",
                data_min=float(scaler.data_min_[0]),
                data_max=float(scaler.data_max_[0]),
                data_range=float(scaler.data_range_[0]),
                scale=float(scaler.scale_[0]),
                min=float(scaler.min_[0]),
            )

        engine_name = f"Keras {model_type.upper()} Model"
        historical_slice = historical_records[-history_limit:]

        return PredictResponse(
            ticker=ticker,
            model_type=model_type,
            model_name=engine_name,
            forecast_steps=steps_count,
            window_size=window_size,
            last_historical_date=last_date,
            scaler_info=scaler_meta,
            predictions=prediction_items,
            history=historical_slice,
        )
