# AI-Powered Content Moderation System
### Detecting Hate Speech & Trolls in Indian Social Media
**Innovation Practicum 3 — Project Documentation Set**

---

## What's in this package

| # | Document | Purpose |
|---|----------|---------|
| 1 | [`docs/01_PRD.md`](docs/01_PRD.md) | Product Requirements — problem, users, features, success criteria |
| 2 | [`docs/02_TRD.md`](docs/02_TRD.md) | Technical Requirements — APIs, data model, non-functional requirements |
| 3 | [`docs/03_Tech_Stack.md`](docs/03_Tech_Stack.md) | Every tool used, why, and the free tier that covers it |
| 4 | [`docs/04_Implementation_Plan.md`](docs/04_Implementation_Plan.md) | Day-by-day build plan, expanded from your 29-step outline |
| 5 | [`docs/05_Design.md`](docs/05_Design.md) | UI/UX screens, component structure, wireframe descriptions |
| 6 | [`docs/06_System_Flow.md`](docs/06_System_Flow.md) | Architecture + data-flow + sequence diagrams |
| 7 | [`docs/07_AI_Model.md`](docs/07_AI_Model.md) | Dataset analysis, label design, model choice, training & evaluation plan |
| — | `scripts/preprocess_data.py` | **Already run.** Merges your two datasets into a clean, unified, split dataset |
| — | `data/processed/*.csv` | The actual output of that script — ready to fine-tune on today |
| — | `data/raw/*` | Your original OLID + Davidson files, copied in for reference |

## What's already done for you

Your project folder had two real datasets sitting in it — `labeled_data.csv`
(24,783 tweets, Davidson et al. hate-speech corpus) and the OLID set
(13,240 tweets, SemEval-2019). I merged them into one **unified 3-class
schema** (`SAFE` / `OFFENSIVE` / `HATE`), cleaned the text, removed
duplicates, and produced stratified train/val/test splits. That's steps
6–9 of your plan — **done**. The numbers are real, not estimates:

```
Merged pool: 38,023 → 37,749 rows after cleaning/dedup
  OFFENSIVE  22,342  (59.2%)
  SAFE       12,922  (34.2%)
  HATE        2,485  ( 6.6%)

train.csv   30,199 rows
val.csv      3,775 rows
test.csv     3,775 rows
olid_official_test.csv   860 rows  (external, never trained on)
```

**Important honesty note:** both source datasets are **English-only**
Twitter data — they contain no Hindi or Hinglish. Your problem statement
targets Indian social media, so this English pool is your **baseline
model** (Milestone 1). `docs/07_AI_Model.md` lays out exactly how to
extend the same pipeline to Hindi/Hinglish using free public datasets
(HASOC, HateXplain, L3Cube-HingCorpus) as Milestone 2 — this is what will
make the project genuinely stand out, since it's the gap the two research
papers in your project folder explicitly call out.

## Suggested reading order

1. Skim `01_PRD.md` and `02_TRD.md` — understand *what* and *why*.
2. Read `07_AI_Model.md` — this is the technical core of the project.
3. Follow `04_Implementation_Plan.md` day by day; it links back to
   `03_Tech_Stack.md` and `05_Design.md`/`06_System_Flow.md` at the
   points where you need them.
