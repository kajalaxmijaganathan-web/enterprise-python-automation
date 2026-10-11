"""PDF report and chart generation."""

from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak
)

LOGGER = logging.getLogger(__name__)


def generate_pdf_report(summary: dict[str, Any], forecast: pd.DataFrame,
                        output_path: str | Path) -> Path:
    """Create a PDF report and a companion forecast chart."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    chart_path = output.with_name(output.stem + "_forecast.png")

    fig, ax = plt.subplots(figsize=(8, 3.6))
    x = list(range(len(forecast)))
    ax.plot(x, forecast["high_c"], marker="o", label="Daily high (°C)")
    ax.plot(x, forecast["low_c"], marker="o", label="Daily low (°C)")
    ax.set_xticks(x, [str(value) for value in forecast["date"]], rotation=15, ha="right")
    ax.set_title("Three-day temperature forecast")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(chart_path, dpi=160)
    plt.close(fig)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", parent=styles["Title"],
                              alignment=TA_CENTER, fontSize=20, leading=25,
                              textColor=colors.HexColor("#17365D"), spaceAfter=8))
    styles.add(ParagraphStyle(name="SmallNote", parent=styles["Normal"],
                              fontSize=8, textColor=colors.grey))
    story = [
        Paragraph("Automated Weather Intelligence Report", styles["ReportTitle"]),
        Paragraph(f"Generated: {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %Z')}",
                  styles["Normal"]),
        Spacer(1, 6 * mm),
        Paragraph("Executive summary", styles["Heading2"]),
    ]

    metrics = [
        ["Metric", "Value"],
        ["Location / timezone", str(summary.get("location", "Unknown"))],
        ["Observed at", str(summary.get("observed_at", "Unknown"))],
        ["Current temperature", f"{summary['temperature_c']:.1f} °C"],
        ["Feels like", f"{summary['feels_like_c']:.1f} °C"],
        ["Relative humidity", f"{summary['humidity_percent']:.0f}%"],
        ["Wind speed", f"{summary['wind_speed_kmh']:.1f} km/h"],
    ]
    table = Table(metrics, colWidths=[65 * mm, 95 * mm], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FA")]),
        ("PADDING", (0, 0), (-1, -1), 7),
    ]))
    story += [table, Spacer(1, 7 * mm), Paragraph("Forecast visualization", styles["Heading2"]),
              Image(str(chart_path), width=165 * mm, height=74 * mm),
              Spacer(1, 4 * mm), Paragraph("Daily forecast data", styles["Heading2"])]

    forecast_rows = [["Date", "High (°C)", "Low (°C)", "Precipitation chance (%)"]]
    for _, row in forecast.iterrows():
        rain = row.get("precipitation_probability_percent")
        rain_text = "N/A" if pd.isna(rain) else f"{float(rain):.0f}%"
        forecast_rows.append([
            str(row["date"]), f"{float(row['high_c']):.1f}",
            f"{float(row['low_c']):.1f}", rain_text
        ])
    forecast_table = Table(forecast_rows, colWidths=[38 * mm, 30 * mm, 30 * mm, 55 * mm],
                           repeatRows=1)
    forecast_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2F75B5")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story += [forecast_table, Spacer(1, 6 * mm),
              Paragraph("Source: Open-Meteo public forecast API. Weather forecasts can change; "
                        "this report is informational and is not an official warning.",
                        styles["SmallNote"])]

    doc = SimpleDocTemplate(str(output), pagesize=A4, rightMargin=18 * mm,
                            leftMargin=18 * mm, topMargin=16 * mm, bottomMargin=16 * mm,
                            title="Automated Weather Intelligence Report",
                            author="Enterprise Python Automation")
    doc.build(story)
    LOGGER.info("PDF report saved to %s", output.resolve())
    return output
