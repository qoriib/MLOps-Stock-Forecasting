import pickle
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from app.core.config import settings
from app.schemas.model import Model, ModelsResponse

class ModelService:
    def __init__(self):
        self._model_cache: Dict[str, Any] = {}

    def _parse_model_filename(self, filename_stem: str) -> Tuple[str, str]:
        parts = filename_stem.split("_")
        if len(parts) >= 2:
            ticker_symbol = "_".join(parts[:-1])
            model_variant = parts[-1].upper()
            return ticker_symbol, model_variant

        return filename_stem, "SARIMA"

    def load_model(self, ticker: str, model_type: Optional[str] = "sarima") -> Tuple[Any, str]:
        ticker_symbol = ticker.strip().upper()
        selected_type = (model_type or "sarima").strip().lower()

        cache_key = f"{ticker_symbol}:{selected_type}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        if selected_type == "arima":
            target_variant = "ARIMA"
        else:
            target_variant = "SARIMA"

        target_file = settings.MODEL_DIR / f"{ticker_symbol}_{target_variant}.pkl"

        if not target_file.exists():
            if target_variant == "SARIMA":
                target_variant = "ARIMA"
            else:
                target_variant = "SARIMA"

            target_file = settings.MODEL_DIR / f"{ticker_symbol}_{target_variant}.pkl"

        if not target_file.exists():
            raise FileNotFoundError(
                f"Model untuk ticker '{ticker_symbol}' tidak ditemukan di {settings.MODEL_DIR}"
            )

        with open(target_file, "rb") as file_handle:
            model = pickle.load(file_handle)

        cached_result = (model, target_variant)
        self._model_cache[cache_key] = cached_result
        return cached_result

    def get_available_tickers(self) -> List[str]:
        if not settings.MODEL_DIR.exists():
            return []

        tickers_set = set()
        for file_path in settings.MODEL_DIR.glob("*.pkl"):
            ticker_symbol, _ = self._parse_model_filename(file_path.stem)
            if ticker_symbol:
                tickers_set.add(ticker_symbol)

        return sorted(list(tickers_set))

    def get_models(self) -> List[Model]:
        if not settings.MODEL_DIR.exists():
            return []

        model_list: List[Model] = []
        for file_path in sorted(settings.MODEL_DIR.glob("*.pkl")):
            file_stat = file_path.stat()
            ticker_symbol, variant = self._parse_model_filename(file_path.stem)
            modified_time = datetime.fromtimestamp(file_stat.st_mtime).isoformat()

            item = Model(
                ticker=ticker_symbol,
                variant=variant,
                filename=file_path.name,
                model_type=f"{variant} Model",
                file_size_bytes=file_stat.st_size,
                last_modified=modified_time,
            )
            model_list.append(item)

        return model_list

    def get_models_overview(self) -> ModelsResponse:
        tickers = self.get_available_tickers()
        models = self.get_models()

        return ModelsResponse(
            tickers=tickers,
            available_model_types=["sarima", "arima"],
            models=models,
        )

model_service = ModelService()
