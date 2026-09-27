from fastapi import APIRouter
from app.models.schemas import ModelsResponse, PredictRequest, PredictResponse
from app.controllers.models_controller import ModelsController

router = APIRouter(prefix="/api", tags=["models"])

@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="Get Models Overview",
    description="Get metadata of all available models",
)
def get_models_overview():
    return ModelsController.get_models_overview()

@router.post(
    "/models/predict",
    response_model=PredictResponse,
    summary="Predict Stock Prices",
    description="Perform stock price forecasting inference",
)
async def predict_stock_price(payload: PredictRequest):
    return await ModelsController.predict_stock_price(payload)
