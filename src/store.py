import argparse
from datetime import datetime
from pathlib import Path
import dvc.api
import pandas as pd
from src import config


def parse_args():
    parser = argparse.ArgumentParser(description="Generate SQL seed for Cloudflare D1 from stock and forecast data.")
    parser.add_argument(
        "-t", "--tickers",
        nargs="+",
        default=None,
        help="Daftar ticker/simbol saham (contoh: -t BBCA BBRI)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=str(config.SEED_SQL_PATH),
        help="Path file SQL output (default: artifact/seed.sql)"
    )
    return parser.parse_args()


def generate_seed_sql(tickers: list[str], output_file: Path, batch_size: int = 500) -> int:
    """Membaca CSV data historis & prediksi saham dan menghasilkan file SQL seed untuk Cloudflare D1."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    total_records = 0
    now_str = datetime.now().isoformat()

    with open(output_file, "w", encoding="utf-8") as f:
        # Header dan Schema Table D1 (SQLite)
        f.write("-- ========================================================\n")
        f.write(f"-- Cloudflare D1 Database Seed (Historical & Forecasts)\n")
        f.write(f"-- Generated At: {now_str}\n")
        f.write("-- ========================================================\n\n")

        # 1. Tabel Riwayat Harga Saham
        f.write("CREATE TABLE IF NOT EXISTS stock_prices (\n")
        f.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
        f.write("    symbol TEXT NOT NULL,\n")
        f.write("    date TEXT NOT NULL,\n")
        f.write("    open REAL,\n")
        f.write("    high REAL,\n")
        f.write("    low REAL,\n")
        f.write("    close REAL,\n")
        f.write("    volume INTEGER,\n")
        f.write("    UNIQUE(symbol, date)\n")
        f.write(");\n\n")

        f.write("CREATE INDEX IF NOT EXISTS idx_stock_prices_symbol_date\n")
        f.write("    ON stock_prices (symbol, date DESC);\n\n")

        # 2. Tabel Hasil Prediksi / Forecasting Saham
        f.write("CREATE TABLE IF NOT EXISTS stock_forecasts (\n")
        f.write("    id INTEGER PRIMARY KEY AUTOINCREMENT,\n")
        f.write("    symbol TEXT NOT NULL,\n")
        f.write("    date TEXT NOT NULL,\n")
        f.write("    model TEXT NOT NULL,\n")
        f.write("    predicted_price REAL NOT NULL,\n")
        f.write("    target_col TEXT NOT NULL,\n")
        f.write("    created_at TEXT NOT NULL,\n")
        f.write("    UNIQUE(symbol, model, date)\n")
        f.write(");\n\n")

        f.write("CREATE INDEX IF NOT EXISTS idx_stock_forecasts_symbol_date\n")
        f.write("    ON stock_forecasts (symbol, date ASC);\n\n")

        # Ingestion data historis
        for ticker in tickers:
            ticker_clean = ticker.strip().upper()
            csv_path = config.DATA_DIR / f"{ticker_clean}.csv"

            if not csv_path.exists():
                print(f"Peringatan: File historis {csv_path} tidak ditemukan, melewati {ticker_clean}...")
                continue

            df = pd.read_csv(csv_path)
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            if not all(col in df.columns for col in required_cols):
                print(f"Peringatan: Kolom pada {csv_path} tidak lengkap, melewati {ticker_clean}...")
                continue

            symbol_records = len(df)
            total_records += symbol_records
            print(f"Memproses {symbol_records} baris data historis untuk ticker {ticker_clean}...")

            for i in range(0, len(df), batch_size):
                batch_df = df.iloc[i : i + batch_size]
                values_clauses = []

                for _, row in batch_df.iterrows():
                    date_val = str(row["date"])
                    open_val = float(row["open"]) if pd.notna(row["open"]) else "NULL"
                    high_val = float(row["high"]) if pd.notna(row["high"]) else "NULL"
                    low_val = float(row["low"]) if pd.notna(row["low"]) else "NULL"
                    close_val = float(row["close"]) if pd.notna(row["close"]) else "NULL"
                    vol_val = int(row["volume"]) if pd.notna(row["volume"]) else 0

                    values_clauses.append(
                        f"('{ticker_clean}', '{date_val}', {open_val}, {high_val}, {low_val}, {close_val}, {vol_val})"
                    )

                if values_clauses:
                    f.write("INSERT OR REPLACE INTO stock_prices (symbol, date, open, high, low, close, volume) VALUES\n")
                    f.write(",\n".join(f"    {clause}" for clause in values_clauses))
                    f.write(";\n\n")

        # Ingestion data prediksi / forecasting
        for ticker in tickers:
            forecast_csv_path = config.FORECAST_DIR / f"{ticker_clean}_forecast.csv"
            if not forecast_csv_path.exists():
                # Fallback jika ada di DATA_DIR
                forecast_csv_path = config.DATA_DIR / f"{ticker_clean}_forecast.csv"

            if not forecast_csv_path.exists():
                print(f"Info: File prediksi {forecast_csv_path} belum ada, melewati prediksi untuk {ticker_clean}...")
                continue

            fdf = pd.read_csv(forecast_csv_path)
            req_forecast_cols = ["date", "model", "predicted_price", "target_col"]
            if not all(col in fdf.columns for col in req_forecast_cols):
                print(f"Peringatan: Kolom file prediksi {forecast_csv_path} tidak sesuai skema...")
                continue

            forecast_records = len(fdf)
            total_records += forecast_records
            print(f"Memproses {forecast_records} baris data prediksi untuk ticker {ticker_clean}...")

            values_clauses = []
            for _, row in fdf.iterrows():
                date_val = str(row["date"])
                model_val = str(row["model"])
                pred_price = float(row["predicted_price"])
                target_col = str(row["target_col"])

                values_clauses.append(
                    f"('{ticker_clean}', '{date_val}', '{model_val}', {pred_price}, '{target_col}', '{now_str}')"
                )

            if values_clauses:
                f.write("INSERT OR REPLACE INTO stock_forecasts (symbol, date, model, predicted_price, target_col, created_at) VALUES\n")
                f.write(",\n".join(f"    {clause}" for clause in values_clauses))
                f.write(";\n\n")

    print(f"Selesai! Berhasil membuat seed SQL di: {output_file} (Total: {total_records} baris)")
    return total_records


def main():
    args = parse_args()

    # Membaca parameter dari params.yaml via DVC API
    raw_params = dvc.api.params_show()
    params = raw_params.get("ingestion", raw_params)

    tickers = args.tickers or params.get("tickers") or params.get("symbols", [])
    if isinstance(tickers, str):
        tickers = [t.strip() for t in tickers.split(",") if t.strip()]

    if not tickers:
        print("Error: Ticker tidak ditentukan di CLI maupun params.yaml.")
        return

    output_path = Path(args.output)
    generate_seed_sql(tickers, output_path)


if __name__ == "__main__":
    main()
