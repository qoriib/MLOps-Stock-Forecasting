from typing import Any, Dict, List
from pydantic import BaseModel, Field

class HistoricalStockResponse(BaseModel):
    ticker: str = Field(..., examples=["BBCA.JK"], description="Simbol ticker saham")
    total_records: int = Field(..., examples=[1202], description="Jumlah total baris data yang tersedia di dataset")
    returned_records: int = Field(..., examples=[100], description="Jumlah baris data yang dikembalikan pada request ini")
    data: List[Dict[str, Any]] = Field(
        ...,
        description="Daftar objek data historis (kolom date, open, high, low, close, volume)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "ticker": "BBCA.JK",
                "total_records": 1202,
                "returned_records": 1,
                "data": [
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
