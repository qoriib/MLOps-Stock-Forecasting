import argparse
import time
from datetime import datetime, timedelta
from pathlib import Path
import dvc.api
import pandas as pd
import requests
from src import config


def fetch_stock_data(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Mengambil data historis saham dari GoAPI."""
    start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

    all_data = []
    current_end = end_date_obj

    while current_end >= start_date_obj:
        current_start = max(current_end - timedelta(days=364), start_date_obj)
        date_from = current_start.strftime("%Y-%m-%d")
        date_to = current_end.strftime("%Y-%m-%d")

        url = f"{config.BASE_URL}/{symbol}/historical?from={date_from}&to={date_to}"
        print(f"Fetching {symbol}: {date_from} sampai {date_to}")

        res = requests.get(url, headers=config.HEADERS)
        if res.status_code == 200:
            res_json = res.json()
            results = res_json.get("data", {}).get("results", [])
            all_data.extend(results)
        else:
            err_msg = res.json().get("message", f"HTTP {res.status_code}")
            print(f"Peringatan API: {err_msg}")
            break

        current_end = current_start - timedelta(days=1)
        time.sleep(1)

    df = pd.DataFrame(all_data)
    if not df.empty and "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date", ascending=True).drop_duplicates("date").reset_index(drop=True)

    return df


def save_data(df: pd.DataFrame, symbol: str) -> Path:
    """Menyimpan data saham ke artifact/data/{symbol}.csv."""
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = config.DATA_DIR / f"{symbol}.csv"

    df.to_csv(file_path, index=False)
    print(f"Selesai! Total {len(df)} data disimpan ke: {file_path}")
    return file_path


def parse_args():
    parser = argparse.ArgumentParser(description="Ingestion data saham GoAPI.")
    parser.add_argument("-s", "--symbols", nargs="+", default=None, help="Daftar simbol saham (contoh: -s BBCA BBRI)")
    parser.add_argument("--start", type=str, default=None, help="Tanggal awal (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, default=None, help="Tanggal akhir (YYYY-MM-DD)")
    return parser.parse_args()


def main():
    args = parse_args()

    # Membaca parameter langsung menggunakan API resmi DVC
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
            print(f"Peringatan: Data kosong untuk {ticker}.")


if __name__ == "__main__":
    main()