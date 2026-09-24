import argparse
import json
import shutil
import dvc.api
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import config

def store_scaler(ticker: str, target_col: str, train_size: float) -> dict | None:
    parquet_path = config.DATA_DIR / f"{ticker}.parquet"

    if not parquet_path.exists():
        print(f"[Warning] Parquet {parquet_path} tidak ditemukan untuk scaler.")
        return None

    df = pd.read_parquet(parquet_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    train_len = int(len(df) * train_size)
    train_df = df.iloc[:train_len].copy()

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(train_df[[target_col]].values)

    scaler_data = {
        "scaler_type": "MinMaxScaler",
        "ticker": ticker,
        "target_col": target_col,
        "feature_range": list(scaler.feature_range),
        "data_min": float(scaler.data_min_[0]),
        "data_max": float(scaler.data_max_[0]),
        "data_range": float(scaler.data_range_[0]),
        "scale": float(scaler.scale_[0]),
        "min": float(scaler.min_[0]),
        "n_samples_seen": int(scaler.n_samples_seen_),
        "train_samples": len(train_df),
        "total_samples": len(df),
    }

    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    scaler_path = config.MODEL_DIR / f"{ticker}_scaler.json"
    with open(scaler_path, "w", encoding="utf-8") as f:
        json.dump(scaler_data, f, indent=2)
    print(f"[Scaler JSON] Scaler disimpan ke: {scaler_path}")

    return scaler_data


def store_metrics(
    ticker: str,
    target_col: str,
    train_size: float,
    random_state: int,
    epochs: int,
) -> dict | None:
    parquet_path = config.MODEL_DIR / f"{ticker}_hyperparameter.parquet"

    if not parquet_path.exists():
        print(f"[Warning] File riwayat hyperparameter {parquet_path} tidak ditemukan.")
        fallback_metrics_path = config.MODEL_DIR / f"{ticker}_metrics.json"
        if fallback_metrics_path.exists():
            with open(fallback_metrics_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    results_df = pd.read_parquet(parquet_path)
    grouped_by_model = results_df.groupby("model")
    best_indices = grouped_by_model["RMSE"].idxmin().values
    best_configs_df = results_df.loc[best_indices].reset_index(drop=True)

    best_overall_row = best_configs_df.loc[best_configs_df["RMSE"].idxmin()]
    best_overall_model = str(best_overall_row["model"])

    clean_best_configs = {}
    metrics_summary = {}

    for _, row in best_configs_df.iterrows():
        m_name = str(row["model"])
        cfg_dict = row.to_dict()

        clean_cfg = {}
        for k, v in cfg_dict.items():
            if isinstance(v, (np.integer, int)):
                clean_cfg[k] = int(v)
            elif isinstance(v, (np.floating, float)):
                clean_cfg[k] = float(v)
            else:
                clean_cfg[k] = str(v)

        clean_best_configs[m_name] = clean_cfg

        metrics_summary[m_name] = {
            "MSE": float(row.get("MSE", 0.0)),
            "RMSE": float(row.get("RMSE", 0.0)),
            "MAPE": float(row.get("MAPE", 0.0)),
            "R2": float(row.get("R2", 0.0)) if "R2" in row and not pd.isna(row.get("R2")) else 0.0,
            "time_steps": int(row.get("time_steps", 30)),
            "optimizer": str(row.get("optimizer", "Adam")),
            "batch_size": int(row.get("batch_size", 32)),
            "learning_rate": float(row.get("learning_rate", 0.001)),
        }

    metadata = {
        "ticker": ticker,
        "target_col": target_col,
        "train_size": float(train_size),
        "random_state": int(random_state),
        "epochs": int(epochs),
        "best_model": best_overall_model,
        "best_configs": clean_best_configs,
        "metrics": metrics_summary,
    }

    config.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    metrics_path = config.MODEL_DIR / f"{ticker}_metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"[Metrics JSON] Metrik disimpan ke: {metrics_path}")

    return metadata


def copy_backend_assets(tickers: list[str]) -> list[str]:
    backend_assets_dir = config.BASE_DIR / "web" / "backend" / "assets"
    backend_assets_dir.mkdir(parents=True, exist_ok=True)
    copied_files = []

    for ticker in tickers:
        # 1. Salin dataset harga saham .parquet
        src_parquet = config.DATA_DIR / f"{ticker}.parquet"
        dst_parquet = backend_assets_dir / f"{ticker}.parquet"
        if src_parquet.exists():
            shutil.copy2(src_parquet, dst_parquet)
            copied_files.append(str(dst_parquet))
            print(f"[Asset Copy] {src_parquet} -> {dst_parquet}")

        # 2. Salin scaler JSON
        src_scaler = config.MODEL_DIR / f"{ticker}_scaler.json"
        dst_scaler = backend_assets_dir / f"{ticker}_scaler.json"
        if src_scaler.exists():
            shutil.copy2(src_scaler, dst_scaler)
            copied_files.append(str(dst_scaler))
            print(f"[Asset Copy] {src_scaler} -> {dst_scaler}")

        # 3. Salin metrics JSON
        src_metrics = config.MODEL_DIR / f"{ticker}_metrics.json"
        dst_metrics = backend_assets_dir / f"{ticker}_metrics.json"
        if src_metrics.exists():
            shutil.copy2(src_metrics, dst_metrics)
            copied_files.append(str(dst_metrics))
            print(f"[Asset Copy] {src_metrics} -> {dst_metrics}")

        # 4. Salin model Keras (LSTM & GRU)
        for m_type in ["LSTM", "GRU"]:
            src_model = config.MODEL_DIR / f"{ticker}_{m_type}.keras"
            dst_model = backend_assets_dir / f"{ticker}_{m_type}.keras"
            if src_model.exists():
                shutil.copy2(src_model, dst_model)
                copied_files.append(str(dst_model))
                print(f"[Asset Copy] {src_model} -> {dst_model}")

        # 5. Salin juga jika ada format model lain (misal .onnx)
        for extra_model in config.MODEL_DIR.glob(f"{ticker}_*.onnx"):
            dst_extra = backend_assets_dir / extra_model.name
            shutil.copy2(extra_model, dst_extra)
            copied_files.append(str(dst_extra))
            print(f"[Asset Copy] {extra_model} -> {dst_extra}")

    return copied_files


def main():
    parser = argparse.ArgumentParser(description="Penyimpanan artefak scaler, metrik evaluasi, dan penyalinan aset backend")
    parser.add_argument("--ticker", type=str, help="Ticker spesifik yang ingin diproses")
    args = parser.parse_args()

    params = dvc.api.params_show()
    raw_tickers = params.get("tickers", [])
    if isinstance(raw_tickers, str):
        raw_tickers = raw_tickers.split(",")

    all_tickers = [t.strip().upper() for t in raw_tickers if t.strip()]

    target_col = params.get("target_col", "close")
    train_size = float(params.get("train_size", params.get("train_size_ratio", 0.8)))
    random_state = int(params.get("random_state", 42))
    epochs = int(params.get("epochs", 50))

    tickers_to_process = [args.ticker.strip().upper()] if args.ticker else all_tickers
    print(f"=== Memproses Artefak Scaler, Metrik & Copy Aset untuk: {tickers_to_process} ===")

    for ticker in tickers_to_process:
        store_scaler(ticker, target_col, train_size)
        store_metrics(ticker, target_col, train_size, random_state, epochs)

    # Langkah penyalinan artefak ke web/backend/assets agar tidak relatif ke ../..
    copy_backend_assets(tickers_to_process)


if __name__ == "__main__":
    main()
