# Backend — AI Content Moderation API

FastAPI service that loads your fine-tuned model from Hugging Face Hub,
predicts SAFE / OFFENSIVE / HATE for submitted text, logs every prediction
to a database, and serves dashboard stats.

## Run it locally

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env              # edit MODEL_REPO if your model is at a
                                   # different path than lohithg8408/content-moderation

uvicorn app.main:app --reload
```

The **first time** you start it, it downloads your model from Hugging Face
(a few hundred MB) — this can take a minute or two depending on your
connection, then it's cached locally for every restart after that.

Watch the terminal output for this line:
```
[model] Loaded on device=cpu. Labels: {0: 'SAFE', 1: 'OFFENSIVE', 2: 'HATE'}
```
If the labels shown aren't `SAFE` / `OFFENSIVE` / `HATE`, something went
wrong when the model was pushed to the Hub — go back to the training
notebook, Step 7, and confirm `id2label`/`label2id` were passed into
`AutoModelForSequenceClassification.from_pretrained(...)`, then re-push.

## Test it

Open **http://localhost:8000/docs** — FastAPI auto-generates an
interactive UI where you can try every endpoint by hand, no `curl` needed.

Or from the terminal:
```bash
curl -X POST http://localhost:8000/api/v1/moderate \
  -H "Content-Type: application/json" \
  -d '{"text": "you are such an idiot"}'
```

Expected shape:
```json
{
  "id": "a1b2c3d4-...",
  "label": "OFFENSIVE",
  "confidence": {"SAFE": 0.04, "OFFENSIVE": 0.91, "HATE": 0.05},
  "explanation": [{"token": "idiot", "weight": 0.42}]
}
```

Check the stats endpoint after a few requests:
```bash
curl http://localhost:8000/api/v1/stats
```

## Project layout

```
backend/
  app/
    main.py          FastAPI app + CORS + route registration
    model.py          loads the HF model ONCE at startup, predict() + explain()
    schemas.py         Pydantic request/response models
    db.py               SQLAlchemy engine/session (SQLite locally, Postgres in prod)
    models_db.py         ModerationLog table definition
    routes/
      moderate.py         POST /api/v1/moderate, POST /api/v1/moderate/batch
      stats.py             GET /api/v1/stats
  requirements.txt
  .env.example
```

## Next steps

- **Frontend**: build the Analyze screen + dashboard against these three
  endpoints (see `docs/05_Design.md` and `docs/04_Implementation_Plan.md`
  Phase 4).
- **Deploy**: push this `backend/` folder to your GitHub repo, then follow
  `docs/04_Implementation_Plan.md` Phase 6, step 24 (Render). Set
  `MODEL_REPO` and `DATABASE_URL` as environment variables in the Render
  dashboard — don't commit your real `.env` file.
