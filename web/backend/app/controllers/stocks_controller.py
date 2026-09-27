import logging
from fastapi import HTTPException, status
from app.models.schemas import HistoricalResponse
from app.services.model_service import ModelService
from app.services.stock_service import StockService

logger = logging.getLogger(__name__)

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
            logger.warning(f"Ticker '{clean_ticker}' not found in models")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker '{clean_ticker}' not found. Available tickers: {', '.join(available_tickers)}",
            )

        if start_date > end_date:
            logger.warning(f"Invalid date range: {start_date} > {end_date}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid date range: start_date '{start_date}' cannot be after end_date '{end_date}'",
            )

        history_response = await StockService.get_stock_history(
            ticker=clean_ticker,
            start_date=start_date,
            end_date=end_date,
        )

        if history_response is None or len(history_response.data) == 0:
            logger.warning(f"History not found for '{clean_ticker}'")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No historical price data found for ticker '{clean_ticker}' between {start_date} and {end_date}",
            )

        return history_response
