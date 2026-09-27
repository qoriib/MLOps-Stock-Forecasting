#!/usr/bin/env python3
import glob
import os
import sys
import pandas as pd

def format_currency(val):
    try:
        return f"Rp {float(val):,.2f}"
    except (ValueError, TypeError):
        return str(val)

def generate_report():
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    lines = []

    lines.append("## 📊 Machine Learning Pipeline Summary\n")

    # 1. Dataset Information
    data_files = sorted(glob.glob("artifact/data/*.csv"))
    if data_files:
        lines.append("### 📁 Dataset Overview\n")
        lines.append("| Ticker | Records | Date Range | Latest Close Price |")
        lines.append("| :--- | :---: | :---: | :---: |")

        for df_path in data_files:
            ticker = os.path.basename(df_path).replace(".csv", "")
            try:
                df = pd.read_csv(df_path)
                df["date"] = pd.to_datetime(df["date"], utc=True)
                min_date = df["date"].min().strftime("%Y-%m-%d")
                max_date = df["date"].max().strftime("%Y-%m-%d")
                latest_close = df.iloc[-1]["close"]
                lines.append(f"| **`{ticker}`** | {len(df):,} | {min_date} to {max_date} | {format_currency(latest_close)} |")
            except Exception as e:
                lines.append(f"| **`{ticker}`** | Error loading data | - | - |")
        lines.append("\n")

    # 2. Champion Models (Best Performance)
    hp_files = sorted(glob.glob("artifact/model/*_hyperparameter.csv"))
    if hp_files:
        lines.append("### 🏆 Champion Models (Best Performance)\n")
        lines.append("| Ticker | Model | Time Steps | Optimizer | Batch | Learning Rate | RMSE | MAPE |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

        for hp_path in hp_files:
            ticker = os.path.basename(hp_path).replace("_hyperparameter.csv", "")
            try:
                hp_df = pd.read_csv(hp_path)
                if not hp_df.empty and "MAPE" in hp_df.columns:
                    best = hp_df.sort_values(by="MAPE").iloc[0]
                    lines.append(
                        f"| **`{ticker}`** | **{best['model']}** | {int(best['time_steps'])} | "
                        f"{best['optimizer']} | {int(best['batch_size'])} | {best['learning_rate']} | "
                        f"{float(best['RMSE']):.2f} | **{float(best['MAPE']):.2f}%** |"
                    )
            except Exception as e:
                lines.append(f"| **`{ticker}`** | Error loading model metrics | - | - | - | - | - | - |")
        lines.append("\n")

        # 3. Detailed Hyperparameter Comparison per Ticker
        lines.append("<details>\n<summary>🔍 <b>View Detailed Hyperparameter Grid Results</b></summary>\n<br>\n")
        for hp_path in hp_files:
            ticker = os.path.basename(hp_path).replace("_hyperparameter.csv", "")
            try:
                hp_df = pd.read_csv(hp_path)
                if not hp_df.empty:
                    lines.append(f"#### `{ticker}` Hyperparameters\n")
                    lines.append("| Model | Time Steps | Optimizer | Batch | LR | Epochs | RMSE | MAPE |")
                    lines.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
                    sorted_df = hp_df.sort_values(by="MAPE")
                    for _, row in sorted_df.iterrows():
                        lines.append(
                            f"| {row['model']} | {int(row['time_steps'])} | {row['optimizer']} | "
                            f"{int(row['batch_size'])} | {row['learning_rate']} | {int(row['epochs_trained'])} | "
                            f"{float(row['RMSE']):.2f} | {float(row['MAPE']):.2f}% |"
                        )
                    lines.append("\n")
            except Exception as e:
                lines.append(f"Could not load details for {ticker}: {e}\n")
        lines.append("</details>\n")

    report_content = "\n".join(lines)

    if summary_path:
        with open(summary_path, "a") as f:
            f.write(report_content + "\n")
        print("ML report successfully appended to GITHUB_STEP_SUMMARY.")
    else:
        print(report_content)

if __name__ == "__main__":
    generate_report()
