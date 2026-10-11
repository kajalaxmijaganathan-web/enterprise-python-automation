"""Public API integration using Open-Meteo (no API key required)."""

from __future__ import annotations

import logging
from typing import Any

import requests

LOGGER = logging.getLogger(__name__)
API_URL = "https://api.open-meteo.com/v1/forecast"


class APIClientError(RuntimeError):
    """Raised when an API request fails or returns unexpected data."""


def fetch_weather(latitude: float = 13.0827, longitude: float = 80.2707,
                  timeout: int = 15) -> dict[str, Any]:
    """Fetch current weather and a short daily forecast for a location.

    Defaults to Chennai, India. Open-Meteo is a public API and does not
    require an API key for ordinary non-commercial use.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "forecast_days": 3,
        "timezone": "auto",
    }
    try:
        response = requests.get(API_URL, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        LOGGER.exception("Weather API request failed")
        raise APIClientError(f"Could not retrieve weather data: {exc}") from exc
    except ValueError as exc:
        raise APIClientError("Weather API returned invalid JSON.") from exc

    if not isinstance(payload, dict) or "current" not in payload:
        raise APIClientError("Weather API response is missing the current weather section.")
    return payload
