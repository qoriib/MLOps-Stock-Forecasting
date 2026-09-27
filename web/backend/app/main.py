from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import APP_NAME
from app.services.database_service import DatabaseService
from app.routes.models import router as models_router
from app.routes.stocks import router as stocks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await DatabaseService.init_db()
    yield
    await DatabaseService.close_db()

app = FastAPI(
    title=APP_NAME,
    description="FastAPI Inference Backend for Stock Forecasting",
    lifespan=lifespan,
)

allowed_origins = ["*"]
allowed_methods = ["*"]
allowed_headers = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=allowed_methods,
    allow_headers=allowed_headers,
)

app.include_router(models_router)
app.include_router(stocks_router)

@app.get("/")
def root():
    available_endpoints = {
        "models": "/api/models",
        "predict": "/api/models/predict",
        "stocks": "/api/stocks/{ticker}",
        "docs": "/docs",
    }
    response_payload = {
        "project": APP_NAME,
        "endpoints": available_endpoints,
    }
    return response_payload
