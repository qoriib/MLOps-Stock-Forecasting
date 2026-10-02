import argparse
import logging
import mlflow
import shutil
import yaml
from mlflow.tracking import MlflowClient
from pathlib import Path
from src import config

logger = logging.getLogger("sync_assets_script")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Konfigurasi tracking URI jika disetel
if config.MLFLOW_TRACKING_URI:
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

mlflow_client = MlflowClient()


def get_version_number(version_item) -> int:
    # Ekstrak nomor versi numerik
    return int(version_item.version)


def promote_champion_models(ticker: str) -> None:
    # Telusuri setiap tipe arsitektur model
    for model_type in config.MODELS:
        registered_model_name = f"{ticker}_{model_type}"

        try:
            # Ambil seluruh versi model terdaftar dari MLflow
            available_versions = mlflow_client.search_model_versions(f"name = '{registered_model_name}'")
            if not available_versions:
                continue

            # Urutkan berdasarkan nomor versi dan ambil versi paling mutakhir
            sorted_versions = sorted(available_versions, key=get_version_number)
            latest_version_number = sorted_versions[-1].version

            # Sematkan alias champion pada model versi terbaru
            mlflow_client.set_registered_model_alias(registered_model_name, "champion", latest_version_number)
            logger.info(f"[MLflow] {registered_model_name} v{latest_version_number} dipromosikan ke @champion")
        except Exception as error_exception:
            logger.info(f"[MLflow] Promosi model {registered_model_name} dilewati: {error_exception}")


def sync_assets(ticker: str) -> None:
    # Iterasi penyalinan aset model dan scaler untuk setiap arsitektur
    for model_type in config.MODELS:
        registered_model_name = f"{ticker}_{model_type}"

        try:
            # Dapatkan metadata versi model champion
            champion_version = mlflow_client.get_model_version_by_alias(registered_model_name, "champion")

            # Unduh dan salin file model champion ke backend
            source_model_path = mlflow.artifacts.download_artifacts(
                artifact_uri=f"models:/{registered_model_name}@champion/data/model.keras"
            )
            destination_model_path = config.get_backend_model_path(ticker, model_type)
            shutil.copy2(source_model_path, destination_model_path)
            logger.info(f"[Backend Asset] Model disalin: {destination_model_path.name}")

            # Unduh dan salin scaler dari run champion
            source_scaler_path = mlflow.artifacts.download_artifacts(
                run_id=champion_version.run_id,
                artifact_path=f"scaler/{ticker}_scaler.pkl",
            )
            destination_scaler_path = config.get_backend_scaler_path(ticker)
            shutil.copy2(source_scaler_path, destination_scaler_path)
            logger.info(f"[Backend Asset] Scaler disalin: {destination_scaler_path.name}")
        except Exception as error_exception:
            logger.warning(f"[Backend Asset] Gagal sinkronisasi dari MLflow ({error_exception}), menyalin dari artefak lokal...")

            # Fallback: salin file model langsung dari artefak lokal
            local_model_path = config.get_model_path(ticker, model_type)
            destination_model_path = config.get_backend_model_path(ticker, model_type)
            if local_model_path.exists():
                shutil.copy2(local_model_path, destination_model_path)
                logger.info(f"[Backend Asset] Model lokal disalin: {destination_model_path.name}")

            # Fallback: salin file scaler langsung dari artefak lokal
            local_scaler_path = config.get_scaler_path(ticker)
            destination_scaler_path = config.get_backend_scaler_path(ticker)
            if local_scaler_path.exists():
                shutil.copy2(local_scaler_path, destination_scaler_path)
                logger.info(f"[Backend Asset] Scaler lokal disalin: {destination_scaler_path.name}")


def load_tickers_from_params() -> list:
    # Baca daftar tickers dari file params.yaml
    params_path = config.BASE_DIR / "params.yaml"
    if params_path.exists():
        with open(params_path, "r") as params_file:
            loaded_yaml = yaml.safe_load(params_file)
            if loaded_yaml and "TICKERS" in loaded_yaml:
                return loaded_yaml["TICKERS"]
    return ["BBCA.JK"]


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="Script: Sync Champion Models & Scalers to Backend Assets")
    parser.add_argument("--ticker", type=str, default=None, help="Ticker saham spesifik (default: semua ticker dari params.yaml)")

    # Parsing parameter input
    arguments = parser.parse_args()

    # Tentukan daftar ticker yang akan diproses
    if arguments.ticker:
        target_tickers = [arguments.ticker.strip().upper()]
    else:
        target_tickers = load_tickers_from_params()

    # Eksekusi promosi model dan sinkronisasi aset untuk setiap ticker
    for current_ticker in target_tickers:
        logger.info(f"=== Menjalankan Sinkronisasi Aset Backend untuk: {current_ticker} ===")
        promote_champion_models(ticker=current_ticker)
        sync_assets(ticker=current_ticker)
        logger.info(f"=== Selesai Sinkronisasi Aset Backend untuk: {current_ticker} ===")


if __name__ == "__main__":
    main()
