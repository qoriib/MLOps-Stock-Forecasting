import argparse
import dvc.api
import pandas as pd
import yfinance as yf
import config

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

    # Bersihkan Data
    df = df.reset_index()
    df["ticker"] = ticker

    # Standarisasi nama kolom ke lowercase
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # Simpan File Parquet
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    parquet_path = config.DATA_DIR / f"{ticker}.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"[Parquet] {len(df)} baris disimpan ke: {parquet_path}")

    return df

def main():
    parser = argparse.ArgumentParser(description="Ingestion data saham dari Yahoo Finance")
    parser.add_argument("--ticker", type=str, help="Ticker spesifik yang ingin diunduh (opsional)")
    args = parser.parse_args()

    params = dvc.api.params_show()
    START_DATE = params["START_DATE"]
    END_DATE = params["END_DATE"]
    TICKERS = [t.strip().upper() for t in params["TICKERS"]]

    tickers_to_process = [args.ticker.strip().upper()] if args.ticker else TICKERS

    for ticker in tickers_to_process:
        fetch_data(ticker, START_DATE, END_DATE)

if __name__ == "__main__":
    main()