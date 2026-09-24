import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import PredictRequest, PredictResponse
from app.services.forecast_service import execute_forecast

logger = logging.getLogger("predict_route")
router = APIRouter(prefix="/api", tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict_stock_price(payload: PredictRequest):
    """Melakukan peramalan harga saham multi-step ke depan."""
    if not payload.ticker:
        raise HTTPException(status_code=400, detail="Field 'ticker' wajib diisi.")

    try:
        result = execute_forecast(payload)
        return result
    except ValueError as e:
        logger.warning(f"Validation error during prediction: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Terjadi kegagalan saat proses inferensi model.")
