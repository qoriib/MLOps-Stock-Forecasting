import datetime
from typing import Any, Dict, List, Optional
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
        description="Ticker simbol saham (contoh: BBCA.JK)",
        examples=["BBCA.JK"],
    )
    steps: int = Field(
        default=30,
        ge=1,
        le=180,
        description="Jumlah hari prediksi ke depan (1 s.d. 180 hari)",
    )
    model_type: str = Field(
        default="lstm",
        description="Tipe arsitektur model ('lstm' atau 'gru')",
        examples=["lstm"],
    )
    start_date: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Filter tanggal awal historis (YYYY-MM-DD)",
    )
    end_date: Optional[str] = Field(
        default=None,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Filter tanggal akhir historis (YYYY-MM-DD)",
    )
    history_limit: int = Field(
        default=30,
        ge=5,
        le=500,
        description="Batas riwayat data historis yang disertakan pada response",
    )

    @field_validator("ticker")
    @classmethod
    def validate_ticker(cls, ticker_value: str) -> str:
        clean_ticker = ticker_value.strip().upper()
        if not clean_ticker:
            raise ValueError("Ticker tidak boleh kosong.")
        return clean_ticker

    @field_validator("model_type")
    @classmethod
    def validate_model_type(cls, model_type_value: str) -> str:
        clean_model_type = model_type_value.strip().lower()
        valid_model_types = ["lstm", "gru"]
        if clean_model_type not in valid_model_types:
            raise ValueError("model_type hanya mendukung 'lstm' atau 'gru'.")
        return clean_model_type

    @model_validator(mode="after")
    def validate_date_range(self) -> "PredictRequest":
        if self.start_date is not None and self.end_date is not None:
            parsed_start_date = datetime.date.fromisoformat(self.start_date)
            parsed_end_date = datetime.date.fromisoformat(self.end_date)
            if parsed_start_date > parsed_end_date:
                raise ValueError("start_date tidak boleh lebih besar dari end_date.")
        return self

class PredictionItem(BaseModel):
    date: str
    predicted_price: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None

class ScalerMeta(BaseModel):
    scaler_type: str
    data_min: float
    data_max: float
    data_range: float
    scale: float
    min: float

class BestConfigItem(BaseModel):
    model: str
    time_steps: int
    optimizer: str
    batch_size: int
    learning_rate: float
    MSE: float
    RMSE: float
    MAPE: float
    R2: Optional[float] = 0.0

class ModelVariantMetrics(BaseModel):
    MSE: Optional[float] = None
    RMSE: float
    MAPE: float
    R2: Optional[float] = 0.0
    time_steps: Optional[int] = None
    optimizer: Optional[str] = None
    batch_size: Optional[int] = None
    learning_rate: Optional[float] = None

class TickerMetrics(BaseModel):
    ticker: str
    target_col: Optional[str] = None
    train_size: Optional[float] = None
    random_state: Optional[int] = None
    epochs: Optional[int] = None
    best_model: Optional[str] = None
    best_configs: Optional[Dict[str, BestConfigItem]] = None
    metrics: Dict[str, Optional[ModelVariantMetrics]] = Field(default_factory=dict)

class PredictResponse(BaseModel):
    ticker: str
    model_type: str
    model_name: str
    forecast_steps: int
    window_size: Optional[int] = None
    best_config: Optional[BestConfigItem] = None
    metrics: Optional[ModelVariantMetrics] = None
    last_historical_date: str
    scaler_info: Optional[ScalerMeta] = None
    predictions: List[PredictionItem]
    history: Optional[List[HistoricalItem]] = None

class ModelsResponse(BaseModel):
    tickers: List[str]
    models: List[str]
