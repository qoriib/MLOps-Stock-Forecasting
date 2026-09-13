import os
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

def fetch_data(ticker: str, start_date: str, end_date: str) -> None:
    print(f"Mengunduh data {ticker} ({start_date} s.d. {end_date})...")
    
    try:
        df = yf.Ticker(ticker).history(start=start_date, end=end_date)
        if df.empty:
            print(f"Peringatan: Tidak ada data untuk {ticker}.")
            return
    except Exception as e:
        print(f"Error saat mengunduh {ticker}: {e}")
        return

    # Bersihkan Data
    df = df.reset_index()
    df['Date'] = df['Date'].dt.date
    df['ticker'] = ticker
    
    # Rename kolom
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # Simpan File
    os.makedirs(config.DATA_DIR, exist_ok=True)
    file_path = os.path.join(config.DATA_DIR, f"{ticker}.csv")
    df.to_csv(file_path, index=False)
    
    print(f"Selesai! {len(df)} baris disimpan ke: {file_path}")

def main():
    params = dvc.api.params_show()
    
    raw_tickers = params.get("tickers", [])

    if isinstance(raw_tickers, str):
        raw_tickers = raw_tickers.split(",")

    tickers = []

    for t in raw_tickers:
        cleaned_ticker = t.strip().upper()

        if cleaned_ticker:
            tickers.append(cleaned_ticker)

    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if not tickers:
        print("Error: Parameter 'tickers' belum ditentukan di params.yaml.")
        return

    if not start_date:
        print("Error: Parameter 'start_date' belum ditentukan di params.yaml.")
        return

    if not end_date:
        print("Error: Parameter 'end_date' belum ditentukan di params.yaml.")
        return

    for ticker in tickers:
        fetch_data(ticker, start_date, end_date)

if __name__ == "__main__":
    main()