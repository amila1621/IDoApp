from datetime import datetime
from sqlmodel import SQLModel
from app.models import Priority, Category



class TaskCreate(SQLModel):
    title:str
    due_at: datetime | None = None
    category: Category = Category.personal_selfcare
    is_outdoor: bool = False
    duration_minutes: int | None = None
    brest_time: str | None = None
    priority: Priority = Priority.medium




class TaskUpdate(SQLModel):
    title: str | None = None
    done: bool | None = None
    due_at: datetime | None = None
    category: Category | None = None
    is_outdoor: bool | None = None
    duration_minutes: int | None = None
    best_time: str | None = None
    priority: Priority | None = None