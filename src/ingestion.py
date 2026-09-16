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

def df_to_sql_inserts(df: pd.DataFrame, ticker: str, chunk_size: int = 200) -> str:
    sql_lines = []
    
    rows = []
    for _, row in df.iterrows():
        d_str = str(row['date'])
        o_val = float(row.get('open', 0.0))
        h_val = float(row.get('high', 0.0))
        l_val = float(row.get('low', 0.0))
        c_val = float(row.get('close', 0.0))
        v_val = int(row.get('volume', 0))
        rows.append(f"('{ticker}', '{d_str}', {o_val:.4f}, {h_val:.4f}, {l_val:.4f}, {c_val:.4f}, {v_val})")
        
        if len(rows) >= chunk_size:
            sql_lines.append(
                "INSERT INTO stock_prices (ticker, date, open, high, low, close, volume) VALUES\n  "
                + ",\n  ".join(rows)
                + ";"
            )
            rows = []
            
    if rows:
        sql_lines.append(
            "INSERT INTO stock_prices (ticker, date, open, high, low, close, volume) VALUES\n  "
            + ",\n  ".join(rows)
            + ";"
        )
        
    return "\n\n".join(sql_lines)

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
    df['Date'] = df['Date'].dt.date
    df['ticker'] = ticker
    
    # Rename kolom
    df.columns = df.columns.str.lower()
    df = df.drop_duplicates("date").sort_values("date")

    # 1. Simpan File CSV (untuk pipeline pelatihan DVC)
    os.makedirs(config.DATA_DIR, exist_ok=True)
    csv_path = os.path.join(config.DATA_DIR, f"{ticker}.csv")
    df.to_csv(csv_path, index=False)
    print(f"[CSV] {len(df)} baris disimpan ke: {csv_path}")

    # 2. Simpan File SQL Seeding per ticker (khusus INSERT data untuk Cloudflare D1)
    sql_path = os.path.join(config.DATA_DIR, f"{ticker}_seed.sql")
    sql_content = f"-- Seeding data harga pasar untuk {ticker}\n" + df_to_sql_inserts(df, ticker) + "\n"
    with open(sql_path, "w", encoding="utf-8") as f:
        f.write(sql_content)
    print(f"[SQL Seed] Skrip seeding data disimpan ke: {sql_path}")

    return df


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

    all_dfs = {}
    for ticker in tickers:
        df = fetch_data(ticker, start_date, end_date)
        if df is not None:
            all_dfs[ticker] = df

    # Simpan master seed.sql yang menggabungkan seluruh data seeding ticker (murni data insert)
    if all_dfs:
        seed_path = os.path.join(config.DATA_DIR, "seed.sql")
        master_sql_parts = ["-- Seeding terpadu seluruh data pasar saham untuk Cloudflare D1"]
        for ticker, df in all_dfs.items():
            master_sql_parts.append(f"-- Data Inserts {ticker}")
            master_sql_parts.append(df_to_sql_inserts(df, ticker))
        master_sql_content = "\n\n".join(master_sql_parts) + "\n"
        with open(seed_path, "w", encoding="utf-8") as f:
            f.write(master_sql_content)
        print(f"[SQL Seed Master] Berhasil membuat seed.sql terpadu di: {seed_path}")

        # Salin juga ke web/backend/seed.sql untuk kenyamanan developer
        backend_seed_path = os.path.join(config.BASE_DIR, "web", "backend", "seed.sql")
        with open(backend_seed_path, "w", encoding="utf-8") as f:
            f.write(master_sql_content)
        print(f"[SQL Seed Backend] seed.sql disalin ke backend: {backend_seed_path}")


if __name__ == "__main__":
    main()