from fastapi import APIRouter, HTTPException, Path as PathParam, Query

from app.schemas.stock import HistoricalStockResponse
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api", tags=["Stocks"])


@router.get(
    "/stocks/{ticker}",
    response_model=HistoricalStockResponse,
    summary="Ambil Data Riwayat Saham Historis",
    description="Membaca dan mengambil sejumlah `limit` baris rekaman historis harga saham dari file artefak CSV (`artifact/data/{ticker}.csv`).",
    response_description="Objek berisi jumlah total rekaman dan deretan data historis (open, high, low, close, volume).",
    responses={
        404: {"description": "File dataset CSV untuk ticker saham yang diminta tidak ditemukan."},
        500: {"description": "Gagal membaca atau mem-parsing file CSV."},
    },
)
def get_historical_stock(
    ticker: str = PathParam(
        ...,
        examples=["BBCA.JK"],
        description="Simbol ticker saham IDX yang ingin diambil riwayat datanya",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=2000,
        examples=[100],
        description="Maksimal baris data terbaru yang diambil untuk chart visualisasi",
    ),
):
    """Membaca riwayat data saham dari artifact/data/{ticker}.csv untuk visualisasi frontend."""
    try:
        return stock_service.get_historical_data(ticker=ticker, limit=limit)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data historis: {e}")
