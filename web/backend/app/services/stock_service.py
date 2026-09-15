import pandas as pd
from app.core.config import settings
from app.schemas.stock import HistoricalStockResponse

class StockService:
    def get_historical_data(
        self,
        ticker: str,
        limit: int = 100,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> HistoricalStockResponse:
        ticker_symbol = ticker.strip().upper()
        file_path = settings.DATA_DIR / f"{ticker_symbol}.csv"

        if not file_path.exists():
            raise FileNotFoundError(f"Data historis untuk '{ticker_symbol}' tidak ditemukan.")

        dataframe = pd.read_csv(file_path)
        total_records = len(dataframe)

        if start_date and end_date:
            dataframe = dataframe[(dataframe["date"] >= start_date) & (dataframe["date"] <= end_date)]
        elif start_date:
            dataframe = dataframe[dataframe["date"] >= start_date]
        elif end_date:
            dataframe = dataframe[dataframe["date"] <= end_date]

        recent_records = dataframe.tail(limit).to_dict(orient="records")

        return HistoricalStockResponse(
            ticker=ticker_symbol,
            total_records=total_records,
            returned_records=len(recent_records),
            data=recent_records,
        )

stock_service = StockService()
