from pathlib import Path

# Path Direktori
BASE_DIR = Path(__file__).resolve().parent.parent

# Direktori Artifact
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
MODEL_DIR = ARTIFACT_DIR / "model"

