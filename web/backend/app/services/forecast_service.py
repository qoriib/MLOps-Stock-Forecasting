import datetime
import logging
import math
import os
from pathlib import Path
from typing import Any, List, Optional, Tuple

import numpy as np
import pandas as pd

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
    ScalerMeta,
)
from app.services.data_service import (
    get_stock_history,
    get_ticker_metrics,
    get_ticker_scaler,
)

logger = logging.getLogger("forecast_service")

# Cache model in memory: key -> (model, engine_label)
_MODEL_CACHE = {}


def _get_forecast_model(ticker: str, model_type: str) -> Tuple[Optional[Any], str]:
    """
    Memuat model Keras murni langsung dari asset lokal (ASSETS_DIR) yang disimpan oleh store.py.
    """
    key = f"{ticker}_{model_type.upper()}"
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key]

    candidate_model_paths = [
        ASSETS_DIR / f"{key}.keras",
        Path("artifact/model") / f"{key}.keras",
    ]

    for p in candidate_model_paths:
        if p.exists():
            try:
                import keras

                local_keras = keras.models.load_model(p)
                engine_desc = f"Local Keras Model ({model_type.upper()}) [Asset: {p.name}]"
                _MODEL_CACHE[key] = (local_keras, engine_desc)
                logger.info(f"Model Keras lokal berhasil dimuat dari: {p}")
                return _MODEL_CACHE[key]
            except Exception as ke:
                logger.warning(f"Gagal memuat file Keras lokal {p}: {ke}")

    logger.warning(
        f"File model {key}.keras tidak ditemukan di asset lokal ({ASSETS_DIR}). Menggunakan mesin peramalan simulasi."
    )
    return (None, f"Numerical Recurrent Simulation Engine ({model_type.upper()}) [Fallback]")


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
    """Eksekusi inferensi peramalan harga saham multi-step langsung menggunakan Keras Model dan MinMaxScaler."""
    ticker = params.ticker.strip().upper()
    raw_model = (params.model_type or DEFAULT_MODEL_TYPE).lower()
    model_type = "gru" if raw_model == "gru" else "lstm"
    model_type_upper = model_type.upper()
    steps = params.steps if params.steps and params.steps > 0 else DEFAULT_STEPS
    history_limit = params.history_limit or DEFAULT_HISTORY_LIMIT

    # 1. Dapatkan metrik dan konfigurasi terbaik
    model_metrics = get_ticker_metrics(ticker)
    best_config = (
        model_metrics.best_configs.get(model_type_upper)
        if model_metrics and model_metrics.best_configs
        else None
    )
    variant_metrics = model_metrics.metrics.get(model_type_upper) if model_metrics else None

    window_size = (
        best_config.time_steps
        if best_config
        else (variant_metrics.time_steps if variant_metrics and variant_metrics.time_steps else DEFAULT_WINDOW_SIZE)
    )

    # 2. Ambil data historis pasar
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

    # Harga penutupan asli (Rp)
    close_prices = np.array([r.close for r in all_records], dtype=np.float32)

    # 3. Eksekusi inferensi peramalan multi-step
    forecast_model, engine_name = _get_forecast_model(ticker, model_type)
    scaler = get_ticker_scaler(ticker)

    predicted_prices = []
    current_window_raw = list(close_prices[-window_size:])

    if forecast_model is not None and scaler is not None:
        try:
            for _ in range(steps):
                # Ambil window terakhir sebesar window_size (harga asli Rp)
                window_raw = np.array(current_window_raw[-window_size:], dtype=np.float32).reshape(-1, 1)

                # 1. Normalisasi fitur dengan Scaler (0, 1)
                window_scaled = scaler.transform(window_raw)

                # 2. Bentuk input 3D: (1, time_steps, 1)
                input_3d = window_scaled.reshape(1, window_size, 1)

                # 3. Prediksi menggunakan Keras model
                pred_scaled = forecast_model.predict(input_3d, verbose=0)

                # 4. Inverse transform kembali ke harga asli Rupiah
                pred_price_arr = scaler.inverse_transform(pred_scaled)
                pred_price = float(pred_price_arr.flatten()[0])

                predicted_prices.append(pred_price)
                current_window_raw.append(pred_price)
        except Exception as e:
            logger.error(
                f"Error saat inferensi Keras untuk {ticker}: {e}. Beralih ke mesin simulasi.",
                exc_info=True,
            )
            forecast_model = None
            predicted_prices = []
            current_window_raw = list(close_prices[-window_size:])

    if forecast_model is None:
        # Fallback recurrent simulation engine langsung pada harga asli
        recent_window = current_window_raw[-10:]
        trend_momentum = (recent_window[-1] - recent_window[0]) / len(recent_window)
        weights = np.linspace(0.5, 1.0, window_size)
        weight_sum = np.sum(weights)

        for step in range(steps):
            window_slice = np.array(current_window_raw[-window_size:])
            base_est = float(np.sum(window_slice * weights) / weight_sum)
            decay = math.exp(-0.03 * step)
            multiplier = 1.05 if model_type == "lstm" else 0.95
            delta = trend_momentum * decay * multiplier
            activated_delta = math.tanh(delta / (base_est * 0.01 + 1e-6)) * (base_est * 0.005)
            next_val = float(base_est + activated_delta)

            predicted_prices.append(next_val)
            current_window_raw.append(next_val)

        engine_name = f"Numerical Recurrent Simulation Engine ({model_type_upper}) [Fallback]"

    # 4. Ambil metadata Scaler untuk respons API (jika tersedia)
    scaler = get_ticker_scaler(ticker)
    if scaler is not None and hasattr(scaler, "data_min_"):
        scaler_meta = ScalerMeta(
            scaler_type="MinMaxScaler",
            data_min=float(scaler.data_min_[0]),
            data_max=float(scaler.data_max_[0]),
            data_range=float(scaler.data_range_[0]) if scaler.data_range_[0] > 0 else 1.0,
            scale=float(scaler.scale_[0]),
            min=float(scaler.min_[0]),
        )
    else:
        scaler_meta = None

    # 5. Hitung Confidence Interval 95%
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
        price = round(float(predicted_prices[idx]), 2)
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
        scaler_info=scaler_meta,
        predictions=prediction_items,
        history=all_records[-history_limit:],
    )
