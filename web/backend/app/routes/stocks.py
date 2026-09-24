from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import HistoricalResponse
from app.services.data_service import get_stock_history

router = APIRouter(prefix="/api", tags=["stocks"])


@router.get("/stocks/{ticker}", response_model=HistoricalResponse)
def get_stock_data(
    ticker: str,
    limit: int = Query(default=500, ge=1, le=2000),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    """Mendapatkan data historis harga saham untuk ticker tertentu."""
    history = get_stock_history(ticker, limit=limit, start_date=start_date, end_date=end_date)
    if not history:
        raise HTTPException(
            status_code=404,
            detail=f"Data saham untuk ticker '{ticker}' tidak ditemukan.",
        )
    return history
