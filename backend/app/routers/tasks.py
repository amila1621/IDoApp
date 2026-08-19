

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session

from app.db import get_session
from app.models import Task
from app.schemas import TaskCreate, TaskUpdate
from app.llm.enrich import enrich_task
from app.weather import fetch_forecast, needs_weather, weather_message

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=Task)
def create_task(payload: TaskCreate, session: Session = Depends(get_session)):
    task = Task(**payload.model_dump())
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

    


@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task 

@router.patch("/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task_data = payload.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        setattr(task, key, value)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return None


@router.post("/enrich")
def enrich(payload: dict, session: Session = Depends(get_session)):
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=422, detail="Missing 'text' in request body")
    enriched = enrich_task(text)

    task = Task(
        title=enriched["title"],
        category=enriched["category"],
        is_outdoor=enriched["is_outdoor"],
        due_at=enriched["due_at"],
        duration_minutes=enriched["duration_minutes"],
        best_time=enriched["best_time"],
        
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return { "task": task, "source": enriched["source"] }



@router.get("")
def list_tasks(session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()

    forecast = fetch_forecast()

    result = []
    for task in tasks:
        item = task.model_dump()
        item["weather"] = None
        if forecast and needs_weather(task):
            day = task.due_at.date()
            if day in forecast:
                item["weather"] = weather_message(forecast[day])
        result.append(item)
    return result