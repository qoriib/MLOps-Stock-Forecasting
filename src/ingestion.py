from pathlib import Path
import dvc.api
import pandas as pd
import yfinance as yf

try:
    from src import config
except ImportError:
    import config

COL_RENAME = {
    "Open": "open",
    "High": "high",
    "Low": "low",
    "Close": "close",
    "Volume": "volume",
}


def fetch_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    print(f"Mengunduh data {ticker} dari {start_date} sampai {end_date}...")

    try:
        stock = yf.Ticker(ticker)
        df_hist = stock.history(start=start_date, end=end_date)
    except Exception as e:
        print(f"Error saat mengunduh data {ticker}: {e}")
        return pd.DataFrame()

    if df_hist.empty:
        print(f"Peringatan: Data kosong dari Yahoo Finance untuk {ticker}.")
        return pd.DataFrame()

    df_hist = df_hist.reset_index()

    # Standarisasi kolom dan format tanggal
    df_hist["date"] = pd.to_datetime(df_hist["Date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    df_hist["ticker"] = ticker
    df_hist = df_hist.rename(columns=COL_RENAME)

    required_cols = ["ticker", "date", "open", "high", "low", "close", "volume"]
    df_hist = df_hist[[col for col in required_cols if col in df_hist.columns]]
    df_hist = df_hist.sort_values("date", ascending=True).drop_duplicates("date").reset_index(drop=True)

    return df_hist


def save_data(df: pd.DataFrame, ticker: str) -> Path:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = config.DATA_DIR / f"{ticker}.csv"

    df.to_csv(file_path, index=False)
    print(f"Selesai! Total {len(df)} baris data disimpan ke: {file_path}")
    return file_path


def main():
    params = dvc.api.params_show()

    tickers = params.get("tickers", [])
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(",") if t.strip()]

    start_date = params.get("start_date")
    end_date = params.get("end_date")

    if not tickers:
        print("Error: Ticker saham tidak ditentukan di params.yaml.")
        return

    if not start_date or not end_date:
        print("Error: Parameter 'start_date' dan 'end_date' harus ditentukan di params.yaml.")
        return

    # Proses setiap ticker saham dan simpan ke artifact/data/raw/{ticker}.csv
    for ticker in tickers:
        ticker_clean = ticker.strip().upper()
        df = fetch_stock_data(ticker_clean, start_date, end_date)
        if not df.empty:
            save_data(df, ticker_clean)
        else:
            print(f"Peringatan: Gagal menyimpan data untuk {ticker_clean}.")


if __name__ == "__main__":
    main()