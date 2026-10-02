import argparse
import json
import logging
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple
from src import config

logger = logging.getLogger("data_understanding_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_data(ticker: str) -> pd.DataFrame:
    # Memuat data historis saham dari disk
    csv_file_path = config.get_data_path(ticker)
    logger.info(f"[Data Understanding] Memuat data {ticker} dari {csv_file_path.name}...")

    # Baca file csv dan konversi tipe tanggal
    stock_dataframe = pd.read_csv(csv_file_path)
    stock_dataframe["date"] = pd.to_datetime(stock_dataframe["date"])
    stock_dataframe = stock_dataframe.sort_values("date").reset_index(drop=True)
    return stock_dataframe


def check_date_gaps(stock_dataframe: pd.DataFrame) -> Tuple[int, pd.DatetimeIndex]:
    # Tentukan batas tanggal observasi
    min_date = stock_dataframe["date"].min()
    max_date = stock_dataframe["date"].max()

    # Identifikasi selisih tanggal kalender yang tidak ada di bursa
    full_date_range = pd.date_range(start=min_date, end=max_date, freq="D")
    missing_dates = full_date_range.difference(stock_dataframe["date"])
    gap_count = len(missing_dates)

    # Catat ringkasan informasi dataset
    logger.info(f"Periode Observasi : {min_date.strftime('%Y-%m-%d')} s/d {max_date.strftime('%Y-%m-%d')}")
    logger.info(f"Total Baris Data  : {len(stock_dataframe)}")
    logger.info(f"Jumlah Gap Tanggal: {gap_count}")
    return gap_count, missing_dates


def compute_statistics(stock_dataframe: pd.DataFrame, target_column: str) -> Dict[str, Dict[str, float]]:
    # Hitung agregasi statistik kolom target
    target_series = stock_dataframe[target_column]
    return {
        target_column: {
            "mean": float(target_series.mean()),
            "std": float(target_series.std()),
            "min": float(target_series.min()),
            "25%": float(target_series.quantile(0.25)),
            "50%": float(target_series.median()),
            "75%": float(target_series.quantile(0.75)),
            "max": float(target_series.max()),
        }
    }


def plot_historical_price(stock_dataframe: pd.DataFrame, ticker: str, target_column: str, output_path: Path) -> Path:
    # Buat kanvas grafik garis
    plt.figure(figsize=(13, 5))
    sns.lineplot(data=stock_dataframe, x="date", y=target_column)

    # Atur anotasi sumbu dan judul grafik
    plt.xlabel("Tanggal")
    plt.ylabel(f"Harga ({target_column.capitalize()})")
    plt.title(f"Pergerakan Harga Historis - {ticker}")
    plt.tight_layout()

    # Simpan hasil render gambar ke file
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info(f"[Artifact] Plot tren historis disimpan ke: {output_path.name}")
    return output_path


def save_understanding_metrics(summary_dictionary: dict, ticker: str) -> Path:
    # Simpan kamus statistik ke format JSON
    metrics_file_path = config.get_metrics_path(ticker, "data_understanding")
    with open(metrics_file_path, "w") as json_file:
        json.dump(summary_dictionary, json_file, indent=2)
    logger.info(f"[Artifact] Ringkasan data understanding disimpan ke: {metrics_file_path.name}")
    return metrics_file_path


def run_data_understanding(ticker: str, target_col: str = "close") -> dict:
    # Tahap 1: Memuat dataset
    stock_dataframe = load_data(ticker=ticker)

    # Tahap 2: Menganalisis gap tanggal kalender
    gap_count, _ = check_date_gaps(stock_dataframe=stock_dataframe)

    # Tahap 3: Menghitung statistik deskriptif target
    statistics_summary = compute_statistics(stock_dataframe=stock_dataframe, target_column=target_col)

    # Tahap 4: Menggambar visualisasi tren harga historis
    plot_file_path = config.get_plot_path(ticker, "historical_price")
    plot_historical_price(
        stock_dataframe=stock_dataframe,
        ticker=ticker,
        target_column=target_col,
        output_path=plot_file_path,
    )

    # Tahap 5: Menyusun dan mengekspor ringkasan metrik
    summary_dictionary = {
        "ticker": ticker,
        "target_col": target_col,
        "min_date": stock_dataframe["date"].min().strftime("%Y-%m-%d"),
        "max_date": stock_dataframe["date"].max().strftime("%Y-%m-%d"),
        "total_rows": len(stock_dataframe),
        "gap_count": gap_count,
        "stats": statistics_summary,
    }
    save_understanding_metrics(summary_dictionary=summary_dictionary, ticker=ticker)

    return summary_dictionary


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 2: Data Understanding")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--target-col", type=str, default="close", help="Nama kolom target (default: close)")

    # Parsing parameter input
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()

    # Eksekusi pipeline data understanding
    logger.info(f"=== Menjalankan Stage Data Understanding untuk: {ticker} ===")
    run_data_understanding(ticker=ticker, target_col=arguments.target_col)
    logger.info(f"=== Selesai Stage Data Understanding untuk: {ticker} ===")


if __name__ == "__main__":
    main()
