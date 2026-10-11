import pytest

from enterprise_automation.data_processor import summarize_weather


@pytest.fixture
def sample_payload():
    return {
        "timezone": "Asia/Kolkata",
        "latitude": 13.08,
        "longitude": 80.27,
        "current": {
            "time": "2026-10-11T09:00",
            "temperature_2m": 31.2,
            "relative_humidity_2m": 68,
            "apparent_temperature": 35.0,
            "wind_speed_10m": 12.4,
            "weather_code": 2,
        },
        "daily": {
            "time": ["2026-10-11", "2026-10-12"],
            "temperature_2m_max": [33.0, 32.0],
            "temperature_2m_min": [27.0, 26.0],
            "precipitation_probability_max": [10, 25],
        },
    }


def test_summarize_weather_returns_metrics_and_forecast(sample_payload):
    summary, forecast = summarize_weather(sample_payload)
    assert summary["location"] == "Asia/Kolkata"
    assert summary["temperature_c"] == 31.2
    assert len(forecast) == 2
    assert list(forecast.columns) == [
        "date", "high_c", "low_c", "precipitation_probability_percent"
    ]


def test_missing_current_field_raises_value_error(sample_payload):
    del sample_payload["current"]["temperature_2m"]
    with pytest.raises(ValueError, match="Missing current weather fields"):
        summarize_weather(sample_payload)


def test_empty_daily_forecast_raises_value_error(sample_payload):
    sample_payload["daily"] = {
        "time": [], "temperature_2m_max": [],
        "temperature_2m_min": [], "precipitation_probability_max": []
    }
    with pytest.raises(ValueError, match="no daily forecast"):
        summarize_weather(sample_payload)


def test_invalid_payload_raises_value_error():
    with pytest.raises(ValueError, match="dictionary"):
        summarize_weather([])
