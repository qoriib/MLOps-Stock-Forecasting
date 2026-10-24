import re
import argparse
from pathlib import Path


def transform_report(report_file: Path, blob_base_url: str, output_file: Path | None = None) -> str:
    if not report_file.exists():
        print(f"Warning: Report file does not exist: {report_file}")
        return ""

    content = report_file.read_text(encoding="utf-8")
    blob_base = blob_base_url.rstrip("/")

    transformed_content = re.sub(r"\((?:\.\./|\./)?(?:artifact/)?plots/([^)]+)\)", rf"({blob_base}/\1)", content)

    target_path = output_file if output_file else report_file
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(transformed_content, encoding="utf-8")
    print(f"Successfully transformed {report_file} and saved to {target_path}")

    return transformed_content


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Transform relative plot paths in markdown report to Azure Blob Storage URLs."
    )
    parser.add_argument("--report-file", type=Path, required=True, help="Path to markdown report file.")
    parser.add_argument("--blob-base-url", type=str, required=True, help="Base URL for Azure Blob Storage container.")
    parser.add_argument(
        "--output-file",
        type=Path,
        default=None,
        help="Path to write transformed markdown. Defaults to overwriting --report-file.",
    )

    args = parser.parse_args()
    transform_report(
        report_file=args.report_file,
        blob_base_url=args.blob_base_url,
        output_file=args.output_file,
    )


if __name__ == "__main__":
    main()
