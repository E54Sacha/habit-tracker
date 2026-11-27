"""Habit tracker API."""

from fastapi import FastAPI
from sqlalchemy import text

from .db import engine
from .routers import auth

app = FastAPI(title="Habit tracker API")
app.include_router(auth.router)


@app.get("/health")
def health() -> dict:
    """Used to wake the free server and by Render's health check; also checks the database answers."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"status": "ok"}
