from app.llm import enrich as enrich_module
from app.llm import client
from datetime import datetime
from app.llm.resolve import resolve_when, TZ



def test_resolve_tomorrow():
    now = datetime(2026, 8, 17, 9, 0, tzinfo=TZ)  # a Monday
    result = resolve_when("tomorrow", now)
    assert result.date() == datetime(2026, 8, 18, tzinfo=TZ).date()


def test_resolve_next_monday():
    now = datetime(2026, 8, 17, 9, 0, tzinfo=TZ)  # Monday
    result = resolve_when("next monday", now)
    assert result.date() == datetime(2026, 8, 24, tzinfo=TZ).date()


def test_resolve_no_expression_returns_none():
    assert resolve_when(None) is None
    assert resolve_when("") is None

def test_enrich_uses_llm_when_available(monkeypatch):
    # Pretend a key is set and Claude returns valid JSON.
    monkeypatch.setattr(client, "available", lambda: True)
    monkeypatch.setattr(
        client, "complete",
        lambda text: '{"title": "Go for a run", "category": "health_fitness", '
                     '"is_outdoor": true, "when_expression": "tomorrow", '
                     '"duration_minutes": 30, "priority": "medium", "best_time": "morning"}',
    )
    now = datetime(2026, 8, 17, 9, 0, tzinfo=TZ)
    result = enrich_module.enrich_task("go for a run tomorrow", now=now)

    assert result["title"] == "Go for a run"
    assert result["category"] == "health_fitness"
    assert result["is_outdoor"] is True
    assert result["due_at"].date() == datetime(2026, 8, 18, tzinfo=TZ).date()
    assert result["source"] == "llm"


def test_enrich_falls_back_when_llm_fails(monkeypatch):
    # Pretend a key is set but Claude raises an error.
    monkeypatch.setattr(client, "available", lambda: True)
    def boom(text):
        raise client.LLMError("simulated API failure")
    monkeypatch.setattr(client, "complete", boom)

    now = datetime(2026, 8, 17, 9, 0, tzinfo=TZ)
    result = enrich_module.enrich_task("buy milk tomorrow", now=now)

    assert result["source"] == "fallback"
    assert result["title"] == "buy milk tomorrow"
   


def test_enrich_falls_back_when_no_key(monkeypatch):
    # No API key → straight to fallback, never calls Claude.
    monkeypatch.setattr(client, "available", lambda: False)
    result = enrich_module.enrich_task("read a book")
    assert result["source"] == "fallback"
    assert result["title"] == "read a book"


    