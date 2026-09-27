import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ASSETS_DIR = BASE_DIR / "assets"
MONGODB_URL = os.getenv("MONGODB_URL") or os.getenv("DATABASE_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "stock_forecasting")

APP_NAME = "Stock Forecast Inference API"
