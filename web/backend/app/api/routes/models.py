from fastapi import APIRouter

from app.schemas.model_info import ModelsResponse
from app.services.model_service import model_service

router = APIRouter(prefix="/api", tags=["Models"])


@router.get(
    "/models",
    response_model=ModelsResponse,
    summary="Daftar Ticker & Metadata Model Terpadu",
    description="Endpoint terpadu untuk mendapatkan daftar kode ticker saham IDX yang tersedia beserta rincian teknis seluruh model time-series terlatih.",
    response_description="Objek berisi daftar simbol ticker dan metadata model.",
)
def get_models():
    """Mengambil daftar ticker yang siap inferensi dan detail metadata model."""
    return model_service.get_models_overview()
