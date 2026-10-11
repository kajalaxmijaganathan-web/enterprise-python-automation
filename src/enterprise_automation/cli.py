"""Command-line interface."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .api_client import fetch_weather
from .data_processor import summarize_weather
from .report_generator import generate_pdf_report
from .scheduler import run_scheduler


def configure_logging(log_file: str | None = None) -> None:
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(path, encoding="utf-8"))
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=handlers,
        force=True,
    )


def build_report(latitude: float, longitude: float, output: str) -> Path:
    payload = fetch_weather(latitude=latitude, longitude=longitude)
    summary, forecast = summarize_weather(payload)
    return generate_pdf_report(summary, forecast, output)


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="enterprise-report",
        description="Fetch public weather data, analyze it, and create a PDF report."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    report = subparsers.add_parser("generate", help="Generate one PDF report.")
    report.add_argument("--latitude", type=float, default=13.0827, help="Latitude (default: Chennai).")
    report.add_argument("--longitude", type=float, default=80.2707, help="Longitude (default: Chennai).")
    report.add_argument("--output", default="reports/weather_report.pdf", help="PDF output path.")
    report.add_argument("--log-file", default="logs/automation.log", help="Log file path; use '' to disable.")
    scheduled = subparsers.add_parser("schedule", help="Generate now and repeat at an interval.")
    scheduled.add_argument("--latitude", type=float, default=13.0827)
    scheduled.add_argument("--longitude", type=float, default=80.2707)
    scheduled.add_argument("--output", default="reports/weather_report.pdf")
    scheduled.add_argument("--every-minutes", type=int, default=60)
    scheduled.add_argument("--log-file", default="logs/automation.log")
    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()
    configure_logging(getattr(args, "log_file", None) or None)
    if args.command == "generate":
        path = build_report(args.latitude, args.longitude, args.output)
        print(f"Report created successfully: {path.resolve()}")
    elif args.command == "schedule":
        if args.every_minutes < 1:
            parser.error("--every-minutes must be at least 1")
        job = lambda: build_report(args.latitude, args.longitude, args.output)
        run_scheduler(job, every_minutes=args.every_minutes)


if __name__ == "__main__":
    main()
