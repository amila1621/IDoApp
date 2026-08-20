

import logging

from datetime import datetime
from pydantic import ValidationError

from app.llm import client 
from app.llm.resolve import resolve_when
from app.schemas_llm import Enrichment
from app.models import Category

logger = logging.getLogger(__name__)

def enrich_task(text: str, now: datetime | None = None) -> dict:
  """ Turn raw task in to enrich fields. Tries LLM 1st, Fall back to minimal task on nay malformed LLM output. Always returns a dict with the fields of Enrichment. """
  if not client.available():
    return _fallback(text, now)
  try:
    raw = client.complete(text)
    data = Enrichment.model_validate_json(client.strip_fences(raw))
  except (client.LLMError, ValidationError) as e:
    logger.warning("LLM enrichment failed for text '%s' with error: %s", text, str(e))
    return _fallback(text, now)

  return {
    "title": data.title,
    "category": data.category,
    "is_outdoor": data.is_outdoor,
    "due_at": resolve_when(data.when_expression, now),
    "duration_minutes": data.duration_minutes,
    "priority": data.priority,
    "best_time": data.best_time,
    "steps": data.steps,
    "source": "llm"
   
  }


def _fallback(text: str, now: datetime | None = None) -> dict:
    """ Pure Python fallback if LLM is not available or fails. Returns a dict with the fields of Enrichment. """
    return {
        "title": text,
        "category": Category.personal_selfcare,
        "is_outdoor": False,
        "due_at": resolve_when(None, now),
        "priority": "medium",
        "duration_minutes": None,
        "best_time": None,
        "steps": [],
        "source": "fallback"
    }


