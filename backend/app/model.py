"""
Loads the fine-tuned model ONCE at import time (i.e. once per server
process, not once per request -- this is the single biggest latency
lever on a free-tier CPU box, see docs/02_TRD.md section 6).
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from .config import MODEL_REPO

print(f"[model] Loading '{MODEL_REPO}' from Hugging Face Hub ...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_REPO)
model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

id2label = model.config.id2label
print(f"[model] Loaded on device={device}. Labels: {id2label}")
if set(id2label.values()) != {"SAFE", "OFFENSIVE", "HATE"}:
    print(
        "[model] WARNING: expected labels SAFE/OFFENSIVE/HATE but got "
        f"{list(id2label.values())}. Check that the model was pushed with "
        "id2label set correctly during training (see the training notebook, "
        "Step 7)."
    )


def _softmax_probs(text: str):
    inputs = tokenizer(
        text, truncation=True, padding=True, max_length=128, return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=1)[0]
    return probs, logits


def predict(text: str):
    """Returns (label: str, confidence: dict[str, float], explanation: list[dict])"""
    probs, logits = _softmax_probs(text)
    predicted_id = int(torch.argmax(logits, dim=1)[0])
    label = id2label[predicted_id]
    confidence = {id2label[i]: round(p.item(), 4) for i, p in enumerate(probs)}

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
