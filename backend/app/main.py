import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .model import load_model, is_ready
from .routes import moderate, stats

# Creates the moderation_log table if it doesn't exist yet. For SQLite this
# just works. For Postgres/Supabase this also works fine for a practicum
# project -- a real production app would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app):
    """Startup: kick off model download in a background thread so the
    server can bind its port immediately (Render's free-tier port scan
    times out after ~5 minutes -- the old design blocked port binding
    for the entire download duration and got killed)."""
    thread = threading.Thread(target=load_model, daemon=True)
    thread.start()
    yield


app = FastAPI(
    title="AI Content Moderation API",
    description="Detects SAFE / OFFENSIVE / HATE content in social media text.",
    version="1.0",
    lifespan=lifespan,
)

# CORS_ORIGINS: comma-separated list of allowed origins.
# Local dev: defaults to "*" (any origin).
# Production: set to your Vercel URL, e.g. "https://hate-speech-moderation.vercel.app"
cors_origins = os.environ.get("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(moderate.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Content Moderation API is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": is_ready()}
