import pickle
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from app.core.config import settings
from app.schemas.model_info import ModelInfo, ModelsResponse

class ModelService:
    def __init__(self):
        self._model_cache: Dict[str, Any] = {}

    def _extract_ticker_and_variant(self, stem: str) -> Tuple[str, str]:
        upper_stem = stem.upper()
        if upper_stem.endswith("_ARIMA"):
            return stem[:-6], "ARIMA"
        elif upper_stem.endswith("_SARIMA"):
            return stem[:-7], "SARIMA"
        else:
            return stem, "SARIMA"

    def load_model(self, ticker: str, model_type: Optional[str] = "sarima") -> Tuple[Any, str]:
        clean_ticker = ticker.strip().upper()
        requested_variant = (model_type or "sarima").strip().lower()

        cache_key = f"{clean_ticker}:{requested_variant}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        model_dir = settings.MODEL_DIR

        # Susun urutan prioritas kandidat file berdasarkan varian yang dipilih
        candidates = []
        resolved_variant = "SARIMA"

        if requested_variant == "arima":
            candidates = [
                model_dir / f"{clean_ticker}_ARIMA.pkl",
            ]
            resolved_variant = "ARIMA"
        elif requested_variant == "sarima":
            candidates = [
                model_dir / f"{clean_ticker}_SARIMA.pkl",
            ]
            resolved_variant = "SARIMA"
        else:
            # Default fallback jika memilih best/auto: utamakan SARIMA lalu ARIMA
            candidates = [
                model_dir / f"{clean_ticker}_SARIMA.pkl",
                model_dir / f"{clean_ticker}_ARIMA.pkl",
            ]
            resolved_variant = "SARIMA"

        # Cari file pertama yang ada di filesystem
        target_file = None
        for cand in candidates:
            if cand.exists():
                target_file = cand
                _, resolved_variant = self._extract_ticker_and_variant(cand.stem)
                break

        # Fallback fleksibel jika belum ditemukan
        if not target_file:
            wildcard_matches = list(model_dir.glob(f"{clean_ticker}*.pkl"))
            if wildcard_matches:
                target_file = wildcard_matches[0]
                _, resolved_variant = self._extract_ticker_and_variant(target_file.stem)
            else:
                raise FileNotFoundError(
                    f"Model '{requested_variant}' untuk ticker '{clean_ticker}' tidak ditemukan di {model_dir}"
                )

        with open(target_file, "rb") as f:
            model = pickle.load(f)

        result = (model, resolved_variant)
        self._model_cache[cache_key] = result
        return result

    def get_available_tickers(self) -> List[str]:
        model_dir = settings.MODEL_DIR
        if not model_dir.exists():
            return []
        
        tickers = set()
        for p in model_dir.glob("*.pkl"):
            base_ticker, _ = self._extract_ticker_and_variant(p.stem)
            if base_ticker:
                tickers.add(base_ticker)
                
        return sorted(list(tickers))

    def get_models_info(self) -> List[ModelInfo]:
        model_dir = settings.MODEL_DIR
        if not model_dir.exists():
            return []

        models: List[ModelInfo] = []
        for model_path in sorted(model_dir.glob("*.pkl")):
            stat = model_path.stat()
            base_ticker, variant = self._extract_ticker_and_variant(model_path.stem)
            model_type = "ARIMA/SARIMA"
            try:
                m, _ = self.load_model(base_ticker, model_type=variant.lower())
                model_type = type(m).__name__
            except Exception:
                pass

            models.append(
                ModelInfo(
                    ticker=base_ticker,
                    variant=variant,
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
        return ModelsResponse(
            tickers=tickers,
            available_model_types=["sarima", "arima"],
            models=models,
        )

model_service = ModelService()

