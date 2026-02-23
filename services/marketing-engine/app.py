from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ElevatedIQ Marketing Engine", version="0.1.0")


class Campaign(BaseModel):
    name: str
    budget: float
    channel: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/campaigns")
def create_campaign(c: Campaign):
    # Stub: persist and schedule campaign in production
    return {"status": "created", "campaign": c.model_dump()}


@app.get("/")
def root():
    return {"service": "marketing-engine", "version": "0.1.0"}
