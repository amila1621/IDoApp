from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import SQLModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Category(str, Enum):
    health_fitness = "health_fitness"
    finance = "finance"
    shopping = "shopping"
    work_career = "work_career"
    personal_selfcare = "personal_selfcare"
    family_relationships = "family_relationships"
    home_maintenance = "home_maintenance"
    household_chores = "household_chores"
    learning_growth = "learning_growth"


class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    done: bool = Field(default=False)

    # LLM-enriched fields
    category: Category = Field(default=Category.personal_selfcare)
    due_at: datetime | None = Field(default=None)
    is_outdoor: bool = Field(default=False)
    duration_minutes: int | None = Field(default=None)
    best_time: str | None = Field(default=None)
    steps: Optional[list] = Field(default=None, sa_column=Column(JSON))

    priority: Priority = Field(default=Priority.medium)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
