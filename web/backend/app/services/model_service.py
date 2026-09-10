import pickle
from datetime import datetime
from typing import Dict, List, Any
from app.core.config import settings
from app.schemas.model_info import ModelInfo, ModelsResponse

class ModelService:
    def __init__(self):
        self._model_cache: Dict[str, Any] = {}

    def load_model(self, ticker: str) -> Any:
        clean_ticker = ticker.strip().upper()
        if clean_ticker in self._model_cache:
            return self._model_cache[clean_ticker]

        model_dir = settings.MODEL_DIR
        model_file = model_dir / f"{clean_ticker}.pkl"
        if not model_file.exists():
            # Fallback jika ada kecocokan prefix
            candidates = list(model_dir.glob(f"{clean_ticker}*.pkl"))
            if candidates:
                model_file = candidates[0]
            else:
                raise FileNotFoundError(
                    f"Model untuk ticker '{clean_ticker}' tidak ditemukan di {model_dir}"
                )

        with open(model_file, "rb") as f:
            model = pickle.load(f)

        self._model_cache[clean_ticker] = model
        return model

    def get_available_tickers(self) -> List[str]:
        model_dir = settings.MODEL_DIR
        if not model_dir.exists():
            return []
        return sorted([p.stem for p in model_dir.glob("*.pkl")])

    def get_models_info(self) -> List[ModelInfo]:
        model_dir = settings.MODEL_DIR
        if not model_dir.exists():
            return []

        models: List[ModelInfo] = []
        for model_path in model_dir.glob("*.pkl"):
            stat = model_path.stat()
            ticker = model_path.stem
            model_type = "ARIMA/SARIMA"
            try:
                m = self.load_model(ticker)
                model_type = type(m).__name__
            except Exception:
                pass

            models.append(
                ModelInfo(
                    ticker=ticker,
                    filename=model_path.name,
                    model_type=model_type,
                    file_size_bytes=stat.st_size,
                    last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                )
            )
        return models

    def get_models_overview(self) -> ModelsResponse:
        tickers = self.get_available_tickers()
        models = self.get_models_info()
        return ModelsResponse(tickers=tickers, models=models)

model_service = ModelService()
