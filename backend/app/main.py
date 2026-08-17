
from fastapi import FastAPI

app = FastAPI(title="Todo APP Api")

@app.get("/health")
def health():
    return{ "status": "OK"}