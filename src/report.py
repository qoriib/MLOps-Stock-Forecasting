import argparse
import glob
import logging
from pathlib import Path
import pandas as pd
from src import config

logger = logging.getLogger("report_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_dataset_section() -> str:
    data_files = sorted(glob.glob(str(config.DATA_DIR / "*.csv")))
    if not data_files:
        return ""

    records = []
    for file_path in data_files:
        ticker = Path(file_path).stem
        try:
            df = pd.read_csv(file_path)
            min_date = str(df["date"].min()).split()[0]
            max_date = str(df["date"].max()).split()[0]
            latest_close = df.iloc[-1]["close"]

            records.append({
                "Ticker": ticker,
                "Jumlah Data": len(df),
                "Date Range": f"{min_date} to {max_date}",
                "Latest Close": round(float(latest_close), 2),
            })
        except Exception as e:
            logger.warning(f"Gagal memproses data {ticker}: {e}")
            records.append({
                "Ticker": ticker,
                "Jumlah Data": 0,
                "Date Range": str(e),
                "Latest Close": 0,
            })

    if not records:
        return ""

    content = ["## Dataset Overview\n"]
    dataset_df = pd.DataFrame(records)
    content.append(dataset_df.to_markdown(index=False))
    content.append("\n")
    return "\n".join(content)


def build_champion_section() -> str:
    hp_files = sorted(glob.glob(str(config.MODEL_DIR / "*_hyperparameter.csv")))
    if not hp_files:
        return ""

    records = []
    for hp_path in hp_files:
        ticker = Path(hp_path).stem.replace("_hyperparameter", "")
        try:
            hp_df = pd.read_csv(hp_path)
            if not hp_df.empty and "MAPE" in hp_df.columns:
                best = hp_df.sort_values(by="MAPE").iloc[0]
                records.append({
                    "Ticker": ticker,
                    "Model": best["model"],
                    "Time Steps": best["time_steps"],
                    "Optimizer": best["optimizer"],
                    "Batch Size": best["batch_size"],
                    "Learning Rate": best["learning_rate"],
                    "RMSE": round(float(best["RMSE"]), 2),
                    "MAPE": round(float(best["MAPE"]), 2),
                })
        except Exception as e:
            logger.warning(f"Gagal membaca hyperparameter {ticker}: {e}")

    if not records:
        return ""

    content = ["## Champion Models\n"]
    champion_df = pd.DataFrame(records)
    content.append(champion_df.to_markdown(index=False))
    content.append("\n")
    return "\n".join(content)


def generate_report(output_path: Path) -> str:
    sections = [
        build_dataset_section(),
        build_champion_section(),
    ]
    report_content = "\n".join(filter(None, sections))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_content)
    logger.info(f"[Artifact] Laporan berhasil disimpan ke: {output_path}")

    return report_content


def main():
    parser = argparse.ArgumentParser(description="Generate ML pipeline report")
    parser.add_argument(
        "--output",
        type=str,
        default=str(config.ARTIFACT_DIR / "report.md"),
        help="Path ke file output markdown laporan",
    )
    args = parser.parse_args()
    out_file = Path(args.output)

    logger.info("=== Menjalankan Stage Report ===")
    generate_report(out_file)
    logger.info("=== Selesai Stage Report ===")


if __name__ == "__main__":
    main()
