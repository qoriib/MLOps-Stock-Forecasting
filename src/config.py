import os
from dotenv import load_dotenv
from pathlib import Path

# Inisialisasi path dasar proyek
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent

# Muat variabel environment
load_dotenv()

# Direktori penyimpanan artefak pipeline
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
MODEL_DIR = ARTIFACT_DIR / "model"
PLOTS_DIR = ARTIFACT_DIR / "plots"
METRICS_DIR = ARTIFACT_DIR / "metrics"

# Direktori aset aplikasi backend
BACKEND_DIR = BASE_DIR / "web" / "backend"
BACKEND_ASSETS_DIR = BACKEND_DIR / "assets"

# Daftar arsitektur model
MODELS = ["LSTM", "GRU"]

# URL server tracking MLflow
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")


def get_experiment_name(ticker: str) -> str:
    # Format nama eksperimen MLflow berbasis ticker
    return f"Stock-Forecasting-{ticker}"


def get_data_path(ticker: str) -> Path:
    # Pastikan direktori ada dan tentukan path CSV data mentah
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"{ticker}.csv"


def get_prepared_data_path(ticker: str) -> Path:
    # Pastikan direktori ada dan tentukan path file NPZ data siap latih
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"{ticker}_prepared.npz"


def get_plot_path(ticker: str, plot_name: str) -> Path:
    # Pastikan direktori ada dan tentukan path file gambar plot
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    return PLOTS_DIR / f"{ticker}_{plot_name}.png"


def get_metrics_path(ticker: str, stage_name: str) -> Path:
    # Pastikan direktori ada dan tentukan path file JSON metrik
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    return METRICS_DIR / f"{ticker}_{stage_name}.json"


def get_scaler_path(ticker: str) -> Path:
    # Pastikan direktori ada dan tentukan path serialisasi scaler
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"{ticker}_scaler.pkl"


def get_model_path(ticker: str, model_type: str) -> Path:
    # Pastikan direktori ada dan tentukan path model Keras
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"{ticker}_{model_type}.keras"


def get_hyperparameter_path(ticker: str) -> Path:
    # Pastikan direktori ada dan tentukan path rekapitulasi CSV hyperparameter
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    return METRICS_DIR / f"{ticker}_hyperparameter.csv"


def get_backend_model_path(ticker: str, model_type: str) -> Path:
    # Pastikan direktori ada dan tentukan path target model untuk backend
    BACKEND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    return BACKEND_ASSETS_DIR / f"{ticker}_{model_type}.keras"


def get_backend_scaler_path(ticker: str) -> Path:
    # Pastikan direktori ada dan tentukan path target scaler untuk backend
    BACKEND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    return BACKEND_ASSETS_DIR / f"{ticker}_scaler.pkl"
