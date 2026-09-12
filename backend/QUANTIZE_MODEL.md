# Why the deploy OOM'd, and what actually fixes it

## The two errors you saw

**1. `Network is unreachable` connecting to Supabase**
Supabase's *direct* connection host (`db.<ref>.supabase.co`) resolves to
an IPv6-only address. Render's free tier doesn't route outbound IPv6, so
that connection can never succeed there. Fix: use Supabase's **Session
Pooler** connection string instead (Supabase dashboard → Connect →
Session pooler tab) — it's IPv4-compatible (e.g. `aws-0-<region>.pooler.supabase.com:5432/postgres` or port 6543). Note the username becomes
`postgres.<project-ref>`, not just `postgres`. Update `DATABASE_URL`
accordingly (see `.env.example`).

**2. `502 Bad Gateway` / `Out of memory (used over 512Mi)`**
This one isn't a config mistake — it's structural. `bert-base-multilingual-cased`
covers 100+ languages, so its vocabulary is ~120,000 tokens (English-only
BERT has ~30,000). That vocabulary becomes the model's embedding table,
and embedding table size = vocab_size × hidden_dim — for this model,
that's **~92 million parameters just for the embedding lookup**, before
counting the 12 transformer layers on top. In full precision (float32,
4 bytes/parameter), the whole model is **~711MB**. Render's free tier
caps out at 512MB total, for the whole process. The model alone is
already bigger than the budget. When uvicorn tries to load it, the Linux cgroup
kills the process immediately, leading to **502 Bad Gateway**.

## The fix: quantize to INT8 (v2 — no `optimum`)

`backend/export_and_quantize_model.ipynb` (Colab, no GPU needed):

1. Uses PyTorch's native `torch.onnx.export` to export your model to ONNX. (No `optimum` library used, avoiding the `huggingface-hub` dependency conflict in Colab).
2. Quantizes it to INT8 dynamically — specifically targeting **both** `MatMul` (the
   attention/feed-forward layers) **and** `Gather` (the embedding
   lookup).
3. Sanity-checks that predictions still look right after quantization.
4. Pushes the result to a new Hugging Face repo
   (`lohithg8408/content-moderation-onnx-int8`).

Expected result: ~711MB shrinks to ~150-180MB.
At serve time, `backend/app/model.py` loads `onnxruntime` directly on CPU without needing PyTorch (`torch`), so total RAM usage stays comfortably under ~200MB, well below Render's 512MB limit.

## After running the notebook in Colab

1. Update `MODEL_REPO` in Render environment variables to `lohithg8408/content-moderation-onnx-int8`.
2. Ensure `DATABASE_URL` in Render is set to your Supabase Session Pooler URI.
