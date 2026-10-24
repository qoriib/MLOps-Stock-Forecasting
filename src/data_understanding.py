import argparse
import json
import logging
import pandas as pd
from pathlib import Path
from typing import Dict
from src import config

logger = logging.getLogger("data_understanding_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def load_data(ticker: str) -> pd.DataFrame:
    # Memuat data historis saham dari disk
    csv_file_path = config.get_data_path(ticker)
    logger.info(f"[Data Understanding] Memuat data {ticker} dari {csv_file_path.name}")

    # Baca file csv
    stock_dataframe = pd.read_csv(csv_file_path, parse_dates=["date"])
    return stock_dataframe


def compute_statistics(stock_dataframe: pd.DataFrame, target_column: str) -> Dict[str, Dict[str, float]]:
    # Hitung statistik deskriptif kolom target
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


def save_understanding_metrics(summary_dictionary: dict, ticker: str) -> Path:
    # Simpan kamus statistik deskriptif ke format JSON
    metrics_file_path = config.get_metrics_path(ticker, "understanding")

    with open(metrics_file_path, "w", encoding="utf-8") as json_file:
        json.dump(summary_dictionary, json_file, indent=2)
    
    logger.info(f"[Artifact] Ringkasan understanding disimpan ke: {metrics_file_path.name}")
    return metrics_file_path


def run_data_understanding(ticker: str, target_col: str = "close") -> dict:
    # Tahap 1: Memuat dataset
    stock_dataframe = load_data(ticker=ticker)

    # Tahap 2: Menghitung statistik deskriptif target
    statistics_summary = compute_statistics(stock_dataframe=stock_dataframe, target_column=target_col)

    # Tahap 3: Menyusun dan mengekspor ringkasan metrik statistik deskriptif
    summary_dictionary = {
        "ticker": ticker,
        "target_col": target_col,
        "min_date": stock_dataframe["date"].min().strftime("%Y-%m-%d"),
        "max_date": stock_dataframe["date"].max().strftime("%Y-%m-%d"),
        "total_rows": len(stock_dataframe),
        "stats": statistics_summary,
    }
    
    save_understanding_metrics(summary_dictionary=summary_dictionary, ticker=ticker)

    return summary_dictionary


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="Data Understanding")
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
