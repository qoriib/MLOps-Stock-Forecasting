import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from app.core.config import settings
from app.schemas.model import Model, ModelsResponse

class ModelService:
    def __init__(self):
        self._model_cache: Dict[str, Any] = {}
        self._scaler_cache: Dict[str, Any] = {}
        self._metrics_cache: Dict[str, Any] = {}

    def _parse_model_filename(self, filename_stem: str) -> Tuple[str, str]:
        parts = filename_stem.split("_")
        if len(parts) >= 2:
            ticker_symbol = "_".join(parts[:-1])
            model_variant = parts[-1].upper()
            return ticker_symbol, model_variant

        return filename_stem, "LSTM"

    def _find_model_file(self, ticker_symbol: str, target_variant: str) -> Optional[Path]:
        """Cari file model dengan ekstensi .keras, .h5, atau .pkl."""
        candidate_extensions = [".keras", ".h5", ".pkl"]
        for ext in candidate_extensions:
            file_path = settings.MODEL_DIR / f"{ticker_symbol}_{target_variant}{ext}"
            if file_path.exists():
                return file_path
        return None

    def load_model(self, ticker: str, model_type: Optional[str] = "lstm") -> Tuple[Any, str]:
        ticker_symbol = ticker.strip().upper()
        selected_type = (model_type or "lstm").strip().lower()

        cache_key = f"{ticker_symbol}:{selected_type}"
        if cache_key in self._model_cache:
            return self._model_cache[cache_key]

        target_variant = selected_type.upper()
        target_file = self._find_model_file(ticker_symbol, target_variant)

        # Fallback jika varian yang diminta tidak ditemukan
        if not target_file:
            fallback_variants = ["LSTM", "GRU", "SARIMA", "ARIMA"]
            for fallback in fallback_variants:
                if fallback != target_variant:
                    target_file = self._find_model_file(ticker_symbol, fallback)
                    if target_file:
                        target_variant = fallback
                        break

        if not target_file:
            raise FileNotFoundError(
                f"Model untuk ticker '{ticker_symbol}' tidak ditemukan di {settings.MODEL_DIR}"
            )

        # Muat model sesuai format file
        if target_file.suffix in [".keras", ".h5"]:
            try:
                import keras
                model = keras.models.load_model(target_file)
            except Exception:
                import tensorflow as tf
                model = tf.keras.models.load_model(target_file)
        else:
            with open(target_file, "rb") as file_handle:
                model = pickle.load(file_handle)

        cached_result = (model, target_variant)
        self._model_cache[cache_key] = cached_result
        return cached_result

    def load_scaler(self, ticker: str) -> Optional[Any]:
        ticker_symbol = ticker.strip().upper()
        if ticker_symbol in self._scaler_cache:
            return self._scaler_cache[ticker_symbol]

        scaler_file = settings.MODEL_DIR / f"{ticker_symbol}_scaler.pkl"
        if not scaler_file.exists():
            return None

        with open(scaler_file, "rb") as file_handle:
            scaler = pickle.load(file_handle)

        self._scaler_cache[ticker_symbol] = scaler
        return scaler

    def load_metrics(self, ticker: str) -> Optional[Dict[str, Any]]:
        ticker_symbol = ticker.strip().upper()
        if ticker_symbol in self._metrics_cache:
            return self._metrics_cache[ticker_symbol]

        metrics_file = settings.MODEL_DIR / f"{ticker_symbol}_metrics.json"
        if not metrics_file.exists():
            return None

        with open(metrics_file, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)

        self._metrics_cache[ticker_symbol] = metrics_data
        return metrics_data

    def _is_model_file(self, file_path: Path) -> bool:
        if file_path.suffix not in [".keras", ".h5", ".pkl"]:
            return False
        # Abaikan file scaler atau artefak non-model lainnya
        if file_path.name.endswith("_scaler.pkl") or file_path.name.endswith("_metrics.json"):
            return False
        return True

    def get_available_tickers(self) -> List[str]:
        if not settings.MODEL_DIR.exists():
            return []

        tickers_set = set()
        for file_path in settings.MODEL_DIR.iterdir():
            if self._is_model_file(file_path):
                ticker_symbol, _ = self._parse_model_filename(file_path.stem)
                if ticker_symbol:
                    tickers_set.add(ticker_symbol)

        return sorted(list(tickers_set))

    def get_models(self) -> List[Model]:
        if not settings.MODEL_DIR.exists():
            return []

        model_list: List[Model] = []
        for file_path in sorted(settings.MODEL_DIR.iterdir()):
            if not self._is_model_file(file_path):
                continue

            file_stat = file_path.stat()
            ticker_symbol, variant = self._parse_model_filename(file_path.stem)
            modified_time = datetime.fromtimestamp(file_stat.st_mtime).isoformat()

            model_type_desc = f"Sequential ({variant})" if variant in ["LSTM", "GRU"] else f"{variant} Model"

            item = Model(
                ticker=ticker_symbol,
                variant=variant,
                filename=file_path.name,
                model_type=model_type_desc,
                file_size_bytes=file_stat.st_size,
                last_modified=modified_time,
            )
            model_list.append(item)

        return model_list

    def get_models_overview(self) -> ModelsResponse:
        tickers = self.get_available_tickers()
        models = self.get_models()

        # Deteksi tipe model yang tersedia berdasarkan file yang ada
        discovered_types = set()
        for m in models:
            discovered_types.add(m.variant.lower())

        available_types = ["lstm", "gru"]
        for t in discovered_types:
            if t not in available_types:
                available_types.append(t)

        return ModelsResponse(
            tickers=tickers,
            available_model_types=available_types,
            models=models,
        )

model_service = ModelService()
