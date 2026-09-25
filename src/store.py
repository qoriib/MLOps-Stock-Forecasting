import argparse
import os
import json
import logging
import pickle
import shutil
import dvc.api
import numpy as np
import pandas as pd
from pathlib import Path
from src import config

logger = logging.getLogger("store_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def promote_and_store_champion_models(ticker: str) -> None:
    """
    1. Mempromosikan versi model terbaru ke alias @champion dan @production di MLflow Model Registry.
    2. Mengambil scaler dari MLflow Model Registry (seluruhnya dari MLflow) dan menyalin ke backend assets.
    3. Memuat model Keras terbaru dengan alias @champion dari MLflow dan menyalin ke web/backend/assets.
    """
    backend_assets_dir = config.BASE_DIR / "web" / "backend" / "assets"
    backend_assets_dir.mkdir(parents=True, exist_ok=True)

    tracking_uri = getattr(config, "MLFLOW_TRACKING_URI", os.getenv("MLFLOW_TRACKING_URI", ""))
    client = None

    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)
        client = MlflowClient()
    except Exception as e:
        logger.warning(f"[MLflow] Inisialisasi client MLflow dilewati: {e}")

    for model_type in ["LSTM", "GRU"]:
        reg_model_name = f"{ticker}_{model_type}"

        # 1. Promosi ke alias @champion & @production di MLflow Model Registry
        if client is not None:
            try:
                model_versions = client.search_model_versions(f"name = '{reg_model_name}'")
                if model_versions:
                    sorted_versions = sorted(model_versions, key=lambda v: int(v.version))
                    target_version = sorted_versions[-1].version
                    client.set_registered_model_alias(
                        name=reg_model_name,
                        alias="champion",
                        version=target_version,
                    )
                    client.set_registered_model_alias(
                        name=reg_model_name,
                        alias="production",
                        version=target_version,
                    )
                    try:
                        client.transition_model_version_stage(
                            name=reg_model_name,
                            version=target_version,
                            stage="Production",
                        )
                    except Exception:
                        pass
                    logger.info(
                        f"[MLflow Registry] {reg_model_name} versi {target_version} dipromosikan ke alias: @champion & @production"
                    )
            except Exception as me:
                logger.info(f"[MLflow Registry] Model {reg_model_name} belum terdaftar di MLflow ({me})")

        # 2. Muat model Keras terbaru dengan alias @champion dari MLflow
        loaded_model = None
        backend_model_path = backend_assets_dir / f"{ticker}_{model_type}.keras"
        local_model_path = config.get_model_path(ticker, model_type)

        try:
            import mlflow.keras

            model_uri = f"models:/{reg_model_name}@champion"
            logger.info(f"[MLflow] Memuat model Keras champion dari MLflow URI: {model_uri}...")
            loaded_model = mlflow.keras.load_model(model_uri)
            logger.info(f"[MLflow] Berhasil memuat model {reg_model_name}@champion dari MLflow.")
        except Exception:
            # Coba unduh artefak langsung dari MLflow Registry
            try:
                from mlflow.artifacts import download_artifacts

                art_dir = Path(download_artifacts(artifact_uri=f"models:/{reg_model_name}@champion"))
                keras_files = list(art_dir.glob("**/*.keras"))
                if keras_files:
                    import keras

                    loaded_model = keras.models.load_model(keras_files[0])
                    logger.info(f"[MLflow Artifact] Berhasil memuat model dari artefak MLflow: {keras_files[0]}")
            except Exception as ae:
                logger.info(f"[MLflow] Model tidak dapat dimuat dari MLflow ({ae}), beralih ke file lokal.")

        # 3. Salin/simpan model .keras ke backend assets
        if loaded_model is not None:
            try:
                loaded_model.save(backend_model_path)
                logger.info(f"[Backend Asset] Model {reg_model_name} (champion) disimpan ke: {backend_model_path}")
            except Exception as se:
                logger.warning(f"[Backend Asset] Gagal menyimpan model MLflow ({se}), mencoba copy dari disk lokal...")
                if local_model_path.exists():
                    shutil.copy2(local_model_path, backend_model_path)
                    logger.info(f"[Backend Asset] Model {reg_model_name} disalin dari artifact ke: {backend_model_path}")
        elif local_model_path.exists():
            shutil.copy2(local_model_path, backend_model_path)
            logger.info(f"[Backend Asset] Model {reg_model_name} disalin dari artifact ke: {backend_model_path}")
        else:
            logger.warning(f"[Backend Asset] Model {reg_model_name} tidak ditemukan di MLflow maupun artifact lokal.")

    # 4. Ambil scaler sepenuhnya dari MLflow artefak dan simpan ke backend assets
    backend_scaler_path = backend_assets_dir / f"{ticker}_scaler.pkl"
    scaler_saved = False

    for model_type in ["GRU", "LSTM"]:
        reg_model_name = f"{ticker}_{model_type}"
        try:
            from mlflow.artifacts import download_artifacts

            art_dir = Path(download_artifacts(artifact_uri=f"models:/{reg_model_name}@champion"))
            scaler_files = list(art_dir.glob(f"**/{ticker}_scaler.pkl")) or list(art_dir.glob("**/*scaler*.pkl"))
            if scaler_files:
                shutil.copy2(scaler_files[0], backend_scaler_path)
                logger.info(f"[MLflow Scaler] Berhasil mengambil scaler dari MLflow: {scaler_files[0]} -> {backend_scaler_path}")
                scaler_saved = True
                break
        except Exception as e:
            logger.debug(f"[MLflow Scaler] Pencarian scaler di {reg_model_name}@champion dilewati: {e}")

    # Fallback ke artifact/model lokal jika MLflow belum memiliki scaler
    if not scaler_saved:
        local_scaler = config.get_scaler_path(ticker)
        if local_scaler.exists():
            shutil.copy2(local_scaler, backend_scaler_path)
            logger.info(f"[Asset Scaler] Scaler disalin dari artifact lokal ke backend: {backend_scaler_path}")
        else:
            logger.warning(f"[Asset Scaler] Scaler untuk {ticker} tidak ditemukan di MLflow maupun artifact lokal.")

    # 5. Salin file pendukung (hyperparameter & data parquet) ke backend assets untuk kebutuhan bundling
    hyperparam_src = config.get_hyperparameter_path(ticker)
    if hyperparam_src.exists():
        hyperparam_dst = backend_assets_dir / f"{ticker}_hyperparameter.csv"
        shutil.copy2(hyperparam_src, hyperparam_dst)
        logger.info(f"[Backend Asset] Hyperparameter CSV disalin ke: {hyperparam_dst}")

    parquet_src = config.get_data_path(ticker)
    if parquet_src.exists():
        parquet_dst = backend_assets_dir / f"{ticker}.parquet"
        shutil.copy2(parquet_src, parquet_dst)
        logger.info(f"[Backend Asset] Parquet disalin ke: {parquet_dst}")


def main():
    parser = argparse.ArgumentParser(description="Penyimpanan model champion dari MLflow, upsert data, dan promosi model")
    parser.add_argument("--ticker", type=str, help="Ticker spesifik yang ingin diproses")
    args = parser.parse_args()

    params = dvc.api.params_show()
    tickers = [t.strip().upper() for t in params["TICKERS"]]

    tickers_to_process = [args.ticker.strip().upper()] if args.ticker else tickers
    logger.info(f"=== Menjalankan Stage Store untuk: {tickers_to_process} ===")

    for ticker in tickers_to_process:
        # Promosikan model ke @champion di MLflow, ambil scaler & model seluruhnya dari MLflow, dan bundle ke backend assets
        promote_and_store_champion_models(ticker)


if __name__ == "__main__":
    main()
