import pandas as pd
from app.core.config import settings
from app.schemas.stock import HistoricalStockResponse

class StockService:
    def get_historical_data(self, ticker: str, limit: int = 100) -> HistoricalStockResponse:
        ticker_clean = ticker.strip().upper()
        csv_file = settings.DATA_DIR / f"{ticker_clean}.csv"

        if not csv_file.exists():
            raise FileNotFoundError(f"Data historis '{ticker_clean}.csv' tidak ditemukan.")

        df = pd.read_csv(csv_file)
        total_records = len(df)
        df_limited = df.tail(limit).to_dict(orient="records")

        return HistoricalStockResponse(
            ticker=ticker_clean,
            total_records=total_records,
            returned_records=len(df_limited),
            data=df_limited,
        )

stock_service = StockService()
