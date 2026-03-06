"""Zero-dep deterministic hash vectorizer."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_CAMEL_RE = re.compile(r"(?<=[a-z])(?=[A-Z])")


class HashEmbedder:
    """Deterministic hashed n-gram vectorizer. No deps, no downloads, no network."""

    name: str = "hash-v1"

    def __init__(self, dim: int = 1024, ngram_range: tuple[int, int] = (3, 5)) -> None:
        """  init  ."""
        self.dim = dim
        self.ngram_range = ngram_range

    def _tokenize(self, text: str) -> list[str]:
        """ tokenize."""
        words = _WORD_RE.findall(text)
        tokens: list[str] = []
        for word in words:
            parts = _CAMEL_RE.sub(" ", word).split()
            for part in parts:
                for sub in part.split("_"):
                    if sub:
                        tokens.append(sub.lower())
        return tokens

    def _ngrams(self, text: str) -> list[str]:
        """ ngrams."""
        lower = text.lower()
        grams: list[str] = []
        for n in range(self.ngram_range[0], self.ngram_range[1] + 1):
            for i in range(len(lower) - n + 1):
                grams.append(lower[i : i + n])
        return grams

    def embed(self, text: str) -> list[float]:
        """embed."""
        tokens = self._tokenize(text)
        all_features = tokens + self._ngrams(text)
        counts = Counter(all_features)

        vector = [0.0] * self.dim
        for feature, count in counts.items():
            h = hashlib.sha256(feature.encode()).hexdigest()
            bucket = int(h[:8], 16) % self.dim
            sign = 1.0 if int(h[8:10], 16) % 2 == 0 else -1.0
            vector[bucket] += sign * count

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """embed texts."""
        return [self.embed(t) for t in texts]

    def embed_batch(self, texts: list[tuple[str, str]]) -> dict[str, list[float]]:
        """embed batch."""
        return {name: self.embed(text) for name, text in texts}


def _coerce_embed_inputs(texts: list[tuple[str, str]] | list[str]) -> list[tuple[str, str]]:
    """Normalize embedding inputs to ``(node_id, text)`` pairs."""
    if not texts:
        return []

    normalized: list[tuple[str, str]] = []
    for idx, item in enumerate(texts):
        if isinstance(item, tuple):
            if len(item) != 2:
                raise TypeError("default_embed_batch tuple entries must be (node_id, text)")
            node_id, content = item
        else:
            node_id, content = str(idx), item
        normalized.append((node_id, content))

    return normalized


_default_embedder: HashEmbedder | None = None


def default_embed(text: str) -> list[float]:
    """default embed."""
    global _default_embedder
    if _default_embedder is None:
        _default_embedder = HashEmbedder()
    return _default_embedder.embed(text)


def default_embed_batch(texts: list[tuple[str, str]] | list[str]) -> dict[str, list[float]]:
    """default embed batch."""
    global _default_embedder
    if _default_embedder is None:
        _default_embedder = HashEmbedder()
    return _default_embedder.embed_batch(_coerce_embed_inputs(texts))
