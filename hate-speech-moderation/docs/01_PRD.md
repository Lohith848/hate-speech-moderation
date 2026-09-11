# Product Requirements Document (PRD)
## AI-Powered Content Moderation System for Indian Social Media

**Version 1.0** | Innovation Practicum 3

---

## 1. Problem Statement

Social media use in India has grown to hundreds of millions of active
users, communicating across English, Hindi, and code-mixed Hinglish.
Manual moderation cannot keep pace with this volume, and existing
automated tools are built and tested almost exclusively on English data —
they miss abuse expressed in Hindi, Hinglish, sarcasm, and culturally
specific slurs. The result is a moderation gap that lets hate speech,
targeted harassment, and trolling spread on Indian platforms while
sometimes over-flagging harmless regional-language speech.

This project builds a working AI system that classifies a piece of
user-generated text (a post/comment/tweet) into one of three categories —
**Safe**, **Offensive/Troll**, or **Hate Speech** — with a confidence
score and a short explanation, exposed through a simple web app with an
admin analytics dashboard.

## 2. Goals

| Goal | Success looks like |
|---|---|
| Build a working classifier | ≥ 85% accuracy, ≥ 0.80 macro-F1 on held-out test data |
| Handle Indian-language content | Baseline on English data first, then measurable performance on Hindi/Hinglish samples (Milestone 2) |
| Ship an end-to-end product | A user can type text, get a prediction, and see it logged in an admin dashboard — all deployed, publicly reachable, free of cost |
| Be explainable, not a black box | Every prediction shows which words/phrases drove the decision |
| Be reproducible for the report | Every number in the final report traces back to a script in this repo |

## 3. Non-goals (explicitly out of scope)

- Real-time firehose ingestion from live Twitter/Instagram APIs (both now
  require paid tiers — see `03_Tech_Stack.md`). The system accepts text
  via manual input or CSV/API for evaluation instead of live scraping.
- Image, audio, or video moderation (OCR/multimodal). Text-only for this
  practicum; noted as future work, same as the second reference paper in
  the project folder.
- Automatic account-level actions (banning, shadow-banning). The system
  **flags** content; enforcement decisions stay with a human moderator.
- Full legal/regulatory compliance (IT Rules 2021 intermediary
  obligations) — acknowledged in the report but not implemented.

## 4. Users & Use Cases

| User | Need | How the product serves it |
|---|---|---|
| **Platform moderator / admin** | Triage large volumes of flagged content quickly | Dashboard: queue sorted by confidence, filters by category, daily/weekly counts |
| **End user submitting content for a moderation check** (demo purposes) | Know if their text would be flagged, and why | Analyze screen: text box → prediction, confidence, highlighted trigger words |
| **You (the evaluator/grader)** | Verify the system actually works and is reproducible | Metrics report, confusion matrix, a live deployed demo link |

## 5. Features (MVP scope, mapped to your 29-step plan)

### 5.1 Core detection engine
- Fine-tuned transformer model (see `07_AI_Model.md`) served behind a
  `/predict` API.
- Input: raw text string (post/comment).
- Output: `label` (SAFE / OFFENSIVE / HATE), `confidence` (0–1 per class),
  `explanation` (top contributing tokens).

### 5.2 Web application
- **Analyze page**: textbox, "Analyze" button, result card
  (label + confidence bar + explanation).
- **History**: every analyzed post stored with timestamp, label,
  confidence.
- **Admin dashboard**: total posts analyzed, count per label, trend chart
  over time (see `05_Design.md` for exact layout).

### 5.3 API
- `POST /api/v1/moderate` — single-text prediction.
- `POST /api/v1/moderate/batch` — CSV upload, batch prediction (useful for
  your own testing/report generation).
- `GET /api/v1/stats` — aggregated dashboard numbers.

## 6. Success Criteria (how you'll grade yourself before submission)

- [ ] Model reaches ≥ 85% accuracy / ≥ 0.80 macro-F1 on `test.csv`.
- [ ] Model evaluated on `olid_official_test.csv` (external set) to prove
      it isn't just memorizing the training distribution.
- [ ] End-to-end flow works: type text in deployed frontend → correct
      label appears within ~2 seconds → entry appears in dashboard.
- [ ] At least one Hindi/Hinglish qualitative test case shown in the
      report, with an honest discussion of where the baseline model
      struggles (this is expected and is itself a valid finding).
- [ ] All code in GitHub, all documents in this pack, demo video recorded.

## 7. Constraints

- **Budget: ₹0.** Every tool in `03_Tech_Stack.md` has a free tier
  sufficient for a practicum-scale demo.
- **Compute:** model fine-tuning done on Google Colab's free GPU
  (T4, ~12 hour session limit, no cost).
- **Timeline:** designed to fit the day-by-day schedule in
  `04_Implementation_Plan.md`.

## 8. Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Class imbalance — HATE is only 6.6% of the merged dataset | Class-weighted loss during training; report macro-F1, not just accuracy (see `07_AI_Model.md`) |
| No Hindi/Hinglish data in the two provided datasets | Documented as a known baseline limitation; Milestone 2 adds HASOC/HateXplain/HingCorpus |
| Free-tier services sleep/spin-down (Render free web services) | Document expected cold-start delay (~30–50s) in the demo video/report so it isn't mistaken for a bug |
| Over-flagging legitimate regional-language political/religious speech | Explanation feature + human-in-the-loop framing (system flags, doesn't auto-delete) |
