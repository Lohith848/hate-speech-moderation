# Tech Stack — 100% Free Tier

Every item below has a free tier that comfortably covers a practicum-scale
demo. Nothing here requires a credit card at signup unless noted.

## AI / ML

| Tool | Role | Why this one | Cost |
|---|---|---|---|
| **Google Colab** | Fine-tuning compute (free T4 GPU) | No local GPU needed; sessions up to ~12h | Free |
| **Hugging Face Transformers + Datasets** | Model + training loop | Industry-standard, huge model zoo, works directly with your CSVs | Free (open source) |
| **Hugging Face Hub** | Store your fine-tuned model weights, versioned | Free public repos; loads directly into your FastAPI backend at deploy time (no need to bundle 400MB in git) | Free |
| **Model: `bert-base-multilingual-cased` (baseline) → `google/muril-base-cased` (Indian-language milestone)** | The classifier itself | mBERT/MuRIL are open, free, and pretrained on Indian languages (MuRIL specifically on 17 Indian languages + transliterated data) — see `07_AI_Model.md` for the full rationale | Free |
| **scikit-learn** | Metrics, train/val/test split | Standard, lightweight | Free |
| **Captum or a simple attention/gradient-based explainer** | Explanation feature (FR-4) | Works with any HF model, no extra infra | Free |

## Backend

| Tool | Role | Why |
|---|---|---|
| **FastAPI** | REST API | Async, auto-generated OpenAPI docs, Python (same language as the ML code — one less context switch) |
| **Uvicorn** | ASGI server | Standard FastAPI pairing |
| **SQLAlchemy** | ORM | Works identically against SQLite (local dev) and PostgreSQL (prod) — no rewrite needed when you switch |
| **Pydantic** | Request/response validation | Ships with FastAPI, gives you FR-8 validation almost for free |

## Database

| Tool | Role | Why |
|---|---|---|
| **SQLite** | Local development | Zero setup, a single file |
| **Supabase (Postgres, free tier)** | Production database | Free tier: 500MB DB, generous enough for a demo's moderation logs |

## Frontend

| Tool | Role | Why |
|---|---|---|
| **React (Vite)** | UI framework | Fast dev server, minimal config compared to CRA |
| **Tailwind CSS** | Styling | Fast to build a clean dashboard without hand-writing CSS |
| **Recharts** | Dashboard charts | Simple React charting, free, no account needed |
| **Axios / fetch** | Talk to the backend API | Standard |

## Hosting / Deployment

| Tool | Role | Free tier limit worth knowing |
|---|---|---|
| **Vercel** | Frontend hosting | Generous free tier for personal/hobby projects |
| **Render** | Backend hosting | Free web services **spin down after inactivity** and take ~30-50s to "cold start" on the next request — mention this in your demo video so it doesn't look like a bug |
| **Supabase** | Postgres hosting | Free project pauses after ~1 week of inactivity — just needs one request to wake it, similar caveat |
| **GitHub** | Source control, project structure | Free public/private repos |

## Why not the "obvious" alternatives

| Instead of | We use | Reason |
|---|---|---|
| Twitter/X API for live data collection | The two datasets already provided (Davidson + OLID) | X API free tier no longer supports meaningful search/collection; using pre-existing labeled datasets is both free and faster to a working model |
| A giant model like XLM-RoBERTa-large | mBERT-base / MuRIL-base | Large models won't fit in Render's free 512MB RAM tier and will be too slow on CPU-only inference |
| A managed ML endpoint (SageMaker, Vertex AI) | Self-hosted FastAPI + HF model | Managed inference endpoints are not free; a small transformer runs fine on a free CPU box for demo-level traffic |

## Local dev prerequisites

- Python 3.10+
- Node.js 18+
- Git
- A free Hugging Face account (for `huggingface-cli login` when pushing
  your fine-tuned model)
- A free Google account (Colab, GitHub, Vercel, Render, Supabase can all
  use the same one)
