#!/usr/bin/env python3
"""
Shared embedding utilities for Memory V2.
Uses snowflake-arctic-embed2 on TrueNAS Ollama.
"""

import requests
import hashlib

OLLAMA_HOST = "http://localhost:11434"
EMBED_MODEL = "snowflake-arctic-embed2:latest"


def get_embedding(text: str) -> list[float]:
    """Get embedding vector for a text string."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embedding"]


def get_embeddings_batch(texts: list[str], batch_size: int = 10) -> list[list[float]]:
    """Get embeddings for multiple texts."""
    results = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for text in batch:
            results.append(get_embedding(text))
    return results


def content_hash(text: str) -> str:
    """Generate a content hash for deduplication."""
    return hashlib.md5(text.strip().lower().encode()).hexdigest()[:16]
