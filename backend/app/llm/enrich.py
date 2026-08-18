

from datetime import datetime
from pydantic import ValidationError

from app.llm import client 
from app.llm.resolve import resolve_when
from app.schemas_llm import Enrichment
from app.models import Category


def enrich_task(text: str, now: datetime | None = None) -> dict:
  """ Turn raw task in to enrich fields. Tries LLM 1st, Fall back to minimal task on nay malformed LLM output. Always returns a dict with the fields of Enrichment. """
  if not client.available():
    return _fallback(text, now)
  try:
    raw = client.complete(text)
    data = Enrichment.model_validate_json(client.strip_fences(raw))
  except (client.LLMError, ValidationError):
    return _fallback(text, now)

  return {
    "title": data.title,
    "category": data.category,
    "is_outdoor": data.is_outdoor,
    "due_at": resolve_when(data.when_expression, now),
    "duration_minutes": data.duration_minutes,
    "best_time": data.best_time,
    "source": "llm"
   
  }


def _fallback(text: str, now: datetime | None = None) -> dict:
    """ Pure Python fallback if LLM is not available or fails. Returns a dict with the fields of Enrichment. """
    return {
        "title": text,
        "category": Category.personal_selfcare,
        "is_outdoor": False,
        "due_at": resolve_when(None, now),
        "duration_minutes": None,
        "best_time": None,
        "source": "fallback"
    }


