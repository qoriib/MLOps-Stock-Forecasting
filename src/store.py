import argparse
import logging
import shutil
import dvc.api
from src import config

logger = logging.getLogger("store_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def promote_champion_models(ticker: str) -> None:
    """Mempromosikan versi model terbaru ke alias @champion dan @production di MLflow."""
    try:
        import mlflow
        from mlflow.tracking import MlflowClient

        if config.MLFLOW_TRACKING_URI:
            mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

        client = MlflowClient()
        for model_type in ["LSTM", "GRU"]:
            reg_model_name = f"{ticker}_{model_type}"
            versions = client.search_model_versions(f"name = '{reg_model_name}'")
            if versions:
                latest_v = sorted(versions, key=lambda v: int(v.version))[-1].version
                client.set_registered_model_alias(reg_model_name, "champion", latest_v)
                client.set_registered_model_alias(reg_model_name, "production", latest_v)
                logger.info(f"[MLflow] {reg_model_name} v{latest_v} dipromosikan ke @champion & @production")
    except Exception as e:
        logger.info(f"[MLflow] Promosi model {ticker} dilewati: {e}")


def sync_backend_assets(ticker: str) -> None:
    """Menyalin artefak model, scaler, dan data ke backend assets mengandalkan config."""
    config.BACKEND_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Salin Model (.keras)
    for model_type in ["LSTM", "GRU"]:
        src_model = config.get_model_path(ticker, model_type)
        dst_model = config.get_backend_model_path(ticker, model_type)
        if src_model.exists():
            shutil.copy2(src_model, dst_model)
            logger.info(f"[Backend Asset] Model disalin: {dst_model.name}")

    # 2. Salin Scaler (.pkl)
    src_scaler = config.get_scaler_path(ticker)
    dst_scaler = config.get_backend_scaler_path(ticker)
    if src_scaler.exists():
        shutil.copy2(src_scaler, dst_scaler)
        logger.info(f"[Backend Asset] Scaler disalin: {dst_scaler.name}")

    # 3. Salin Data Parquet & Hyperparameter CSV
    src_parquet = config.get_data_path(ticker)
    dst_parquet = config.get_backend_asset_path(f"{ticker}.parquet")
    if src_parquet.exists():
        shutil.copy2(src_parquet, dst_parquet)
        logger.info(f"[Backend Asset] Parquet disalin: {dst_parquet.name}")

    src_hp = config.get_hyperparameter_path(ticker)
    dst_hp = config.get_backend_asset_path(f"{ticker}_hyperparameter.csv")
    if src_hp.exists():
        shutil.copy2(src_hp, dst_hp)
        logger.info(f"[Backend Asset] Hyperparameter CSV disalin: {dst_hp.name}")


def main():
    parser = argparse.ArgumentParser(description="Penyalinan aset ke backend dan promosi model MLflow")
    parser.add_argument("--ticker", type=str, help="Ticker spesifik yang ingin diproses")
    args = parser.parse_args()

    params = dvc.api.params_show()
    tickers = [args.ticker.strip().upper()] if args.ticker else [t.strip().upper() for t in params["TICKERS"]]
    logger.info(f"=== Menjalankan Stage Store untuk: {tickers} ===")

    for ticker in tickers:
        promote_champion_models(ticker)
        sync_backend_assets(ticker)


if __name__ == "__main__":
    main()
