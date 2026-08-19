
from datetime import datetime
from zoneinfo import ZoneInfo


import dateparser

TZ = ZoneInfo("Europe/Helsinki")

def resolve_when(expression: str | None, now: datetime | None = None) -> datetime | None:
    """Turn a text phrase into a concrete Helsinki time datetime object. If the expression is None, return None."""

    if not expression:
        return None

    now = now or datetime.now(TZ)

    # dateparser fails on "next monday" but handles "monday" fine
    # (PREFER_DATES_FROM=future already means the upcoming one).
    expression = expression.strip()
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] #only remove "next" if it's followed by a weekday, otherwise leave it
    parts = expression.lower().split(" ")
    if len(parts) >= 2 and parts[0] == "next" and parts[1] in weekdays:
        expression = expression[5:] # remove "next " from the front of the expression

    settings = {
        "RELATIVE_BASE": now,
        "TIMEZONE": "Europe/Helsinki",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "PREFER_DATES_FROM": "future",
    }

    parsed = dateparser.parse(expression, settings=settings, languages=["en", "fi"])

    if parsed is None:
        # Drop trailing words one at a time until a date parses.
        # "next monday afternoon" -> "next monday afternoon" (fail)
        #   -> "next monday" (parses)
        words = expression.split(" ")
        while parsed is None and len(words) > 1:
            words = words[:-1]  # remove last word
            parsed = dateparser.parse(" ".join(words), settings=settings, languages=["en", "fi"])
     

        

    return parsed



