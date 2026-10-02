import argparse
import datetime
import logging
import pandas as pd
import yfinance as yf
from pathlib import Path
from typing import Optional, Tuple
from src import config

logger = logging.getLogger("data_ingestion_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def resolve_dates(range_days: int, end_date: str) -> Tuple[str, str, str]:
    cleaned_end_date = end_date.strip()

    # Evaluasi mode tanggal akhir otomatis atau spesifik
    if cleaned_end_date == "auto":
        today_date = datetime.date.today()
        yahoo_end_date = today_date + datetime.timedelta(days=1)
        end_date_string = yahoo_end_date.strftime("%Y-%m-%d")
        display_end_date = f"{today_date.strftime('%Y-%m-%d')} (hari ini)"
        reference_date = today_date
    else:
        reference_date = datetime.datetime.strptime(cleaned_end_date, "%Y-%m-%d").date()
        end_date_string = reference_date.strftime("%Y-%m-%d")
        display_end_date = end_date_string

    # Kalkulasi batas tanggal awal berdasarkan rentang hari
    start_date = reference_date - datetime.timedelta(days=range_days)
    start_date_string = start_date.strftime("%Y-%m-%d")

    return start_date_string, end_date_string, display_end_date


def fetch_raw_data(ticker: str, start_date: str, end_date: str, display_end: str) -> pd.DataFrame:
    # Ambil data historis dari Yahoo Finance API
    logger.info(f"[Yahoo Finance] Mengunduh data historis {ticker} ({start_date} s.d. {display_end})...")
    downloaded_dataframe = yf.Ticker(ticker).history(start=start_date, end=end_date)
    return downloaded_dataframe


def clean_and_standardize_data(raw_dataframe: pd.DataFrame) -> pd.DataFrame:
    # Reset indeks dan seragamkan penamaan kolom ke huruf kecil
    cleaned_dataframe = raw_dataframe.reset_index()
    cleaned_dataframe.columns = cleaned_dataframe.columns.str.lower()

    # Eliminasi baris tanggal duplikat dan urutkan secara kronologis
    cleaned_dataframe = cleaned_dataframe.drop_duplicates("date").sort_values("date").reset_index(drop=True)
    return cleaned_dataframe


def save_ingested_data(stock_dataframe: pd.DataFrame, ticker: str) -> Path:
    # Siapkan direktori dan simpan dataframe ke format csv
    csv_file_path = config.get_data_path(ticker)
    stock_dataframe.to_csv(csv_file_path, index=False)
    logger.info(f"[Artifact] {len(stock_dataframe)} baris data disimpan ke: {csv_file_path.name}")
    return csv_file_path


def run_data_ingestion(ticker: str, range_days: int, end_date: str = "auto") -> pd.DataFrame:
    # Hitung rentang tanggal penarikan
    start_date, end_date_string, display_end_date = resolve_dates(
        range_days=range_days,
        end_date=end_date,
    )

    # Unduh data mentah saham
    raw_dataframe = fetch_raw_data(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date_string,
        display_end=display_end_date,
    )

    # Bersihkan data lalu simpan ke artefak
    cleaned_dataframe = clean_and_standardize_data(raw_dataframe=raw_dataframe)
    save_ingested_data(stock_dataframe=cleaned_dataframe, ticker=ticker)
    return cleaned_dataframe


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 1: Data Ingestion")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (misal: BBCA.JK)")
    parser.add_argument("--range-days", type=int, required=True, help="Rentang hari ke belakang")
    parser.add_argument("--end-date", type=str, default="auto", help="Tanggal akhir (auto atau YYYY-MM-DD)")

    # Parsing parameter input
    arguments = parser.parse_args()
    ticker = arguments.ticker.strip().upper()

    # Eksekusi pipeline data ingestion
    logger.info(f"=== Menjalankan Stage Data Ingestion untuk: {ticker} ===")
    run_data_ingestion(ticker=ticker, range_days=arguments.range_days, end_date=arguments.end_date)
    logger.info(f"=== Selesai Stage Data Ingestion untuk: {ticker} ===")


if __name__ == "__main__":
    main()
