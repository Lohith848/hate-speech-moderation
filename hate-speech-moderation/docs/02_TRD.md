# Technical Requirements Document (TRD)
## AI-Powered Content Moderation System

---

## 1. System Overview

Three deployable pieces:

1. **Model service** — a fine-tuned transformer packaged so FastAPI can
   load it and run inference.
2. **Backend API** — FastAPI app: serves predictions, stores history in a
   database, exposes dashboard stats.
3. **Frontend** — React app: analyze screen + admin dashboard, talks to
   the backend over REST.

See `06_System_Flow.md` for the full architecture diagram.

## 2. Functional Requirements

| ID | Requirement |
|---|---|
| FR-1 | System shall accept a single text input and return label + confidence within 3 seconds (warm) |
| FR-2 | System shall support three labels: `SAFE`, `OFFENSIVE`, `HATE` |
| FR-3 | System shall return a per-class confidence score (softmax probabilities, sum to 1) |
| FR-4 | System shall return an explanation: the tokens/words that contributed most to the prediction |
| FR-5 | System shall persist every prediction (text, label, confidence, timestamp) to a database |
| FR-6 | System shall expose aggregate stats: total analyzed, count per label, timeline |
| FR-7 | System shall support batch prediction via CSV upload for evaluation/report generation |
| FR-8 | System shall reject empty or >1000-character inputs with a clear 4xx error, not a crash |

## 3. Non-Functional Requirements

| Category | Requirement |
|---|---|
| Performance | p95 inference latency < 1.5s on a warm CPU-only free-tier instance (batch size 1) |
| Availability | Best-effort on free tiers; document expected cold-start delay rather than promise 24/7 uptime |
| Accuracy | ≥ 85% accuracy, ≥ 0.80 macro-F1 on held-out `test.csv` (see `07_AI_Model.md`) |
| Scalability | Not a requirement for this practicum — single-instance free-tier deployment is acceptable |
| Security | No PII stored beyond the submitted text itself; no auth needed for demo, but document as a gap for a real product |
| Portability | Entire stack runs from open-source, free-tier services — no vendor lock-in requiring payment |
| Explainability | Every prediction must ship with a human-readable reason, not just a label |

## 4. Data Model

### `moderation_log` table
| Column | Type | Notes |
|---|---|---|
| `id` | UUID / autoincrement PK | |
| `text` | TEXT | original input, capped at 1000 chars |
| `label` | VARCHAR(20) | `SAFE` / `OFFENSIVE` / `HATE` |
| `confidence_safe` | FLOAT | softmax prob |
| `confidence_offensive` | FLOAT | softmax prob |
| `confidence_hate` | FLOAT | softmax prob |
| `explanation` | TEXT (JSON) | top contributing tokens + weights |
| `source` | VARCHAR(20) | `web` / `batch` / `api` |
| `created_at` | TIMESTAMP | default now() |

### `daily_stats` (materialized/derived, or computed on read for MVP)
| Column | Type |
|---|---|
| `date` | DATE |
| `total_count` | INT |
| `safe_count` | INT |
| `offensive_count` | INT |
| `hate_count` | INT |

For MVP scale (a practicum demo, not production traffic), `daily_stats`
can simply be a `GROUP BY DATE(created_at)` query over `moderation_log` —
no need for a separate materialized table until volume actually justifies it.

## 5. API Contract

### `POST /api/v1/moderate`
```json
// Request
{ "text": "string, 1-1000 chars" }

// Response 200
{
  "label": "OFFENSIVE",
  "confidence": { "SAFE": 0.04, "OFFENSIVE": 0.91, "HATE": 0.05 },
  "explanation": [
    { "token": "idiot", "weight": 0.42 },
    { "token": "shut up", "weight": 0.31 }
  ],
  "id": "log-entry-id"
}

// Response 422 (validation)
{ "detail": "text must be between 1 and 1000 characters" }
```

### `POST /api/v1/moderate/batch`
- `multipart/form-data` with a CSV file, one `text` column.
- Response: same shape as above, as a list, plus a downloadable results CSV.

### `GET /api/v1/stats?range=7d`
```json
{
  "total": 1245,
  "by_label": { "SAFE": 800, "OFFENSIVE": 380, "HATE": 65 },
  "timeline": [
    { "date": "2026-09-04", "SAFE": 110, "OFFENSIVE": 40, "HATE": 6 }
  ]
}
```

## 6. Model Serving Requirements

- Model loaded once at process startup (not per-request) — this alone is
  the difference between 200ms and 5s inference on a free-tier CPU box.
- Model artifact size must fit Render's free-tier RAM (512MB) —
  see `07_AI_Model.md` for why this rules out full XLM-R-large and points
  to a distilled/base model instead.
- Inference must run on CPU (free tiers have no GPU) — quantization
  (dynamic INT8 via `torch.quantization` or `optimum`) is recommended if
  latency is a problem after testing.

## 7. Environments

| Environment | Purpose | Where |
|---|---|---|
| Development | Local coding + testing | Your laptop |
| Training | Fine-tuning the model | Google Colab (free GPU) |
| Staging/Prod (single tier for a practicum) | Public demo | Vercel (frontend) + Render (backend) + Supabase (DB) |

## 8. Testing Requirements

- Unit tests for the FastAPI endpoints (happy path + validation errors).
- Model evaluation script producing accuracy/precision/recall/F1 +
  confusion matrix on `test.csv` and `olid_official_test.csv`.
- Manual test matrix (documented in `04_Implementation_Plan.md`, step 21):
  safe / offensive / hateful / Hindi / Hinglish / edge cases (empty
  string, emoji-only, very long text).
