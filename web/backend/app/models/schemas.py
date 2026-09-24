from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class HistoricalItem(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class HistoricalResponse(BaseModel):
    ticker: str
    total_records: int
    returned_records: int
    data: List[HistoricalItem]


class PredictRequest(BaseModel):
    ticker: str
    steps: Optional[int] = 30
    model_type: Optional[str] = "lstm"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    history_limit: Optional[int] = 30


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
    default_ticker: str
    default_model_type: str
    available_model_types: List[str]
    runtime: str
    model_metrics: Dict[str, TickerMetrics]
