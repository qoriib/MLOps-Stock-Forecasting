import json
import logging
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from sqlalchemy import select, desc

from app.config import ASSETS_DIR, DEFAULT_TICKER, DATABASE_URL
from app.database import (
    get_db_session,
    StockPrice,
    ModelMetric,
)
from app.models.schemas import (
    HistoricalItem,
    HistoricalResponse,
    ScalerMeta,
    TickerMetrics,
    ModelVariantMetrics,
    BestConfigItem,
)

logger = logging.getLogger("data_service")


def get_available_tickers() -> List[str]:
    """Mendapatkan daftar ticker dari PostgreSQL (fallback ke assets .parquet jika belum ada DB)."""
    # 1. Coba dari PostgreSQL
    try:
        session = get_db_session()
        stmt = select(StockPrice.ticker).distinct().order_by(StockPrice.ticker)
        db_tickers = session.scalars(stmt).all()
        session.close()
        if db_tickers:
            return sorted([str(t).upper() for t in db_tickers])
    except Exception as e:
        logger.warning(f"Gagal mengambil daftar ticker dari PostgreSQL ({e}), mencoba fallback ke assets...")

    # 2. Fallback ke assets directory
    if ASSETS_DIR.exists():
        tickers = []
        for f in ASSETS_DIR.glob("*.parquet"):
            tickers.append(f.stem.upper())
        if tickers:
            return sorted(tickers)

    return [DEFAULT_TICKER]


def get_ticker_metrics(ticker: str) -> Optional[TickerMetrics]:
    """Mengambil metadata metrik dan konfigurasi hyperparameter optimal dari PostgreSQL (fallback ke JSON)."""
    clean_ticker = ticker.strip().upper()

    # 1. Coba dari PostgreSQL
    try:
        session = get_db_session()
        stmt = select(ModelMetric).where(ModelMetric.ticker == clean_ticker)
        db_metrics = session.scalars(stmt).all()
        session.close()

        if db_metrics:
            metrics_summary = {}
            best_configs = {}
            best_model_name = "LSTM"

            for m in db_metrics:
                m_name = m.model_name.upper()
                if m.is_best:
                    best_model_name = m_name

                eval_obj = ModelVariantMetrics(
                    MSE=float(m.mse),
                    RMSE=float(m.rmse),
                    MAPE=float(m.mape),
                    R2=float(m.r2 or 0.0),
                    time_steps=int(m.time_steps),
                    optimizer=str(m.optimizer),
                    batch_size=int(m.batch_size),
                    learning_rate=float(m.learning_rate),
                )
                metrics_summary[m_name] = eval_obj

                best_cfg_obj = BestConfigItem(
                    model=m_name,
                    time_steps=int(m.time_steps),
                    optimizer=str(m.optimizer),
                    batch_size=int(m.batch_size),
                    learning_rate=float(m.learning_rate),
                    RMSE=float(m.rmse),
                    MAPE=float(m.mape),
                    MSE=float(m.mse),
                )
                best_configs[m_name] = best_cfg_obj

            return TickerMetrics(
                ticker=clean_ticker,
                target_col="close",
                train_size=0.8,
                random_state=42,
                epochs=50,
                best_model=best_model_name,
                best_configs=best_configs,
                metrics=metrics_summary,
            )
    except Exception as e:
        logger.warning(f"Gagal membaca metrik dari PostgreSQL ({e}), mencoba fallback ke file JSON...")

    # 2. Fallback ke file JSON di assets
    metrics_file = ASSETS_DIR / f"{clean_ticker}_metrics.json"
    if metrics_file.exists():
        try:
            data = json.loads(metrics_file.read_text(encoding="utf-8"))
            return TickerMetrics(**data)
        except Exception as e:
            logger.error(f"Error reading metrics JSON for {clean_ticker}: {e}")

    return None


def get_ticker_scaler(ticker: str):
    """Mengambil objek MinMaxScaler dari file .pkl (ASSETS_DIR, artifact/model/, atau unduh otomatis dari MLflow)."""
    clean_ticker = ticker.strip().upper()

    candidate_paths = [
        ASSETS_DIR / f"{clean_ticker}_scaler.pkl",
        Path("artifact/model") / f"{clean_ticker}_scaler.pkl",
    ]

    for scaler_path in candidate_paths:
        if scaler_path.exists():
            try:
                with open(scaler_path, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error reading scaler pkl from {scaler_path}: {e}")

    # Fallback: Unduh otomatis dari MLflow jika belum tersedia di disk lokal
    try:
        import mlflow
        from mlflow.artifacts import download_artifacts
        from app.config import MLFLOW_TRACKING_URI

        if MLFLOW_TRACKING_URI:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

        logger.info(f"Mencoba mengunduh artefak scaler untuk {clean_ticker} dari MLflow...")
        downloaded_file = download_artifacts(
            artifact_uri=f"models:/{clean_ticker}_LSTM/Production/scaler/{clean_ticker}_scaler.pkl",
            dst_path=str(ASSETS_DIR)
        )
        if Path(downloaded_file).exists():
            with open(downloaded_file, "rb") as f:
                return pickle.load(f)
    except Exception as e:
        logger.info(f"Fallback download scaler dari MLflow dilewati ({e})")

    logger.warning(f"Scaler PKL tidak ditemukan untuk {clean_ticker}")
    return None


def get_stock_history(
    ticker: str,
    limit: int = 500,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Optional[HistoricalResponse]:
    """Membaca data historis saham langsung dari PostgreSQL (fallback ke .parquet)."""
    clean_ticker = ticker.strip().upper()

    # 1. Coba dari PostgreSQL
    try:
        session = get_db_session()
        query = select(StockPrice).where(StockPrice.ticker == clean_ticker)
        if start_date:
            query = query.where(StockPrice.date >= pd.to_datetime(start_date).date())
        if end_date:
            query = query.where(StockPrice.date <= pd.to_datetime(end_date).date())

        query = query.order_by(StockPrice.date.asc())
        records = session.scalars(query).all()
        session.close()

        if records:
            total_records = len(records)
            sliced_records = records[-limit:] if limit and limit > 0 else records

            items = [
                HistoricalItem(
                    date=r.date.strftime("%Y-%m-%d"),
                    open=float(r.open),
                    high=float(r.high),
                    low=float(r.low),
                    close=float(r.close),
                    volume=float(r.volume),
                )
                for r in sliced_records
            ]

            return HistoricalResponse(
                ticker=clean_ticker,
                total_records=total_records,
                returned_records=len(items),
                data=items,
            )
    except Exception as e:
        logger.warning(f"Gagal membaca stock history dari PostgreSQL ({e}), mencoba fallback ke .parquet...")

    # 2. Fallback ke file .parquet
    candidate_parquets = [
        ASSETS_DIR / f"{clean_ticker}.parquet",
        Path("artifact/data") / f"{clean_ticker}.parquet",
    ]
    for parquet_file in candidate_parquets:
        if parquet_file.exists():
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
                logger.error(f"Error loading stock history from parquet for {clean_ticker}: {e}")

    return None
