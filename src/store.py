import argparse
import os
import json
import logging
import pickle
import shutil
import dvc.api
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from src import config
from src.database import upsert_stock_prices, upsert_model_metrics

logger = logging.getLogger("store_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def store_scaler(ticker: str, target_col: str, train_size: float) -> MinMaxScaler:
    """Melatih dan menyimpan scaler MinMaxScaler ke file .pkl (artifact & backend assets)."""
    parquet_path = config.get_data_path(ticker)
    df = pd.read_parquet(parquet_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    train_len = int(len(df) * train_size)
    train_df = df.iloc[:train_len].copy()

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(train_df[[target_col]].values)

    # 1. Simpan di direktori artifact/model
    scaler_path = config.get_scaler_path(ticker)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)
    logger.info(f"[Scaler PKL] Scaler disimpan ke: {scaler_path}")

    # 2. Salin ke web/backend/assets untuk runtime backend
    backend_assets_dir = config.BASE_DIR / "web" / "backend" / "assets"
    backend_assets_dir.mkdir(parents=True, exist_ok=True)
    backend_scaler_path = backend_assets_dir / f"{ticker}_scaler.pkl"
    shutil.copy2(scaler_path, backend_scaler_path)
    logger.info(f"[Asset Scaler] Scaler disalin ke backend: {backend_scaler_path}")

    return scaler


def store_stock_data_to_postgres(ticker: str) -> None:
    """Memasukkan data historis saham dari parquet ke PostgreSQL tanpa redundansi."""
    parquet_path = config.get_data_path(ticker)
    if not parquet_path.exists():
        logger.warning(f"File parquet tidak ditemukan: {parquet_path}")
        return

    df = pd.read_parquet(parquet_path)
    try:
        count = upsert_stock_prices(df, ticker)
        logger.info(f"[PostgreSQL Data] Berhasil upsert {count} baris data saham {ticker} ke tabel stock_prices")
    except Exception as e:
        logger.warning(f"[PostgreSQL Data] Upsert ke PostgreSQL dilewati / error ({e}).")


def promote_models_to_production(ticker: str) -> None:
    """Mempromosikan versi model terbaru ke stage Production di MLflow Model Registry."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        tracking_uri = getattr(config, "MLFLOW_TRACKING_URI", os.getenv("MLFLOW_TRACKING_URI", ""))
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

        client = MlflowClient()

        for model_type in ["LSTM", "GRU"]:
            reg_model_name = f"{ticker}_{model_type}"
            try:
                latest_versions = client.get_latest_versions(reg_model_name)
                if latest_versions:
                    target_version = latest_versions[-1].version
                    client.transition_model_version_stage(
                        name=reg_model_name,
                        version=target_version,
                        stage="Production",
                        archive_existing_versions=True
                    )
                    logger.info(f"[MLflow Registry] {reg_model_name} versi {target_version} dipromosikan ke stage: Production")

                    try:
                        client.set_registered_model_alias(name=reg_model_name, alias="champion", version=target_version)
                        client.set_registered_model_alias(name=reg_model_name, alias="production", version=target_version)
                    except Exception:
                        pass
            except Exception as me:
                logger.info(f"[MLflow Registry] Model {reg_model_name} belum terdaftar di MLflow ({me})")
    except Exception as e:
        logger.warning(f"[MLflow Registry] Promosi model ke Production dilewati ({e})")


def main():
    parser = argparse.ArgumentParser(description="Penyimpanan scaler .pkl, upsert data, dan promosi model MLflow ke Production")
    parser.add_argument("--ticker", type=str, help="Ticker spesifik yang ingin diproses")
    args = parser.parse_args()

    params = dvc.api.params_show()
    tickers = [t.strip().upper() for t in params["TICKERS"]]

    TARGET_COL = params["TARGET_COL"]
    TRAIN_SIZE = float(params["TRAIN_SIZE"])

    tickers_to_process = [args.ticker.strip().upper()] if args.ticker else tickers
    logger.info(f"=== Menjalankan Stage Store untuk: {tickers_to_process} ===")

    for ticker in tickers_to_process:
        # 1. Simpan Scaler tetap berupa file .pkl
        store_scaler(ticker, TARGET_COL, TRAIN_SIZE)

        # 2. Masukkan data historis ke PostgreSQL (tanpa redundansi)
        store_stock_data_to_postgres(ticker)

        # 3. Promosikan model ke stage Production di MLflow Model Registry
        promote_models_to_production(ticker)


if __name__ == "__main__":
    main()
