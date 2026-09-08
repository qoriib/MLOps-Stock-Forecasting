import os
from pathlib import Path
from dotenv import load_dotenv

# Path Direktori
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# Konfigurasi API
API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.goapi.io/stock/idx"
HEADERS = {"accept": "application/json", "X-API-KEY": API_KEY}

# Direktori Artifact
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
MODEL_DIR = ARTIFACT_DIR / "model"
