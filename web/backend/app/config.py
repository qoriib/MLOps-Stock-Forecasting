import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

ASSETS_DIR = BASE_DIR / "assets"
DATABASE_URL = os.getenv("DATABASE_URL", "")

APP_NAME = "Stock Forecast Inference API"
