import argparse
import csv
import logging
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("load_test_runner")


def run_locust_headless(
    host: str,
    locustfile_path: Path,
    users: int = 150,
    spawn_rate: int = 15,
    run_time: str = "45s",
    csv_prefix: Path = Path("results"),
) -> int:
    command = [
        sys.executable,
        "-m",
        "locust",
        "-f",
        str(locustfile_path),
        "--headless",
        "--host",
        host,
        "-u",
        str(users),
        "-r",
        str(spawn_rate),
        "--run-time",
        run_time,
        "--csv",
        str(csv_prefix),
        "--only-summary",
    ]

    logger.info(f"Menjalankan Load Testing: CCU={users}, Spawn Rate={spawn_rate}/s, Durasi={run_time}, Target={host}")
    logger.info(f"Output Prefix: {csv_prefix}")

    process = subprocess.run(command)
    return process.returncode


def generate_report(
    csv_prefix: Path,
    output_file: Path,
    host: str,
    users: int,
    spawn_rate: int,
    run_time: str,
) -> None:
    stats_csv_file = Path(f"{csv_prefix}_stats.csv")
    if not stats_csv_file.exists():
        logger.warning(f"File hasil CSV {stats_csv_file} tidak ditemukan.")
        return

    rows = []
    with open(stats_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        return

    total_row = rows[-1]
    detail_rows = rows[:-1]

    total_requests = int(total_row.get("Request Count", 0))
    total_failures = int(total_row.get("Failure Count", 0))
    failure_rate = (total_failures / total_requests * 100) if total_requests > 0 else 0.0
    total_avg = round(float(total_row.get("Average Response Time", 0)), 2)
    total_rps = round(float(total_row.get("Requests/s", 0)), 2)

    error_status = "Pass" if failure_rate < 1.0 else "Fail"
    latency_status = "Pass" if total_avg < 1000.0 else "Review"

    lines = [
        "# Load Test Report",
        "",
        "## Test Configuration",
        "",
        "| Target Host | Peak CCU | Spawn Rate | Duration |",
        "|:---|---:|---:|:---|",
        f"| {host} | {users} | {spawn_rate}/s | {run_time} |",
        "",
        "## Endpoint Statistics",
        "",
        "| Method | Endpoint | Requests | Failures | Median (ms) | Avg (ms) | p90 (ms) | p95 (ms) | RPS |",
        "|:---|:---|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for item in detail_rows:
        method = item.get("Type", "-")
        name = item.get("Name", "-")
        req_count = item.get("Request Count", "0")
        fail_count = item.get("Failure Count", "0")
        med = item.get("50%", "0")
        avg = round(float(item.get("Average Response Time", 0)), 2)
        p90 = item.get("90%", "0")
        p95 = item.get("95%", "0")
        rps = round(float(item.get("Requests/s", 0)), 2)
        lines.append(
            f"| {method} | {name} | {req_count} | {fail_count} | {med} | {avg} | {p90} | {p95} | {rps} |"
        )

    lines.append(
        f"| TOTAL | Semua Endpoint | {total_requests} | {total_failures} | {total_row.get('50%', '0')} | {total_avg} | {total_row.get('90%', '0')} | {total_row.get('95%', '0')} | {total_rps} |"
    )

    lines.extend([
        "",
        "## Performance Summary",
        "",
        "| Metric | Value | Target | Status |",
        "|:---|:---|:---|:---|",
        f"| Total Requests | {total_requests} | - | - |",
        f"| Error Rate | {failure_rate:.2f}% | < 1.0% | {error_status} |",
        f"| Avg Latency | {total_avg} ms | < 1000 ms | {latency_status} |",
        f"| Throughput | {total_rps} req/s | - | - |",
        "",
    ])

    report_content = "\n".join(lines)
    output_file.write_text(report_content, encoding="utf-8")
    logger.info(f"Laporan load test Markdown berhasil disimpan ke: {output_file}")


def print_summary(csv_prefix: Path) -> None:
    stats_csv_file = Path(f"{csv_prefix}_stats.csv")
    if not stats_csv_file.exists():
        logger.warning(f"File hasil CSV {stats_csv_file} tidak ditemukan.")
        return

    rows = []
    with open(stats_csv_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        return

    total_row = rows[-1]
    logger.info("=== Ringkasan Hasil Load Testing ===")
    logger.info(f"Total Requests  : {total_row.get('Request Count', '0')}")
    logger.info(f"Total Failures  : {total_row.get('Failure Count', '0')}")
    logger.info(f"Requests/s      : {total_row.get('Requests/s', '0')}")
    logger.info(f"Avg Response    : {total_row.get('Average Response Time', '0')} ms")


def main():
    parser = argparse.ArgumentParser(description="Runner: Locust Headless Load Testing (CCU 50-1000)")
    parser.add_argument("--host", type=str, default="http://127.0.0.1:8000", help="Base URL target backend")
    parser.add_argument("--users", type=int, default=1000, help="Jumlah Concurrent Users puncak (default: 1000)")
    parser.add_argument("--spawn-rate", type=int, default=45, help="Rasio spawn user per detik (default: 45)")
    parser.add_argument("--run-time", type=str, default="45s", help="Durasi pengujian (default: 45s)")
    parser.add_argument("--output-dir", type=str, default="result", help="Subdirektori penyimpanan hasil pengujian")
    parser.add_argument("--report-name", type=str, default="report.md", help="Nama file markdown report")

    args = parser.parse_args()

    tests_dir = Path(__file__).resolve().parent
    locustfile = tests_dir / "locustfile.py"
    result_dir = tests_dir / args.output_dir
    result_dir.mkdir(parents=True, exist_ok=True)

    csv_prefix = result_dir / "results"
    output_report_file = result_dir / args.report_name

    exit_code = run_locust_headless(
        host=args.host,
        locustfile_path=locustfile,
        users=args.users,
        spawn_rate=args.spawn_rate,
        run_time=args.run_time,
        csv_prefix=csv_prefix,
    )

    generate_report(
        csv_prefix=csv_prefix,
        output_file=output_report_file,
        host=args.host,
        users=args.users,
        spawn_rate=args.spawn_rate,
        run_time=args.run_time,
    )

    print_summary(csv_prefix=csv_prefix)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
