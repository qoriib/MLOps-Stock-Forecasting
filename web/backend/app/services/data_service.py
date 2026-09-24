import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from app.config import ASSETS_DIR, DEFAULT_TICKER
from app.models.schemas import (
    HistoricalItem,
    HistoricalResponse,
    ScalerMeta,
    TickerMetrics,
)

logger = logging.getLogger("data_service")


def get_available_tickers() -> List[str]:
    """Mendapatkan daftar ticker dari file .parquet di folder assets."""
    if not ASSETS_DIR.exists():
        logger.warning(f"Assets directory not found: {ASSETS_DIR}")
        return [DEFAULT_TICKER]

    tickers = []
    for f in ASSETS_DIR.glob("*.parquet"):
        tickers.append(f.stem.upper())

    tickers.sort()
    return tickers if tickers else [DEFAULT_TICKER]


def get_ticker_metrics(ticker: str) -> Optional[TickerMetrics]:
    """Mengambil metadata metrik dan konfigurasi hyperparameter optimal dari {ticker}_metrics.json."""
    clean_ticker = ticker.strip().upper()
    metrics_file = ASSETS_DIR / f"{clean_ticker}_metrics.json"

    if not metrics_file.exists():
        logger.warning(f"Metrics file not found: {metrics_file}")
        return None

    try:
        data = json.loads(metrics_file.read_text(encoding="utf-8"))
        return TickerMetrics(**data)
    except Exception as e:
        logger.error(f"Error reading metrics for {clean_ticker}: {e}")
        return None


def get_ticker_scaler(ticker: str) -> Optional[ScalerMeta]:
    """Mengambil parameter MinMaxScaler dari {ticker}_scaler.json."""
    clean_ticker = ticker.strip().upper()
    scaler_file = ASSETS_DIR / f"{clean_ticker}_scaler.json"

    if not scaler_file.exists():
        logger.warning(f"Scaler file not found: {scaler_file}")
        return None

    try:
        data = json.loads(scaler_file.read_text(encoding="utf-8"))
        return ScalerMeta(
            scaler_type=data.get("scaler_type", "MinMaxScaler"),
            data_min=float(data["data_min"]),
            data_max=float(data["data_max"]),
            data_range=float(data["data_range"]),
            scale=float(data["scale"]),
            min=float(data["min"]),
        )
    except Exception as e:
        logger.error(f"Error reading scaler for {clean_ticker}: {e}")
        return None


def get_stock_history(
    ticker: str,
    limit: int = 500,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Optional[HistoricalResponse]:
    """Membaca data historis saham langsung dari file .parquet."""
    clean_ticker = ticker.strip().upper()
    parquet_file = ASSETS_DIR / f"{clean_ticker}.parquet"

    if not parquet_file.exists():
        logger.warning(f"Parquet file not found: {parquet_file}")
        return None

    try:
        df = pd.read_parquet(parquet_file)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df = df.sort_values("date").reset_index(drop=True)

        if start_date:
            df = df[df["date"] >= start_date]
        if end_date:
            df = df[df["date"] <= end_date]

        total_records = len(df)
        sliced_df = df.tail(limit)

        items = [
            HistoricalItem(
                date=str(row["date"]),
                open=float(row.get("open", 0.0)),
                high=float(row.get("high", 0.0)),
                low=float(row.get("low", 0.0)),
                close=float(row.get("close", 0.0)),
                volume=float(row.get("volume", 0.0)),
            )
            for _, row in sliced_df.iterrows()
        ]

        return HistoricalResponse(
            ticker=clean_ticker,
            total_records=total_records,
            returned_records=len(items),
            data=items,
        )
    except Exception as e:
        logger.error(f"Error loading stock history for {clean_ticker}: {e}")
        return None
