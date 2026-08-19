

from datetime import date, datetime

import httpx

from app.llm.resolve import TZ

# MY current Location
LAT = 66.5039
LON = 25.7294



_OPEN_METEO = "https://api.open-meteo.com/v1/forecast"

# Open-Meteo WMO weather codes → short human labels (subset we care about).
_CODE_LABELS = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    71: "light snow", 73: "snow", 75: "heavy snow",
    80: "rain showers", 81: "rain showers", 82: "heavy showers",
    95: "thunderstorm",
}



def fetch_forecast() -> dict:
    """Fetch the 7-day daily forecast for the fixed location.Returns a dict keyed by date, or None if the API is unavailable. Never raises — weather is an enhancement, not a hard dependency."""
    try:
        resp = httpx.get(
            _OPEN_METEO, 
            params={
                "latitude": LAT,
                "longitude": LON,
                "daily": "weathercode,temperature_2m_max,temperature_2m_min,precipitation_sum",
                "timezone": "Europe/Helsinki",
                "forecast_days": 7,
            },
            timeout=5.0,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
    except Exception:
        return None

    result: dict[ date, dict] = {}
    for i, day_str in enumerate(daily["time"]):
        day = datetime.fromisoformat(day_str).date()
        result[day] = {
        "code": daily["weathercode"][i],
        "label": _CODE_LABELS.get(daily["weathercode"][i], "unknown"),
        "temp_max": daily["temperature_2m_max"][i],
        "temp_min": daily["temperature_2m_min"][i],
        "precip": daily["precipitation_sum"][i],
        
        }

    return result


def needs_weather(task, now: datetime | None = None) -> bool:
    """A task qualifies for a forecast only if all conditions hold."""
    now = now or datetime.now(TZ)
    if not task.is_outdoor:
        return False
    if task.done:
        return False
    if task.due_at is None:
        return False
    days_ahead = (task.due_at.date() - now.date()).days
    return 0 <= days_ahead <= 6  # only show forecast for the next 7 days


def weather_message(day_forcast: dict | None) -> str:
    """Turn a day's forecast into a short human warning/note."""
    label = day_forcast["label"]
    temp = day_forcast["temp_max"]
    precip = day_forcast["precip"]
    if precip >= 1.0:
        return f"Forecast: {label}, {temp}°C, {precip}mm rain"
    return f"{label}, {temp}°C"


    