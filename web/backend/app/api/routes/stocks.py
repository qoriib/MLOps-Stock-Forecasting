from fastapi import APIRouter, HTTPException, Path as PathParam, Query
from app.schemas.stock import HistoricalStockResponse
from app.services.stock_service import stock_service

router = APIRouter(prefix="/api", tags=["Stocks"])

@router.get(
    "/stocks/{ticker}",
    response_model=HistoricalStockResponse,
    summary="Ambil Data Riwayat Saham",
    description="Mengambil data historis harga saham berdasarkan simbol ticker.",
    response_description="Data historis harga saham.",
    responses={
        404: {"description": "Data historis untuk ticker yang diminta tidak ditemukan."},
        500: {"description": "Terjadi kesalahan saat membaca data historis."},
    },
)
def get_historical_stock(
    ticker: str = PathParam(
        ...,
        examples=["BBCA.JK"],
        description="Simbol ticker saham.",
    ),
    limit: int = Query(
        default=100,
        ge=1,
        le=2000,
        examples=[100],
        description="Jumlah baris data historis yang diambil.",
    ),
):
    try:
        return stock_service.get_historical_data(ticker=ticker, limit=limit)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat data historis: {e}")
