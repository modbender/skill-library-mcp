"""Cross-file connection suggestions driven by lexical overlap or LLM feedback."""

from __future__ import annotations

from collections.abc import Callable

from .graph import Edge, Graph, Node
from ._batch import batch_or_single
from ._util import _extract_json, _tokenize


def _safe_float(value: object, default: float = 0.0) -> float:
    """ safe float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _node_file(node: Node | None) -> str | None:
    """ node file."""
    if node is None:
        return None
    file_value = node.metadata.get("file")
    return str(file_value) if isinstance(file_value, str) else None


def suggest_connections(
    graph: Graph,
    llm_fn: Callable[[str, str], str] | None = None,
    llm_batch_fn: Callable[[list[dict]], list[dict]] | None = None,
    max_candidates: int = 20,
) -> list[tuple[str, str, float, str]]:
    """Suggest new cross-file edges based on content overlap.

    Finds pairs of nodes from different files that might be related.
    If ``llm_fn`` is provided, asks LLM to confirm and score the connection.
    Otherwise uses a simple word-overlap score.
    """
    if max_candidates <= 0:
        return []

    node_items = list(graph._nodes.items())
    scored_candidates: list[tuple[str, str, float]] = []

    for left_index, (source_id, source_node) in enumerate(node_items):
        source_file = _node_file(source_node)
        if not source_file:
            continue
        source_tokens = _tokenize(source_node.content)
        if not source_tokens:
            continue

        for target_id, target_node in node_items[left_index + 1 :]:
            target_file = _node_file(target_node)
            if target_file is None or source_file == target_file:
                continue

            target_tokens = _tokenize(target_node.content)
            if not target_tokens:
                continue

            shared = source_tokens & target_tokens
            if not shared:
                continue
            union = source_tokens | target_tokens
            if not union:
                continue
            overlap = len(shared) / len(union)
            scored_candidates.append((source_id, target_id, overlap))

    scored_candidates.sort(key=lambda item: (item[2], item[0], item[1]), reverse=True)
    scored_candidates = scored_candidates[:max_candidates]

    if llm_fn is None and llm_batch_fn is None:
        suggested: list[tuple[str, str, float, str]] = []
        for source_id, target_id, overlap in scored_candidates:
            suggested.append((source_id, target_id, overlap, f"word overlap score: {overlap:.4f}"))
        return suggested

    requests: list[dict] = []
    for idx, (source_id, target_id, overlap) in enumerate(scored_candidates):
        source_node = graph.get_node(source_id)
        target_node = graph.get_node(target_id)
        source_file = _node_file(source_node) or "unknown"
        target_file = _node_file(target_node) or "unknown"
        if source_node is None or target_node is None:
            continue

        system = (
            "Given two document chunks from different files, decide if they should be connected. "
            'Return JSON: {"should_connect": true/false, "weight": 0.0-1.0, "reason": "brief"}'
        )
        user = (
            f"Chunk A (from {source_file}): {source_node.content}\n\n"
            f"Chunk B (from {target_file}): {target_node.content}"
        )
        requests.append({"id": f"req_{idx}", "system": system, "user": user})

    responses = batch_or_single(requests=requests, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    response_by_id = {str(item["id"]): str(item.get("response", "")) for item in responses}

    suggested: list[tuple[str, str, float, str]] = []
    for idx, (source_id, target_id, overlap) in enumerate(scored_candidates):
        source_node = graph.get_node(source_id)
        target_node = graph.get_node(target_id)
        if source_node is None or target_node is None:
            continue
        response = response_by_id.get(f"req_{idx}", "")
        if not response:
            continue
        try:
            payload = _extract_json(response)
            if payload is None:
                continue
            if not bool(payload.get("should_connect", False)):
                continue
            reason = str(payload.get("reason", "") or "")
            weight = _safe_float(payload.get("weight"), overlap)
            weight = max(0.0, min(1.0, weight))
            suggested.append((source_id, target_id, weight, reason))
        except (Exception, SystemExit):
            continue

    return suggested


def apply_connections(graph: Graph, connections: list[tuple[str, str, float, str]]) -> int:
    """apply connections."""
    added = 0
    seen: set[tuple[str, str]] = set()
    for source_id, target_id, weight, reason in connections:
        if source_id == target_id:
            continue
        if (source_id, target_id) in seen:
            continue
        if graph.get_node(source_id) is None or graph.get_node(target_id) is None:
            continue

        source_node = graph.get_node(source_id)
        target_node = graph.get_node(target_id)
        source_file = _node_file(source_node) or None
        target_file = _node_file(target_node) or None
        if source_file is None or target_file is None or source_file == target_file:
            continue

        existing = graph._edges.get(source_id, {}).get(target_id)
        graph.add_edge(
            Edge(
                source=source_id,
                target=target_id,
                weight=weight,
                kind="cross_file",
                metadata={"reason": reason, "kind": "cross_file", "source": "connect"},
            )
        )
        seen.add((source_id, target_id))
        if existing is None:
            added += 1

    return added
