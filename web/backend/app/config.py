import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
# Assets path can be overridden by ASSETS_DIR environment variable
ASSETS_DIR = Path(os.getenv("ASSETS_DIR", BASE_DIR / "assets"))

# Database & MLOps Tracking Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/stock_db")
MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")

# Application Metadata
APP_NAME = "Stock Forecast Inference API"
APP_VERSION = "2.0.0"
APP_RUNTIME = "Python FastAPI on Azure App Service"

# Forecasting Defaults
DEFAULT_TICKER = "BBCA.JK"
DEFAULT_MODEL_TYPE = "lstm"
AVAILABLE_MODEL_TYPES = ["lstm", "gru"]
DEFAULT_WINDOW_SIZE = 30
DEFAULT_STEPS = 30
DEFAULT_HISTORY_LIMIT = 30
CONFIDENCE_INTERVAL_Z = 1.96  # 95% Confidence Interval
