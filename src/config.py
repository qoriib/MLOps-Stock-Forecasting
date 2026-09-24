from pathlib import Path

# Path Direktori
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent

# Direktori Artifact
ARTIFACT_DIR = BASE_DIR / "artifact"
DATA_DIR = ARTIFACT_DIR / "data"
MODEL_DIR = ARTIFACT_DIR / "model"
NOTEBOOK_DIR = ARTIFACT_DIR / "notebook"
