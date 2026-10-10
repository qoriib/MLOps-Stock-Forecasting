import asyncio
import datetime
import logging
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf
from app.models.entities import StockMetadata, StockPrice
from app.models.schemas import HistoricalItem, HistoricalResponse
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

_sync_locks: Dict[str, asyncio.Lock] = {}
_last_sync_time: Dict[str, datetime.datetime] = {}
_stock_data_cache: Dict[str, Tuple[datetime.datetime, list]] = {}
SYNC_INTERVAL_SECONDS = 900  # 15 minutes cache debounce
STOCK_CACHE_TTL_SECONDS = 600  # 10 minutes cache TTL

def _fetch_yfinance_history(ticker: str, start_date: Optional[str]) -> Optional[pd.DataFrame]:
    ticker_instance = yf.Ticker(ticker)
    if start_date is not None:
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        dataframe = ticker_instance.history(
            start=start_date,
            end=tomorrow_date.strftime("%Y-%m-%d"),
        )
    else:
        two_years_ago = datetime.date.today() - datetime.timedelta(days=730)
        tomorrow_date = datetime.date.today() + datetime.timedelta(days=1)
        dataframe = ticker_instance.history(
            start=two_years_ago.strftime("%Y-%m-%d"),
            end=tomorrow_date.strftime("%Y-%m-%d"),
        )
    return dataframe

class StockService:
    @classmethod
    async def get_all_cached_prices(cls, ticker: str) -> list:
        clean_ticker = ticker.strip().upper()
        now_time = datetime.datetime.now(datetime.timezone.utc)
        cached = _stock_data_cache.get(clean_ticker)
        if cached is not None:
            cached_time, records = cached
            if (now_time - cached_time).total_seconds() < STOCK_CACHE_TTL_SECONDS:
                return records

        await DatabaseService.ensure_initialized()
        records = await StockPrice.find(
            StockPrice.metadata.ticker == clean_ticker
        ).sort("+timestamp").to_list()

        _stock_data_cache[clean_ticker] = (now_time, records)
        return records

    @classmethod
    async def get_latest_cached_date(cls, ticker: str) -> Optional[datetime.date]:
        cached = _stock_data_cache.get(ticker)
        if cached is not None:
            cached_time, records = cached
            if records and (datetime.datetime.now(datetime.timezone.utc) - cached_time).total_seconds() < STOCK_CACHE_TTL_SECONDS:
                return records[-1].timestamp.date()

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
            dataframe = await asyncio.to_thread(_fetch_yfinance_history, ticker, start_date)

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
            seen_dates = set()

            for item in prepared_records:
                record_date = item["date"]
                if record_date not in existing_timestamps and record_date not in seen_dates:
                    seen_dates.add(record_date)
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
                new_documents.sort(key=lambda d: d.timestamp)
                await StockPrice.insert_many(new_documents)
                _stock_data_cache.pop(ticker.upper(), None)
                logger.info(f"Saved {len(new_documents)} records for {ticker}")
        except Exception as sync_error:
            logger.error(f"Sync failed for {ticker}: {sync_error}")

    @classmethod
    async def ensure_stock_cached(cls, ticker: str) -> None:
        now_time = datetime.datetime.now(datetime.timezone.utc)
        last_attempt = _last_sync_time.get(ticker)
        if last_attempt is not None:
            elapsed = (now_time - last_attempt).total_seconds()
            if elapsed < SYNC_INTERVAL_SECONDS:
                return

        if ticker not in _sync_locks:
            _sync_locks[ticker] = asyncio.Lock()

        async with _sync_locks[ticker]:
            last_attempt = _last_sync_time.get(ticker)
            if last_attempt is not None:
                elapsed = (now_time - last_attempt).total_seconds()
                if elapsed < SYNC_INTERVAL_SECONDS:
                    return

            _last_sync_time[ticker] = now_time

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
        start_date: str,
        end_date: str,
    ) -> Optional[HistoricalResponse]:
        clean_ticker = ticker.strip().upper()
        await cls.ensure_stock_cached(clean_ticker)

        parsed_start = datetime.date.fromisoformat(start_date)
        parsed_end = datetime.date.fromisoformat(end_date)

        all_records = await cls.get_all_cached_prices(clean_ticker)
        if not all_records:
            return None

        seen_dates = set()
        items = []
        for record in all_records:
            record_date = record.timestamp.date()
            if parsed_start <= record_date <= parsed_end:
                date_string = record_date.strftime("%Y-%m-%d")
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

        if not items:
            return None

        return HistoricalResponse(
            ticker=clean_ticker,
            data=items,
        )
