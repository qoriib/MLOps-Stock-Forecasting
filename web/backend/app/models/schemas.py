from typing import List
import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

class HistoricalItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float

class HistoricalResponse(BaseModel):
    ticker: str
    data: List[HistoricalItem]

class PredictRequest(BaseModel):
    ticker: str = Field(
        ...,
        min_length=2,
        max_length=20,
        pattern=r"^[A-Za-z0-9.]+$",
        description="Stock ticker symbol (e.g. BBCA.JK)",
        examples=["BBCA.JK"],
    )
    model: str = Field(
        default="lstm",
        description="Model architecture name ('lstm' or 'gru')",
        examples=["lstm"],
    )
    start_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Start date (YYYY-MM-DD) - Required",
        examples=["2026-09-28"],
    )
    end_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="End date (YYYY-MM-DD) - Required",
        examples=["2026-10-02"],
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, ticker_value: str) -> str:
        clean_ticker = ticker_value.strip().upper()
        if not clean_ticker:
            raise ValueError("Ticker cannot be empty.")
        return clean_ticker

    @field_validator("model")
    @classmethod
    def validate_model(cls, model_value: str) -> str:
        clean_model = model_value.strip().lower()
        valid_models = ["lstm", "gru"]
        if clean_model not in valid_models:
            raise ValueError("model only supports 'lstm' or 'gru'.")
        return clean_model

    @model_validator(mode="after")
    def validate_date_range(self) -> "PredictRequest":
        parsed_start = datetime.date.fromisoformat(self.start_date)
        parsed_end = datetime.date.fromisoformat(self.end_date)
        if parsed_start > parsed_end:
            raise ValueError("start_date cannot be greater than end_date.")
        return self

class PredictionItem(BaseModel):
    date: str
    predicted_price: float

class PredictResponse(BaseModel):
    ticker: str
    model: str
    predictions: List[PredictionItem]

class ModelsResponse(BaseModel):
    tickers: List[str]
    models: List[str]
