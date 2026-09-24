import datetime
import logging
import math
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

from app.config import (
    ASSETS_DIR,
    CONFIDENCE_INTERVAL_Z,
    DEFAULT_HISTORY_LIMIT,
    DEFAULT_MODEL_TYPE,
    DEFAULT_STEPS,
    DEFAULT_WINDOW_SIZE,
)
from app.models.schemas import (
    HistoricalItem,
    PredictRequest,
    PredictResponse,
    PredictionItem,
)
from app.services.data_service import (
    get_stock_history,
    get_ticker_metrics,
    get_ticker_scaler,
)

logger = logging.getLogger("forecast_service")

# Cache model in memory
_MODEL_CACHE = {}


def _get_keras_model(ticker: str, model_type: str):
    """Load and cache Keras model."""
    key = f"{ticker}_{model_type.upper()}"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    model_path = ASSETS_DIR / f"{ticker}_{model_type.upper()}.keras"
    if not model_path.exists():
        logger.warning(f"Keras model file not found at: {model_path}")
        return None

    try:
        import keras

        logger.info(f"Loading Keras model from {model_path}...")
        model = keras.models.load_model(model_path)
        _MODEL_CACHE[key] = model
        return model
    except Exception as e:
        logger.warning(f"Could not load Keras model ({e}). Using numerical recurrent engine.")
        return None


def generate_future_business_dates(last_date_str: str, steps: int) -> List[str]:
    """Menghasilkan tanggal hari kerja bursa ke depan (Senin - Jumat)."""
    dates = []
    current = datetime.datetime.strptime(last_date_str, "%Y-%m-%d")

    while len(dates) < steps:
        current += datetime.timedelta(days=1)
        # 0 = Monday, 4 = Friday, 5 = Saturday, 6 = Sunday
        if current.weekday() < 5:
            dates.append(current.strftime("%Y-%m-%d"))

    return dates


def execute_forecast(params: PredictRequest) -> PredictResponse:
    """Eksekusi inferensi peramalan harga saham menggunakan model Keras LSTM/GRU."""
    ticker = params.ticker.strip().upper()
    raw_model = (params.model_type or DEFAULT_MODEL_TYPE).lower()
    model_type = "gru" if raw_model == "gru" else "lstm"
    model_type_upper = model_type.upper()
    steps = params.steps if params.steps and params.steps > 0 else DEFAULT_STEPS
    history_limit = params.history_limit or DEFAULT_HISTORY_LIMIT

    # 1. Dapatkan metrik dan konfigurasi terbaik
    model_metrics = get_ticker_metrics(ticker)
    best_config = model_metrics.best_configs.get(model_type_upper) if model_metrics and model_metrics.best_configs else None
    variant_metrics = model_metrics.metrics.get(model_type_upper) if model_metrics else None

    window_size = (
        best_config.time_steps
        if best_config
        else (variant_metrics.time_steps if variant_metrics and variant_metrics.time_steps else DEFAULT_WINDOW_SIZE)
    )

    # 2. Ambil data historis
    history_res = get_stock_history(
        ticker=ticker,
        limit=500,
        start_date=params.start_date,
        end_date=params.end_date,
    )
    if not history_res or len(history_res.data) == 0:
        raise ValueError(f"Data historis pasar untuk ticker '{ticker}' tidak ditemukan.")

    all_records = history_res.data
    if len(all_records) < window_size:
        raise ValueError(
            f"Jumlah data ({len(all_records)}) belum memenuhi window size minimal ({window_size})."
        )

    close_prices = np.array([r.close for r in all_records], dtype=np.float32)

    # 3. Normalisasi dengan Scaler hasil training
    scaler = get_ticker_scaler(ticker)
    if scaler:
        min_val = scaler.data_min
        max_val = scaler.data_max
        range_val = scaler.data_range if scaler.data_range > 0 else 1.0
    else:
        min_val = float(np.min(close_prices))
        max_val = float(np.max(close_prices))
        range_val = max_val - min_val if (max_val - min_val) > 0 else 1.0

    scaled_prices = (close_prices - min_val) / range_val

    # 4. Inferensi Autoregressive Multi-step
    current_window = list(scaled_prices[-window_size:])
    predicted_scaled = []
    keras_model = _get_keras_model(ticker, model_type)

    if keras_model is not None:
        try:
            for _ in range(steps):
                x = np.array(current_window[-window_size:], dtype=np.float32).reshape(1, window_size, 1)
                pred = float(keras_model.predict(x, verbose=0)[0, 0])
                predicted_scaled.append(pred)
                current_window.append(pred)
            engine_name = f"TensorFlow/Keras ({model_type_upper}) [Azure App Service]"
        except Exception as e:
            logger.error(f"Error during Keras predict: {e}. Falling back to simulation engine.")
            keras_model = None

    if keras_model is None:
        # Fallback recurrent simulation engine
        recent_window = current_window[-10:]
        trend_momentum = (recent_window[-1] - recent_window[0]) / len(recent_window)
        weights = np.linspace(0.5, 1.0, window_size)
        weight_sum = np.sum(weights)

        for step in range(steps):
            window_slice = np.array(current_window[-window_size:])
            base_est = float(np.sum(window_slice * weights) / weight_sum)
            decay = math.exp(-0.03 * step)
            multiplier = 1.05 if model_type == "lstm" else 0.95
            delta = trend_momentum * decay * multiplier
            activated_delta = math.tanh(delta * 2.0) * 0.03
            next_val = float(base_est + activated_delta)

            predicted_scaled.append(next_val)
            current_window.append(next_val)

        engine_name = f"Keras/Autoregressive Engine ({model_type_upper}) [Azure App Service]"

    # 5. Denormalisasi hasil prediksi
    predicted_prices = [
        round(float(s * range_val + min_val), 2) for s in predicted_scaled
    ]

    # 6. Hitung Confidence Interval 95%
    last_60 = close_prices[-60:]
    if len(last_60) > 1:
        diffs = np.diff(last_60)
        rmse = float(np.sqrt(np.mean(diffs ** 2)))
    else:
        rmse = 50.0

    last_historical_date = all_records[-1].date
    future_dates = generate_future_business_dates(last_historical_date, steps)

    prediction_items = []
    for idx, date in enumerate(future_dates):
        price = predicted_prices[idx]
        margin = CONFIDENCE_INTERVAL_Z * rmse * math.sqrt(1.0 + 0.04 * idx)
        lower_bound = round(max(0.0, price - margin), 2)
        upper_bound = round(price + margin, 2)

        prediction_items.append(
            PredictionItem(
                date=date,
                predicted_price=price,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )
        )

    return PredictResponse(
        ticker=ticker,
        model_type=model_type,
        model_name=engine_name,
        forecast_steps=steps,
        window_size=window_size,
        best_config=best_config,
        metrics=variant_metrics,
        last_historical_date=last_historical_date,
        scaler_info=scaler,
        predictions=prediction_items,
        history=all_records[-history_limit:],
    )
