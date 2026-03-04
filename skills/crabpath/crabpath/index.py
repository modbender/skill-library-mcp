"""Pure vector index used by CrabPath."""

from __future__ import annotations

import json
import math
from pathlib import Path


class VectorIndex:
    """In-memory map of node IDs to caller-provided vectors.

    Brute-force cosine similarity. O(n) per query where n = number of vectors.
    Practical limit: ~10,000 nodes for <10ms query latency.
    For larger graphs, provide a custom index via callbacks.
    """

    def __init__(self) -> None:
        """  init  ."""
        self._vectors: dict[str, list[float]] = {}

    def upsert(self, node_id: str, vector: list[float]) -> None:
        """upsert."""
        self._vectors[node_id] = list(vector)

    def search(self, query_vector: list[float], top_k: int = 10) -> list[tuple[str, float]]:
        """search."""
        if top_k <= 0:
            return []
        scores = []
        for node_id, vector in self._vectors.items():
            score = self.cosine(query_vector, vector)
            scores.append((node_id, score))
        scores.sort(key=lambda item: item[1], reverse=True)
        return scores[:top_k]

    def remove(self, node_id: str) -> None:
        """remove."""
        self._vectors.pop(node_id, None)

    def save(self, path: str) -> None:
        """save."""
        Path(path).write_text(json.dumps(self._vectors, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str) -> "VectorIndex":
        """load."""
        index = cls()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        for node_id, vector in data.items():
            index._vectors[node_id] = list(vector)
        return index

    @staticmethod
    def cosine(a: list[float], b: list[float]) -> float:
        """cosine."""
        if not a or not b:
            return 0.0
        if len(a) != len(b):
            return 0.0

        dot = 0.0
        norm_a = 0.0
        norm_b = 0.0
        for x, y in zip(a, b):
            dot += x * y
            norm_a += x * x
            norm_b += y * y

        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        return dot / (math.sqrt(norm_a) * math.sqrt(norm_b))
