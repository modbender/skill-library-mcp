"""
Embedder — singleton wrapper for sentence-transformers.
Uses Unix socket server when available (instant), falls back to local model (~6s first call).
"""
import json
import socket
import logging
import numpy as np

log = logging.getLogger(__name__)

SOCKET_PATH = "/tmp/openclaw-embed.sock"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIM = 384

_model = None


def _try_server(action: str, **kwargs) -> dict | None:
    """Try to use the embedding server. Returns None if unavailable."""
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect(SOCKET_PATH)
        request = {"action": action, **kwargs}
        s.sendall((json.dumps(request) + "\n").encode())
        data = b""
        while True:
            chunk = s.recv(1048576)  # 1MB buffer for batch embeddings
            if not chunk:
                break
            data += chunk
            if b"\n" in data:
                break
        s.close()
        resp = json.loads(data.decode().strip())
        if "error" in resp:
            log.warning(f"Server error: {resp['error']}")
            return None
        return resp
    except (ConnectionRefusedError, FileNotFoundError, OSError):
        return None


def _get_model():
    """Lazy-load local model as fallback."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def embed(text: str) -> np.ndarray:
    """Embed a single text. Returns normalized 384-dim vector."""
    # Try server first
    resp = _try_server("embed", text=text)
    if resp and "embedding" in resp:
        return np.array(resp["embedding"], dtype=np.float32)
    # Fallback to local
    return _get_model().encode(text, normalize_embeddings=True).astype(np.float32)


def embed_batch(texts: list[str]) -> np.ndarray:
    """Embed multiple texts. Returns array of normalized vectors."""
    if not texts:
        return np.array([], dtype=np.float32)
    # Try server first
    resp = _try_server("embed_batch", texts=texts)
    if resp and "embeddings" in resp:
        return np.array(resp["embeddings"], dtype=np.float32)
    # Fallback to local
    return _get_model().encode(texts, normalize_embeddings=True, batch_size=32).astype(np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


def cosine_search(query_vec: np.ndarray, corpus_vecs: np.ndarray, top_k: int = 10) -> list[tuple[int, float]]:
    """Find top-k most similar vectors. Returns list of (index, score)."""
    if len(corpus_vecs) == 0:
        return []
    sims = corpus_vecs @ query_vec / (np.linalg.norm(corpus_vecs, axis=1) * np.linalg.norm(query_vec) + 1e-8)
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [(int(i), float(sims[i])) for i in top_indices]
