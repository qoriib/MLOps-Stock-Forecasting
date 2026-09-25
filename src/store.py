import argparse
import logging
import shutil
import mlflow
from mlflow.tracking import MlflowClient
from src import config

logger = logging.getLogger("store_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def promote_champion_models(ticker: str) -> None:
    try:
        if config.MLFLOW_TRACKING_URI:
            mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

        client = MlflowClient()

        for model_type in config.MODELS:
            reg_model_name = f"{ticker}_{model_type}"
            versions = client.search_model_versions(f"name = '{reg_model_name}'")

            if versions:
                latest_v = sorted(versions, key=lambda v: int(v.version))[-1].version
                client.set_registered_model_alias(reg_model_name, "champion", latest_v)
                logger.info(f"[MLflow] {reg_model_name} v{latest_v} dipromosikan ke @champion")

    except Exception as e:
        logger.info(f"[MLflow] Promosi model {ticker} dilewati: {e}")

def sync_backend_assets(ticker: str) -> None:
    config.BACKEND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # Salin Model
    for model_type in config.MODELS:
        src_model = config.get_model_path(ticker, model_type)
        dst_model = config.get_backend_model_path(ticker, model_type)
        if src_model.exists():
            shutil.copy2(src_model, dst_model)
            logger.info(f"[Backend Asset] Model disalin: {dst_model.name}")

    # Salin Scaler
    src_scaler = config.get_scaler_path(ticker)
    dst_scaler = config.get_backend_scaler_path(ticker)
    if src_scaler.exists():
        shutil.copy2(src_scaler, dst_scaler)
        logger.info(f"[Backend Asset] Scaler disalin: {dst_scaler.name}")

def main():
    parser = argparse.ArgumentParser(description="Penyalinan aset ke backend dan promosi model MLflow")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham yang diproses (misal: BBCA.JK)")
    args = parser.parse_args()

    ticker = args.ticker.strip().upper()
    logger.info(f"=== Menjalankan Stage Store untuk: {ticker} ===")
    promote_champion_models(ticker)
    sync_backend_assets(ticker)
    logger.info(f"=== Selesai Stage Store untuk: {ticker} ===")

if __name__ == "__main__":
    main()
