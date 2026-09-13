import os

# Path Direktori
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SRC_DIR)

# Direktori Artifact
ARTIFACT_DIR = os.path.join(BASE_DIR, "artifact")
DATA_DIR = os.path.join(ARTIFACT_DIR, "data")
MODEL_DIR = os.path.join(ARTIFACT_DIR, "model")
