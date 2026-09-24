import argparse
import dvc.api
import pandas as pd
import yfinance as yf
import config

COL_RENAME = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
}

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

    # Rename kolom
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
    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if not start_date:
        print("Error: Parameter 'start_date' belum ditentukan di params.yaml.")
        return

    if not end_date:
        print("Error: Parameter 'end_date' belum ditentukan di params.yaml.")
        return

    if args.ticker:
        tickers = [args.ticker.strip().upper()]
    else:
        raw_tickers = params.get("tickers", [])
        if isinstance(raw_tickers, str):
            raw_tickers = raw_tickers.split(",")

        tickers = []
        for t in raw_tickers:
            cleaned_ticker = t.strip().upper()
            if cleaned_ticker:
                tickers.append(cleaned_ticker)

    if not tickers:
        print("Error: Parameter 'tickers' belum ditentukan di params.yaml.")
        return

    for ticker in tickers:
        fetch_data(ticker, start_date, end_date)


if __name__ == "__main__":
    main()