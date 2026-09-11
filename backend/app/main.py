import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routes import moderate, stats

# Creates the moderation_log table if it doesn't exist yet. For SQLite this
# just works. For Postgres/Supabase this also works fine for a practicum
# project -- a real production app would use Alembic migrations instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Content Moderation API",
    description="Detects SAFE / OFFENSIVE / HATE content in social media text.",
    version="1.0",
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
    return {"status": "healthy"}
