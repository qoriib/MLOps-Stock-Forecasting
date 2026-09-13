import os
from pathlib import Path

BASE_DIR = next(
    (p for p in Path(__file__).resolve().parents if (p / "artifact").exists()),
    Path(".")
)

class Settings:
    PROJECT_NAME: str = "MLOps Stock Forecasting API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "REST API inferensi machine learning peramalan harga saham"
    OPENAPI_URL: str = "/openapi.json"

    # Directory Artifacts
    MODEL_DIR: Path = Path(os.getenv("MODEL_DIR", BASE_DIR / "artifact" / "model"))
    DATA_DIR: Path = Path(os.getenv("DATA_DIR", BASE_DIR / "artifact" / "data"))

    # Server & CORS
    CORS_ORIGINS: list[str] = ["*"]
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8080))

settings = Settings()
