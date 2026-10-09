import argparse
import json
import logging
import mlflow
import shutil
import yaml
from mlflow.tracking import MlflowClient
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from src import config

logger = logging.getLogger("model_packaging")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Konfigurasi tracking URI jika disetel
if config.MLFLOW_TRACKING_URI:
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

mlflow_client = MlflowClient()


def get_version_number(version_item) -> int:
    # Ekstrak nomor versi numerik model terdaftar
    return int(version_item.version)


def load_local_evaluation_metrics(ticker: str) -> Dict[str, Dict[str, Any]]:
    # Memuat metrik evaluasi lokal dari artifact/metrics/{ticker}_evaluation.json
    evaluation_file = config.get_metrics_path(ticker, "evaluation")
    metrics_by_model: Dict[str, Dict[str, Any]] = {}
    if evaluation_file.exists():
        try:
            with open(evaluation_file, "r") as file_handler:
                eval_records = json.load(file_handler)
                for item in eval_records:
                    m_name = item.get("model")
                    if m_name:
                        metrics_by_model[m_name] = item
        except Exception as error_exception:
            logger.warning(f"Gagal membaca file evaluasi lokal {evaluation_file.name}: {error_exception}")
    return metrics_by_model


def get_model_metrics(
    registered_model_name: str,
    version_number: str,
    local_metrics: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    # Mengambil nilai RMSE, MAPE, dan R2 dari run MLflow atau fallback evaluasi lokal
    rmse, mape, r2 = None, None, None

    # Coba ekstrak dari MLflow run
    try:
        model_version_meta = mlflow_client.get_model_version(registered_model_name, version_number)
        run_data = mlflow_client.get_run(model_version_meta.run_id).data
        rmse = run_data.metrics.get("RMSE")
        mape = run_data.metrics.get("MAPE")
        r2 = run_data.metrics.get("R2")
    except Exception as mlflow_error:
        logger.debug(f"Tidak dapat membaca metrik dari MLflow run: {mlflow_error}")

    # Fallback ke metrik evaluasi lokal jika di MLflow belum ada
    if local_metrics:
        if rmse is None and "RMSE" in local_metrics:
            rmse = float(local_metrics["RMSE"])
        if mape is None and "MAPE" in local_metrics:
            mape = float(local_metrics["MAPE"])
        if r2 is None and "R2" in local_metrics:
            r2 = float(local_metrics["R2"])

    return rmse, mape, r2


def check_threshold_eligibility(
    rmse: Optional[float],
    mape: Optional[float],
    r2: Optional[float],
    threshold_mape: float,
    threshold_r2: float,
) -> Tuple[bool, str]:
    # Memvalidasi apakah model memenuhi ambang batas: MAPE < threshold_mape dan R2 > threshold_r2
    if mape is None or r2 is None:
        return False, "Metrik MAPE atau R2 tidak ditemukan."

    if mape >= threshold_mape:
        return False, f"MAPE={mape:.2f}% tidak memenuhi ambang batas (< {threshold_mape}%)."

    if r2 <= threshold_r2:
        return False, f"R2={r2:.4f} tidak memenuhi ambang batas (> {threshold_r2})."

    return True, f"Lolos ambang batas (MAPE={mape:.2f}% < {threshold_mape}%, R2={r2:.4f} > {threshold_r2})."


def promote_champion_models(
    ticker: str,
    threshold_mape: float = 10.0,
    threshold_r2: float = 0.80,
) -> Dict[str, bool]:
    # Evaluasi status challenger dan promosi ke champion jika memenuhi ambang batas
    promotion_results = {}
    local_eval_metrics = load_local_evaluation_metrics(ticker)

    for model_type in config.MODELS:
        registered_model_name = f"{ticker}_{model_type}"
        promotion_results[model_type] = False

        try:
            available_versions = mlflow_client.search_model_versions(f"name = '{registered_model_name}'")
            if not available_versions:
                logger.warning(f"[MLflow] Tidak ditemukan versi model terdaftar untuk {registered_model_name}.")
                continue

            # Urutkan berdasarkan versi terbaru
            sorted_versions = sorted(available_versions, key=get_version_number)
            latest_version_entry = sorted_versions[-1]
            latest_version_number = latest_version_entry.version

            # Ambil metrik performa
            model_local_metric = local_eval_metrics.get(model_type)
            rmse, mape, r2 = get_model_metrics(
                registered_model_name=registered_model_name,
                version_number=latest_version_number,
                local_metrics=model_local_metric,
            )

            # Validasi ambang batas kelayakan champion
            is_eligible, reason = check_threshold_eligibility(
                rmse=rmse,
                mape=mape,
                r2=r2,
                threshold_mape=threshold_mape,
                threshold_r2=threshold_r2,
            )

            rmse_str = f"{rmse:.2f}" if rmse is not None else "N/A"
            mape_str = f"{mape:.2f}%" if mape is not None else "N/A"
            r2_str = f"{r2:.4f}" if r2 is not None else "N/A"

            if is_eligible:
                # Model LOLOS ambang batas: Promosikan dari challenger menjadi champion
                mlflow_client.set_registered_model_alias(registered_model_name, "champion", latest_version_number)
                promotion_results[model_type] = True
                logger.info(
                    f"[MLflow] Model {registered_model_name} v{latest_version_number} "
                    f"(RMSE={rmse_str}, MAPE={mape_str}, R2={r2_str}) LOLOS ambang batas -> DIPROMOSIKAN ke @champion"
                )
            else:
                # Model TIDAK LOLOS: Tetap sebagai challenger, TIDAK BISA jadi champion
                logger.warning(
                    f"[MLflow] Model {registered_model_name} v{latest_version_number} "
                    f"(RMSE={rmse_str}, MAPE={mape_str}, R2={r2_str}) DITOLAK menjadi champion: {reason}. "
                    f"Status tetap sebagai @challenger."
                )

        except Exception as error_exception:
            logger.warning(f"[MLflow] Gagal memproses promosi model {registered_model_name}: {error_exception}")

    return promotion_results


def package_assets(
    ticker: str,
    threshold_mape: float = 10.0,
    threshold_r2: float = 0.80,
    promotion_results: Optional[Dict[str, bool]] = None,
) -> None:
    # Mengemas aset model champion dan scaler ke web/backend/assets
    local_eval_metrics = load_local_evaluation_metrics(ticker)

    for model_type in config.MODELS:
        registered_model_name = f"{ticker}_{model_type}"
        has_champion = False

        # 1. Coba unduh dari MLflow dengan alias @champion
        try:
            champion_version = mlflow_client.get_model_version_by_alias(registered_model_name, "champion")
            source_model_path = mlflow.artifacts.download_artifacts(
                artifact_uri=f"models:/{registered_model_name}@champion/data/model.keras"
            )
            destination_model_path = config.get_backend_model_path(ticker, model_type)
            shutil.copy2(source_model_path, destination_model_path)
            logger.info(f"[Backend Asset] Model champion dari MLflow disalin: {destination_model_path.name}")

            source_scaler_path = mlflow.artifacts.download_artifacts(
                run_id=champion_version.run_id,
                artifact_path=f"scaler/{ticker}_scaler.pkl",
            )
            destination_scaler_path = config.get_backend_scaler_path(ticker)
            shutil.copy2(source_scaler_path, destination_scaler_path)
            logger.info(f"[Backend Asset] Scaler champion dari MLflow disalin: {destination_scaler_path.name}")
            has_champion = True

        except Exception as mlflow_error:
            logger.info(
                f"[Backend Asset] Model {registered_model_name}@champion tidak ditemukan di MLflow ({mlflow_error}). "
                f"Memeriksa kelayakan file lokal..."
            )

        # 2. Fallback lokal: Hanya salin jika lolos ambang batas
        if not has_champion:
            model_local_metric = local_eval_metrics.get(model_type, {})
            mape_local = model_local_metric.get("MAPE")
            r2_local = model_local_metric.get("R2")
            rmse_local = model_local_metric.get("RMSE")

            is_eligible, reason = check_threshold_eligibility(
                rmse=rmse_local,
                mape=mape_local,
                r2=r2_local,
                threshold_mape=threshold_mape,
                threshold_r2=threshold_r2,
            )

            if is_eligible:
                local_model_path = config.get_model_path(ticker, model_type)
                destination_model_path = config.get_backend_model_path(ticker, model_type)
                if local_model_path.exists():
                    shutil.copy2(local_model_path, destination_model_path)
                    logger.info(f"[Backend Asset] Model lokal lolos ambang batas disalin: {destination_model_path.name}")

                local_scaler_path = config.get_scaler_path(ticker)
                destination_scaler_path = config.get_backend_scaler_path(ticker)
                if local_scaler_path.exists():
                    shutil.copy2(local_scaler_path, destination_scaler_path)
                    logger.info(f"[Backend Asset] Scaler lokal disalin: {destination_scaler_path.name}")
            else:
                logger.warning(
                    f"[Backend Asset] Model {registered_model_name} TIDAK MEMENUHI ambang batas ({reason}). "
                    f"Aset backend TIDAK ditimpa untuk menjaga stabilitas produksi."
                )


# Alias untuk kompatibilitas
sync_assets = package_assets


def load_tickers_from_params(params_file: str = "params.yaml") -> list:
    # Baca daftar tickers dari file params.yaml
    params_dict = config.load_params(params_file)
    if "TICKERS" in params_dict:
        return params_dict["TICKERS"]
    return ["BBCA.JK"]


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="Script: Package Champion Models & Scalers to Backend Assets")
    parser.add_argument("--ticker", type=str, default=None, help="Ticker saham spesifik (default: semua ticker dari params.yaml)")
    parser.add_argument("--params-file", type=str, default="params.yaml", help="Path params.yaml (default: params.yaml)")

    arguments = parser.parse_args()

    params_dict = config.load_params(arguments.params_file)
    threshold_mape = float(params_dict.get("THRESHOLD_MAPE", 10.0))
    threshold_r2 = float(params_dict.get("THRESHOLD_R2", 0.80))

    if arguments.ticker:
        target_tickers = [arguments.ticker.strip().upper()]
    else:
        target_tickers = load_tickers_from_params(arguments.params_file)

    logger.info(
        f"Kriteria Promosi Champion: MAPE < {threshold_mape}%, R2 > {threshold_r2} "
        f"(dari konfigurasi: {arguments.params_file})"
    )

    for current_ticker in target_tickers:
        logger.info(f"=== Menjalankan Evaluasi Champion & Pengemasan Aset: {current_ticker} ===")
        promotion_results = promote_champion_models(
            ticker=current_ticker,
            threshold_mape=threshold_mape,
            threshold_r2=threshold_r2,
        )
        package_assets(
            ticker=current_ticker,
            threshold_mape=threshold_mape,
            threshold_r2=threshold_r2,
            promotion_results=promotion_results,
        )
        logger.info(f"=== Selesai Evaluasi Champion & Pengemasan Aset: {current_ticker} ===")


if __name__ == "__main__":
    main()
