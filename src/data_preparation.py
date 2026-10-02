import argparse
import logging
import pickle
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple
from sklearn.preprocessing import MinMaxScaler
from src import config

logger = logging.getLogger("data_preparation_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_data(ticker: str) -> pd.DataFrame:
    # Memuat data historis saham dari disk
    csv_file_path = config.get_data_path(ticker)
    logger.info(f"[Data Preparation] Memuat data {ticker} dari {csv_file_path.name}...")

    # Baca file csv dan urutkan tanggal secara kronologis
    stock_dataframe = pd.read_csv(csv_file_path)
    stock_dataframe["date"] = pd.to_datetime(stock_dataframe["date"])
    stock_dataframe = stock_dataframe.sort_values("date").reset_index(drop=True)
    return stock_dataframe


def split_data(stock_dataframe: pd.DataFrame, train_size: float = 0.90) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Hitung batas indeks pemotongan sekuensial
    train_record_count = int(len(stock_dataframe) * train_size)

    # Pisahkan subset latih dan subset uji tanpa pengacakan urutan
    train_dataframe = stock_dataframe.iloc[:train_record_count].copy().reset_index(drop=True)
    test_dataframe = stock_dataframe.iloc[train_record_count:].copy().reset_index(drop=True)

    # Catat statistik distribusi data
    train_percentage = int(train_size * 100)
    test_percentage = int((1.0 - train_size) * 100)
    logger.info(f"Jumlah Data Latih ({train_percentage}%)    : {len(train_dataframe)}")
    logger.info(f"Jumlah Data Uji ({test_percentage}%)  : {len(test_dataframe)}")
    return train_dataframe, test_dataframe


def fit_and_transform_scaler(
    train_dataframe: pd.DataFrame, test_dataframe: pd.DataFrame, target_column: str = "close"
) -> Tuple[MinMaxScaler, np.ndarray, np.ndarray]:
    # Inisialisasi normalisasi Min-Max rentang 0 hingga 1
    scaler_instance = MinMaxScaler(feature_range=(0, 1))

    # Fitting parameter skala hanya pada data latih untuk mencegah kebocoran data
    train_scaled_array = scaler_instance.fit_transform(train_dataframe[[target_column]].values)
    test_scaled_array = scaler_instance.transform(test_dataframe[[target_column]].values)

    # Catat nilai minimum dan maksimum dari data latih
    min_scale_value = scaler_instance.data_min_[0]
    max_scale_value = scaler_instance.data_max_[0]
    logger.info(f"Min Scaler (Train): {min_scale_value:.2f}, Max Scaler: {max_scale_value:.2f}")
    return scaler_instance, train_scaled_array, test_scaled_array


def save_scaler(scaler_instance: MinMaxScaler, ticker: str) -> Path:
    # Serialisasi dan simpan objek scaler ke disk
    scaler_file_path = config.get_scaler_path(ticker)
    with open(scaler_file_path, "wb") as file_handler:
        pickle.dump(scaler_instance, file_handler)
    logger.info(f"[Artifact] Scaler tersimpan di: {scaler_file_path.name}")
    return scaler_file_path


def save_prepared_dataset(
    train_scaled_array: np.ndarray,
    test_scaled_array: np.ndarray,
    train_dataframe: pd.DataFrame,
    test_dataframe: pd.DataFrame,
    target_column: str,
    ticker: str,
) -> Path:
    # Simpan array fitur terstandarisasi dan target aktual ke file NPZ
    prepared_file_path = config.get_prepared_data_path(ticker)
    np.savez_compressed(
        prepared_file_path,
        train_scaled=train_scaled_array,
        test_scaled=test_scaled_array,
        y_train=train_dataframe[target_column].values,
        y_test=test_dataframe[target_column].values,
        dates_train=train_dataframe["date"].dt.strftime("%Y-%m-%d").values.astype(str),
        dates_test=test_dataframe["date"].dt.strftime("%Y-%m-%d").values.astype(str),
    )
    logger.info(f"[Artifact] Data siap latih tersimpan di: {prepared_file_path.name}")
    return prepared_file_path


def run_data_preparation(ticker: str, train_size: float = 0.90, target_col: str = "close"):
    # Tahap 1: Memuat dataset historis
    stock_dataframe = load_data(ticker=ticker)

    # Tahap 2: Membagi data latih dan uji secara kronologis
    train_dataframe, test_dataframe = split_data(stock_dataframe=stock_dataframe, train_size=train_size)

    # Tahap 3: Normalisasi nilai harga menggunakan Min-Max Scaler
    scaler_instance, train_scaled_array, test_scaled_array = fit_and_transform_scaler(
        train_dataframe=train_dataframe,
        test_dataframe=test_dataframe,
        target_column=target_col,
    )

    # Tahap 4: Menyimpan objek scaler untuk kebutuhan inferensi
    save_scaler(scaler_instance=scaler_instance, ticker=ticker)

    # Tahap 5: Menyimpan dataset terkompresi ke artefak
    save_prepared_dataset(
        train_scaled_array=train_scaled_array,
        test_scaled_array=test_scaled_array,
        train_dataframe=train_dataframe,
        test_dataframe=test_dataframe,
        target_column=target_col,
        ticker=ticker,
    )


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 3: Data Preparation")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--train-size", type=float, default=0.90, help="Proporsi data latih (default: 0.90)")
    parser.add_argument("--target-col", type=str, default="close", help="Nama kolom target (default: close)")

    # Parsing parameter input
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()

    # Eksekusi pipeline data preparation
    logger.info(f"=== Menjalankan Stage Data Preparation untuk: {ticker} ===")
    run_data_preparation(
        ticker=ticker,
        train_size=arguments.train_size,
        target_col=arguments.target_col,
    )
    logger.info(f"=== Selesai Stage Data Preparation untuk: {ticker} ===")


if __name__ == "__main__":
    main()
