"""
embed.py — Embedding via Ollama (nomic-embed-text, 768 dimensions).

Uses the Ollama API at localhost:11434. The model is fixed —
nomic-embed-text is installed during `akb install`.
"""

import json
import time
import urllib.request

import numpy as np

OLLAMA_ENDPOINT = "http://localhost:11434/v1/embeddings"
MODEL = "nomic-embed-text"
DIM = 768


def _get_endpoint() -> str:
    return OLLAMA_ENDPOINT


def embed_texts(texts: list[str], batch_size: int = 32) -> np.ndarray:
    """Embed texts via Ollama. Returns (N, DIM) L2-normalized float32 array."""
    if not texts:
        return np.zeros((0, DIM), dtype=np.float32)

    url = _get_endpoint()
    if not url.endswith("/embeddings"):
        url += "/embeddings"

    all_vecs = []
    for i in range(0, len(texts), batch_size):
        batch = [t.replace("\x00", "")[:2500] for t in texts[i:i + batch_size]]
        payload = json.dumps({"input": batch, "model": MODEL}).encode()

        for attempt in range(5):
            try:
                req = urllib.request.Request(url, data=payload, headers={
                    "Content-Type": "application/json",
                })
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = json.loads(resp.read())
                break
            except (urllib.error.HTTPError, urllib.error.URLError, OSError) as e:
                if attempt < 4:
                    wait = 2 ** attempt
                    print(f"  [embed] Retry {attempt+1}/5: {e} (wait {wait}s)")
                    time.sleep(wait)
                else:
                    raise

        for emb in sorted(data["data"], key=lambda x: x["index"]):
            all_vecs.append(emb["embedding"])

    vecs = np.array(all_vecs, dtype=np.float32)
    # L2 normalize
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    norms = np.where(norms == 0, 1.0, norms)
    return vecs / norms


def embed_query(query: str) -> np.ndarray:
    """Embed a single query. Returns (dim,) float32 vector."""
    return embed_texts([query])[0]


def get_dim() -> int:
    """Return embedding dimension (fixed: 768 for nomic-embed-text)."""
    return DIM
