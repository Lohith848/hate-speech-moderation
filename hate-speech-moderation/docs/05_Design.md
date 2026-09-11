# Design Document
## UI/UX, Screens & Component Structure

---

## 1. Design principles

- **Human-in-the-loop, not auto-censorship.** The tool flags and
  explains; it never silently deletes. Copy and UI language should say
  "flagged for review," not "blocked" or "banned."
- **Explain every prediction.** A bare label with no reason invites
  distrust — every result shows the confidence breakdown and the
  triggering words.
- **Fast to scan on a small screen too** — since the dashboard is the
  part a moderator would use repeatedly, keep it to one clear number per
  card, not dense tables, on the primary view.

## 2. Screens

### 2.1 Analyze screen (`/`)

```
┌──────────────────────────────────────────┐
│  Content Moderation Demo                  │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │ Type or paste a post/comment...       │ │
│  │                                        │ │
│  └──────────────────────────────────────┘ │
│                            [ Analyze ]     │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  🟠 OFFENSIVE          (91% confident) │ │
│  │  ▓▓▓▓▓▓▓▓▓▓▓▓░░░  Confidence bar      │ │
│  │                                        │ │
│  │  Why: "idiot", "shut up" contributed   │ │
│  │  most to this prediction               │ │
│  └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

- Color coding: SAFE = green, OFFENSIVE = amber, HATE = red. Consistent
  across every screen.
- Confidence bar shows the *predicted* class's probability, with the full
  3-way breakdown available on hover/tap (don't clutter the primary view).
- Explanation renders as highlighted spans inside the original text, not
  just a bullet list — this is what actually builds trust with a
  moderator reviewing the call.
- Empty/invalid input: inline validation message, no page reload.

### 2.2 Admin dashboard (`/dashboard`)

```
┌──────────────────────────────────────────┐
│  Dashboard                    [Last 7d ▾] │
│                                            │
│  ┌────────┐ ┌────────┐ ┌────────┐         │
│  │ 1,245  │ │  800   │ │  380   │  ┌────┐ │
│  │ Total  │ │  Safe  │ │Offens. │  │ 65 │ │
│  │analyzed│ │        │ │        │  │Hate│ │
│  └────────┘ └────────┘ └────────┘  └────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Trend over time (stacked area chart) │ │
│  │  [Recharts: SAFE/OFFENSIVE/HATE lines]│ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Recent flagged content (table)       │ │
│  │  time | text (truncated) | label |conf│ │
│  └──────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

- Four summary cards at top (total / safe / offensive / hate), color
  matching the analyze screen.
- One trend chart (Recharts `AreaChart`, stacked by label).
- A recent-activity table, sortable by confidence, filterable by label —
  this is the actual moderation triage view.

### 2.3 Batch upload screen (`/batch`) — supports FR-7

- Drag-and-drop / file-picker for a CSV with a `text` column.
- Progress indicator while the backend processes rows.
- Results table + a "Download results CSV" button — this is also how
  you'll generate report-ready output for your own testing (step 21 of
  your plan).

## 3. Component structure (React)

```
src/
  components/
    AnalyzeForm.jsx        # textbox + button + validation
    ResultCard.jsx          # label, confidence bar, explanation
    StatsCard.jsx            # single dashboard summary number
    TrendChart.jsx           # Recharts wrapper
    ActivityTable.jsx        # recent/flagged content table
    BatchUpload.jsx           # CSV upload + results
  pages/
    AnalyzePage.jsx
    DashboardPage.jsx
    BatchPage.jsx
  api/
    client.js                # axios instance + all API calls in one place
  App.jsx                     # routes
```

Keep `api/client.js` as the single place that knows the backend base URL
— makes switching from local dev to the deployed Render URL a one-line
change (`.env` variable), not a search-and-replace across components.

## 4. Visual style

- Neutral base (white/near-white background, dark gray text) so the
  SAFE/OFFENSIVE/HATE color coding stays the dominant signal.
- One accent font weight for numbers on the dashboard (e.g., a heavier
  weight for the big total-count numbers) — keeps it scannable.
- No heavy branding needed; this is a practicum demo, not a product
  launch — clarity beats polish here.
