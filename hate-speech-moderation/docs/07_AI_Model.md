# AI Model Documentation
## Dataset, Label Design, Model Selection, Training & Evaluation Plan

---

## 1. Datasets used

### 1.1 What you actually have

| Dataset | Rows | Language | Labels | Source |
|---|---|---|---|---|
| `labeled_data.csv` | 24,783 tweets | English | 0=hate_speech, 1=offensive_language, 2=neither | Davidson et al., 2017, *"Automated Hate Speech Detection and the Problem of Offensive Language"* |
| OLID (`olid-training-v1_0.tsv` + test files) | 13,240 train / 860 test | English | Hierarchical: subtask_a (NOT/OFF), subtask_b (TIN/UNT), subtask_c (IND/GRP/OTH) | Zampieri et al., 2019, SemEval-2019 Task 6 (OffensEval) |

**Both are English-only Twitter datasets.** Neither contains Hindi or
Hinglish. This matters for your problem statement and is addressed
directly in Section 6 below — don't let anyone (including a grader) think
this was missed; it's a deliberate, documented staging decision.

### 1.2 Why merge two different labeling schemes into one

Davidson gives you a flat 3-class label. OLID gives you a *hierarchy*
(is it offensive? → is it targeted? → is the target a group?). Rather than
pick one and throw the other away, merging both roughly **doubles your
training data** and — more importantly — OLID's hierarchy is exactly what
lets you approximate a genuine **hate speech** category (identity/group
targeted) versus generic **trolling/offensive** content, which Davidson's
"offensive_language" class conflates with everything from swearing to
targeted insults.

### 1.3 Unified label schema

| Label | Meaning | Davidson source | OLID source |
|---|---|---|---|
| `SAFE` | No offense detected | class 2 (neither) | subtask_a = NOT |
| `OFFENSIVE` | Profanity, insults, trolling — not identity-targeted | class 1 (offensive_language) | subtask_a=OFF & subtask_b=UNT, **or** subtask_a=OFF & subtask_b=TIN & subtask_c∈{IND,OTH} |
| `HATE` | Targeted, identity-based hate speech (religion, caste, gender, ethnicity, political group, etc.) | class 0 (hate_speech) | subtask_a=OFF & subtask_b=TIN & subtask_c=GRP |

**Why `GRP` = HATE:** OLID's own annotation guide (`olid-annotation.txt`
in your project files) defines a GRP target as *"a group of people
considered as a unity due to the same ethnicity, gender, sexual
orientation, political affiliation, religious belief, or something
else"* — that is the standard definition of a hate-speech target used
across the literature. `IND` (a named individual) and `OTH` (an
organization/event/situation) are targeted insults, but not identity-based
hate speech, so they map to `OFFENSIVE`.

**Known limitation, state it plainly in your report:** this is a
mapping, not a re-annotation. A handful of GRP-targeted posts might be
closer to harassment than "hate speech" in the strictest sense, and vice
versa. This is normal in NLP dataset-merging work and is exactly the kind
of limitation a good report calls out rather than hides.

### 1.4 Actual numbers after cleaning (already run — see `scripts/preprocess_data.py`)

```
Merged pool: 38,023 rows → 37,749 after removing empties + duplicates

Class distribution:
  OFFENSIVE   22,342   (59.2%)
  SAFE        12,922   (34.2%)
  HATE         2,485   ( 6.6%)

train.csv    30,199 rows  (80%, stratified)
val.csv       3,775 rows  (10%, stratified)
test.csv      3,775 rows  (10%, stratified)

olid_official_test.csv   860 rows — OLID's own SemEval test set,
                          reconstructed from testset-level{a,b,c}.tsv +
                          labels-level{a,b,c}.csv, kept OUT of training.
                          Used purely as an external "did this generalize
                          or did it just memorize the training
                          distribution?" check.
```

**The class imbalance is real and must be handled, not ignored.** HATE is
only 6.6% of the data. A model that never predicts HATE could still score
~93% "accuracy" while being useless — this is exactly why Section 4
below requires macro-F1 and per-class recall, not just accuracy, as the
primary metrics.

## 2. Model Selection

### 2.1 What the research says (from the papers in your project folder)

Both reference papers independently landed on the same conclusion:
transformer models beat classical ML and even LSTMs on this task.

| Model | Accuracy | F1 | Source |
|---|---|---|---|
| Logistic Regression | 84.2% | 80.6% | Patel et al., 2025 |
| LSTM | 88.9% | 85.9% | Patel et al., 2025 |
| **BERT** | **93.5%** | **91.1%** | Patel et al., 2025 |

The same paper's language-wise breakdown is the most important number
for *your* project specifically:

| Language | Precision | Recall | F1 |
|---|---|---|---|
| English | 93.4% | 91.5% | 92.4% |
| Hindi | 89.2% | 88.1% | 88.6% |
| Hinglish | 85.5% | 83.2% | 84.3% |

This tells you exactly what to expect: performance degrades from English
→ Hindi → Hinglish, and Hinglish (code-mixed) is the genuinely hard part
— consistent with what the second paper in your folder identifies as an
open research gap (multimodal, context-aware, code-mixed moderation).

### 2.2 What you'll actually fine-tune

| Stage | Model | Why |
|---|---|---|
| **Milestone 1 — baseline (English)** | `bert-base-multilingual-cased` (mBERT) | Free, well-documented, small enough to fit Render's free-tier RAM, and — critically — already multilingual, so Milestone 2 is a fine-tuning *continuation*, not a rebuild |
| **Milestone 2 — Indian-language extension** | `google/muril-base-cased` | Purpose-built by Google for 17 Indian languages **including transliterated (Hinglish-style) text** — directly addresses the code-mixed weakness both papers flag. Free on Hugging Face. |
| Considered and rejected for MVP | `xlm-roberta-large`, `ai4bharat/indic-bert` (heavier variants) | Larger models improve accuracy marginally but won't fit the free-tier 512MB RAM inference budget from `02_TRD.md` — good future-work note, bad MVP choice |

Practical note: `bert-base-multilingual-cased` and `muril-base-cased` are
both ~180M parameters (~700MB fp32, ~180MB with dynamic INT8
quantization) — quantize before deploying to Render's free tier (see
`04_Implementation_Plan.md`, step 13).

## 3. Preprocessing (already implemented in `scripts/preprocess_data.py`)

1. Unescape HTML entities (`&amp;` → `&`).
2. Strip leading `RT @user:` boilerplate.
3. Normalize URLs → literal `URL`, mentions → literal `@USER` (matches
   OLID's own convention, so both datasets end up in the same style).
4. Collapse whitespace.
5. Drop empty strings and exact duplicates.
6. **Deliberately did NOT lowercase, strip emoji, or remove punctuation.**
   BERT-family cased models use case and punctuation as signal (ALL CAPS,
   "!!!", emoji all correlate with offense/hate in this data) — stripping
   them, as older TF-IDF/Logistic-Regression pipelines typically do,
   throws away useful information for a transformer model.
7. Stratified 80/10/10 split by unified label, fixed seed (42) for
   reproducibility.

## 4. Training Plan (Google Colab, free T4 GPU)

```python
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    TrainingArguments, Trainer
)
import evaluate, numpy as np

MODEL_NAME = "bert-base-multilingual-cased"   # swap to google/muril-base-cased for Milestone 2
LABELS = ["SAFE", "OFFENSIVE", "HATE"]

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(
    MODEL_NAME, num_labels=3
)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=128)

# class weights to counter the 59/34/7 imbalance (Section 1.4)
class_weights = torch.tensor([1.0, 0.55, 5.2])  # inverse-frequency, tune on val set

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=32,
    learning_rate=2e-5,
    weight_decay=0.01,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    fp16=True,   # Colab T4 supports mixed precision -> ~2x faster
)
```

- **Epochs:** 3–4 is typically enough for BERT-family fine-tuning before
  overfitting on a dataset this size; watch `val` macro-F1 each epoch and
  keep the best checkpoint (`load_best_model_at_end=True` above).
- **Class weights:** use a weighted `CrossEntropyLoss` (or focal loss if
  macro-F1 is still weak on HATE after weighting) inside a custom
  `Trainer.compute_loss` — this single change matters more than almost
  any other hyperparameter given the 6.6% HATE share.
- **Max sequence length 128** is generous for tweet-length text (280
  chars ≈ 60-80 BERT tokens) and keeps training fast on the free GPU.

## 5. Evaluation

Report all of these — not just accuracy:

| Metric | Why it's required here |
|---|---|
| Accuracy | Baseline number, but misleading alone given the imbalance |
| **Macro-F1** | Treats all 3 classes equally — the real headline number for this project |
| Per-class Precision/Recall/F1 | Shows specifically how well HATE (the hardest, rarest class) is caught |
| Confusion matrix | Shows exactly what's confused with what (expect some OFFENSIVE↔HATE confusion — that's the genuinely hard boundary) |
| Evaluation on `olid_official_test.csv` | Proves generalization beyond the merged train/val/test split, since this data was **never seen** in training |

```python
from sklearn.metrics import classification_report, confusion_matrix
preds = trainer.predict(test_dataset)
y_pred = np.argmax(preds.predictions, axis=1)
print(classification_report(y_true, y_pred, target_names=LABELS))
print(confusion_matrix(y_true, y_pred))
```

## 6. Extending to Hindi & Hinglish (Milestone 2 — this is what makes it "your best project")

Since the provided datasets are English-only, genuine Indian-language
coverage is an explicit second phase, not an afterthought:

1. **Add data:** all free, public, citable —
   - **HASOC** (Hate Speech and Offensive Content Identification —
     Hindi/English/German, used in FIRE shared tasks)
   - **HateXplain** (English, but widely used alongside Indian-language
     work, and gives you span-level rationales for free — directly useful
     for the explanation feature, FR-4)
   - **L3Cube-HingCorpus / HingBERT resources** (Hinglish, code-mixed,
     built specifically for this problem)
2. **Re-map** each new dataset's labels into the same `SAFE` /
   `OFFENSIVE` / `HATE` schema — the same discipline as Section 1.3.
3. **Switch the base model** to `google/muril-base-cased` and continue
   fine-tuning (either from the Milestone-1 checkpoint or from scratch on
   the combined pool — try both, keep whichever wins on val macro-F1).
4. **Re-evaluate per language** the same way the reference paper does
   (Table in Section 2.1) — this per-language breakdown is your strongest
   report content, because it's an honest, measured account of where the
   system works and where it doesn't, rather than a single inflated
   accuracy number.

## 7. Explainability (FR-4)

Simplest free approach for a transformer classifier: **attention-weight
or gradient-based token attribution** using `captum`'s
`LayerIntegratedGradients` against the model's embedding layer, or a
simpler occlusion method (mask each word, see how much the predicted
class probability drops). Return the top 3-5 tokens by attribution score
as the `explanation` field in the API response (see `02_TRD.md` §5).

## 8. Model Card (fill in after training — required for your final report)

```
Model: [bert-base-multilingual-cased fine-tuned | google/muril-base-cased fine-tuned]
Training data: Davidson (2017) + OLID (2019), merged & relabeled, N=30,199
Intended use: Text moderation triage for Indian social media content (English baseline / Hindi+Hinglish extension)
Known limitations:
  - HATE class is underrepresented (6.6% of training data)
  - Baseline model trained on English-only data; Hindi/Hinglish performance
    depends on Milestone 2 data addition
  - Label schema is a documented mapping from two source annotation
    schemes, not a fresh human annotation
Metrics: [fill in from Section 5 after training]
```
