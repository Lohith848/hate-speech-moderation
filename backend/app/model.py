"""
Loads the quantized ONNX model in a background thread so the server can
bind its port immediately (Render free tier requirement).

Uses plain onnxruntime and numpy for inference -- NO PyTorch (`torch`) is
imported at serve time. This reduces the deployment memory footprint from
~712MB down to ~150MB, completely preventing Render free-tier 512MB OOM crashes.
"""
import os
import threading
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer, AutoConfig
from huggingface_hub import hf_hub_download

from .config import MODEL_REPO

SEQ_LEN = 128

# Module-level state — populated by load_model(), read by predict().
_tokenizer = None
_session = None
_input_names = set()
_id2label = {}
_ready = threading.Event()


def load_model():
    """Download and load the ONNX model in a background thread.
    Safe to call multiple times -- only the first call does work."""
    global _tokenizer, _session, _input_names, _id2label

    if _ready.is_set():
        return

    try:
        print(f"[model] Loading ONNX model '{MODEL_REPO}' from Hugging Face Hub ...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_REPO)
        config = AutoConfig.from_pretrained(MODEL_REPO)
        _id2label = {int(k): v for k, v in config.id2label.items()}

        print(f"[model] Downloading model.onnx from '{MODEL_REPO}' ...")
        onnx_path = hf_hub_download(repo_id=MODEL_REPO, filename="model.onnx")

        # CPUExecutionProvider for lightweight, stable free-tier CPU inference
        _session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        _input_names = {i.name for i in _session.get_inputs()}

        print(f"[model] Loaded successfully on CPU. Labels: {_id2label}")
        _ready.set()
        print("[model] Ready to serve predictions.")
    except Exception as e:
        print(f"[model] ERROR loading model '{MODEL_REPO}': {e}")


def is_ready() -> bool:
    """True once the model has been fully loaded."""
    return _ready.is_set()


def _softmax(logits):
    e = np.exp(logits - np.max(logits))
    return e / e.sum()


def _run(text: str):
    inputs = _tokenizer(
        text, truncation=True, padding=True, max_length=SEQ_LEN, return_tensors="np"
    )
    onnx_inputs = {
        name: inputs[name].astype(np.int64)
        for name in inputs
        if name in _input_names
    }
    logits = _session.run(None, onnx_inputs)[0][0]
    return _softmax(logits)


def predict(text: str):
    """Returns (label: str, confidence: dict[str, float], explanation: list[dict])"""
    if not _ready.is_set():
        raise RuntimeError("Model is still loading, please try again in a moment.")

    probs = _run(text)
    predicted_id = int(np.argmax(probs))
    label = _id2label[predicted_id]
    confidence = {_id2label[i]: round(float(p), 4) for i, p in enumerate(probs)}

    explanation = _explain(text, label_id=predicted_id, base_prob=float(probs[predicted_id]))
    return label, confidence, explanation


def _explain(text: str, label_id: int, base_prob: float, top_k: int = 5):
    """Occlusion-based explanation: remove each word, see how much the
    predicted class's probability drops without it. Capped at 40 words to
    keep it fast on a free-tier CPU."""
    words = text.split()[:40]
    if not words:
        return []

    scores = []
    for i in range(len(words)):
        modified = " ".join(words[:i] + words[i + 1:])
        if not modified:
            continue
        probs = _run(modified)
        drop = base_prob - float(probs[label_id])
        scores.append({"token": words[i], "weight": round(max(drop, 0.0), 4)})

    scores.sort(key=lambda x: x["weight"], reverse=True)
    return [s for s in scores[:top_k] if s["weight"] > 0]
