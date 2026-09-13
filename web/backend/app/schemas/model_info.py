from typing import List
from pydantic import BaseModel, Field

class ModelInfo(BaseModel):
    ticker: str = Field(..., examples=["BBCA.JK"], description="Simbol ticker saham")
    variant: str = Field(default="BEST", examples=["BEST", "ARIMA", "SARIMA"], description="Varian model peramalan")
    filename: str = Field(..., examples=["BBCA.JK.pkl"], description="Nama file artefak model serial")
    model_type: str = Field(..., examples=["SARIMAXResultsWrapper"], description="Tipe arsitektur model time-series")
    file_size_bytes: int = Field(..., examples=[28045213], description="Ukuran file model dalam satuan bytes")
    last_modified: str = Field(
        ...,
        examples=["2026-09-11T00:30:00"],
        description="Waktu terakhir file model dimodifikasi (ISO 8601)",
    )

class ModelsResponse(BaseModel):
    tickers: List[str] = Field(
        ...,
        examples=[["BBCA.JK", "BBRI.JK"]],
        description="Daftar simbol ticker saham IDX yang tersedia",
    )
    available_model_types: List[str] = Field(
        default=["sarima", "arima"],
        description="Daftar varian model yang dapat dipilih untuk inferensi",
    )
    models: List[ModelInfo] = Field(
        ...,
        description="Rincian informasi metadata dari setiap model yang tersedia",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tickers": ["BBCA.JK", "BBRI.JK"],
                "available_model_types": ["sarima", "arima"],
                "models": [
                    {
                        "ticker": "BBCA.JK",
                        "variant": "SARIMA",
                        "filename": "BBCA.JK_SARIMA.pkl",
                        "model_type": "SARIMAXResultsWrapper",
                        "file_size_bytes": 28045213,
                        "last_modified": "2026-09-11T00:30:00",
                    }
                ],
            }
        }
    }
