import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from app.core.config import settings
from app.schemas.prediction import PredictionItem, PredictResponse
from app.services.model_service import model_service

class ForecastService:
    def predict(self, ticker: str, steps: int = 30, model_type: Optional[str] = "sarima") -> PredictResponse:
        ticker_symbol = ticker.strip().upper()
        model, resolved_variant = model_service.load_model(ticker_symbol, model_type=model_type)

        predictions_mean, conf_int = self._calculate_forecast(model, steps)
        last_date, recent_history = self._get_recent_history(ticker_symbol)
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

        return PredictResponse(
            ticker=ticker_symbol,
            model_type=resolved_variant.lower(),
            model_name=type(model).__name__,
            forecast_steps=steps,
            last_historical_date=last_date,
            predictions=prediction_items,
            history=recent_history,
        )

    def _calculate_forecast(self, model: Any, steps: int) -> Tuple[Any, Optional[Any]]:
        # Format model pmdarima (auto_arima)
        if hasattr(model, "predict"):
            predictions, conf_intervals = model.predict(n_periods=steps, return_conf_int=True)
            return predictions, conf_intervals

        # Format model statsmodels
        forecast_result = model.get_forecast(steps=steps)
        predictions = forecast_result.predicted_mean
        conf_intervals = forecast_result.conf_int()

        if hasattr(conf_intervals, "values"):
            conf_intervals = conf_intervals.values

        if hasattr(predictions, "values"):
            predictions = predictions.values

        return predictions, conf_intervals

    def _get_recent_history(self, ticker_symbol: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
        csv_file_path = settings.DATA_DIR / f"{ticker_symbol}.csv"
        if not csv_file_path.exists():
            return None, []

        dataframe = pd.read_csv(csv_file_path)
        if dataframe.empty or "date" not in dataframe.columns:
            return None, []

        last_date_record = str(dataframe["date"].iloc[-1])
        recent_records = dataframe.tail(30).to_dict(orient="records")
        return last_date_record, recent_records

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
