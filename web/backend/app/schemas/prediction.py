from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PredictionItem(BaseModel):
    date: str = Field(
        ...,
        examples=["2026-09-15"],
        description="Tanggal peramalan (format YYYY-MM-DD)",
    )
    predicted_price: float = Field(
        ...,
        examples=[9850.50],
        description="Estimasi harga saham yang diramalkan",
    )
    lower_bound: Optional[float] = Field(
        None,
        examples=[9620.25],
        description="Batas bawah interval keyakinan 95%",
    )
    upper_bound: Optional[float] = Field(
        None,
        examples=[10080.75],
        description="Batas atas interval keyakinan 95%",
    )

class PredictRequest(BaseModel):
    ticker: str = Field(
        ...,
        examples=["BBCA.JK"],
        description="Simbol ticker saham",
    )
    model_type: Optional[str] = Field(
        default="lstm",
        examples=["lstm", "gru"],
        description="Varian model: lstm atau gru",
    )
    steps: int = Field(
        default=30,
        ge=1,
        le=180,
        examples=[30],
        description="Jumlah hari kerja langkah peramalan",
    )
    start_date: Optional[str] = Field(
        default=None,
        examples=["2026-08-01"],
        description="Batas awal tanggal riwayat yang disertakan",
    )
    end_date: Optional[str] = Field(
        default=None,
        examples=["2026-09-02"],
        description="Batas akhir tanggal riwayat yang disertakan",
    )
    history_limit: Optional[int] = Field(
        default=30,
        ge=5,
        le=1000,
        examples=[30],
        description="Jumlah baris data historis maksimal yang disertakan",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BBCA.JK",
                "model_type": "lstm",
                "steps": 30,
                "start_date": "2026-08-01",
                "end_date": "2026-09-02",
            }
        }
    }

class PredictResponse(BaseModel):
    ticker: str = Field(..., examples=["BBCA.JK"], description="Simbol ticker saham")
    model_type: str = Field(
        default="lstm",
        examples=["lstm", "gru"],
        description="Varian model yang digunakan",
    )
    model_name: str = Field(
        ...,
        examples=["Sequential (LSTM)"],
        description="Nama arsitektur model yang digunakan",
    )
    forecast_steps: int = Field(..., examples=[30], description="Jumlah langkah peramalan")
    last_historical_date: Optional[str] = Field(
        None,
        examples=["2026-09-11"],
        description="Tanggal data historis terakhir",
    )
    predictions: List[PredictionItem] = Field(
        ...,
        description="Daftar estimasi harga masa depan",
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Daftar 30 record harga historis terbaru",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BBCA.JK",
                "model_type": "lstm",
                "model_name": "Sequential (LSTM)",
                "forecast_steps": 2,
                "last_historical_date": "2026-09-11",
                "predictions": [
                    {
                        "date": "2026-09-14",
                        "predicted_price": 9850.5,
                        "lower_bound": 9620.25,
                        "upper_bound": 10080.75,
                    },
                    {
                        "date": "2026-09-15",
                        "predicted_price": 9890.0,
                        "lower_bound": 9640.0,
                        "upper_bound": 10140.0,
                    },
                ],
                "history": [
                    {
                        "date": "2026-09-11",
                        "open": 9800.0,
                        "high": 9900.0,
                        "low": 9750.0,
                        "close": 9825.0,
                        "volume": 45000000,
                    }
                ],
            }
        }
    }
