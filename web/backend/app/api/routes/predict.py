from fastapi import APIRouter, HTTPException

from app.schemas.prediction import PredictRequest, PredictResponse
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/api", tags=["Predictions"])


@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Prediksi Harga Saham Masa Depan",
    description="""
Menjalankan inferensi deret waktu (*time-series forecasting*) menggunakan model ARIMA/SARIMA terlatih.

* **Payload Input**: Simbol ticker saham (`ticker`) dan jumlah langkah hari bursa ke depan (`steps`).
* **Output**: Estimasi harga, rentang keyakinan (95% *confidence interval*), dan 30 rekaman data historis terakhir.
""",
    response_description="Hasil peramalan harga saham beserta batas interval kepercayaan.",
    responses={
        404: {"description": "Model untuk ticker saham yang diminta tidak ditemukan di direktori artefak."},
        500: {"description": "Terjadi kesalahan komputasi saat menjalankan inferensi model."},
    },
)
def predict(req: PredictRequest):
    """Menghasilkan prediksi harga saham masa depan berdasarkan ticker."""
    try:
        return forecast_service.predict(ticker=req.ticker, steps=req.steps)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses prediksi: {e}")
