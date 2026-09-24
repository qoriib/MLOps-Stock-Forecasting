import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import APP_NAME, APP_RUNTIME, APP_VERSION
from app.routes.models import router as models_router
from app.routes.stocks import router as stocks_router
from app.routes.predict import router as predict_router

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Production-ready FastAPI Inference Backend for Stock Forecasting MLOps on Azure App Service.",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(models_router)
app.include_router(stocks_router)
app.include_router(predict_router)


@app.get("/")
def root():
    return {
        "status": "healthy",
        "project": APP_NAME,
        "version": APP_VERSION,
        "runtime": APP_RUNTIME,
        "endpoints": {
            "health": "/health",
            "models": "/api/models",
            "stocks": "/api/stocks/{ticker}",
            "predict": "/api/predict",
            "docs": "/docs",
        },
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
