"""Helpers for optional LLM/embedding batch execution."""

from __future__ import annotations

from collections.abc import Callable


def batch_or_single(
    requests: list[dict],
    llm_fn: Callable[[str, str], str] | None = None,
    llm_batch_fn: Callable[[list[dict]], list[dict]] | None = None,
    max_workers: int = 8,
) -> list[dict]:
    """Execute LLM requests using a batch callback when available, otherwise parallel single calls."""
    if llm_batch_fn is not None:
        return llm_batch_fn(requests)
    if llm_fn is None:
        raise ValueError("either llm_fn or llm_batch_fn must be provided")
    if not requests:
        return []

    from concurrent.futures import ThreadPoolExecutor

    def _call(req: dict) -> dict:
        """Call LLM for one request."""
        try:
            response = llm_fn(req["system"], req["user"])
            return {"id": req["id"], "response": response}
        except Exception as e:  # noqa: BLE001
            return {"id": req["id"], "response": "", "error": str(e)}

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        return list(pool.map(_call, requests))


def batch_or_single_embed(
    texts: list[tuple[str, str]],
    embed_fn: Callable[[str], list[float]] | None = None,
    embed_batch_fn: Callable[[list[tuple[str, str]]], dict[str, list[float]]] | None = None,
    max_workers: int = 8,
) -> dict[str, list[float]]:
    """Execute embedding requests with either batched or single-text callbacks.

    Contract:
    - ``texts`` is always ``list[tuple[node_id, text]]`` for both single and batch paths.
    - ``embed_fn`` receives only ``text`` and returns ``list[float]``.
    - ``embed_batch_fn`` receives ``list[tuple[node_id, text]]`` and returns
      ``dict[node_id, list[float]]``.
    """
    if embed_batch_fn is not None:
        return embed_batch_fn(texts)
    if embed_fn is None:
        raise ValueError("either embed_fn or embed_batch_fn must be provided")

    from concurrent.futures import ThreadPoolExecutor

    def _call(item: tuple[str, str]) -> tuple[str, list[float]]:
        """Call embedder for one text."""
        node_id, text = item
        return node_id, embed_fn(text)

    results: dict[str, list[float]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for node_id, vector in pool.map(_call, texts):
            results[node_id] = vector
    return results
