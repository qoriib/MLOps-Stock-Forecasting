from fastapi import APIRouter
from app.models.schemas import ModelsResponse, PredictRequest, PredictResponse
from app.controllers.models_controller import ModelsController

router = APIRouter(prefix="/api", tags=["models"])

@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="Get Models Overview",
    description="Mendapatkan metadata seluruh model",
)
def get_models_overview():
    return ModelsController.get_models_overview()

@router.post(
    "/models/predict",
    response_model=PredictResponse,
    summary="Predict Stock Prices",
    description="Melakukan inferensi peramalan harga saham",
)
def predict_stock_price(payload: PredictRequest):
    return ModelsController.predict_stock_price(payload)
