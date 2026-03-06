"""Local embeddings. Install: pip install crabpath[embeddings]"""

from __future__ import annotations


def local_embed_fn(text: str) -> list[float]:
    """local embed fn."""
    if not hasattr(local_embed_fn, "_model"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("pip install crabpath[embeddings]") from None
        local_embed_fn._model = SentenceTransformer("all-MiniLM-L6-v2")
    return local_embed_fn._model.encode(text).tolist()


def local_embed_batch_fn(texts: list[tuple[str, str]]) -> dict[str, list[float]]:
    """local embed batch fn."""
    if not hasattr(local_embed_batch_fn, "_model"):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            raise ImportError("pip install crabpath[embeddings]") from None
        local_embed_batch_fn._model = SentenceTransformer("all-MiniLM-L6-v2")
    model = local_embed_batch_fn._model
    ids = [nid for nid, _ in texts]
    contents = [content for _, content in texts]
    vectors = model.encode(contents).tolist()
    return dict(zip(ids, vectors))
