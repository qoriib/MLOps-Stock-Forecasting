import logging
from fastapi import HTTPException, status
from app.models.schemas import ModelsResponse, PredictRequest, PredictResponse
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)

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
            logger.warning(f"Ticker '{clean_ticker}' not found in models")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Ticker '{clean_ticker}' not found. Available tickers: {', '.join(available_tickers)}",
            )

        if clean_model not in available_models:
            logger.warning(f"Model '{clean_model}' not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model architecture '{clean_model}' not found. Available models: {', '.join(available_models)}",
            )

        try:
            return await ModelService.execute_forecast(payload)
        except ValueError as validation_error:
            logger.warning(f"Validation error: {validation_error}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(validation_error),
            )
        except Exception as unexpected_error:
            logger.error(f"Inference error: {unexpected_error}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to execute model forecast: {str(unexpected_error)}",
            )
