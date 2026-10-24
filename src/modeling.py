import argparse
import itertools
import keras
import logging
import mlflow
import os
import pickle
import numpy as np
import pandas as pd
from src import config
from joblib import Parallel, delayed
from keras import layers, optimizers
from pathlib import Path
from sklearn.metrics import mean_squared_error
from tqdm import tqdm
from typing import Any, Dict, List, Tuple

logger = logging.getLogger("modeling_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_model(model_type: str, time_steps: int, learning_rate: float) -> keras.Sequential:
    # Reset sesi Keras
    keras.backend.clear_session()

    # Inisialisasi objek optimizer
    optimizer_instance = optimizers.Adam(learning_rate=learning_rate)

    # Susun arsitektur jaringan saraf berulang standar
    neural_network = keras.Sequential()
    neural_network.add(layers.Input(shape=(time_steps, 1)))

    if model_type == "LSTM":
        neural_network.add(layers.LSTM(units=50, return_sequences=False))
    elif model_type == "GRU":
        neural_network.add(layers.GRU(units=50, return_sequences=False))
    else:
        raise ValueError(f"Tipe model {model_type} tidak valid.")

    # Lapisan output regresi
    neural_network.add(layers.Dense(units=1))

    # Kompilasi dengan Mean Squared Error (MSE) sesuai spesifikasi metodologi penelitian
    neural_network.compile(
        optimizer=optimizer_instance,
        loss=keras.losses.MeanSquaredError(),
        metrics=["mae"],
    )

    return neural_network


def calculate_metrics(actual_values: np.ndarray, predicted_values: np.ndarray) -> Dict[str, float]:
    # Hitung metrik evaluasi MSE, RMSE, dan MAPE
    mean_sq_error = float(mean_squared_error(actual_values, predicted_values))
    root_mean_sq_error = float(np.sqrt(mean_sq_error))
    mean_abs_percentage_error = float(np.mean(np.abs((actual_values - predicted_values) / actual_values)) * 100)

    return {
        "MSE": mean_sq_error,
        "RMSE": root_mean_sq_error,
        "MAPE": mean_abs_percentage_error,
    }


def execute_trial(
    trial_params: Tuple[int, int, float, str],
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
    actual_test_values: np.ndarray,
    scaler_instance: Any,
    epochs: int,
    random_state: int = 42,
) -> Tuple[Dict[str, Any], List[np.ndarray]]:
    # Unpack parameter kombinasi eksperimen
    time_steps, batch_size, learning_rate, model_type = trial_params

    # Buat sequence dataset untuk data latih
    dataset_train = keras.utils.timeseries_dataset_from_array(
        data=train_scaled[:-1],
        targets=train_scaled[time_steps:, 0],
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=True,
        seed=random_state,
    )

    # Buat sequence dataset untuk data uji
    test_context_inputs = np.concatenate([train_scaled[-time_steps:], test_scaled], axis=0)
    dataset_test = keras.utils.timeseries_dataset_from_array(
        data=test_context_inputs[:-1],
        targets=None,
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=False,
    )

    # Siapkan callback penghentian dini
    early_stopping_callback = [
        keras.callbacks.EarlyStopping(
            monitor="loss",
            patience=10,
            restore_best_weights=True,
        )
    ]

    # Bangun dan latih model
    trained_network = build_model(
        model_type=model_type,
        time_steps=time_steps,
        learning_rate=learning_rate,
    )
    training_history = trained_network.fit(
        dataset_train,
        epochs=epochs,
        shuffle=False,
        callbacks=early_stopping_callback,
        verbose=0,
    )

    # Lakukan inferensi data uji
    scaled_predictions = trained_network.predict(dataset_test, verbose=0)
    inversed_predictions = scaler_instance.inverse_transform(scaled_predictions).flatten()

    # Hitung metrik performa pengujian
    evaluation_metrics = calculate_metrics(actual_values=actual_test_values, predicted_values=inversed_predictions)

    # Catat rekap hasil eksperimen
    trial_record = {
        "model": model_type,
        "time_steps": time_steps,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "epochs_trained": len(training_history.epoch),
        **evaluation_metrics,
    }

    # Ambil bobot model untuk rekonstruksi efisien
    model_weights = trained_network.get_weights()

    return trial_record, model_weights


def run_modeling(
    ticker: str,
    time_steps: List[int],
    batch_sizes: List[int],
    learning_rates: List[float],
    models_list: List[str],
    epochs: int = 500,
    random_state: int = 42,
    target_col: str = "close",
    n_jobs: int = -1,
):
    # Tahap 1: Inisialisasi seed dan MLflow tracking
    np.random.seed(random_state)
    keras.utils.set_random_seed(random_state)

    if config.MLFLOW_TRACKING_URI:
        mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)

    mlflow.set_experiment(config.get_experiment_name(ticker))

    # Tahap 2: Muat dataset siap latih dan artefak pendukung
    prepared_arrays = np.load(config.get_prepared_data_path(ticker), allow_pickle=True)
    train_scaled = prepared_arrays["train_scaled"]
    test_scaled = prepared_arrays["test_scaled"]
    actual_test_values = prepared_arrays["y_test"]

    with open(config.get_scaler_path(ticker), "rb") as file_handler:
        scaler_instance = pickle.load(file_handler)

    # Tahap 3: Susun kombinasi hyperparameter grid search
    parameter_combinations = list(
        itertools.product(time_steps, batch_sizes, learning_rates, models_list)
    )

    if n_jobs is None or n_jobs <= 0:
        n_jobs = min(4, os.cpu_count() or 1)

    logger.info(f"Memulai Grid Search ({len(parameter_combinations)} kombinasi, n_jobs={n_jobs}) untuk {ticker}")
    
    hyperparameter_records = []

    # Inisialisasi tracking performa model terbaik per arsitektur
    best_models_data = {}
    for model_name in models_list:
        best_models_data[model_name] = {
            "rmse": float("inf"),
            "record": None,
            "weights": None,
        }

    # Tahap 4: Eksekusi grid search dalam sesi MLflow
    run_name = f"{ticker}_Hyperparameter"
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({
            "target": target_col,
            "stage": "hyperparameter",
            "n_jobs": str(n_jobs),
        })

        parallel_generator = Parallel(n_jobs=n_jobs, return_as="generator")(
            delayed(execute_trial)(
                trial_params=trial_params,
                train_scaled=train_scaled,
                test_scaled=test_scaled,
                actual_test_values=actual_test_values,
                scaler_instance=scaler_instance,
                epochs=epochs,
                random_state=random_state,
            )
            for trial_params in parameter_combinations
        )

        progress_bar = tqdm(
            parallel_generator,
            total=len(parameter_combinations),
            desc=f"Grid Search ({n_jobs} jobs)",
            unit="trial",
        )

        # Iterasi setiap hasil trial paralel
        for single_record, model_weights in progress_bar:
            hyperparameter_records.append(single_record)
            current_rmse = single_record["RMSE"]
            current_model_type = single_record["model"]

            # Catat setiap eksperimen hyperparameter ke MLflow sebagai nested child run
            trial_run_name = (
                f"{ticker}_{current_model_type}_ts{single_record['time_steps']}"
                f"_bs{single_record['batch_size']}_lr{single_record['learning_rate']}"
            )

            try:
                with mlflow.start_run(run_name=trial_run_name, nested=True):
                    mlflow.set_tags({
                        "ticker": ticker,
                        "model": current_model_type,
                        "stage": "hyperparameter",
                    })

                    mlflow.log_params({
                        "ticker": ticker,
                        "model": current_model_type,
                        "target_col": target_col,
                        "time_steps": single_record["time_steps"],
                        "batch_size": single_record["batch_size"],
                        "learning_rate": single_record["learning_rate"],
                        "epochs": epochs
                    })

                    mlflow.log_metrics({
                        "MSE": float(single_record["MSE"]),
                        "RMSE": float(single_record["RMSE"]),
                        "MAPE": float(single_record["MAPE"]),
                        "epochs_trained": int(single_record["epochs_trained"]),
                    })

            except Exception as exc:
                logger.warning(f"Gagal mencatat eksperimen {trial_run_name} ke MLflow: {exc}")

            # Simpan rekam jejak dan bobot jika performa RMSE lebih baik
            if current_rmse < best_models_data[current_model_type]["rmse"]:
                best_models_data[current_model_type]["rmse"] = current_rmse
                best_models_data[current_model_type]["record"] = single_record
                best_models_data[current_model_type]["weights"] = model_weights

            progress_bar.set_postfix({
                "Model": current_model_type,
                "RMSE": f"{current_rmse:.2f}",
                "LSTM_Best": f"{best_models_data.get('LSTM', {}).get('rmse', float('inf')):.2f}",
                "GRU_Best": f"{best_models_data.get('GRU', {}).get('rmse', float('inf')):.2f}",
            })

        # Rekonstruksi dan simpan model terbaik per arsitektur
        for model_name in models_list:
            model_info = best_models_data[model_name]

            if model_info["weights"] is not None:
                best_time_steps = model_info["record"]["time_steps"]
                best_lr = model_info["record"]["learning_rate"]
                best_network = build_model(
                    model_type=model_name,
                    time_steps=best_time_steps,
                    learning_rate=best_lr,
                )
                best_network.set_weights(model_info["weights"])
                model_save_path = config.get_model_path(ticker, model_name)
                best_network.save(model_save_path)
                logger.info(f"[Model Saved] Model {model_name} terbaik disimpan ke: {model_save_path.name}")

        # Tahap 5: Simpan hasil eksperimen ke CSV dan log ke MLflow
        hyperparameter_csv_path = config.get_hyperparameter_path(ticker)
        hyperparameter_dataframe = pd.DataFrame(hyperparameter_records)
        hyperparameter_dataframe.to_csv(hyperparameter_csv_path, index=False)
        logger.info(f"[Artifact] Hyperparameter tersimpan di: {hyperparameter_csv_path.name}")

        mlflow.log_artifact(str(hyperparameter_csv_path), artifact_path="hyperparameter")


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="Modeling")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--epochs", type=int, default=500, help="Jumlah epoch pelatihan")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed")
    parser.add_argument("--target-col", type=str, default="close", help="Nama kolom target prediksi")
    parser.add_argument("--n-jobs", type=int, default=4, help="Jumlah worker parallel (-1 untuk auto)")
    parser.add_argument("--time-steps", type=int, nargs="+", default=[20, 30], help="Daftar time steps")
    parser.add_argument("--batch-sizes", type=int, nargs="+", default=[16, 32], help="Daftar batch sizes")
    parser.add_argument("--learning-rates", type=float, nargs="+", default=[0.001, 0.0001], help="Daftar learning rates")

    # Parsing parameter CLI
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()
    models_list = config.MODELS

    hyperparameters = [
        ("TIME_STEPS", arguments.time_steps),
        ("BATCH_SIZES", arguments.batch_sizes),
        ("LEARNING_RATES", arguments.learning_rates),
        ("MODELS", models_list),
        ("EPOCHS", arguments.epochs),
    ]

    # Eksekusi pipeline modeling
    logger.info(f"=== Menjalankan Stage Modeling untuk: {ticker} ===")
    logger.info(f"Hyperparameters: {hyperparameters}")

    run_modeling(
        ticker=ticker,
        time_steps=arguments.time_steps,
        batch_sizes=arguments.batch_sizes,
        learning_rates=arguments.learning_rates,
        models_list=models_list,
        epochs=arguments.epochs,
        random_state=arguments.random_state,
        target_col=arguments.target_col,
        n_jobs=arguments.n_jobs,
    )
    logger.info(f"=== Selesai Stage Modeling untuk: {ticker} ===")


if __name__ == "__main__":
    main()
