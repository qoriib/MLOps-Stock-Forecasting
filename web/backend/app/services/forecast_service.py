import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import settings
from app.schemas.prediction import PredictionItem, PredictResponse
from app.services.model_service import model_service

class ForecastService:
    def predict(self, ticker: str, steps: int = 30, model_type: Optional[str] = "best") -> PredictResponse:
        ticker_clean = ticker.strip().upper()
        model, resolved_variant = model_service.load_model(ticker_clean, model_type=model_type)

        # Hitung prediksi dan interval keyakinan
        predictions_mean, conf_int = self._calculate_forecast(model, steps)

        # Dapatkan data tanggal historis terakhir dan 30 baris data terbaru
        last_historical_date, recent_history = self._get_recent_history(ticker_clean)

        # Hitung rentang hari kerja ke depan (bdate_range)
        future_dates = self._generate_future_business_dates(last_historical_date, steps)

        # Format item prediksi
        items: List[PredictionItem] = []
        for i, date_val in enumerate(future_dates):
            pred_val = float(predictions_mean[i])
            lower = float(conf_int[i, 0]) if conf_int is not None else None
            upper = float(conf_int[i, 1]) if conf_int is not None else None

            items.append(
                PredictionItem(
                    date=date_val.strftime("%Y-%m-%d"),
                    predicted_price=round(pred_val, 2),
                    lower_bound=round(lower, 2) if lower is not None else None,
                    upper_bound=round(upper, 2) if upper is not None else None,
                )
            )

        return PredictResponse(
            ticker=ticker_clean,
            model_type=resolved_variant.lower(),
            model_name=type(model).__name__,
            forecast_steps=steps,
            last_historical_date=last_historical_date,
            predictions=items,
            history=recent_history,
        )

    def _calculate_forecast(self, model: Any, steps: int) -> Tuple[Any, Optional[Any]]:
        try:
            forecast_res = model.get_forecast(steps=steps)
            predictions_mean = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int()
            # Pastikan conf_int dalam bentuk numpy array jika dataframe
            if hasattr(conf_int, "values"):
                conf_int = conf_int.values
        except Exception:
            # Fallback jika model pmdarima atau model yang mendukung predict() / forecast() biasa
            if hasattr(model, "predict"):
                try:
                    preds, conf_int = model.predict(n_periods=steps, return_conf_int=True)
                    predictions_mean = preds
                except Exception:
                    predictions_mean = model.predict(n_periods=steps)
                    conf_int = None
            elif hasattr(model, "forecast"):
                predictions_mean = model.forecast(steps=steps)
                conf_int = None
            else:
                raise ValueError(f"Format model {type(model).__name__} tidak didukung untuk peramalan.")

        if hasattr(predictions_mean, "values"):
            predictions_mean = predictions_mean.values

        return predictions_mean, conf_int

    def _get_recent_history(self, ticker_clean: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        last_historical_date = None
        recent_history: List[Dict[str, Any]] = []

        data_csv = settings.DATA_DIR / f"{ticker_clean}.csv"
        if data_csv.exists():
            try:
                df = pd.read_csv(data_csv)
                if "date" in df.columns and len(df) > 0:
                    last_historical_date = str(df["date"].iloc[-1])
                    recent_history = df.tail(30).to_dict(orient="records")
            except Exception:
                pass

        return last_historical_date, recent_history

    def _generate_future_business_dates(
        self, last_historical_date: Optional[str], steps: int
    ) -> pd.DatetimeIndex:
        if last_historical_date:
            start_dt = pd.to_datetime(last_historical_date) + pd.Timedelta(days=1)
        else:
            start_dt = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))

        return pd.bdate_range(start=start_dt, periods=steps)

forecast_service = ForecastService()
