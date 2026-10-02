import argparse
import itertools
import keras
import logging
import mlflow
import pickle
import yaml
import numpy as np
import pandas as pd
from keras import layers, optimizers
from pathlib import Path
from sklearn.metrics import mean_squared_error
from tqdm import tqdm
from typing import Any, Dict, List, Tuple
from src import config

logger = logging.getLogger("modeling_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def create_windowed_dataset(
    train_array: np.ndarray,
    test_array: np.ndarray,
    time_steps: int,
    batch_size: int,
    random_state: int = 42,
):
    # Buat sequence dataset untuk data latih
    dataset_train = keras.utils.timeseries_dataset_from_array(
        data=train_array[:-1],
        targets=train_array[time_steps:, 0],
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=True,
        seed=random_state,
    )

    # Gabungkan konteks akhir data latih untuk jendela uji pertama
    test_inputs = np.concatenate([train_array[-time_steps:], test_array], axis=0)

    # Buat sequence dataset untuk data uji tanpa pengacakan urutan
    dataset_test = keras.utils.timeseries_dataset_from_array(
        data=test_inputs[:-1],
        targets=test_inputs[time_steps:, 0],
        sequence_length=time_steps,
        batch_size=batch_size,
        shuffle=False,
    )

    return dataset_train, dataset_test


def build_model(model_type: str, time_steps: int, optimizer_name: str, learning_rate: float) -> keras.Sequential:
    # Reset sesi Keras untuk membersihkan memori komputasi
    keras.backend.clear_session()

    # Inisialisasi objek optimizer
    if optimizer_name == "SGD":
        optimizer_instance = optimizers.SGD(learning_rate=learning_rate)
    elif optimizer_name == "Adam":
        optimizer_instance = optimizers.Adam(learning_rate=learning_rate)
    elif optimizer_name == "RMSprop":
        optimizer_instance = optimizers.RMSprop(learning_rate=learning_rate)
    else:
        raise ValueError(f"Optimizer {optimizer_name} tidak didukung.")

    # Susun arsitektur jaringan saraf berulang
    neural_network = keras.Sequential()
    neural_network.add(layers.Input(shape=(time_steps, 1)))

    if model_type == "LSTM":
        neural_network.add(layers.LSTM(units=50, return_sequences=False))
    elif model_type == "GRU":
        neural_network.add(layers.GRU(units=50, return_sequences=False))
    else:
        raise ValueError(f"Tipe model {model_type} tidak valid.")

    # Tambahkan lapisan output regresi dan kompilasi
    neural_network.add(layers.Dense(units=1))
    neural_network.compile(optimizer=optimizer_instance, loss="mean_squared_error")

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
    trial_params: Tuple[int, str, int, float, str],
    train_scaled: np.ndarray,
    test_scaled: np.ndarray,
    actual_test_values: np.ndarray,
    scaler_instance: Any,
    epochs: int,
    random_state: int = 42,
) -> Tuple[Dict[str, Any], keras.Sequential]:
    # Unpack parameter kombinasi eksperimen
    time_steps, optimizer_name, batch_size, learning_rate, model_type = trial_params

    # Buat sliding window generator
    dataset_train, dataset_test = create_windowed_dataset(
        train_array=train_scaled,
        test_array=test_scaled,
        time_steps=time_steps,
        batch_size=batch_size,
        random_state=random_state,
    )

    # Siapkan callback penghentian dini
    early_stopping_callback = [
        keras.callbacks.EarlyStopping(
            monitor="loss",
            patience=8,
            restore_best_weights=True,
        )
    ]

    # Bangun dan latih model
    trained_network = build_model(
        model_type=model_type,
        time_steps=time_steps,
        optimizer_name=optimizer_name,
        learning_rate=learning_rate,
    )
    training_history = trained_network.fit(
        dataset_train,
        epochs=epochs,
        shuffle=False,
        callbacks=early_stopping_callback,
        verbose=0,
    )

    # Lakukan inferensi dan kembalikan ke skala harga asli
    scaled_predictions = trained_network.predict(dataset_test, verbose=0)
    inversed_predictions = scaler_instance.inverse_transform(scaled_predictions).flatten()

    # Hitung metrik performa pengujian
    evaluation_metrics = calculate_metrics(actual_values=actual_test_values, predicted_values=inversed_predictions)

    # Catat rekap hasil eksperimen
    trial_record = {
        "model": model_type,
        "time_steps": time_steps,
        "optimizer": optimizer_name,
        "batch_size": batch_size,
        "learning_rate": learning_rate,
        "epochs_trained": len(training_history.epoch),
        **evaluation_metrics,
    }

    return trial_record, trained_network


def run_modeling(
    ticker: str,
    time_steps: List[int],
    optimizers_list: List[str],
    batch_sizes: List[int],
    learning_rates: List[float],
    models_list: List[str],
    epochs: int = 50,
    random_state: int = 42,
    target_col: str = "close",
):
    # Tahap 1: Inisialisasi seed dan MLflow tracking
    keras.utils.set_random_seed(random_state)
    np.random.seed(random_state)

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

    raw_dataframe = pd.read_csv(config.get_data_path(ticker))

    # Tahap 3: Susun kombinasi hyperparameter grid search
    parameter_combinations = list(
        itertools.product(time_steps, optimizers_list, batch_sizes, learning_rates, models_list)
    )

    logger.info(f"Memulai Grid Search ({len(parameter_combinations)} kombinasi) untuk {ticker}...")
    hyperparameter_records = []
    progress_bar = tqdm(parameter_combinations, desc="Grid Search", unit="trial")

    # Inisialisasi tracking performa model terbaik per arsitektur
    best_models_data = {}
    for model_name in models_list:
        best_models_data[model_name] = {
            "rmse": float("inf"),
            "record": None,
            "model": None,
        }

    # Tahap 4: Eksekusi grid search dalam sesi MLflow
    run_name = f"{ticker}_Hyperparameter"
    with mlflow.start_run(run_name=run_name):
        mlflow.set_tags({
            "target": target_col,
            "stage": "hyperparameter",
        })

        if not raw_dataframe.empty:
            dataset_source = mlflow.data.from_pandas(raw_dataframe, targets=target_col, name=f"{ticker}_data")
            mlflow.log_input(dataset_source, context="training_and_testing")

        # Iterasi setiap kombinasi parameter
        for trial_params in progress_bar:
            single_record, trained_network = execute_trial(
                trial_params=trial_params,
                train_scaled=train_scaled,
                test_scaled=test_scaled,
                actual_test_values=actual_test_values,
                scaler_instance=scaler_instance,
                epochs=epochs,
                random_state=random_state,
            )

            hyperparameter_records.append(single_record)
            current_rmse = single_record["RMSE"]
            current_model_type = single_record["model"]

            # Simpan model jika performa RMSE lebih baik dari rekor sebelumnya
            if current_rmse < best_models_data[current_model_type]["rmse"]:
                best_models_data[current_model_type]["rmse"] = current_rmse
                best_models_data[current_model_type]["record"] = single_record
                best_models_data[current_model_type]["model"] = trained_network

                model_save_path = config.get_model_path(ticker, current_model_type)
                trained_network.save(model_save_path)

            progress_bar.set_postfix({
                "Model": current_model_type,
                "RMSE": f"{current_rmse:.2f}",
                "LSTM_Best": f"{best_models_data.get('LSTM', {}).get('rmse', float('inf')):.2f}",
                "GRU_Best": f"{best_models_data.get('GRU', {}).get('rmse', float('inf')):.2f}",
            })

        # Tahap 5: Simpan hasil eksperimen ke CSV dan log ke MLflow
        hyperparameter_csv_path = config.get_hyperparameter_path(ticker)
        hyperparameter_dataframe = pd.DataFrame(hyperparameter_records)
        hyperparameter_dataframe.to_csv(hyperparameter_csv_path, index=False)
        logger.info(f"[Artifact] Hyperparameter tersimpan di: {hyperparameter_csv_path.name}")

        mlflow.log_artifact(str(hyperparameter_csv_path), artifact_path="hyperparameter")
        metrics_to_log = {}
        for model_name in models_list:
            if best_models_data[model_name]["rmse"] != float("inf"):
                metrics_to_log[f"{model_name}_RMSE"] = float(best_models_data[model_name]["rmse"])
        if metrics_to_log:
            mlflow.log_metrics(metrics_to_log)


def load_params_file(params_file_path: str) -> dict:
    # Muat konfigurasi dari file YAML
    with open(params_file_path, "r") as file_handler:
        return yaml.safe_load(file_handler) or {}


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 4: Modeling")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--params-file", type=str, default="params.yaml", help="Path params.yaml")
    parser.add_argument("--epochs", type=int, default=None, help="Epochs pelatihan")
    parser.add_argument("--random-state", type=int, default=None, help="Random seed")
    parser.add_argument("--target-col", type=str, default=None, help="Target column")

    # Parsing parameter CLI dan file konfigurasi eksternal
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()
    file_parameters = load_params_file(arguments.params_file)

    # Tetapkan nilai parameter numerik dasar
    epochs = file_parameters.get("EPOCHS", 50)
    if arguments.epochs is not None:
        epochs = arguments.epochs

    random_state = file_parameters.get("RANDOM_STATE", 42)
    if arguments.random_state is not None:
        random_state = arguments.random_state

    target_column = file_parameters.get("TARGET_COL", "close")
    if arguments.target_col is not None:
        target_column = arguments.target_col

    # Ambil parameter grid search langsung dari konfigurasi
    time_steps = file_parameters.get("TIME_STEPS", [10])
    optimizers_list = file_parameters.get("OPTIMIZERS", ["Adam"])
    batch_sizes = file_parameters.get("BATCH_SIZES", [8])
    learning_rates = file_parameters.get("LEARNING_RATES", [0.01])
    models_list = config.MODELS

    # Eksekusi pipeline modeling
    logger.info(f"=== Menjalankan Stage Modeling untuk: {ticker} ===")
    logger.info(
        f"Hyperparameters: TIME_STEPS={time_steps}, OPTIMIZERS={optimizers_list}, "
        f"BATCH_SIZES={batch_sizes}, LEARNING_RATES={learning_rates}, "
        f"MODELS={models_list}, EPOCHS={epochs}, RANDOM_STATE={random_state}"
    )

    run_modeling(
        ticker=ticker,
        time_steps=time_steps,
        optimizers_list=optimizers_list,
        batch_sizes=batch_sizes,
        learning_rates=learning_rates,
        models_list=models_list,
        epochs=epochs,
        random_state=random_state,
        target_col=target_column,
    )
    logger.info(f"=== Selesai Stage Modeling untuk: {ticker} ===")


if __name__ == "__main__":
    main()
