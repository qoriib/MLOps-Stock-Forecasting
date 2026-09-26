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
    def predict_stock_price(payload: PredictRequest) -> PredictResponse:
        try:
            return ModelService.execute_forecast(payload)
        except ValueError as validation_error:
            logger.warning(f"Validation or model asset missing: {validation_error}")
            raise HTTPException(status_code=404, detail=str(validation_error))
        except Exception as unexpected_error:
            logger.error(f"Prediction inference failure: {unexpected_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Terjadi kesalahan saat proses inferensi model: {str(unexpected_error)}",
            )
