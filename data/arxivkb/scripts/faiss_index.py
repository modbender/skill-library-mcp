"""
faiss_index.py — FAISS index manager for ArXivKB.

Uses IndexFlatIP (inner product = cosine similarity on normalized vectors).
"""

import os
import numpy as np

try:
    import faiss
except ImportError:
    faiss = None


class FaissIndex:
    def __init__(self, data_dir: str, dim: int = 768):
        self.path = os.path.join(os.path.expanduser(data_dir), "faiss", "arxivkb.faiss")
        self.dim = dim
        self.index = None
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    def load(self):
        if faiss is None:
            raise ImportError("faiss-cpu required: pip install faiss-cpu")
        if os.path.exists(self.path):
            self.index = faiss.read_index(self.path)
            self.dim = self.index.d
        else:
            self.index = faiss.IndexFlatIP(self.dim)

    def add(self, vectors: np.ndarray) -> list[int]:
        """Add vectors. Returns list of FAISS IDs (sequential from current ntotal)."""
        start = self.index.ntotal
        self.index.add(vectors.astype(np.float32))
        return list(range(start, self.index.ntotal))

    def search(self, query_vec: np.ndarray, top_k: int = 10) -> list[tuple[int, float]]:
        """Search. Returns [(faiss_id, score), ...]."""
        if self.index is None or self.index.ntotal == 0:
            return []
        q = query_vec.reshape(1, -1).astype(np.float32)
        scores, ids = self.index.search(q, min(top_k, self.index.ntotal))
        return [(int(ids[0][i]), float(scores[0][i])) for i in range(len(ids[0])) if ids[0][i] >= 0]

    def save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.path)

    @property
    def size(self) -> int:
        return self.index.ntotal if self.index else 0
