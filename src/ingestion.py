import argparse
from datetime import datetime
from pathlib import Path
import dvc.api
import pandas as pd
import yfinance as yf
from src import config


def resolve_ticker(symbol: str) -> str:
    """Mengubah simbol saham lokal ke format Yahoo Finance (misal: BBCA -> BBCA.JK)."""
    clean_sym = symbol.strip().upper()
    if "." in clean_sym:
        return clean_sym
    # Asumsi saham 4 huruf tanpa titik adalah saham Bursa Efek Indonesia (IDX)
    if len(clean_sym) == 4 and clean_sym.isalpha():
        return f"{clean_sym}.JK"
    return clean_sym


def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Mengambil data historis saham menggunakan library yfinance (tanpa API key)."""
    yf_symbol = resolve_ticker(symbol)
    print(f"Mengunduh data {symbol} (Ticker: {yf_symbol}) dari {start_date} sampai {end_date}...")

    try:
        ticker = yf.Ticker(yf_symbol)
        hist = ticker.history(start=start_date, end=end_date)
    except Exception as e:
        print(f"Error saat mengunduh data {yf_symbol}: {e}")
        return pd.DataFrame()

    if hist.empty:
        # Coba download langsung dengan symbol asli jika format .JK gagal
        if yf_symbol != symbol:
            print(f"Mencoba ticker alternatif: {symbol}...")
            try:
                hist = yf.Ticker(symbol).history(start=start_date, end=end_date)
            except Exception:
                pass

    if hist.empty:
        print(f"Peringatan: Data kosong dari Yahoo Finance untuk {symbol}.")
        return pd.DataFrame()

    hist = hist.reset_index()

    # Standarisasi kolom dan format tanggal
    hist["date"] = pd.to_datetime(hist["Date"]).dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    hist["symbol"] = symbol.upper()

    col_rename = {
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    }
    hist = hist.rename(columns=col_rename)

    required_cols = ["symbol", "date", "open", "high", "low", "close", "volume"]
    hist = hist[[col for col in required_cols if col in hist.columns]]
    hist = hist.sort_values("date", ascending=True).drop_duplicates("date").reset_index(drop=True)

    return hist


def save_data(df: pd.DataFrame, symbol: str) -> Path:
    """Menyimpan data saham ke artifact/data/{symbol}.csv."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = config.DATA_DIR / f"{symbol}.csv"

    df.to_csv(file_path, index=False)
    print(f"Selesai! Total {len(df)} baris data disimpan ke: {file_path}")
    return file_path


def parse_args():
    parser = argparse.ArgumentParser(description="Ingestion data saham menggunakan yfinance.")
    parser.add_argument("-s", "--symbols", nargs="+", default=None, help="Daftar simbol saham (contoh: -s BBCA BBRI)")
    parser.add_argument("--start", type=str, default=None, help="Tanggal awal (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=None, help="Tanggal akhir (YYYY-MM-DD)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Membaca parameter dari params.yaml via DVC API
    params = dvc.api.params_show().get("ingestion", {})

    symbols = args.symbols or params.get("symbols", [])
    if isinstance(symbols, str):
        symbols = [s.strip() for s in symbols.split(",") if s.strip()]

    start_date = args.start or params.get("start_date")
    end_date = args.end or params.get("end_date")

    if not symbols:
        print("Error: Simbol saham tidak ditentukan di CLI maupun params.yaml.")
        return

    if not start_date or not end_date:
        print("Error: Tanggal awal (--start) dan tanggal akhir (--end) harus ditentukan.")
        return

    # Proses setiap simbol saham dan simpan ke artifact/data/{symbol}.csv
    for symbol in symbols:
        ticker = symbol.strip().upper()
        df = fetch_stock_data(ticker, start_date, end_date)
        if not df.empty:
            save_data(df, ticker)
        else:
            print(f"Peringatan: Gagal menyimpan data untuk {ticker}.")


if __name__ == "__main__":
    main()