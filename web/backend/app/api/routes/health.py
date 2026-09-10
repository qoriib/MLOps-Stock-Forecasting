from datetime import datetime
from fastapi import APIRouter

from app.schemas.health import HealthResponse
from app.services.model_service import model_service

router = APIRouter(tags=["Health & Status"])

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Healthcheck Probe",
    description="Endpoint pemeriksaan kesiapan (*readiness*) dan kesehatan (*liveness*) server yang digunakan oleh Google Cloud Run atau container orchestrator.",
    response_description="Status server beserta jumlah model yang siap melayani inferensi.",
)
def healthcheck():
    """Healthcheck probe untuk Google Cloud Run."""
    available_tickers = model_service.get_available_tickers()
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        models_count=len(available_tickers),
        available_tickers=available_tickers,
    )
