import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ============================================================
# Inisialisasi Aplikasi FastAPI
# ============================================================
app = FastAPI(
    title="MLOps Stock Forecasting API",
    description="Inference API for time-series stock forecasting models (ARIMA/SARIMA) deployed on Google Cloud Run.",
    version="1.0.0",
)

# CORS Middleware agar dapat diakses oleh frontend manapun
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# Path Discovery (Fleksibel untuk Lokal dan Docker Container)
# ============================================================
CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent

def resolve_directory(env_var: str, candidates: List[Path]) -> Path:
    if os.environ.get(env_var):
        return Path(os.environ[env_var])
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

MODEL_DIR = resolve_directory(
    "MODEL_DIR",
    [
        ROOT_DIR / "artifact" / "model",
        CURRENT_DIR / "artifact" / "model",
        CURRENT_DIR / "model",
        Path("/app/artifact/model"),
        Path("/app/model"),
    ]
)

DATA_DIR = resolve_directory(
    "DATA_DIR",
    [
        ROOT_DIR / "artifact" / "data",
        CURRENT_DIR / "artifact" / "data",
        CURRENT_DIR / "data",
        Path("/app/artifact/data"),
        Path("/app/data"),
    ]
)

# In-memory cache model untuk efisiensi latensi inferensi
_model_cache: Dict[str, object] = {}


def load_model(ticker: str):
    """Memuat model pickled dari direktori model dengan caching."""
    clean_ticker = ticker.strip().upper()
    if clean_ticker in _model_cache:
        return _model_cache[clean_ticker]

    model_file = MODEL_DIR / f"{clean_ticker}.pkl"
    if not model_file.exists():
        # Fallback tanpa ekstensi jika ada
        candidates = list(MODEL_DIR.glob(f"{clean_ticker}*.pkl"))
        if candidates:
            model_file = candidates[0]
        else:
            raise FileNotFoundError(f"Model untuk ticker '{clean_ticker}' tidak ditemukan di {MODEL_DIR}")

    with open(model_file, "rb") as f:
        model = pickle.load(f)

    _model_cache[clean_ticker] = model
    return model


# ============================================================
# Pydantic Schemas
# ============================================================
class PredictionItem(BaseModel):
    date: str
    predicted_price: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None


class PredictRequest(BaseModel):
    ticker: str = Field(..., example="BBCA.JK", description="Simbol ticker saham IDX (contoh: BBCA.JK)")
    steps: int = Field(default=30, ge=1, le=180, description="Jumlah hari kerja langkah peramalan (1 - 180)")


class PredictResponse(BaseModel):
    ticker: str
    model_name: str
    forecast_steps: int
    last_historical_date: Optional[str]
    predictions: List[PredictionItem]


class ModelInfo(BaseModel):
    ticker: str
    filename: str
    model_type: str
    file_size_bytes: int
    last_modified: str


# ============================================================
# API Endpoints
# ============================================================
@app.get("/")
def root():
    """Root info endpoint."""
    return {
        "status": "online",
        "service": "MLOps Stock Forecasting Inference API",
        "docs_url": "/docs",
        "endpoints": {
            "health": "GET /health",
            "list_models": "GET /api/models",
            "predict_post": "POST /api/predict",
            "predict_get": "GET /api/predict/{ticker}",
            "historical": "GET /api/stocks/{ticker}",
        }
    }


@app.get("/health")
def healthcheck():
    """Healthcheck probe untuk Google Cloud Run."""
    available_models = [p.stem for p in MODEL_DIR.glob("*.pkl")] if MODEL_DIR.exists() else []
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_count": len(available_models),
        "available_tickers": available_models,
    }


@app.get("/api/models", response_model=List[ModelInfo])
def list_models():
    """Daftar model time-series yang siap digunakan untuk inferensi."""
    if not MODEL_DIR.exists():
        return []

    models = []
    for model_path in MODEL_DIR.glob("*.pkl"):
        stat = model_path.stat()
        ticker = model_path.stem
        # Coba identifikasi tipe model
        model_type = "ARIMA/SARIMA"
        try:
            m = load_model(ticker)
            model_type = type(m).__name__
        except Exception:
            pass

        models.append(
            ModelInfo(
                ticker=ticker,
                filename=model_path.name,
                model_type=model_type,
                file_size_bytes=stat.st_size,
                last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            )
        )
    return models


@app.post("/api/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """Menghasilkan prediksi harga saham masa depan berdasarkan ticker."""
    ticker_clean = req.ticker.strip().upper()
    steps = req.steps

    try:
        model = load_model(ticker_clean)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memuat model: {e}")

    try:
        forecast_res = model.get_forecast(steps=steps)
        predictions_mean = forecast_res.predicted_mean
        conf_int = forecast_res.conf_int()
    except Exception:
        # Fallback jika model hanya mendukung forecast() biasa
        predictions_mean = model.forecast(steps=steps)
        conf_int = None

    # Tentukan tanggal awal masa depan (hari kerja)
    last_historical_date = None
    data_csv = DATA_DIR / f"{ticker_clean}.csv"
    if data_csv.exists():
        try:
            df = pd.read_csv(data_csv)
            if "date" in df.columns and len(df) > 0:
                last_historical_date = str(df["date"].iloc[-1])
        except Exception:
            pass

    if last_historical_date:
        start_dt = pd.to_datetime(last_historical_date) + pd.Timedelta(days=1)
    else:
        start_dt = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))

    future_dates = pd.bdate_range(start=start_dt, periods=steps)

    items = []
    for i, date_val in enumerate(future_dates):
        pred_val = float(predictions_mean[i])
        lower = float(conf_int[i, 0]) if conf_int is not None else None
        upper = float(conf_int[i, 1]) if conf_int is not None else None

        items.append(
            PredictionItem(
                date=date_val.strftime("%Y-%m-%d"),
                predicted_price=round(pred_val, 2),
                lower_bound=round(lower, 2) if lower is not None else None,
                upper_bound=round(upper, 2) if upper is not None else None,
            )
        )

    return PredictResponse(
        ticker=ticker_clean,
        model_name=type(model).__name__,
        forecast_steps=steps,
        last_historical_date=last_historical_date,
        predictions=items,
    )


@app.get("/api/predict/{ticker}", response_model=PredictResponse)
def predict_get(
    ticker: str,
    steps: int = Query(default=30, ge=1, le=180, description="Jumlah langkah hari kerja")
):
    """Convenience GET endpoint untuk inferensi peramalan."""
    return predict(PredictRequest(ticker=ticker, steps=steps))


@app.get("/api/stocks/{ticker}")
def get_historical_stock(
    ticker: str,
    limit: int = Query(default=100, ge=1, le=2000, description="Maksimal baris data yang diambil")
):
    """Membaca riwayat data saham dari artifact/data/{ticker}.csv untuk visualisasi frontend."""
    ticker_clean = ticker.strip().upper()
    csv_file = DATA_DIR / f"{ticker_clean}.csv"

    if not csv_file.exists():
        raise HTTPException(status_code=404, detail=f"Data historis '{ticker_clean}.csv' tidak ditemukan.")

    df = pd.read_csv(csv_file)
    total_records = len(df)
    df_limited = df.tail(limit).to_dict(orient="records")

    return {
        "ticker": ticker_clean,
        "total_records": total_records,
        "returned_records": len(df_limited),
        "data": df_limited,
    }


# ============================================================
# Main Entry Point untuk Pengujian Langsung
# ============================================================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
