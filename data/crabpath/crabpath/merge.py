"""Node merge helpers for optional LLM-backed maintenance."""

from __future__ import annotations

import hashlib
from collections.abc import Callable

from .graph import Edge, Graph, Node
from ._batch import batch_or_single
from ._util import _extract_json, _first_line


def _candidate_pairs(graph: Graph, max_content_chars: int = 1200) -> list[tuple[str, str]]:
    """ candidate pairs."""
    pairs: list[tuple[str, str]] = []
    for source_id in graph._nodes:
        source_node = graph.get_node(source_id)
        if source_node is None or len(source_node.content) > max_content_chars:
            continue

        for target_id, edge in graph._edges.get(source_id, {}).items():
            target_node = graph.get_node(target_id)
            if target_node is None:
                continue
            if len(target_node.content) > max_content_chars:
                continue
            if target_id <= source_id:
                continue

            reverse = graph._edges.get(target_id, {}).get(source_id)
            if reverse is None:
                continue
            if min(edge.weight, reverse.weight) < 0.8:
                continue
            pairs.append((source_id, target_id))
    return pairs

def suggest_merges(
    graph: Graph,
    llm_fn: Callable[[str, str], str] | None = None,
    llm_batch_fn: Callable[[list[dict]], list[dict]] | None = None,
) -> list[tuple[str, str]]:
    """Find pairs of small nodes that always co-fire and suggest merging.

    If llm_fn is provided, ask LLM to confirm merge makes sense.
    """
    candidate_pairs = _candidate_pairs(graph)
    confirmed: list[tuple[str, str]] = []
    if llm_fn is None and llm_batch_fn is None:
        return candidate_pairs.copy()

    requests: list[dict] = []
    request_index_by_pair: dict[tuple[str, str], int] = {}
    for pair_index, (source_id, target_id) in enumerate(candidate_pairs):
        source_node = graph.get_node(source_id)
        target_node = graph.get_node(target_id)
        if source_node is None or target_node is None:
            continue

        requests.append(
            {
                "id": f"req_{pair_index}",
                "system": (
                    "You are a memory graph organizer. Given two chunks that always co-activate, "
                    'decide if they should be merged into one node. Return JSON: {"should_merge": true/false, "reason": "..."}'
                ),
                "user": (
                    f"Node A ({source_id}):\n{source_node.content}\n\n"
                    f"Node B ({target_id}):\n{target_node.content}"
                ),
            }
        )
        request_index_by_pair[(source_id, target_id)] = pair_index

    responses = batch_or_single(requests=requests, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    response_by_id = {str(item["id"]): str(item.get("response", "")) for item in responses}

    for source_id, target_id in candidate_pairs:
        pair_index = request_index_by_pair.get((source_id, target_id))
        if pair_index is None:
            continue
        response = response_by_id.get(f"req_{pair_index}", "")
        if not response:
            continue
        try:
            payload = _extract_json(response)
            if payload is None:
                continue
            if bool(payload.get("should_merge", False)):
                confirmed.append((source_id, target_id))
        except (Exception, SystemExit):
            continue

    return confirmed


def _unique_merge_id(graph: Graph, node_a: str, node_b: str) -> str:
    """ unique merge id."""
    base = hashlib.sha1(f"{node_a}|{node_b}".encode("utf-8")).hexdigest()[:12]
    candidate = f"merged:{base}"
    suffix = 0
    while graph.get_node(candidate) is not None:
        suffix += 1
        candidate = f"merged:{base}:{suffix}"
    return candidate


def apply_merge(graph: Graph, node_a: str, node_b: str) -> str:
    """Merge two nodes into one.

    Returns the new node ID.
    """
    first = graph.get_node(node_a)
    second = graph.get_node(node_b)
    if first is None and second is None:
        return node_a
    if first is None:
        return node_b
    if second is None:
        return node_a

    merged_id = _unique_merge_id(graph, node_a, node_b)
    merged_content = f"{first.content}\n\n{second.content}"
    merged_summary = _first_line(merged_content)
    merged_metadata = {
        "merged_from": [node_a, node_b],
        "source": "llm-merge",
    }

    rewired: dict[tuple[str, str], Edge] = {}
    for source_id, target_map in list(graph._edges.items()):
        for target_id, edge in target_map.items():
            new_source = merged_id if source_id in {node_a, node_b} else source_id
            new_target = merged_id if target_id in {node_a, node_b} else target_id
            if new_source == new_target:
                continue
            key = (new_source, new_target)
            existing = rewired.get(key)
            if existing is None or edge.weight > existing.weight:
                rewired[key] = Edge(
                    source=new_source,
                    target=new_target,
                    weight=edge.weight,
                    kind=edge.kind,
                    metadata=dict(edge.metadata),
                )

    graph.remove_node(node_a)
    graph.remove_node(node_b)
    graph.add_node(Node(id=merged_id, content=merged_content, summary=merged_summary, metadata=merged_metadata))
    for edge in rewired.values():
        graph.add_edge(edge)

    return merged_id
