from fastapi import APIRouter
from app.api.routes import models, predict, stocks

api_router = APIRouter()

api_router.include_router(models.router)
api_router.include_router(predict.router)
api_router.include_router(stocks.router)
