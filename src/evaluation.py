import argparse
import json
import keras
import logging
import mlflow
import mlflow.keras
import pickle
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mlflow import MlflowClient
from mlflow.models.signature import infer_signature
from pathlib import Path
from typing import Any, Dict, List
from src import config

logger = logging.getLogger("evaluation_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_best_configurations(ticker: str) -> pd.DataFrame:
    # Memuat konfigurasi terbaik untuk setiap jenis arsitektur model
    hyperparameter_dataframe = pd.read_csv(config.get_hyperparameter_path(ticker))
    best_indices = hyperparameter_dataframe.groupby("model")["RMSE"].idxmin().values
    best_configurations_dataframe = hyperparameter_dataframe.loc[best_indices].reset_index(drop=True)
    return best_configurations_dataframe


def evaluate_and_plot(
    ticker: str,
    target_column: str,
    config_row: Dict[str, Any],
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
    actual_test_values: np.ndarray,
    actual_train_values: np.ndarray,
    dates_train: np.ndarray,
    dates_test: np.ndarray,
    scaler_instance: Any,
    mlflow_client: MlflowClient,
) -> Dict[str, Any]:
    # Ekstrak parameter model
    model_name = str(config_row["model"])
    time_steps = int(config_row["time_steps"])
    batch_size = int(config_row["batch_size"])

    logger.info(f"Mengevaluasi model {model_name} (time_steps={time_steps}, batch_size={batch_size})...")

    # Muat model Keras yang tersimpan
    model_file_path = config.get_model_path(ticker, model_name)
    loaded_model = keras.models.load_model(model_file_path)

    # Siapkan window data uji
    test_inputs = np.concatenate([train_scaled[-time_steps:], test_scaled], axis=0)
    dataset_test = keras.utils.timeseries_dataset_from_array(
        data=test_inputs[:-1],
        targets=test_inputs[time_steps:, 0],
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=False,
    )

    # Lakukan inferensi dan denormalisasi nilai harga
    scaled_predictions = loaded_model.predict(dataset_test, verbose=0)
    inversed_predictions = scaler_instance.inverse_transform(scaled_predictions).flatten()

    # Visualisasikan perbandingan harga aktual dan hasil prediksi
    plot_file_path = config.get_plot_path(ticker, f"{model_name}_inference")
    figure, axes = plt.subplots(figsize=(13, 5))
    parsed_dates_train = pd.to_datetime(dates_train)
    parsed_dates_test = pd.to_datetime(dates_test)

    train_plot_length = min(len(dates_train), len(dates_test) * 2)
    axes.plot(
        parsed_dates_train[-train_plot_length:],
        actual_train_values[-train_plot_length:],
        label="Train Actual",
        color="tab:blue",
    )
    axes.plot(parsed_dates_test, actual_test_values, label="Test Actual", color="tab:green")
    axes.plot(
        parsed_dates_test,
        inversed_predictions,
        label=f"{model_name} Prediction",
        color="tab:red",
        linestyle="--",
    )

    # Atur label dan simpan plot inferensi
    current_rmse = float(config_row["RMSE"])
    current_mape = float(config_row["MAPE"])
    axes.set_title(f"Inferensi {model_name} - {ticker} (RMSE: {current_rmse:.2f}, MAPE: {current_mape:.2f}%)")
    axes.set_xlabel("Tanggal")
    axes.set_ylabel(f"Harga ({target_column.capitalize()})")
    axes.legend()
    plt.tight_layout()
    figure.savefig(plot_file_path, dpi=150)
    logger.info(f"[Artifact] Plot inferensi disimpan ke: {plot_file_path.name}")

    # Buat signature model untuk registrasi MLflow
    sample_input = np.zeros((1, time_steps, 1), dtype=np.float32)
    sample_output = loaded_model.predict(sample_input, verbose=0)
    tensor_signature = infer_signature(sample_input, sample_output)

    # Catat run registrasi dan berikan alias challenger
    registered_model_name = f"{ticker}_{model_name}"
    run_name = f"{ticker}_{model_name}_Registration"
    scaler_file_path = config.get_scaler_path(ticker)

    try:
        with mlflow.start_run(run_name=run_name):
            mlflow.set_tags({
                "target": target_column,
                "stage": "registration",
            })

            mlflow.log_params(config_row)
            mlflow.log_metrics({
                "RMSE": current_rmse,
                "MAPE": current_mape,
                "MSE": float(config_row["MSE"]),
            })

            mlflow.log_artifact(str(scaler_file_path), artifact_path="scaler")
            mlflow.log_figure(figure, artifact_file=f"{model_name}_inference.png")

            mlflow.keras.log_model(
                model=loaded_model,
                name=f"model_{model_name.lower()}",
                registered_model_name=registered_model_name,
                signature=tensor_signature,
            )

            latest_model_entry = mlflow_client.get_registered_model(registered_model_name)
            latest_version_number = latest_model_entry.latest_versions[0].version

            mlflow_client.set_registered_model_alias(
                name=registered_model_name,
                alias="challenger",
                version=latest_version_number,
            )
            logger.info(f"[MLflow] Model {registered_model_name} (v{latest_version_number}) teregistrasi sebagai @challenger")
    except Exception as error_exception:
        logger.warning(f"[MLflow] Registrasi model {registered_model_name} dilewati: {error_exception}")

    plt.close(figure)

    return {
        "model": model_name,
        "RMSE": current_rmse,
        "MAPE": current_mape,
        "MSE": float(config_row["MSE"]),
        "time_steps": time_steps,
        "batch_size": batch_size,
        "optimizer": config_row.get("optimizer"),
        "learning_rate": config_row.get("learning_rate"),
    }


def run_evaluation(ticker: str, target_col: str = "close") -> List[Dict[str, Any]]:
    # Tahap 1: Hubungkan ke MLflow tracking
    if config.MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.get_experiment_name(ticker))

    # Tahap 2: Ambil konfigurasi hyperparameter terbaik
    best_configurations_dataframe = load_best_configurations(ticker=ticker)

    # Tahap 3: Muat array data siap latih dan artefak scaler
    prepared_data_path = config.get_prepared_data_path(ticker)
    prepared_arrays = np.load(prepared_data_path, allow_pickle=True)
    train_scaled = prepared_arrays["train_scaled"]
    test_scaled = prepared_arrays["test_scaled"]
    actual_test_values = prepared_arrays["y_test"]
    actual_train_values = prepared_arrays["y_train"]
    dates_train = prepared_arrays["dates_train"]
    dates_test = prepared_arrays["dates_test"]

    scaler_file_path = config.get_scaler_path(ticker)
    with open(scaler_file_path, "rb") as file_handler:
        scaler_instance = pickle.load(file_handler)

    # Tahap 4: Inisialisasi klien MLflow
    mlflow_client = MlflowClient()
    evaluation_results = []

    # Tahap 5: Evaluasi dan visualisasikan tiap arsitektur model
    for _, row_data in best_configurations_dataframe.iterrows():
        config_dictionary = row_data.to_dict()
        evaluated_item = evaluate_and_plot(
            ticker=ticker,
            target_column=target_col,
            config_row=config_dictionary,
            train_scaled=train_scaled,
            test_scaled=test_scaled,
            actual_test_values=actual_test_values,
            actual_train_values=actual_train_values,
            dates_train=dates_train,
            dates_test=dates_test,
            scaler_instance=scaler_instance,
            mlflow_client=mlflow_client,
        )
        evaluation_results.append(evaluated_item)

    # Tahap 6: Ekspor ringkasan evaluasi ke file JSON
    evaluation_metrics_file = config.get_metrics_path(ticker, "evaluation")
    with open(evaluation_metrics_file, "w") as file_handler:
        json.dump(evaluation_results, file_handler, indent=2)
    logger.info(f"[Artifact] Ringkasan evaluasi tersimpan di: {evaluation_metrics_file.name}")

    return evaluation_results


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 5: Evaluation & Registration")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--target-col", type=str, default="close", help="Nama kolom target")

    # Parsing parameter input
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()

    # Eksekusi pipeline evaluation
    logger.info(f"=== Menjalankan Stage Evaluation untuk: {ticker} ===")
    run_evaluation(ticker=ticker, target_col=arguments.target_col)
    logger.info(f"=== Selesai Stage Evaluation untuk: {ticker} ===")


if __name__ == "__main__":
    main()
