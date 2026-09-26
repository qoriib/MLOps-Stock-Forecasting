from typing import Optional
import pandas as pd
from sqlalchemy import select

from app.models.entities import StockPrice
from app.models.schemas import HistoricalItem, HistoricalResponse
from app.services.database_service import DatabaseService


class StockService:
    @classmethod
    def get_stock_history(
        cls,
        ticker: str,
        limit: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Optional[HistoricalResponse]:
        clean_ticker = ticker.strip().upper()
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

            selected_records = records[-limit:]
            items = []
            for record in selected_records:
                item = HistoricalItem(
                    date=record.date.strftime("%Y-%m-%d"),
                    open=float(record.open),
                    high=float(record.high),
                    low=float(record.low),
                    close=float(record.close),
                    volume=float(record.volume),
                )
                items.append(item)

            total_records_count = len(records)
            returned_records_count = len(items)

            return HistoricalResponse(
                ticker=clean_ticker,
                total_records=total_records_count,
                returned_records=returned_records_count,
                data=items,
            )
