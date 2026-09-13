from fastapi import APIRouter, HTTPException
from app.schemas.prediction import PredictRequest, PredictResponse
from app.services.forecast_service import forecast_service

router = APIRouter(prefix="/api", tags=["Predictions"])

@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Prediksi Harga Saham",
    description="Inferensi peramalan harga saham menggunakan model ARIMA atau SARIMA.",
    response_description="Hasil prediksi harga saham beserta rentang interval keyakinan.",
    responses={
        404: {"description": "Model untuk ticker saham yang diminta tidak ditemukan."},
        500: {"description": "Terjadi kesalahan saat menjalankan inferensi model."},
    },
)
def predict(req: PredictRequest):
    try:
        return forecast_service.predict(
            ticker=req.ticker,
            steps=req.steps,
            model_type=req.model_type,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memproses prediksi: {e}")
