# Frontend — AI Content Moderation Demo

React (Vite) + Tailwind app with three screens: Analyze, Dashboard, and
Batch upload. Talks to the FastAPI backend over REST — see
`src/api/client.js` for the one place that knows the backend's URL.

## Run it locally

Make sure the backend is already running first (see `backend/README.md`),
then in a **second terminal**:

```bash
cd frontend
npm install

cp .env.example .env    # confirm VITE_API_BASE_URL matches where your
                         # backend is actually running (default: localhost:8000)

npm run dev
```

Open the URL it prints (usually **http://localhost:5173**).

## What's on each screen

- **Analyze** (`/`) — textbox, Analyze button, result card with a
  confidence bar, per-class breakdown, and the input text highlighted by
  which words drove the prediction.
- **Dashboard** (`/dashboard`) — total/safe/offensive/hate counts, a
  stacked trend chart, and a recent-activity table. Pulls from
  `GET /api/v1/stats`.
- **Batch** (`/batch`) — upload a CSV with a `text` column, get
  predictions for every row, download the results as CSV.

## Project layout

```
frontend/
  src/
    api/client.js         all backend calls in one place
    labelStyles.js         shared SAFE/OFFENSIVE/HATE colors
    components/
      AnalyzeForm.jsx
      ResultCard.jsx
      StatsCard.jsx
      TrendChart.jsx
      ActivityTable.jsx
      BatchUpload.jsx
    pages/
      AnalyzePage.jsx
      DashboardPage.jsx
      BatchPage.jsx
    App.jsx                 routes + nav bar
    main.jsx                  entry point
```

## Before you deploy (Vercel)

1. Push this `frontend/` folder to your GitHub repo.
2. In Vercel, import the repo, set the root directory to `frontend`.
3. Add environment variable `VITE_API_BASE_URL` = your deployed Render
   backend URL.
4. Deploy. See `docs/04_Implementation_Plan.md` Phase 6, step 23 for more.
