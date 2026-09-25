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
    """Mengambil metadata metrik dan konfigurasi model optimal langsung dari file asset CSV hyperparameter."""
    clean_ticker = ticker.strip().upper()

    # 1. Baca langsung dari file CSV hyperparameter di assets lokal
    csv_candidates = [
        ASSETS_DIR / f"{clean_ticker}_hyperparameter.csv",
        Path("artifact/model") / f"{clean_ticker}_hyperparameter.csv",
    ]
    for csv_file in csv_candidates:
        if csv_file.exists():
            try:
                df_hp = pd.read_csv(csv_file)
                if not df_hp.empty:
                    metrics_summary = {}
                    best_configs = {}
                    best_model_name = "LSTM"
                    min_overall_rmse = float("inf")

                    for m_name in ["LSTM", "GRU"]:
                        sub_df = df_hp[df_hp["model"].str.upper() == m_name]
                        if not sub_df.empty:
                            best_row = sub_df.sort_values("RMSE").iloc[0]
                            rmse_val = float(best_row["RMSE"])
                            mse_val = float(best_row["MSE"])
                            mape_val = float(best_row["MAPE"])
                            ts_val = int(best_row["time_steps"])
                            opt_val = str(best_row["optimizer"])
                            bs_val = int(best_row["batch_size"])
                            lr_val = float(best_row["learning_rate"])

                            eval_obj = ModelVariantMetrics(
                                MSE=mse_val,
                                RMSE=rmse_val,
                                MAPE=mape_val,
                                R2=0.0,
                                time_steps=ts_val,
                                optimizer=opt_val,
                                batch_size=bs_val,
                                learning_rate=lr_val,
                            )
                            metrics_summary[m_name] = eval_obj

                            best_cfg_obj = BestConfigItem(
                                model=m_name,
                                time_steps=ts_val,
                                optimizer=opt_val,
                                batch_size=bs_val,
                                learning_rate=lr_val,
                                RMSE=rmse_val,
                                MAPE=mape_val,
                                MSE=mse_val,
                            )
                            best_configs[m_name] = best_cfg_obj

                            if rmse_val < min_overall_rmse:
                                min_overall_rmse = rmse_val
                                best_model_name = m_name

                    if metrics_summary:
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
            except Exception as ce:
                logger.error(f"Error parsing hyperparameter CSV for {clean_ticker}: {ce}")

    # 2. Fallback ke file JSON di assets jika tersedia
    metrics_file = ASSETS_DIR / f"{clean_ticker}_metrics.json"
    if metrics_file.exists():
        try:
            data = json.loads(metrics_file.read_text(encoding="utf-8"))
            return TickerMetrics(**data)
        except Exception as e:
            logger.error(f"Error reading metrics JSON for {clean_ticker}: {e}")

    logger.warning(f"File metrik hyperparameter tidak ditemukan untuk {clean_ticker}")
    return None


def get_ticker_scaler(ticker: str):
    """Mengambil objek MinMaxScaler dari file asset lokal .pkl (ASSETS_DIR atau artifact/model/)."""
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

    logger.warning(f"Scaler PKL tidak ditemukan di {ASSETS_DIR} untuk {clean_ticker}")
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
