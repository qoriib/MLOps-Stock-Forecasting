import logging
from fastapi import HTTPException
from app.models.schemas import ModelsResponse, PredictRequest, PredictResponse
from app.services.model_service import ModelService

logger = logging.getLogger("models_controller")

class ModelsController:
    @staticmethod
    def get_models_overview() -> ModelsResponse:
        available_tickers, available_models = ModelService.get_available_assets()
        return ModelsResponse(
            tickers=available_tickers,
            models=available_models,
        )

    @staticmethod
    async def predict_stock_price(payload: PredictRequest) -> PredictResponse:
        available_tickers, available_models = ModelService.get_available_assets()
        clean_ticker = payload.ticker.strip().upper()
        clean_model = payload.model.strip().lower()

        if clean_ticker not in available_tickers:
            raise HTTPException(
                status_code=404,
                detail=f"Ticker '{clean_ticker}' tidak tersedia dalam model.",
            )

        if clean_model not in available_models:
            raise HTTPException(
                status_code=404,
                detail=f"Model '{clean_model}' tidak tersedia.",
            )

        try:
            return await ModelService.execute_forecast(payload)
        except ValueError as validation_error:
            logger.warning(f"Validation or data error: {validation_error}")
            raise HTTPException(status_code=400, detail=str(validation_error))
        except Exception as unexpected_error:
            logger.error(f"Prediction inference failure: {unexpected_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Terjadi kesalahan saat proses inferensi model: {str(unexpected_error)}",
            )
