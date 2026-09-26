import argparse
import logging
import shutil
import mlflow
from mlflow.tracking import MlflowClient
from pathlib import Path
from src import config

logger = logging.getLogger("store_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Inisialisasi MLflow Client 
if config.MLFLOW_TRACKING_URI:
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

client = MlflowClient()

def promote_champion_models(ticker: str) -> None:
    for model_type in config.MODELS:
        reg_model_name = f"{ticker}_{model_type}"

        try:
            versions = client.search_model_versions(f"name = '{reg_model_name}'")
            if not versions:
                continue

            sorted_versions = sorted(versions, key=lambda v: int(v.version))
            latest_version = sorted_versions[-1].version

            client.set_registered_model_alias(reg_model_name, "champion", latest_version)
            logger.info(f"[MLflow] {reg_model_name} v{latest_version} dipromosikan ke @champion")

        except Exception as e:
            logger.info(f"[MLflow] Promosi model {reg_model_name} dilewati: {e}")

def sync_backend_assets(ticker: str) -> None:
    for model_type in config.MODELS:
        reg_model_name = f"{ticker}_{model_type}"
        model_version = client.get_model_version_by_alias(reg_model_name, "champion")

        # Salin Model (.keras)
        src_keras = mlflow.artifacts.download_artifacts(
            artifact_uri=f"models:/{reg_model_name}@champion/data/model.keras"
        )
        dst_keras = config.get_backend_model_path(ticker, model_type)
        shutil.copy2(src_keras, dst_keras)
        logger.info(f"[Backend Asset] Model disalin: {dst_keras.name}")

        # Salin Scaler (.pkl)
        src_scaler = mlflow.artifacts.download_artifacts(
            run_id=model_version.run_id,
            artifact_path=f"scaler/{ticker}_scaler.pkl",
        )
        dst_scaler = config.get_backend_scaler_path(ticker)
        shutil.copy2(src_scaler, dst_scaler)
        logger.info(f"[Backend Asset] Scaler disalin: {dst_scaler.name}")

def main():
    parser = argparse.ArgumentParser(description="Promosi model MLflow")
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Ticker saham yang diproses (misal: BBCA.JK)",
    )

    args = parser.parse_args()
    ticker = args.ticker.strip().upper()

    logger.info(f"=== Menjalankan Stage Store untuk: {ticker} ===")
    promote_champion_models(ticker)
    sync_backend_assets(ticker)
    logger.info(f"=== Selesai Stage Store untuk: {ticker} ===")

if __name__ == "__main__":
    main()
