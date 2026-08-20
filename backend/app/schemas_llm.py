
from pydantic import BaseModel , Field
from app.models import Category ,Priority

class Enrichment(BaseModel):
    """ Exactly what the LLM will return to us. """
    title: str = Field(..., description="The title of the task no time words")
    category: Category = Field(..., description="The category of the task form fixed folders")
    is_outdoor: bool = Field(..., description="Is the task outdoor or indoor.True for outdoor, False for indoor")
    when_expression: str | None = Field(None, description="A natural language expression of when the task should be done. e.g. 'tomorrow morning', 'next week', 'in 3 days', 'on Friday at 5pm'")
    duration_minutes: int | None = Field(None, description="Rough estimation in minutes of the duration of the task.")
    priority: Priority = Field(..., description="High for urgent/deadline tasks, low for someday tasks, else medium.")
    best_time: str | None = Field(None, description="A natural language expression of the best time of day to do the task. e.g. 'morning', 'afternoon', 'evening', 'night'")
    steps: list[str] | None = Field(None, description="Concrete sub-steps, ONLY for multi-step projects; empty list otherwise")