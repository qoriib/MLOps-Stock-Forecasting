import argparse
import json
import logging
import pandas as pd
from pathlib import Path
from typing import List
from src import config

logger = logging.getLogger("report_stage")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def build_dataset_summary() -> str:
    records_list = []

    # Temukan seluruh file metrik data understanding yang tersedia
    understanding_files = sorted(config.METRICS_DIR.glob("*_data_understanding.json"))

    # Ekstrak informasi statistik untuk setiap ticker
    for json_file_path in understanding_files:
        with open(json_file_path, "r") as file_pointer:
            data_dictionary = json.load(file_pointer)

        ticker = data_dictionary.get("ticker", json_file_path.stem.replace("_data_understanding", ""))
        target_column = data_dictionary.get("target_col", "close")
        statistics_dictionary = data_dictionary.get("stats", {}).get(target_column, {})

        mean_price = statistics_dictionary.get("mean", 0.0)
        std_price = statistics_dictionary.get("std", 0.0)
        min_price = statistics_dictionary.get("min", 0.0)
        max_price = statistics_dictionary.get("max", 0.0)

        # Catat baris ringkasan dataset
        records_list.append({
            "Ticker": ticker,
            "Period": f"{data_dictionary.get('min_date')} to {data_dictionary.get('max_date')}",
            "Rows": data_dictionary.get("total_rows", 0),
            "Gaps": data_dictionary.get("gap_count", 0),
            "Price (Mean ± Std)": f"{mean_price:.2f} ± {std_price:.2f}",
            "Price Range": f"{min_price:.2f} - {max_price:.2f}",
        })

    if not records_list:
        return ""

    # Konversi data ke tabel markdown
    summary_dataframe = pd.DataFrame(records_list)
    return "## Dataset Overview\n\n" + summary_dataframe.to_markdown(index=False) + "\n\n"


def build_models_summary() -> str:
    records_list = []

    # Temukan seluruh file rekaman hasil hyperparameter
    hyperparameter_files = sorted(config.METRICS_DIR.glob("*_hyperparameter.csv"))

    # Proses perbandingan performa model per ticker
    for csv_file_path in hyperparameter_files:
        ticker = csv_file_path.stem.replace("_hyperparameter", "")
        hyperparameter_dataframe = pd.read_csv(csv_file_path)

        if hyperparameter_dataframe.empty or "MAPE" not in hyperparameter_dataframe.columns:
            continue

        # Identifikasi konfigurasi terbaik dengan nilai MAPE terendah
        best_row_index = hyperparameter_dataframe["MAPE"].idxmin()
        sorted_dataframe = hyperparameter_dataframe.sort_values(by="MAPE")

        # Petakan status promosi model
        for row_index, row_data in sorted_dataframe.iterrows():
            if row_index == best_row_index:
                promotion_status = "Champion"
            else:
                promotion_status = "Candidate"

            records_list.append({
                "Ticker": ticker,
                "Model": row_data["model"],
                "Time Steps": int(row_data["time_steps"]),
                "Batch Size": int(row_data["batch_size"]),
                "Optimizer": row_data["optimizer"],
                "Learning Rate": row_data["learning_rate"],
                "RMSE": round(float(row_data["RMSE"]), 2),
                "MAPE": f"{float(row_data['MAPE']):.2f}%",
                "Status": promotion_status,
            })

    if not records_list:
        return ""

    # Konversi data evaluasi ke tabel markdown
    models_dataframe = pd.DataFrame(records_list)
    return "## Model Evaluation\n\n" + models_dataframe.to_markdown(index=False) + "\n\n"


def generate_report(output_path: Path) -> str:
    # Susun bagian overview dataset
    dataset_section = build_dataset_summary()

    # Susun bagian evaluasi performa model
    models_section = build_models_summary()

    # Gabungkan dan simpan laporan Markdown ke direktori artefak
    report_content = "# Pipeline Report\n\n" + dataset_section + models_section
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_content.strip() + "\n")
    logger.info(f"[Artifact] Laporan berhasil disimpan ke: {output_path}")

    return report_content


def main():
    # Inisialisasi argumen CLI
    parser = argparse.ArgumentParser(description="CRISP-DM Stage 6: Generate Pipeline Report")
    parser.add_argument(
        "--output",
        type=str,
        default=str(config.ARTIFACT_DIR / "report.md"),
        help="Path ke file output markdown laporan",
    )

    # Parsing parameter input
    arguments = parser.parse_args()
    output_file_path = Path(arguments.output)

    # Eksekusi pembuatan laporan
    logger.info("=== Menjalankan Stage Report ===")
    generate_report(output_path=output_file_path)
    logger.info("=== Selesai Stage Report ===")


if __name__ == "__main__":
    main()
