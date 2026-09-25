import argparse
import pandas as pd
import yfinance as yf
from src import config

def fetch_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    print(f"Mengunduh data {ticker} ({start_date} s.d. {end_date})...")

    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if df.empty:
            print(f"Peringatan: Tidak ada data untuk {ticker}.")
            return None
    except Exception as e:
        print(f"Error saat mengunduh {ticker}: {e}")
        return None

    df = df.reset_index()
    df["ticker"] = ticker

    # Standarisasi nama kolom
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # Simpan File Parquet
    parquet_path = config.get_data_path(ticker)
    df.to_parquet(parquet_path, index=False)

    print(f"[Parquet] {len(df)} baris disimpan ke: {parquet_path}")
    return df

def main():
    parser = argparse.ArgumentParser(description="Akuisisi data saham dari Yahoo Finance")
    parser.add_argument("--ticker", type=str, required=True, help="Ticker saham (BBCA.JK)")
    parser.add_argument("--start-date", "--start_date", dest="start_date", type=str, required=True, help="Tanggal awal (YYYY-MM-DD)")
    parser.add_argument("--end-date", "--end_date", dest="end_date", type=str, required=True, help="Tanggal akhir (YYYY-MM-DD)")
    args = parser.parse_args()

    ticker = args.ticker.strip().upper()
    fetch_data(ticker, args.start_date, args.end_date)

if __name__ == "__main__":
    main()