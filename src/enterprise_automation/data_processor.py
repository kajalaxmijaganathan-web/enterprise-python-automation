"""Validation and transformation for weather API data."""

from __future__ import annotations

from typing import Any

import pandas as pd


def summarize_weather(payload: dict[str, Any]) -> tuple[dict[str, Any], pd.DataFrame]:
    """Validate an API payload and return a summary and daily forecast table."""
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dictionary.")
    current = payload.get("current")
    daily = payload.get("daily")
    if not isinstance(current, dict) or not isinstance(daily, dict):
        raise ValueError("Payload must contain 'current' and 'daily' objects.")

    required_current = ["temperature_2m", "relative_humidity_2m",
                        "apparent_temperature", "wind_speed_10m"]
    missing = [key for key in required_current if current.get(key) is None]
    if missing:
        raise ValueError(f"Missing current weather fields: {', '.join(missing)}")

    summary = {
        "location": payload.get("timezone", "Unknown location"),
        "latitude": payload.get("latitude"),
        "longitude": payload.get("longitude"),
        "observed_at": current.get("time", "Unknown"),
        "temperature_c": float(current["temperature_2m"]),
        "feels_like_c": float(current["apparent_temperature"]),
        "humidity_percent": float(current["relative_humidity_2m"]),
        "wind_speed_kmh": float(current["wind_speed_10m"]),
        "weather_code": current.get("weather_code", "Unknown"),
    }

    dates = daily.get("time", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    rain = daily.get("precipitation_probability_max", [])
    length = min(len(dates), len(highs), len(lows), len(rain))
    forecast = pd.DataFrame({
        "date": dates[:length],
        "high_c": highs[:length],
        "low_c": lows[:length],
        "precipitation_probability_percent": rain[:length],
    })
    if forecast.empty:
        raise ValueError("The API response contains no daily forecast records.")
    for column in ("high_c", "low_c", "precipitation_probability_percent"):
        forecast[column] = pd.to_numeric(forecast[column], errors="coerce")
    forecast = forecast.dropna(subset=["high_c", "low_c"]).reset_index(drop=True)
    if forecast.empty:
        raise ValueError("The daily forecast contains no valid temperature values.")
    return summary, forecast
