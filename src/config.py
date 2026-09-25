import os
from pathlib import Path
from dotenv import load_dotenv

# Path Direktori
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent

# Load environment variables
load_dotenv()

# Direktori Artifact
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
MODEL_DIR = ARTIFACT_DIR / "model"
NOTEBOOK_DIR = ARTIFACT_DIR / "notebook"

# MLflow Tracking
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")

# Database Configuration 
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/stock_db"
)

# Helper Path
def get_data_path(ticker: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR / f"{ticker}.parquet"

def get_scaler_path(ticker: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"{ticker}_scaler.pkl"

def get_model_path(ticker: str, model_type: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"{ticker}_{model_type}.keras"

def get_experiment_name(ticker: str) -> str:
    return f"Stock-Forecasting-{ticker}"

def get_hyperparameter_path(ticker: str) -> Path:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    return MODEL_DIR / f"{ticker}_hyperparameter.csv"
