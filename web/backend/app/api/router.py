from fastapi import APIRouter

from app.api.routes import health, models, predict, stocks

api_router = APIRouter()

# Include all module routers
api_router.include_router(health.router)
api_router.include_router(models.router)
api_router.include_router(predict.router)
api_router.include_router(stocks.router)
