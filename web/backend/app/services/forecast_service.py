import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import settings
from app.schemas.prediction import PredictionItem, PredictResponse
from app.services.model_service import model_service

class ForecastService:
    def predict(
        self,
        ticker: str,
        steps: int = 30,
        model_type: Optional[str] = "lstm",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        history_limit: Optional[int] = 30,
    ) -> PredictResponse:
        ticker_symbol = ticker.strip().upper()
        model, resolved_variant = model_service.load_model(ticker_symbol, model_type=model_type)

        last_date, recent_history, full_df = self._get_historical_data(
            ticker_symbol,
            start_date=start_date,
            end_date=end_date,
            history_limit=history_limit,
        )

        predictions_mean, conf_int = self._calculate_forecast(
            model=model,
            variant=resolved_variant,
            ticker_symbol=ticker_symbol,
            steps=steps,
            df=full_df,
        )

        future_dates = self._generate_future_business_dates(last_date, steps)

        prediction_items: List[PredictionItem] = []
        for index, forecast_date in enumerate(future_dates):
            price_estimate = round(float(predictions_mean[index]), 2)
            lower_bound_price = None
            upper_bound_price = None

            if conf_int is not None:
                lower_bound_price = round(float(conf_int[index, 0]), 2)
                upper_bound_price = round(float(conf_int[index, 1]), 2)

            item = PredictionItem(
                date=forecast_date.strftime("%Y-%m-%d"),
                predicted_price=price_estimate,
                lower_bound=lower_bound_price,
                upper_bound=upper_bound_price,
            )
            prediction_items.append(item)

        model_display_name = (
            f"Sequential ({resolved_variant})"
            if resolved_variant in ["LSTM", "GRU"]
            else type(model).__name__
        )

        return PredictResponse(
            ticker=ticker_symbol,
            model_type=resolved_variant.lower(),
            model_name=model_display_name,
            forecast_steps=steps,
            last_historical_date=last_date,
            predictions=prediction_items,
            history=recent_history,
        )

    def _calculate_forecast(
        self,
        model: Any,
        variant: str,
        ticker_symbol: str,
        steps: int,
        df: Optional[pd.DataFrame],
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        # 1. Penanganan Model Deep Learning (LSTM & GRU)
        if variant.upper() in ["LSTM", "GRU"]:
            return self._forecast_deep_learning(
                model=model,
                variant=variant.upper(),
                ticker_symbol=ticker_symbol,
                steps=steps,
                df=df,
            )

        # 2. Penanganan Model PMDARIMA (auto_arima)
        if hasattr(model, "predict") and not hasattr(model, "layers"):
            try:
                predictions, conf_intervals = model.predict(n_periods=steps, return_conf_int=True)
                return np.array(predictions), np.array(conf_intervals)
            except Exception:
                pass

        # 3. Penanganan Model Statsmodels (SARIMAX / ARIMA)
        if hasattr(model, "get_forecast"):
            forecast_result = model.get_forecast(steps=steps)
            predictions = forecast_result.predicted_mean
            conf_intervals = forecast_result.conf_int()
            if hasattr(conf_intervals, "values"):
                conf_intervals = conf_intervals.values
            if hasattr(predictions, "values"):
                predictions = predictions.values
            return np.array(predictions), np.array(conf_intervals)

        # Fallback jika model Keras tidak terdeteksi dari variant
        return self._forecast_deep_learning(
            model=model,
            variant="LSTM",
            ticker_symbol=ticker_symbol,
            steps=steps,
            df=df,
        )

    def _forecast_deep_learning(
        self,
        model: Any,
        variant: str,
        ticker_symbol: str,
        steps: int,
        df: Optional[pd.DataFrame],
    ) -> Tuple[np.ndarray, Optional[np.ndarray]]:
        if df is None or df.empty:
            raise ValueError(f"Data historis untuk ticker '{ticker_symbol}' tidak ditemukan.")

        metrics_meta = model_service.load_metrics(ticker_symbol) or {}
        target_col = metrics_meta.get("target_col", "close")
        window_size = int(metrics_meta.get("window_size", 30))

        if target_col not in df.columns:
            if "close" in df.columns:
                target_col = "close"
            elif "open" in df.columns:
                target_col = "open"
            else:
                target_col = df.select_dtypes(include=[np.number]).columns[0]

        series_values = df[target_col].dropna().values
        if len(series_values) < window_size:
            raise ValueError(
                f"Data historis ({len(series_values)} baris) kurang dari window_size ({window_size})."
            )

        # Muat scaler normalizer
        scaler = model_service.load_scaler(ticker_symbol)
        if scaler is None:
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler(feature_range=(0, 1))
            scaler.fit(series_values.reshape(-1, 1))

        # Ambil jendela terakhir
        last_window_raw = series_values[-window_size:].reshape(-1, 1)
        last_window_scaled = scaler.transform(last_window_raw)

        # Current window bentuk tensor 3D: [1, window_size, 1]
        current_window = last_window_scaled.reshape(1, window_size, 1)

        predicted_scaled_list = []
        for _ in range(steps):
            pred_scaled = model.predict(current_window, verbose=0)
            next_val = float(pred_scaled[0, 0])
            predicted_scaled_list.append(next_val)

            # Geser sliding window secara rekursif: buang elemen tertua, masukkan prediksi baru
            current_window = np.append(current_window[:, 1:, :], [[[next_val]]], axis=1)

        predicted_scaled_array = np.array(predicted_scaled_list).reshape(-1, 1)
        predicted_prices = scaler.inverse_transform(predicted_scaled_array).flatten()

        # Estimasi interval keyakinan 95% berdasarkan RMSE evaluasi model
        model_metrics = metrics_meta.get("metrics", {}).get(variant, {})
        rmse = float(model_metrics.get("RMSE", 0.0))
        if rmse <= 0.0:
            diffs = np.diff(series_values[-60:]) if len(series_values) >= 60 else np.diff(series_values)
            rmse = float(np.std(diffs)) if len(diffs) > 0 else 50.0

        # Confidence interval melebar seiring horizon langkah peramalan (sqrt(t))
        conf_intervals = np.zeros((steps, 2))
        for step_idx in range(steps):
            margin = 1.96 * rmse * (1.0 + 0.03 * step_idx)
            pred_val = predicted_prices[step_idx]
            conf_intervals[step_idx, 0] = max(0.0, pred_val - margin)
            conf_intervals[step_idx, 1] = pred_val + margin

        return predicted_prices, conf_intervals

    def _get_historical_data(
        self,
        ticker_symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        history_limit: Optional[int] = 30,
    ) -> Tuple[Optional[str], List[Dict[str, Any]], Optional[pd.DataFrame]]:
        csv_file_path = settings.DATA_DIR / f"{ticker_symbol}.csv"
        if not csv_file_path.exists():
            return None, [], None

        dataframe = pd.read_csv(csv_file_path)
        if dataframe.empty or "date" not in dataframe.columns:
            return None, [], None

        dataframe["date"] = dataframe["date"].astype(str)
        dataframe = dataframe.sort_values("date").reset_index(drop=True)
        last_date_record = str(dataframe["date"].iloc[-1])

        if start_date and end_date:
            filtered = dataframe[(dataframe["date"] >= start_date) & (dataframe["date"] <= end_date)]
            if not filtered.empty:
                recent_records = filtered.to_dict(orient="records")
            else:
                recent_records = dataframe.tail(history_limit or 30).to_dict(orient="records")
        elif start_date:
            filtered = dataframe[dataframe["date"] >= start_date]
            recent_records = filtered.to_dict(orient="records")
        elif end_date:
            filtered = dataframe[dataframe["date"] <= end_date]
            recent_records = filtered.tail(history_limit or 30).to_dict(orient="records")
        else:
            limit = history_limit if history_limit else 30
            recent_records = dataframe.tail(limit).to_dict(orient="records")

        return last_date_record, recent_records, dataframe

    def _generate_future_business_dates(
        self, last_historical_date: Optional[str], steps: int
    ) -> pd.DatetimeIndex:
        if last_historical_date:
            next_day = pd.to_datetime(last_historical_date) + pd.Timedelta(days=1)
            start_date = next_day
        else:
            today_string = datetime.now().strftime("%Y-%m-%d")
            start_date = pd.to_datetime(today_string)

        return pd.bdate_range(start=start_date, periods=steps)

forecast_service = ForecastService()
