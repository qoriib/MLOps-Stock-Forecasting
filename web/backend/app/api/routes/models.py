from fastapi import APIRouter
from app.schemas.model import ModelsResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["Models"])

@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="Daftar Model dan Ticker",
    description="Mengambil daftar ticker saham dan metadata model yang tersedia.",
    response_description="Daftar ticker dan metadata model.",
)
def get_models():
    return model_service.get_models_overview()
