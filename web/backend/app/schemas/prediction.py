from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class PredictionItem(BaseModel):
    date: str = Field(
        ...,
        examples=["2026-09-15"],
        description="Tanggal peramalan bursa hari kerja (format YYYY-MM-DD)",
    )
    predicted_price: float = Field(
        ...,
        examples=[9850.50],
        description="Estimasi harga saham yang diramalkan oleh model",
    )
    lower_bound: Optional[float] = Field(
        None,
        examples=[9620.25],
        description="Batas bawah interval keyakinan 95% (lower confidence interval)",
    )
    upper_bound: Optional[float] = Field(
        None,
        examples=[10080.75],
        description="Batas atas interval keyakinan 95% (upper confidence interval)",
    )

class PredictRequest(BaseModel):
    ticker: str = Field(
        ...,
        examples=["BBCA.JK"],
        description="Simbol ticker saham IDX (contoh: BBCA.JK atau BBRI.JK)",
    )
    model_type: Optional[str] = Field(
        default="sarima",
        examples=["sarima", "arima"],
        description="Pilihan varian model peramalan: 'sarima' (default) atau 'arima'",
    )
    steps: int = Field(
        default=30,
        ge=1,
        le=180,
        examples=[30],
        description="Jumlah hari kerja langkah peramalan (1 - 180 hari)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BBCA.JK",
                "model_type": "sarima",
                "steps": 30,
            }
        }
    }

class PredictResponse(BaseModel):
    ticker: str = Field(..., examples=["BBCA.JK"], description="Simbol ticker saham")
    model_type: str = Field(
        default="sarima",
        examples=["sarima", "arima"],
        description="Varian model yang digunakan untuk peramalan",
    )
    model_name: str = Field(
        ...,
        examples=["ARIMAResultsWrapper"],
        description="Nama kelas arsitektur model yang digunakan",
    )
    forecast_steps: int = Field(..., examples=[30], description="Jumlah langkah peramalan")
    last_historical_date: Optional[str] = Field(
        None,
        examples=["2026-09-11"],
        description="Tanggal data historis terakhir yang tersedia di dataset",
    )
    predictions: List[PredictionItem] = Field(
        ...,
        description="Daftar item estimasi harga untuk setiap tanggal masa depan",
    )
    history: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Daftar 30 record harga historis terbaru sebelum tanggal peramalan",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BBCA.JK",
                "model_name": "SARIMAXResultsWrapper",
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
