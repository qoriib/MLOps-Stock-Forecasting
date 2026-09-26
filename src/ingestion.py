import argparse
import datetime
import logging
import pandas as pd
import yfinance as yf
from typing import Tuple
from src import config

logger = logging.getLogger("ingestion_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def resolve_dates(range_days: int, end_date: str) -> Tuple[str, str, str]:
    clean_end = end_date.strip()

    if clean_end == "auto":
        today = datetime.date.today()
        yf_end_dt = today + datetime.timedelta(days=1)
        end_str = yf_end_dt.strftime("%Y-%m-%d")
        display_end = f"{today.strftime('%Y-%m-%d')} (hari ini)"
        reference_dt = today
    else:
        reference_dt = datetime.datetime.strptime(clean_end, "%Y-%m-%d").date()
        end_str = reference_dt.strftime("%Y-%m-%d")
        display_end = end_str

    start_dt = reference_dt - datetime.timedelta(days=range_days)
    start_str = start_dt.strftime("%Y-%m-%d")

    return start_str, end_str, display_end


def fetch_data(ticker: str, start_date: str, end_date: str, display_end: str = None) -> pd.DataFrame | None:
    display_range_end = display_end if display_end else end_date
    logger.info(f"[Yahoo Finance] Mengunduh data historis {ticker} ({start_date} s.d. {display_range_end})...")

    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if df.empty:
            logger.warning(f"[Yahoo Finance] Tidak ada data ditemukan untuk {ticker}")
            return None
    except Exception as e:
        logger.error(f"[Yahoo Finance] Gagal mengunduh data {ticker}: {e}")
        return None

    df = df.reset_index()

    # Standarisasi nama kolom
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # Simpan File CSV
    csv_path = config.get_data_path(ticker)
    df.to_csv(csv_path, index=False)

    logger.info(f"[Artifact] {len(df)} baris data disimpan ke: {csv_path.name}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Akuisisi data saham dari Yahoo Finance")
    parser.add_argument(
        "--ticker",
        type=str,
        required=True,
        help="Ticker saham yang diproses (misal: BBCA.JK)",
    )
    parser.add_argument(
        "--range-days",
        type=int,
        required=True,
        help="Rentang hari ke belakang (misal: 1825)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default="auto",
        help="Tanggal akhir: 'auto' atau 'YYYY-MM-DD'",
    )

    args = parser.parse_args()
    ticker = args.ticker.strip().upper()

    start_date, end_date, display_end = resolve_dates(args.range_days, args.end_date)

    logger.info(f"=== Menjalankan Stage Ingestion untuk: {ticker} ({start_date} s.d. {display_end}) ===")
    fetch_data(ticker, start_date, end_date, display_end)
    logger.info(f"=== Selesai Stage Ingestion untuk: {ticker} ===")


if __name__ == "__main__":
    main()