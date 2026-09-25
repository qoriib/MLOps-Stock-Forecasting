import argparse
import logging
import pandas as pd
import yfinance as yf
from src import config

logger = logging.getLogger("ingestion_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def fetch_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    logger.info(f"[Yahoo Finance] Mengunduh data historis {ticker} ({start_date} s.d. {end_date})...")

    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if df.empty:
            logger.warning(f"[Yahoo Finance] Tidak ada data ditemukan untuk {ticker}")
            return None
    except Exception as e:
        logger.error(f"[Yahoo Finance] Gagal mengunduh data {ticker}: {e}")
        return None

    df = df.reset_index()
    df["ticker"] = ticker

    # Standarisasi nama kolom
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # Simpan File Parquet
    parquet_path = config.get_data_path(ticker)
    df.to_parquet(parquet_path, index=False)

    logger.info(f"[Artifact] {len(df)} baris data disimpan ke: {parquet_path.name}")
    return df

def main():
    parser = argparse.ArgumentParser(description="Akuisisi data saham dari Yahoo Finance")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham yang diproses (misal: BBCA.JK)")
    parser.add_argument("--start-date", "--start_date", dest="start_date", type=str, required=True, help="Tanggal awal (YYYY-MM-DD)")
    parser.add_argument("--end-date", "--end_date", dest="end_date", type=str, required=True, help="Tanggal akhir (YYYY-MM-DD)")
    args = parser.parse_args()

    ticker = args.ticker.strip().upper()
    logger.info(f"=== Menjalankan Stage Ingestion untuk: {ticker} ({args.start_date} s.d. {args.end_date}) ===")
    fetch_data(ticker, args.start_date, args.end_date)
    logger.info(f"=== Selesai Stage Ingestion untuk: {ticker} ===")

if __name__ == "__main__":
    main()