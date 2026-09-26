from typing import Optional
from fastapi import HTTPException
from app.models.schemas import HistoricalResponse
from app.services.stock_service import StockService

class StocksController:
    @staticmethod
    def get_stock_history(
        ticker: str,
        limit: int = 500,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> HistoricalResponse:
        clean_ticker = ticker.strip().upper()
        history_response = StockService.get_stock_history(
            clean_ticker,
            limit=limit,
            start_date=start_date,
            end_date=end_date,
        )

        if history_response is None or len(history_response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Data harga historis untuk ticker '{clean_ticker}' tidak ditemukan.",
            )

        return history_response
