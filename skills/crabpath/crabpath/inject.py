"""Runtime graph injection helpers for live learning updates."""

from __future__ import annotations

from collections.abc import Callable

from ._util import _first_line
from .graph import Edge, Graph, Node
from .index import VectorIndex


def _resolve_vector(
    content: str,
    vector: list[float] | None,
    embed_fn: Callable[[str], list[float]] | None,
) -> list[float]:
    """Resolve a vector from an explicit list or embedding callback.

    Exactly one of ``vector`` or ``embed_fn`` is required.
    """
    if vector is not None:
        return list(vector)
    if embed_fn is None:
        raise ValueError("either vector or embed_fn must be provided")
    return list(embed_fn(content))


def _safe_float(value: object) -> float:
    """Cast score values to float without raising.

    Falls back to Python's ``float`` conversion semantics for non-numeric inputs.
    """
    return float(value)


def _connect_to_existing(
    graph: Graph,
    index: VectorIndex,
    source_id: str,
    vector: list[float],
    *,
    connect_top_k: int,
    connect_min_sim: float,
) -> list[str]:
    """Connect the injected node to similar existing nodes in both directions.

    Only nodes above ``connect_min_sim`` are linked. Duplicate targets are skipped.
    """
    if connect_top_k <= 0:
        return []

    connected_to: list[str] = []
    for candidate_id, score in index.search(vector, top_k=connect_top_k + 1):
        if candidate_id == source_id:
            continue
        if candidate_id in connected_to:
            continue
        if score < connect_min_sim:
            continue
        if graph.get_node(candidate_id) is None:
            continue

        weight = max(0.0, min(1.0, _safe_float(score)))
        edge_metadata = {"source": "inject", "score": weight}
        graph.add_edge(
            Edge(
                source=source_id,
                target=candidate_id,
                weight=weight,
                kind="cross_file",
                metadata=edge_metadata,
            )
        )
        graph.add_edge(
            Edge(
                source=candidate_id,
                target=source_id,
                weight=weight,
                kind="cross_file",
                metadata=edge_metadata,
            )
        )
        connected_to.append(candidate_id)

    return connected_to


def _apply_inhibitory_edges(
    graph: Graph,
    source_id: str,
    targets: list[str],
    *,
    inhibition_strength: float,
    inhibition_lr: float,
) -> int:
    """Create or retune inhibitory edges from a correction source node.

    Returns the number of newly created inhibitory edges.
    """
    if not targets:
        return 0

    inhibition_lr = max(0.0, inhibition_lr)
    created = 0
    for target_id in targets:
        if graph.get_node(target_id) is None or source_id == target_id:
            continue

        existing = graph._edges.get(source_id, {}).get(target_id)
        existing_kind = existing.kind if existing is not None else None
        new_weight = (
            inhibition_strength
            if existing is None
            else existing.weight + (inhibition_strength - existing.weight) * inhibition_lr
        )
        new_weight = max(-1.0, min(0.0, float(new_weight)))

        if existing is None:
            graph.add_edge(
                Edge(
                    source=source_id,
                    target=target_id,
                    weight=new_weight,
                    kind="inhibitory",
                    metadata={"source": "inject", "type": "correction"},
                )
            )
            created += 1
        else:
            existing.weight = new_weight
            existing.kind = "inhibitory"
            existing.metadata.update({"source": "inject", "type": "correction"})
            graph._edges[source_id][target_id] = existing
            if existing_kind != "inhibitory":
                created += 1

    return created


def inject_node(
    graph: Graph,
    index: VectorIndex,
    node_id: str,
    content: str,
    *,
    summary: str = "",
    metadata: dict | None = None,
    vector: list[float] | None = None,
    embed_fn: Callable[[str], list[float]] | None = None,
    connect_top_k: int = 3,
    connect_min_sim: float = 0.3,
) -> dict:
    """Inject a single node into an active graph and index.

    - If ``vector`` is provided, it is used directly.
    - Otherwise ``embed_fn`` must produce an embedding.
    - The node is connected bidirectionally to up to ``connect_top_k`` similar nodes.

    Returns:
        ``{"node_id": str, "edges_added": int, "connected_to": list[str]}``
    """
    if graph.get_node(node_id) is not None:
        return {"node_id": node_id, "edges_added": 0, "connected_to": []}

    node_vector = _resolve_vector(content=content, vector=vector, embed_fn=embed_fn)

    # Validate dimension matches existing index
    if index._vectors:
        existing_dim = len(next(iter(index._vectors.values())))
        if len(node_vector) != existing_dim:
            raise ValueError(
                f"Vector dimension mismatch: injected {len(node_vector)} vs index {existing_dim}. "
                f"Use an embed_fn that produces {existing_dim}-dim vectors."
            )

    graph.add_node(
        Node(
            node_id,
            content=content,
            summary=summary or _first_line(content),
            metadata=dict(metadata or {}),
        )
    )
    index.upsert(node_id, node_vector)

    connected_to = _connect_to_existing(
        graph=graph,
        index=index,
        source_id=node_id,
        vector=node_vector,
        connect_top_k=connect_top_k,
        connect_min_sim=connect_min_sim,
    )

    return {
        "node_id": node_id,
        "edges_added": len(connected_to) * 2,
        "connected_to": connected_to,
    }


def inject_correction(
    graph: Graph,
    index: VectorIndex,
    node_id: str,
    content: str,
    *,
    summary: str = "",
    metadata: dict | None = None,
    vector: list[float] | None = None,
    embed_fn: Callable[[str], list[float]] | None = None,
    connect_top_k: int = 3,
    connect_min_sim: float = 0.3,
    inhibition_strength: float = -0.5,
    inhibition_lr: float = 0.08,
) -> dict:
    """Inject a correction node and create inhibitory follow-up edges.

    Behaves like :func:`inject_node`, then adds negative edges from the injected
    node to each newly connected neighbor to actively suppress that path.

    Returns:
        ``{"node_id": str, "edges_added": int, "connected_to": list[str], "inhibitory_edges_created": int}``
    """
    correction_metadata = dict(metadata or {})
    correction_metadata.setdefault("type", "CORRECTION")

    result = inject_node(
        graph=graph,
        index=index,
        node_id=node_id,
        content=content,
        summary=summary,
        metadata=correction_metadata,
        vector=vector,
        embed_fn=embed_fn,
        connect_top_k=connect_top_k,
        connect_min_sim=connect_min_sim,
    )

    if result["edges_added"] == 0 and not result["connected_to"]:
        result["inhibitory_edges_created"] = 0
        return result

    inhibitory_edges_created = _apply_inhibitory_edges(
        graph=graph,
        source_id=node_id,
        targets=result["connected_to"],
        inhibition_strength=inhibition_strength,
        inhibition_lr=inhibition_lr,
    )
    result["inhibitory_edges_created"] = inhibitory_edges_created
    return result


def inject_batch(
    graph: Graph,
    index: VectorIndex,
    nodes: list[dict],
    *,
    vectors: dict[str, list[float]] | None = None,
    embed_fn: Callable[[str], list[float]] | None = None,
    embed_batch_fn: Callable[[list[tuple[str, str]]], dict[str, list[float]]] | None = None,
    connect_top_k: int = 3,
    connect_min_sim: float = 0.3,
    inhibition_strength: float = -0.5,
) -> dict:
    """Inject multiple nodes from a normalized input payload.

    Supports mixed node kinds through ``item["type"]``:
    when type is ``CORRECTION``, inhibitory edges are added after insertion.

    Returns:
        ``{"injected": int, "edges_added": int, "inhibitory": int, "skipped": int}``
    """
    if vectors is None:
        vectors = {}
    else:
        vectors = dict(vectors)

    missing: list[tuple[str, str]] = []
    for item in nodes:
        if not isinstance(item, dict):
            continue

        node_id = item.get("id")
        content = item.get("content")
        if not isinstance(node_id, str) or not node_id:
            continue
        if node_id in vectors:
            continue
        if graph.get_node(node_id) is not None:
            continue
        if not isinstance(content, str) or not content:
            continue
        missing.append((node_id, content))

    if missing and embed_fn is None and embed_batch_fn is None:
        raise ValueError("either vectors, embed_batch_fn, or embed_fn must be provided")

    if embed_batch_fn is not None and missing:
        for key, value in embed_batch_fn(missing).items():
            if isinstance(value, list):
                vectors[key] = value

    if embed_fn is not None and missing:
        for node_id, content in missing:
            if node_id in vectors:
                continue
            vectors[node_id] = list(embed_fn(content))

    injected = 0
    edges_added = 0
    inhibitory = 0
    skipped = 0

    for item in nodes:
        if not isinstance(item, dict):
            skipped += 1
            continue

        node_id = item.get("id")
        content = item.get("content")
        if not isinstance(node_id, str) or not node_id:
            skipped += 1
            continue
        if not isinstance(content, str) or not content:
            skipped += 1
            continue
        if graph.get_node(node_id) is not None:
            skipped += 1
            continue
        if node_id not in vectors:
            raise ValueError(f"missing vector for node id {node_id}")

        node_metadata = item.get("metadata")
        if not isinstance(node_metadata, dict):
            node_metadata = None

        node_summary = item.get("summary")
        if not isinstance(node_summary, str):
            node_summary = ""

        node_type = str(item.get("type", "")).upper()
        if node_type == "CORRECTION":
            result = inject_correction(
                graph=graph,
                index=index,
                node_id=node_id,
                content=content,
                summary=node_summary,
                metadata=node_metadata,
                vector=vectors[node_id],
                embed_fn=None,
                connect_top_k=connect_top_k,
                connect_min_sim=connect_min_sim,
                inhibition_strength=inhibition_strength,
            )
            inhibitory += int(result.get("inhibitory_edges_created", 0))
        else:
            result = inject_node(
                graph=graph,
                index=index,
                node_id=node_id,
                content=content,
                summary=node_summary,
                metadata=node_metadata,
                vector=vectors[node_id],
                embed_fn=None,
                connect_top_k=connect_top_k,
                connect_min_sim=connect_min_sim,
            )

        injected += 1
        edges_added += int(result.get("edges_added", 0))

    return {
        "injected": injected,
        "edges_added": edges_added,
        "inhibitory": inhibitory,
        "skipped": skipped,
    }
