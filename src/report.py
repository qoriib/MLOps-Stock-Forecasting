import argparse
import glob
import os
import sys
from pathlib import Path
import pandas as pd
from src.config import ARTIFACT_DIR, DATA_DIR, MODEL_DIR

def format_currency(val):
    try:
        return f"Rp {float(val):,.2f}"
    except (ValueError, TypeError):
        return str(val)

def generate_report(output_path: Path = None) -> str:
    lines = []
    lines.append("## 📊 Machine Learning Pipeline Summary\n")

    # 1. Dataset Overview
    data_files = sorted(glob.glob(str(DATA_DIR / "*.csv")))
    if data_files:
        lines.append("### 📁 Dataset Overview\n")
        lines.append("| Ticker | Records | Date Range | Latest Close Price |")
        lines.append("| :--- | :---: | :---: | :---: |")

        for df_path in data_files:
            ticker = Path(df_path).stem
            try:
                df = pd.read_csv(df_path)
                df["date"] = pd.to_datetime(df["date"], utc=True)
                min_date = df["date"].min().strftime("%Y-%m-%d")
                max_date = df["date"].max().strftime("%Y-%m-%d")
                latest_close = df.iloc[-1]["close"]
                lines.append(f"| **`{ticker}`** | {len(df):,} | {min_date} to {max_date} | {format_currency(latest_close)} |")
            except Exception as e:
                lines.append(f"| **`{ticker}`** | Error loading data: {e} | - | - |")
        lines.append("\n")

    # 2. Champion Models
    hp_files = sorted(glob.glob(str(MODEL_DIR / "*_hyperparameter.csv")))
    if hp_files:
        lines.append("### 🏆 Champion Models (Best Performance)\n")
        lines.append("| Ticker | Model | Time Steps | Optimizer | Batch | Learning Rate | RMSE | MAPE |")
        lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")

        for hp_path in hp_files:
            ticker = Path(hp_path).stem.replace("_hyperparameter", "")
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
                lines.append(f"| **`{ticker}`** | Error loading metrics: {e} | - | - | - | - | - | - |")
        lines.append("\n")

        # 3. Detailed Hyperparameter Tuning Results
        lines.append("<details>\n<summary>🔍 <b>View Detailed Hyperparameter Grid Results</b></summary>\n<br>\n")
        for hp_path in hp_files:
            ticker = Path(hp_path).stem.replace("_hyperparameter", "")
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

    # Save to report output path
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report_content)
        print(f"Report successfully saved to {output_path}")

    # Append to GitHub Step Summary if running in GitHub Actions
    summary_env = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_env:
        with open(summary_env, "a") as summary_file:
            summary_file.write(report_content + "\n")
        print("Report appended to GITHUB_STEP_SUMMARY.")

    return report_content

def main():
    parser = argparse.ArgumentParser(description="Generate ML pipeline summary report")
    parser.add_argument(
        "--output",
        type=str,
        default=str(ARTIFACT_DIR / "report.md"),
        help="Path to output markdown report file",
    )
    args = parser.parse_args()

    out_file = Path(args.output) if args.output else ARTIFACT_DIR / "report.md"
    generate_report(out_file)

if __name__ == "__main__":
    main()
