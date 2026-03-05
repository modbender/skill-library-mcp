"""OpenAI text embedding wrapper."""

from __future__ import annotations

import os

import openai


class OpenAIEmbedder:
    """OpenAI text embedding wrapper."""

    name: str = "openai-text-embedding-3-small"
    dim: int = 1536

    def __init__(self) -> None:
        """  init  ."""
        api_key = os.environ.get("OPENAI_API_KEY")
        self.client = openai.OpenAI(api_key=api_key)

    def embed(self, text: str) -> list[float]:
        """embed."""
        payload = self.client.embeddings.create(model="text-embedding-3-small", input=text)
        return [float(v) for v in payload.data[0].embedding]

    def embed_batch(self, texts: list[tuple[str, str]]) -> dict[str, list[float]]:
        """embed batch."""
        contents = [text for _, text in texts]
        payload = self.client.embeddings.create(model="text-embedding-3-small", input=contents)
        vectors = [[float(v) for v in item.embedding] for item in payload.data]
        return {node_id: vectors[idx] for idx, (node_id, _) in enumerate(texts)}
