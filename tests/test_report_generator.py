import pandas as pd

from enterprise_automation.report_generator import generate_pdf_report


def test_generate_pdf_report_creates_pdf_and_chart(tmp_path):
    summary = {
        "location": "Asia/Kolkata",
        "latitude": 13.08,
        "longitude": 80.27,
        "observed_at": "2026-10-11T09:00",
        "temperature_c": 31.2,
        "feels_like_c": 35.0,
        "humidity_percent": 68,
        "wind_speed_kmh": 12.4,
        "weather_code": 2,
    }
    forecast = pd.DataFrame({
        "date": ["2026-10-11", "2026-10-12"],
        "high_c": [33.0, 32.0],
        "low_c": [27.0, 26.0],
        "precipitation_probability_percent": [10, 25],
    })
    pdf = generate_pdf_report(summary, forecast, tmp_path / "report.pdf")
    assert pdf.exists()
    assert pdf.stat().st_size > 500
    assert (tmp_path / "report_forecast.png").exists()
