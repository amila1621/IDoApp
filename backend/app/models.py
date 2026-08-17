
from datetime import datetime, timezone
from enum import Enum
from sqlmodel import SQLModel, Field

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title : str
    done: bool = Field(default=False)
    due_at: datetime | None = Field(default=None)
    priority: Priority = Field(default=Priority.medium)
    is_outdoor: bool = Field(default=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))



