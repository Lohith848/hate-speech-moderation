# System Flow
## Architecture, Data Flow & Sequence Diagrams

(Diagrams below are Mermaid — they render automatically on GitHub. If your
report/PDF tool doesn't support Mermaid, paste the code into
https://mermaid.live to export a PNG.)

## 1. High-level architecture

```mermaid
flowchart LR
    subgraph Client
        A[React Frontend<br/>Vercel]
    end
    subgraph Server
        B[FastAPI Backend<br/>Render]
        C[(PostgreSQL<br/>Supabase)]
        D[Fine-tuned Model<br/>bundled with backend<br/>or loaded from HF Hub]
    end

    A -- "POST /api/v1/moderate" --> B
    B -- "tokenize + infer" --> D
    D -- "label + confidence" --> B
    B -- "store log entry" --> C
    B -- "response JSON" --> A
    A -- "GET /api/v1/stats" --> B
    B -- "aggregate query" --> C
```

## 2. Model training pipeline (offline, Google Colab)

```mermaid
flowchart TD
    R1[labeled_data.csv<br/>Davidson, 24,783 rows] --> M[preprocess_data.py<br/>clean + unify labels]
    R2[olid-training-v1_0.tsv<br/>OLID, 13,240 rows] --> M
    M --> P[merged_dataset.csv<br/>37,749 rows]
    P --> S{stratified split}
    S --> TR[train.csv 30,199]
    S --> VA[val.csv 3,775]
    S --> TE[test.csv 3,775]
    TR --> FT[Fine-tune mBERT/MuRIL<br/>Colab free GPU]
    VA --> FT
    FT --> EV[Evaluate: accuracy, macro-F1,<br/>per-class metrics, confusion matrix]
    TE --> EV
    OT[olid_official_test.csv<br/>860 rows, external] --> EV
    EV --> HUB[Push best checkpoint<br/>to Hugging Face Hub]
    HUB --> DEPLOY[Backend loads model<br/>at startup]
```

## 3. Request sequence — single text moderation

```mermaid
sequenceDiagram
    participant U as User
    participant F as React Frontend
    participant B as FastAPI Backend
    participant M as Model (in-process)
    participant D as PostgreSQL

    U->>F: Types text, clicks Analyze
    F->>B: POST /api/v1/moderate {text}
    B->>B: Validate length (FR-8)
    B->>M: tokenize(text) -> tensor
    M->>B: logits -> softmax -> {SAFE, OFFENSIVE, HATE}
    B->>M: attribution (top tokens)
    B->>D: INSERT moderation_log row
    D-->>B: ack
    B-->>F: 200 {label, confidence, explanation, id}
    F-->>U: Render ResultCard
```

## 4. Request sequence — dashboard load

```mermaid
sequenceDiagram
    participant U as Admin
    participant F as React Frontend
    participant B as FastAPI Backend
    participant D as PostgreSQL

    U->>F: Opens /dashboard
    F->>B: GET /api/v1/stats?range=7d
    B->>D: GROUP BY date, label
    D-->>B: aggregated rows
    B-->>F: 200 {total, by_label, timeline}
    F-->>U: Render StatsCards + TrendChart + ActivityTable
```

## 5. Data flow summary (plain-English version, for your report)

1. Two public datasets are merged and relabeled into one 3-class schema
   offline, once (`scripts/preprocess_data.py`).
2. A transformer model is fine-tuned on that merged data in Colab, once
   per milestone, and the resulting weights are pushed to Hugging Face Hub.
3. At runtime, the FastAPI backend loads those weights **once** at
   startup (not per-request — this is the single biggest latency lever
   on a free-tier CPU box).
4. Every user request is: validate → tokenize → infer → explain → log to
   Postgres → respond. Nothing here calls back out to Colab or
   re-trains — training and serving are fully decoupled, which is what
   makes the free-tier hosting realistic in the first place.
5. The dashboard reads aggregated rows straight out of Postgres; no
   separate analytics pipeline is needed at this scale.
