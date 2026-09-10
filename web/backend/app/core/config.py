import os
from pathlib import Path
from typing import Any, Dict, List

def resolve_directory(env_var: str, candidates: List[Path]) -> Path:
    """Resolve directory from environment variable or existing candidates."""
    if os.environ.get(env_var):
        return Path(os.environ[env_var])
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]

class Settings:
    # Metadata API & Dokumentasi OpenAPI
    PROJECT_NAME: str = "MLOps Stock Forecasting API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "REST API inferensi machine learning untuk peramalan harga saham time-series (ARIMA/SARIMA)"

    CONTACT: Dict[str, str] = {
        "name": "MLOps Engineering Team",
        "url": "https://github.com/developer/MLOps-Stock-Forecasting",
        "email": "nashrullah.122140162@student.itera.ac.id",
    }

    LICENSE_INFO: Dict[str, str] = {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    }

    TAGS_METADATA: List[Dict[str, Any]] = [
        {
            "name": "Health & Status",
            "description": "Probe kesiapan server dan navigasi endpoint.",
        },
        {
            "name": "Models",
            "description": "Katalog terpadu ticker saham dan metadata model peramalan.",
        },
        {
            "name": "Predictions",
            "description": "Layanan inferensi peramalan deret waktu masa depan.",
        },
        {
            "name": "Stocks",
            "description": "Data historis harga saham dari artefak CSV.",
        },
    ]

    # Endpoint URL OpenAPI Specification
    OPENAPI_URL: str = "/openapi.json"

    # Base Paths
    CORE_DIR: Path = Path(__file__).resolve().parent
    BACKEND_DIR: Path = CORE_DIR.parent.parent
    ROOT_DIR: Path = BACKEND_DIR.parent.parent

    # Directory Artifacts (Model & Data)
    MODEL_DIR: Path = resolve_directory(
        "MODEL_DIR",
        [
            ROOT_DIR / "artifact" / "model",
            BACKEND_DIR.parent / "artifact" / "model",
            BACKEND_DIR / "artifact" / "model",
            BACKEND_DIR / "model",
            Path("/app/artifact/model"),
            Path("/app/model"),
        ],
    )

    DATA_DIR: Path = resolve_directory(
        "DATA_DIR",
        [
            ROOT_DIR / "artifact" / "data",
            BACKEND_DIR.parent / "artifact" / "data",
            BACKEND_DIR / "artifact" / "data",
            BACKEND_DIR / "data",
            Path("/app/artifact/data"),
            Path("/app/data"),
        ],
    )

    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]

    # Server Configuration
    HOST: str = os.environ.get("HOST", "0.0.0.0")
    PORT: int = int(os.environ.get("PORT", 8080))

settings = Settings()
