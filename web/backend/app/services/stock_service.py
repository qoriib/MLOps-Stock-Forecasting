import datetime
import pandas as pd
import yfinance as yf
from typing import Optional
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from app.models.entities import StockPrice
from app.models.schemas import HistoricalItem, HistoricalResponse
from app.services.database_service import DatabaseService

class StockService:
    @classmethod
    def get_latest_cached_date(cls, ticker: str) -> Optional[datetime.date]:
        with DatabaseService.session_scope() as database_session:
            query = select(func.max(StockPrice.date)).where(StockPrice.ticker == ticker)
            latest_date = database_session.scalar(query)
            return latest_date

    @classmethod
    def sync_yfinance_records(cls, ticker: str, start_date: Optional[str] = None) -> None:
        try:
            ticker_instance = yf.Ticker(ticker)
            if start_date is not None:
                tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
                dataframe = ticker_instance.history(
                    start=start_date,
                    end=tomorrow_date.strftime("%Y-%m-%d"),
                )
            else:
                dataframe = ticker_instance.history(period="2y")

            if dataframe is None or dataframe.empty:
                return

            dataframe = dataframe.reset_index()
            dataframe.columns = [str(column_name).lower() for column_name in dataframe.columns]
            dataframe["date"] = pd.to_datetime(dataframe["date"]).dt.date
            dataframe = dataframe.drop_duplicates(subset=["date"])

            records = []
            for row_index, row_data in dataframe.iterrows():
                record_entry = {
                    "ticker": ticker,
                    "date": row_data["date"],
                    "open": float(row_data["open"]),
                    "high": float(row_data["high"]),
                    "low": float(row_data["low"]),
                    "close": float(row_data["close"]),
                    "volume": float(row_data["volume"]),
                }
                records.append(record_entry)

            if records:
                with DatabaseService.session_scope() as database_session:
                    insert_statement = postgres_insert(StockPrice).values(records)
                    upsert_statement = insert_statement.on_conflict_do_update(
                        index_elements=["ticker", "date"],
                        set_={
                            "open": insert_statement.excluded.open,
                            "high": insert_statement.excluded.high,
                            "low": insert_statement.excluded.low,
                            "close": insert_statement.excluded.close,
                            "volume": insert_statement.excluded.volume,
                        },
                    )
                    database_session.execute(upsert_statement)
        except Exception:
            return

    @classmethod
    def ensure_stock_cached(cls, ticker: str) -> None:
        latest_date = cls.get_latest_cached_date(ticker)
        current_today = datetime.date.today()

        if latest_date is None:
            cls.sync_yfinance_records(ticker=ticker)
        elif latest_date < current_today:
            next_start_date = latest_date + datetime.timedelta(days=1)
            if next_start_date <= current_today:
                cls.sync_yfinance_records(
                    ticker=ticker,
                    start_date=next_start_date.strftime("%Y-%m-%d"),
                )

    @classmethod
    def get_stock_history(
        cls,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[HistoricalResponse]:
        clean_ticker = ticker.strip().upper()
        cls.ensure_stock_cached(clean_ticker)

        with DatabaseService.session_scope() as database_session:
            query = select(StockPrice).where(StockPrice.ticker == clean_ticker)
            if start_date is not None:
                parsed_start_date = pd.to_datetime(start_date).date()
                query = query.where(StockPrice.date >= parsed_start_date)
            if end_date is not None:
                parsed_end_date = pd.to_datetime(end_date).date()
                query = query.where(StockPrice.date <= parsed_end_date)

            query = query.order_by(StockPrice.date.asc())
            records = database_session.scalars(query).all()

            if not records:
                return None

            items = []
            for record in records:
                item = HistoricalItem(
                    date=record.date.strftime("%Y-%m-%d"),
                    open=float(record.open),
                    high=float(record.high),
                    low=float(record.low),
                    close=float(record.close),
                    volume=float(record.volume),
                )
                items.append(item)

            return HistoricalResponse(
                ticker=clean_ticker,
                data=items,
            )
