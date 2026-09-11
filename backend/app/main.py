import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .model import load_model, is_ready


@asynccontextmanager
async def lifespan(app):
    """Startup: create DB tables and kick off model download in a background
    thread so the server can bind its port immediately (Render's free-tier
    port scan times out after ~5 minutes)."""
    # Import DB here (not at module top level) so a bad DATABASE_URL
    # doesn't crash the app before the port is bound.
    try:
        from .db import Base, engine
        Base.metadata.create_all(bind=engine)
        print("[db] Tables created / verified.")
    except Exception as e:
        print(f"[db] WARNING: could not connect to database: {e}")
        print("[db] The app will start but /moderate and /stats will fail.")

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

# Import routes AFTER app is created — they don't need DB at import time,
# only at request time.
from .routes import moderate, stats  # noqa: E402

app.include_router(moderate.router)
app.include_router(stats.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "AI Content Moderation API is running"}


@app.get("/health")
def health():
    return {"status": "healthy", "model_loaded": is_ready()}
