from typing import Dict, List
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"], description="Status kesehatan server")
    timestamp: str = Field(
        ...,
        examples=["2026-09-11T01:00:00.000000"],
        description="Waktu pemeriksaan kesehatan dalam format ISO 8601",
    )
    models_count: int = Field(..., examples=[2], description="Jumlah model yang siap digunakan")
    available_tickers: List[str] = Field(
        ...,
        examples=[["BBCA.JK", "BBRI.JK"]],
        description="Daftar simbol ticker saham yang tersedia untuk peramalan",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "healthy",
                "timestamp": "2026-09-11T01:00:00.000000",
                "models_count": 2,
                "available_tickers": ["BBCA.JK", "BBRI.JK"],
            }
        }
    }

class RootResponse(BaseModel):
    status: str = Field(..., examples=["online"], description="Status operasional layanan API")
    service: str = Field(
        ...,
        examples=["MLOps Stock Forecasting Inference API"],
        description="Nama layanan backend",
    )
    openapi_url: str = Field(..., examples=["/openapi.json"], description="Path menuju spesifikasi OpenAPI JSON")
    endpoints: Dict[str, str] = Field(
        ...,
        description="Katalog daftar endpoint utama yang dapat diakses",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "online",
                "service": "MLOps Stock Forecasting Inference API",
                "openapi_url": "/openapi.json",
                "endpoints": {
                    "health": "GET /health",
                    "models": "GET /api/models",
                    "predict": "POST /api/predict",
                    "historical": "GET /api/stocks/{ticker}",
                    "openapi": "GET /openapi.json",
                },
            }
        }
    }
