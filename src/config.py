from pathlib import Path

# Path Direktori
BASE_DIR = Path(__file__).resolve().parent.parent

# Direktori Artifact
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
FORECAST_DIR = ARTIFACT_DIR / "forecast"
MODEL_DIR = ARTIFACT_DIR / "model"
SEED_SQL_PATH = ARTIFACT_DIR / "seed.sql"
