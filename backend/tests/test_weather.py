from datetime import datetime, timedelta

from app.weather import needs_weather
from app.llm.resolve import TZ
from app.models import Task, Category


def _task(**kwargs):
    """Build a Task with sensible defaults, overriding only what's tested."""
    defaults = dict(
        title="x", is_outdoor=True, done=False,
        due_at=datetime.now(TZ) + timedelta(days=1),
        category=Category.health_fitness,
    )
    defaults.update(kwargs)
    return Task(**defaults)


def test_outdoor_dated_soon_needs_weather():
    assert needs_weather(_task()) is True


def test_indoor_task_skips_weather():
    assert needs_weather(_task(is_outdoor=False)) is False


def test_done_task_skips_weather():
    assert needs_weather(_task(done=True)) is False


def test_undated_task_skips_weather():
    assert needs_weather(_task(due_at=None)) is False


def test_far_future_task_skips_weather():
    far = datetime.now(TZ) + timedelta(days=30)
    assert needs_weather(_task(due_at=far)) is False