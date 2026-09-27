from typing import Optional
from fastapi import APIRouter, Path, Query
from app.models.schemas import HistoricalResponse
from app.controllers.stocks_controller import StocksController

router = APIRouter(prefix="/api", tags=["stocks"])

@router.get(
    "/stocks/{ticker}",
    response_model=HistoricalResponse,
    summary="Get Stock Prices",
    description="Retrieve historical OHLCV stock price data for a specific ticker"
)
async def get_stock_data(
    ticker: str = Path(
        ...,
        min_length=2,
        max_length=20,
        pattern=r"^[A-Za-z0-9.]+$",
        description="Stock ticker symbol (e.g. BBCA.JK)",
        examples=["BBCA.JK"],
    ),
    start_date: str = Query(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date filter (YYYY-MM-DD) - Required",
        examples=["2026-01-01"],
    ),
    end_date: str = Query(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date filter (YYYY-MM-DD) - Required",
        examples=["2026-09-25"],
    ),
):
    return await StocksController.get_stock_history(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
    )
