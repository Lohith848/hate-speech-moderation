"""
Loads the fine-tuned model in a background thread so the server can bind
its port immediately (required for Render's free-tier port scan, which
times out after ~5 minutes -- see docs/02_TRD.md section 6).

The old design loaded the model at import time, which blocked port binding
for the entire download+load duration and caused Render to kill the service.
"""
import threading

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .config import MODEL_REPO

# Module-level state — populated by load_model(), read by predict().
_tokenizer = None
_model = None
_device = None
_id2label = None
_ready = threading.Event()  # signals "model is loaded and ready"


def load_model():
    """Download and load the model. Call once from a background thread at
    startup (see main.py lifespan). Safe to call multiple times -- only the
    first call does work."""
    global _tokenizer, _model, _device, _id2label

    if _ready.is_set():
        return

    print(f"[model] Loading '{MODEL_REPO}' from Hugging Face Hub ...")
    _tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO)
    _model = AutoModelForSequenceClassification.from_pretrained(MODEL_REPO)
    _model.eval()

    _device = "cuda" if torch.cuda.is_available() else "cpu"
    _model.to(_device)

    _id2label = _model.config.id2label
    print(f"[model] Loaded on device={_device}. Labels: {_id2label}")
    if set(_id2label.values()) != {"SAFE", "OFFENSIVE", "HATE"}:
        print(
            "[model] WARNING: expected labels SAFE/OFFENSIVE/HATE but got "
            f"{list(_id2label.values())}. Check that the model was pushed with "
            "id2label set correctly during training (see the training notebook, "
            "Step 7)."
        )

    _ready.set()
    print("[model] Ready to serve predictions.")


def is_ready() -> bool:
    """True once the model has been fully loaded."""
    return _ready.is_set()


def _softmax_probs(text: str):
    inputs = _tokenizer(
        text, truncation=True, padding=True, max_length=128, return_tensors="pt"
    ).to(_device)
    with torch.no_grad():
        logits = _model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    return probs, logits


def predict(text: str):
    """Returns (label: str, confidence: dict[str, float], explanation: list[dict])"""
    if not _ready.is_set():
        raise RuntimeError("Model is still loading")

    probs, logits = _softmax_probs(text)
    predicted_id = int(torch.argmax(logits, dim=1)[0])
    label = _id2label[predicted_id]
    confidence = {_id2label[i]: round(p.item(), 4) for i, p in enumerate(probs)}

    explanation = _explain(text, label_id=predicted_id, base_prob=probs[predicted_id].item())
    return label, confidence, explanation


def _explain(text: str, label_id: int, base_prob: float, top_k: int = 5):
    """Occlusion-based explanation: remove each word, see how much the
    predicted class's probability drops without it. A bigger drop means
    that word mattered more to the prediction. No extra ML library needed
    -- just extra forward passes, capped at 40 words to keep it fast on a
    free-tier CPU."""
    words = text.split()[:40]
    if not words:
        return []

    scores = []
    for i in range(len(words)):
        modified = " ".join(words[:i] + words[i + 1:])
        if not modified:
            continue
        probs, _ = _softmax_probs(modified)
        drop = base_prob - probs[label_id].item()
        scores.append({"token": words[i], "weight": round(max(drop, 0.0), 4)})

    scores.sort(key=lambda x: x["weight"], reverse=True)
    return [s for s in scores[:top_k] if s["weight"] > 0]
