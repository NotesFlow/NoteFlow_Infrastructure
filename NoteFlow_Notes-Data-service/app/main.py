from fastapi import FastAPI
from sqlalchemy import text

import app.models
from app.api import router as notes_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


app.include_router(notes_router)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/health/db")
def health_db():
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected",
    }
