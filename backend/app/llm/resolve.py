
from datetime import datetime
from zoneinfo import ZoneInfo


import dateparser

TZ = ZoneInfo("Europe/Helsinki")

def resolve_when(expression: str | None, now: datetime | None = None) -> datetime | None:
    """Turn a text phrase into a concrete Helsinki time datetime object. If the expression is None, return None."""

    if not expression:
        return None

    now = now or datetime.now(TZ)

    return dateparser.parse(
        expression,
        settings={
            "RELATIVE_BASE": now,
            "TIMEZONE": "Europe/Helsinki",
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",  

        },
        languages=["en", "fi"]
        
    )



