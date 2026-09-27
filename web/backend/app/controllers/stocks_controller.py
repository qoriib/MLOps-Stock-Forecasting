from fastapi import HTTPException
from app.models.schemas import HistoricalResponse
from app.services.model_service import ModelService
from app.services.stock_service import StockService

class StocksController:
    @staticmethod
    async def get_stock_history(
        ticker: str,
        start_date: str,
        end_date: str,
    ) -> HistoricalResponse:
        clean_ticker = ticker.strip().upper()
        available_tickers, _ = ModelService.get_available_assets()
        
        if clean_ticker not in available_tickers:
            raise HTTPException(
                status_code=404,
                detail=f"Ticker '{clean_ticker}' tidak tersedia dalam model.",
            )

        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="start_date tidak boleh lebih besar dari end_date.",
            )

        history_response = await StockService.get_stock_history(
            ticker=clean_ticker,
            start_date=start_date,
            end_date=end_date,
        )

        if history_response is None or len(history_response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Data harga historis untuk ticker '{clean_ticker}' tidak ditemukan.",
            )

        return history_response
