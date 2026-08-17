

import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine



# Import models 
from app import models

load_dotenv()

DATABASE_URL = "sqlite:///./todo.db"


engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",
    connect_args={"check_same_thread": False}, # SQLAlchemy serializes access across FastAPI's threads
)


def create_db_and_tables()-> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session