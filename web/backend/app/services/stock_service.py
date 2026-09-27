import datetime
import logging
from typing import Optional
import pandas as pd
import yfinance as yf
from app.models.entities import StockMetadata, StockPrice
from app.models.schemas import HistoricalItem, HistoricalResponse
from app.services.database_service import DatabaseService

logger = logging.getLogger("stock_service")

class StockService:
    @classmethod
    async def get_latest_cached_date(cls, ticker: str) -> Optional[datetime.date]:
        await DatabaseService.ensure_initialized()
        latest_record = await StockPrice.find(
            StockPrice.metadata.ticker == ticker
        ).sort("-timestamp").first_or_none()

        if latest_record is not None:
            return latest_record.timestamp.date()
        return None

    @classmethod
    async def sync_yfinance_records(cls, ticker: str, start_date: Optional[str] = None) -> None:
        try:
            await DatabaseService.ensure_initialized()
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

            prepared_records = []
            for _, row_data in dataframe.iterrows():
                row_date = row_data["date"]
                record_datetime = datetime.datetime(
                    year=row_date.year,
                    month=row_date.month,
                    day=row_date.day,
                    hour=0,
                    minute=0,
                    second=0,
                    tzinfo=datetime.timezone.utc,
                )
                record_item = {
                    "datetime": record_datetime,
                    "date": row_date,
                    "open": float(row_data["open"]),
                    "high": float(row_data["high"]),
                    "low": float(row_data["low"]),
                    "close": float(row_data["close"]),
                    "volume": float(row_data["volume"]),
                }
                prepared_records.append(record_item)

            if not prepared_records:
                return

            prepared_records.sort(key=lambda item: item["datetime"])

            min_dt = min(item["datetime"] for item in prepared_records)
            max_dt = max(item["datetime"] for item in prepared_records)

            existing_docs = await StockPrice.find(
                StockPrice.metadata.ticker == ticker,
                StockPrice.timestamp >= min_dt,
                StockPrice.timestamp <= max_dt,
            ).to_list()

            existing_timestamps = {doc.timestamp.date() for doc in existing_docs}

            metadata_instance = StockMetadata(ticker=ticker)
            new_documents = []
            for item in prepared_records:
                if item["date"] not in existing_timestamps:
                    new_doc = StockPrice(
                        timestamp=item["datetime"],
                        metadata=metadata_instance,
                        open=item["open"],
                        high=item["high"],
                        low=item["low"],
                        close=item["close"],
                        volume=item["volume"],
                    )
                    new_documents.append(new_doc)

            if new_documents:
                await StockPrice.insert_many(new_documents)
                logger.info(f"Berhasil menyimpan {len(new_documents)} data harga time series untuk {ticker}.")
        except Exception as sync_error:
            logger.error(f"Gagal menyinkronkan data yfinance untuk {ticker}: {sync_error}")

    @classmethod
    async def ensure_stock_cached(cls, ticker: str) -> None:
        latest_date = await cls.get_latest_cached_date(ticker)
        current_today = datetime.date.today()

        if latest_date is None:
            await cls.sync_yfinance_records(ticker=ticker)
        elif latest_date < current_today:
            next_start_date = latest_date + datetime.timedelta(days=1)
            if next_start_date <= current_today:
                await cls.sync_yfinance_records(
                    ticker=ticker,
                    start_date=next_start_date.strftime("%Y-%m-%d"),
                )

    @classmethod
    async def get_stock_history(
        cls,
        ticker: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[HistoricalResponse]:
        clean_ticker = ticker.strip().upper()
        await cls.ensure_stock_cached(clean_ticker)

        query_conditions = [StockPrice.metadata.ticker == clean_ticker]

        if start_date is not None:
            parsed_start_date = pd.to_datetime(start_date).date()
            start_datetime = datetime.datetime(
                parsed_start_date.year,
                parsed_start_date.month,
                parsed_start_date.day,
                0, 0, 0,
                tzinfo=datetime.timezone.utc,
            )
            query_conditions.append(StockPrice.timestamp >= start_datetime)

        if end_date is not None:
            parsed_end_date = pd.to_datetime(end_date).date()
            end_datetime = datetime.datetime(
                parsed_end_date.year,
                parsed_end_date.month,
                parsed_end_date.day,
                23, 59, 59,
                tzinfo=datetime.timezone.utc,
            )
            query_conditions.append(StockPrice.timestamp <= end_datetime)

        records = await StockPrice.find(*query_conditions).sort("+timestamp").to_list()

        if not records:
            return None

        seen_dates = set()
        items = []
        for record in records:
            date_string = record.timestamp.strftime("%Y-%m-%d")
            if date_string in seen_dates:
                continue
            seen_dates.add(date_string)
            item = HistoricalItem(
                date=date_string,
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
