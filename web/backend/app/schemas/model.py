from typing import List
from pydantic import BaseModel, Field

class Model(BaseModel):
    ticker: str = Field(..., examples=["BBCA.JK"], description="Simbol ticker saham")
    variant: str = Field(default="LSTM", examples=["LSTM", "GRU", "BEST"], description="Varian model peramalan")
    filename: str = Field(..., examples=["BBCA.JK_LSTM.keras"], description="Nama file model")
    model_type: str = Field(..., examples=["Sequential (LSTM)"], description="Tipe arsitektur model")
    file_size_bytes: int = Field(..., examples=[150000], description="Ukuran file dalam bytes")
    last_modified: str = Field(
        ...,
        examples=["2026-09-17T03:00:00"],
        description="Waktu terakhir file dimodifikasi",
    )

class ModelsResponse(BaseModel):
    tickers: List[str] = Field(
        ...,
        examples=[["BBCA.JK", "BBRI.JK"]],
        description="Daftar simbol ticker saham yang tersedia",
    )
    available_model_types: List[str] = Field(
        default=["lstm", "gru"],
        description="Daftar varian model yang tersedia",
    )
    models: List[Model] = Field(
        ...,
        description="Daftar metadata model",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tickers": ["BBCA.JK", "BBRI.JK"],
                "available_model_types": ["lstm", "gru"],
                "models": [
                    {
                        "ticker": "BBCA.JK",
                        "variant": "LSTM",
                        "filename": "BBCA.JK_LSTM.keras",
                        "model_type": "Sequential (LSTM)",
                        "file_size_bytes": 150000,
                        "last_modified": "2026-09-17T03:00:00",
                    }
                ],
            }
        }
    }
