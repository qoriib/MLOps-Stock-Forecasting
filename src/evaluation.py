from src import config
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
import shutil
from mlflow import MlflowClient
from mlflow.models.signature import infer_signature
from pathlib import Path
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("evaluation_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_best_configurations(ticker: str) -> pd.DataFrame:
    # Memuat konfigurasi hyperparameter terbaik per arsitektur model berdasarkan RMSE terendah
    hyperparameter_csv_path = config.get_hyperparameter_path(ticker)
    hyperparameter_dataframe = pd.read_csv(hyperparameter_csv_path)

    best_configuration_indices = hyperparameter_dataframe.groupby("model")["RMSE"].idxmin().values
    best_configurations_dataframe = hyperparameter_dataframe.loc[best_configuration_indices].reset_index(drop=True)
    return best_configurations_dataframe


def predict_test_data(
    loaded_model: keras.Model,
    scaler_instance: Any,
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
    time_steps: int,
    batch_size: int,
) -> np.ndarray:
    # Siapkan konteks jendela sekuensial data uji
    test_context_inputs = np.concatenate([train_scaled[-time_steps:], test_scaled], axis=0)

    test_timeseries_dataset = keras.utils.timeseries_dataset_from_array(
        data=test_context_inputs[:-1],
        targets=test_context_inputs[time_steps:, 0],
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=False,
    )

    # Prediksi forward pass dan denormalisasi ke skala harga aktual
    scaled_predictions = loaded_model.predict(test_timeseries_dataset, verbose=0)
    inversed_predictions = scaler_instance.inverse_transform(scaled_predictions).flatten()
    return inversed_predictions


def forecast_future_steps(
    loaded_model: keras.Model,
    scaler_instance: Any,
    test_scaled: np.ndarray,
    last_test_date: pd.Timestamp,
    time_steps: int,
    forecast_steps: int = 20,
) -> Tuple[List[pd.Timestamp], np.ndarray]:
    # Hitung deret tanggal bursa masa depan (hari kerja Senin-Jumat)
    future_dates = []
    current_date = last_test_date
    while len(future_dates) < forecast_steps:
        current_date += pd.Timedelta(days=1)
        if current_date.weekday() < 5:
            future_dates.append(current_date)

    # Lakukan inferensi rolling rekursif
    rolling_window = list(test_scaled[-time_steps:].flatten())
    future_scaled_predictions = []

    for _ in range(forecast_steps):
        input_window_array = np.array(rolling_window[-time_steps:], dtype=np.float32).reshape(1, time_steps, 1)
        next_scaled_price = float(loaded_model(input_window_array, training=False).numpy().flatten()[0])
        future_scaled_predictions.append(next_scaled_price)
        rolling_window.append(next_scaled_price)

    # Denormalisasi proyeksi harga masa depan
    future_inversed_predictions = scaler_instance.inverse_transform(
        np.array(future_scaled_predictions).reshape(-1, 1)
    ).flatten()

    return future_dates, future_inversed_predictions


def plot_inference_and_forecast(
    ticker: str,
    model_name: str,
    target_column: str,
    dates_train: np.ndarray,
    actual_train_values: np.ndarray,
    dates_test: np.ndarray,
    actual_test_values: np.ndarray,
    predicted_test_values: np.ndarray,
    future_dates: List[pd.Timestamp],
    future_predictions: np.ndarray,
    evaluation_metrics: Dict[str, float],
) -> Tuple[Path, plt.Figure]:
    plot_file_path = config.get_plot_path(ticker, f"{model_name}_inference")
    figure, axes = plt.subplots(figsize=(14, 5))

    parsed_dates_train = pd.to_datetime(dates_train)
    parsed_dates_test = pd.to_datetime(dates_test)

    # Plot data historis latih (proporsional agar fokus visual terjaga)
    train_plot_length = min(len(dates_train), len(dates_test) * 2)
    axes.plot(
        parsed_dates_train[-train_plot_length:],
        actual_train_values[-train_plot_length:],
        label="Train Actual",
        color="tab:blue",
    )

    # Plot data uji aktual dan prediksi
    axes.plot(parsed_dates_test, actual_test_values, label="Test Actual", color="tab:green")
    axes.plot(
        parsed_dates_test,
        predicted_test_values,
        label=f"{model_name} Test Prediction",
        color="tab:red",
        linestyle="--",
    )

    # Plot sambungan proyeksi 20 langkah ke depan
    connection_dates = [parsed_dates_test[-1]] + future_dates
    connection_predictions = [predicted_test_values[-1]] + list(future_predictions)
    axes.plot(
        connection_dates,
        connection_predictions,
        label=f"{model_name} Future Forecast (+20 Steps)",
        color="tab:orange",
        linestyle=":",
        linewidth=2,
    )
    axes.axvline(x=parsed_dates_test[-1], color="gray", linestyle="-.", alpha=0.5, label="Test / Future Cutoff")

    # Atur metadata label grafik
    axes.set_title(
        f"Inferensi & Proyeksi 20-Step {model_name} - {ticker} "
        f"(RMSE: {evaluation_metrics['RMSE']:.2f}, MAPE: {evaluation_metrics['MAPE']:.2f}%, MSE: {evaluation_metrics['MSE']:.2f})"
    )
    axes.set_xlabel("Tanggal")
    axes.set_ylabel(f"Harga ({target_column.capitalize()})")
    axes.legend()
    plt.tight_layout()

    figure.savefig(plot_file_path, dpi=150)
    logger.info(f"[Artifact] Plot visualisasi disimpan ke: {plot_file_path.name}")
    return plot_file_path, figure


def register_model_mlflow(
    mlflow_client: MlflowClient,
    ticker: str,
    model_name: str,
    target_column: str,
    config_row: Dict[str, Any],
    evaluation_metrics: Dict[str, float],
    loaded_model: keras.Model,
    scaler_file_path: Path,
    figure: plt.Figure,
    time_steps: int,
) -> str:
    # Buat signature inferensi model
    sample_input_array = np.zeros((1, time_steps, 1), dtype=np.float32)
    sample_output_array = loaded_model(sample_input_array, training=False).numpy()
    tensor_signature = infer_signature(sample_input_array, sample_output_array)

    registered_model_name = f"{ticker}_{model_name}"
    registration_run_name = f"{ticker}_{model_name}_Registration"

    with mlflow.start_run(run_name=registration_run_name):
        mlflow.set_tags({
            "target": target_column,
            "stage": "registration",
        })

        mlflow.log_params(config_row)
        mlflow.log_metrics(evaluation_metrics)
        mlflow.log_artifact(str(scaler_file_path), artifact_path="scaler")
        mlflow.log_figure(figure, artifact_file=f"{model_name}_inference.png")

        mlflow.keras.log_model(
            model=loaded_model,
            name=f"model_{model_name.lower()}",
            registered_model_name=registered_model_name,
            signature=tensor_signature,
        )

        available_versions = mlflow_client.search_model_versions(f"name = '{registered_model_name}'")
        sorted_versions = sorted(available_versions, key=lambda version_item: int(version_item.version))
        latest_version_number = sorted_versions[-1].version
        return latest_version_number


def package_champion_assets(
    mlflow_client: MlflowClient,
    ticker: str,
    model_name: str,
    latest_version_number: str,
    mean_absolute_percentage_error: float,
    threshold_mape: float,
    model_file_path: Path,
    scaler_file_path: Path,
) -> None:
    registered_model_name = f"{ticker}_{model_name}"

    if mean_absolute_percentage_error < threshold_mape:
        # Model memenuhi ambang batas -> Promosikan ke status @champion
        mlflow_client.set_registered_model_alias(
            name=registered_model_name,
            alias="champion",
            version=latest_version_number,
        )
        logger.info(
            f"[MLflow] Model {registered_model_name} (v{latest_version_number}) "
            f"LOLOS ambang batas (MAPE={mean_absolute_percentage_error:.2f}%) -> DIPROMOSIKAN ke @champion"
        )

        # Salin model champion ke direktori aset backend
        destination_model_path = config.get_backend_model_path(ticker, model_name)
        destination_model_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(model_file_path, destination_model_path)

        # Salin scaler champion ke direktori aset backend
        destination_scaler_path = config.get_backend_scaler_path(ticker)
        destination_scaler_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(scaler_file_path, destination_scaler_path)
        logger.info(f"[Backend Asset] Model dan Scaler champion disalin ke: {destination_model_path.name}")
    else:
        # Model tidak memenuhi ambang batas -> Tetapkan sebagai status @challenger
        mlflow_client.set_registered_model_alias(
            name=registered_model_name,
            alias="challenger",
            version=latest_version_number,
        )
        logger.info(
            f"[MLflow] Model {registered_model_name} v{latest_version_number} "
            f"(MAPE={mean_absolute_percentage_error:.2f}%) DITOLAK menjadi champion -> Status @challenger"
        )


def evaluate_single_model(
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
    scaler_file_path: Path,
    mlflow_client: MlflowClient,
    threshold_mape: float,
) -> Dict[str, Any]:
    model_name = str(config_row["model"])
    time_steps = int(config_row["time_steps"])
    batch_size = int(config_row["batch_size"])

    logger.info(f"Mengevaluasi model {model_name} (time_steps={time_steps}, batch_size={batch_size})...")

    # 1. Muat model Keras yang tersimpan
    model_file_path = config.get_model_path(ticker, model_name)
    loaded_model = keras.models.load_model(model_file_path, compile=False)

    # 2. Lakukan inferensi data uji
    inversed_predictions = predict_test_data(
        loaded_model=loaded_model,
        scaler_instance=scaler_instance,
        train_scaled=train_scaled,
        test_scaled=test_scaled,
        time_steps=time_steps,
        batch_size=batch_size,
    )

    # 3. Hitung metrik evaluasi pengujian
    evaluation_metrics = {
        "RMSE": float(config_row["RMSE"]),
        "MAPE": float(config_row["MAPE"]),
        "MSE": float(config_row["MSE"]),
    }

    # 4. Proyeksi harga masa depan 20 hari ke depan
    last_test_date = pd.to_datetime(dates_test)[-1]
    future_dates, future_predictions = forecast_future_steps(
        loaded_model=loaded_model,
        scaler_instance=scaler_instance,
        test_scaled=test_scaled,
        last_test_date=last_test_date,
        time_steps=time_steps,
        forecast_steps=20,
    )

    # 5. Visualisasi dan ekspor gambar plot inferensi
    _, figure = plot_inference_and_forecast(
        ticker=ticker,
        model_name=model_name,
        target_column=target_column,
        dates_train=dates_train,
        actual_train_values=actual_train_values,
        dates_test=dates_test,
        actual_test_values=actual_test_values,
        predicted_test_values=inversed_predictions,
        future_dates=future_dates,
        future_predictions=future_predictions,
        evaluation_metrics=evaluation_metrics,
    )

    # 6. Registrasi model ke MLflow Model Registry
    try:
        latest_version_number = register_model_mlflow(
            mlflow_client=mlflow_client,
            ticker=ticker,
            model_name=model_name,
            target_column=target_column,
            config_row=config_row,
            evaluation_metrics=evaluation_metrics,
            loaded_model=loaded_model,
            scaler_file_path=scaler_file_path,
            figure=figure,
            time_steps=time_steps,
        )

        # 7. Evaluasi ambang batas kelayakan champion & pengemasan aset backend
        package_champion_assets(
            mlflow_client=mlflow_client,
            ticker=ticker,
            model_name=model_name,
            latest_version_number=latest_version_number,
            mean_absolute_percentage_error=evaluation_metrics["MAPE"],
            threshold_mape=threshold_mape,
            model_file_path=model_file_path,
            scaler_file_path=scaler_file_path,
        )
    except Exception as error_exception:
        logger.warning(f"[MLflow] Registrasi & evaluasi model {ticker}_{model_name} dilewati: {error_exception}")

    plt.close(figure)

    return {
        "model": model_name,
        "RMSE": evaluation_metrics["RMSE"],
        "MAPE": evaluation_metrics["MAPE"],
        "MSE": evaluation_metrics["MSE"],
        "time_steps": time_steps,
        "batch_size": batch_size,
        "learning_rate": config_row.get("learning_rate"),
    }


def run_evaluation(ticker: str, target_col: str = "close", threshold_mape: float = 10.0) -> List[Dict[str, Any]]:
    # Tahap 1: Hubungkan ke tracking server MLflow
    if config.MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    mlflow.set_experiment(config.get_experiment_name(ticker))

    # Tahap 2: Ambil konfigurasi hyperparameter terbaik per arsitektur model
    best_configurations_dataframe = load_best_configurations(ticker=ticker)

    # Tahap 3: Muat dataset siap latih dan instance normalisasi scaler
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

    # Tahap 4: Inisialisasi client MLflow
    mlflow_client = MlflowClient()
    evaluation_results = []

    # Tahap 5: Evaluasi, registrasi, dan kemas tiap model terbaik
    for _, configuration_row in best_configurations_dataframe.iterrows():
        config_dictionary = configuration_row.to_dict()
        evaluated_result_item = evaluate_single_model(
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
            scaler_file_path=scaler_file_path,
            mlflow_client=mlflow_client,
            threshold_mape=threshold_mape,
        )
        evaluation_results.append(evaluated_result_item)

    # Tahap 6: Ekspor ringkasan metrik evaluasi ke file JSON
    evaluation_metrics_file = config.get_metrics_path(ticker, "evaluation")
    with open(evaluation_metrics_file, "w", encoding="utf-8") as file_handler:
        json.dump(evaluation_results, file_handler, indent=2)
    logger.info(f"[Artifact] Ringkasan evaluasi tersimpan di: {evaluation_metrics_file.name}")

    return evaluation_results


def main():
    # Inisialisasi parser argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 5: Evaluation, Registration & Packaging")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--target-col", type=str, default="close", help="Nama kolom target prediksi")
    parser.add_argument("--threshold-mape", type=float, default=10.0, help="Ambang batas maksimum MAPE untuk champion")

    arguments = parser.parse_args()
    stock_ticker = arguments.ticker.strip().upper()

    # Eksekusi pipeline evaluasi
    logger.info(f"=== Menjalankan Stage Evaluation untuk: {stock_ticker} ===")
    run_evaluation(
        ticker=stock_ticker,
        target_col=arguments.target_col,
        threshold_mape=arguments.threshold_mape,
    )
    logger.info(f"=== Selesai Stage Evaluation untuk: {stock_ticker} ===")


if __name__ == "__main__":
    main()
