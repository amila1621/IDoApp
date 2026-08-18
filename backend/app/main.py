
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db import create_db_and_tables
from app.routers import tasks



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Todo APP Api" , lifespan=lifespan)
app.include_router(tasks.router)

@app.get("/health")
def health():
    return{ "status": "OK"}