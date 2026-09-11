# Implementation Plan
## Step-by-Step, From Scratch to Deployed Demo

This expands your original 29-step outline into concrete, do-this-now
actions. Steps 1–9 are **already done** for you (see `data/processed/`
and `scripts/preprocess_data.py`) — verify them, understand them, then
move on. Estimated pace: roughly one "phase" per week if you're working
part-time on this.

---

## Phase 0 — Foundations (your steps 1–5)

**1-3. Problem, research, requirements** → done — see `01_PRD.md` and
`02_TRD.md`. Read them, adjust anything that doesn't match your actual
constraints (timeline, team size), and treat those documents as the
source of truth for the rest of the build.

**4. Tech stack** → done — see `03_Tech_Stack.md`.

**5. GitHub repo**
```bash
git init hate-speech-moderation
cd hate-speech-moderation
# copy this entire folder structure in
git add .
git commit -m "Initial project structure + docs + merged dataset"
git remote add origin https://github.com/Lohith848/hate-speech-moderation.git
git push -u origin main
```
Suggested `.gitignore`: `venv/`, `node_modules/`, `__pycache__/`, `.env`,
`*.pt` / `*.bin` model weight files (push those to Hugging Face Hub
instead — see Phase 2, step 13 — git repos get slow and hit size limits
with model binaries in them).

## Phase 1 — Data (your steps 6–9) — **already done**

Verify it yourself before trusting it:
```bash
cd scripts
python3 preprocess_data.py
```
You should see the same numbers as `README.md`:
`OFFENSIVE 22,342 / SAFE 12,922 / HATE 2,485`, and `train/val/test` of
`30,199 / 3,775 / 3,775`. If your numbers differ, something changed in
the raw CSVs — re-check before moving on, since every metric downstream
depends on this split being correct and reproducible.

Open `data/processed/train.csv` and read 20-30 rows by hand. This isn't
optional — you should personally see what a `HATE` row looks like versus
an `OFFENSIVE` row before you trust a model to tell them apart.

## Phase 2 — Model (your steps 10–13)

**10-11. Pick + fine-tune a model** — full code and hyperparameters are
in `07_AI_Model.md` §4. Do this in Google Colab:

1. Upload `train.csv`, `val.csv`, `test.csv` to Colab (or mount Google
   Drive).
2. `pip install transformers datasets scikit-learn evaluate accelerate`
3. Run the training script from `07_AI_Model.md` §4, starting with
   `bert-base-multilingual-cased`.
4. Watch validation macro-F1 each epoch; stop when it stops improving
   (usually epoch 3-4).

**12. Evaluate**
```python
from sklearn.metrics import classification_report, confusion_matrix
# ... predict on test.csv AND olid_official_test.csv separately
# report accuracy, macro-F1, per-class P/R/F1, confusion matrix for both
```
Save both reports — you need them for your final report and presentation.

**13. Save + prepare for inference**
```python
model.save_pretrained("./moderation-model")
tokenizer.save_pretrained("./moderation-model")

# Quantize for free-tier RAM/CPU (see 02_TRD.md §6)
from optimum.onnxruntime import ORTQuantizer  # or torch.quantization
# ... quantize to dynamic INT8, re-check accuracy didn't meaningfully drop

# Push to Hugging Face Hub (free, public repo)
huggingface-cli login
model.push_to_hub("lohithg8408/indian-content-moderation-v1")
tokenizer.push_to_hub("ohithg8408/indian-content-moderation-v1")
```

## Phase 3 — Backend (your steps 14–16)

**14. FastAPI app skeleton**
```
backend/
  app/
    main.py          # FastAPI app, CORS, route registration
    model.py          # loads model once at startup, exposes predict()
    schemas.py        # Pydantic request/response models (see 02_TRD.md §5)
    db.py              # SQLAlchemy engine/session
    models_db.py        # ORM models: ModerationLog
    routes/
      moderate.py       # POST /api/v1/moderate, /moderate/batch
      stats.py          # GET /api/v1/stats
  requirements.txt
  .env.example
```
Load the model **once**, at import time in `model.py` — never inside a
route handler, or every request pays the multi-second model-load cost.

**15. The `/moderate` endpoint** — implements the contract in
`02_TRD.md` §5 exactly (label, confidence dict, explanation list, id).

**16. Database**
- Local dev: SQLite (`sqlite:///./dev.db`), zero setup.
- Prod: point the same SQLAlchemy engine at your Supabase Postgres
  connection string via an environment variable — no code change needed,
  which is the whole point of using an ORM here.

Test locally before deploying anything:
```bash
uvicorn app.main:app --reload
curl -X POST localhost:8000/api/v1/moderate -H "Content-Type: application/json" -d '{"text":"you are an idiot"}'
```

## Phase 4 — Frontend (your steps 17–19)

**17-18. React app + Analyze screen** — see `05_Design.md` §2.1 for the
exact layout and §3 for the component breakdown.
```bash
npm create vite@latest frontend -- --template react
cd frontend
npm install axios recharts tailwindcss
```

**19. Admin dashboard** — see `05_Design.md` §2.2. Build `StatsCard`,
`TrendChart`, `ActivityTable` against the `/api/v1/stats` contract.

## Phase 5 — Integration & Testing (your steps 20–22)

**20. Connect everything** — set `VITE_API_BASE_URL` in the frontend's
`.env` to `http://localhost:8000` for local testing, then to the Render
URL after Phase 6.

**21. Test matrix** — run each of these through the deployed Analyze
screen and record the result in your report:

| Input type | Example | Expected |
|---|---|---|
| Safe | "Great weather today, going for a walk" | SAFE, high confidence |
| Offensive/troll | "you're such an idiot lol" | OFFENSIVE |
| Hateful | (a clear group-targeted slur from your test set) | HATE |
| Hindi | (a Hindi sentence) | Record actual result — expect degraded performance on the Milestone-1 baseline; this is expected and worth discussing, not hiding |
| Hinglish | (a code-mixed sentence) | Same as above — this is your most valuable "future work" evidence |
| Edge case | empty string, emoji-only, 2000-char text | Clean 4xx error, no crash |

**22. Fix bugs** found in the matrix above before moving to deployment.

## Phase 6 — Deployment (your steps 23–25)

**23. Frontend → Vercel**
```bash
npm install -g vercel
cd frontend
vercel --prod
```
Set `VITE_API_BASE_URL` as a Vercel environment variable pointing to your
Render backend URL.

**24. Backend → Render**
- New Web Service → connect your GitHub repo → root directory `backend/`.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Set environment variables: `DATABASE_URL` (from Supabase), `HF_MODEL_NAME`.
- **Remember:** free tier spins down after inactivity; first request
  after idle takes ~30-50s. Mention this in your demo video.

**25. Database → Supabase**
- New project (free tier) → copy the Postgres connection string →
  set as `DATABASE_URL` on Render.
- Run your table creation (Alembic migration or a one-off
  `Base.metadata.create_all()` script) once against the prod DB.

## Phase 7 — Documentation & Submission (your steps 26–29)

**26. Report** — you already have the raw material: this whole `docs/`
folder plus your actual evaluation numbers from Phase 2. Structure:
Problem → Related Work (cite the two papers already in your project
folder) → Methodology (`07_AI_Model.md`) → Architecture
(`06_System_Flow.md`) → Results (your real metrics) → Limitations
(Section 6 of `07_AI_Model.md`, honestly stated) → Future Work.

**27. Presentation** — problem statement → live demo →
architecture diagram (reuse `06_System_Flow.md` diagram 1) → results
table → the Hindi/Hinglish limitation as your standout "we understand
this deeply" slide, not something to gloss over.

**28. Demo video** — script it as: type a safe comment → show result →
type an offensive one → show result + explanation → open dashboard, show
it updating → briefly show a Hindi/Hinglish example and narrate the
honest limitation.

**29. Submit** — source code (GitHub link), this documentation set,
report, presentation, deployed frontend URL.
