from fastapi import APIRouter
from app.config import (
    APP_RUNTIME,
    AVAILABLE_MODEL_TYPES,
    DEFAULT_MODEL_TYPE,
    DEFAULT_TICKER,
)
from app.models.schemas import ModelsResponse
from app.services.data_service import get_available_tickers, get_ticker_metrics

router = APIRouter(prefix="/api", tags=["models"])


@router.get("/models", response_model=ModelsResponse)
def get_models_overview():
    """Mendapatkan metadata seluruh model dan metrik optimal per ticker."""
    tickers = get_available_tickers()
    model_metrics = {}

    for ticker in tickers:
        metrics = get_ticker_metrics(ticker)
        if metrics:
            model_metrics[ticker] = metrics

    default_ticker = tickers[0] if tickers else DEFAULT_TICKER

    return ModelsResponse(
        tickers=tickers,
        default_ticker=default_ticker,
        default_model_type=DEFAULT_MODEL_TYPE,
        available_model_types=list(AVAILABLE_MODEL_TYPES),
        runtime=APP_RUNTIME,
        model_metrics=model_metrics,
    )
