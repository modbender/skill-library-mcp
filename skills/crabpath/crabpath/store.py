"""State persistence helpers for CrabPath."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .graph import Edge, Graph, Node
from .hasher import HashEmbedder
from .index import VectorIndex


class ManagedState:
    """Context manager that keeps graph and index state in sync."""

    def __init__(self, path, auto_save_every: int = 10):
        """  init  ."""
        self.graph, self.index, self.meta = load_state(path)
        self.path = path
        self.ops = 0
        self.auto_save_every = auto_save_every

    def save(self) -> None:
        """save."""
        save_state(graph=self.graph, index=self.index, path=self.path, meta=self.meta)

    def tick(self) -> None:
        """tick."""
        self.ops += 1
        if self.auto_save_every <= 0:
            return
        if self.ops % self.auto_save_every == 0:
            self.save()

    def __enter__(self):
        """  enter  ."""
        return self

    def __exit__(self, *args):
        """  exit  ."""
        self.save()


def save_state(
    graph: Graph,
    index: VectorIndex,
    path: str,
    *,
    embedder_name: str | None = None,
    embedder_dim: int | None = None,
    meta: dict[str, object] | None = None,
) -> None:
    """Save graph and index together to one JSON file."""
    state_path = Path(path)
    existing_meta: dict[str, object] = {}
    if state_path.exists():
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            raw_meta = payload.get("meta")
            if isinstance(raw_meta, dict):
                existing_meta = raw_meta

    metadata = dict(existing_meta)
    if meta is not None:
        metadata.update(meta)

    # Resolve embedder: explicit args > meta dict > hash-v1 default
    if embedder_name is None:
        embedder_name = metadata.get("embedder_name")
    if embedder_name is None:
        embedder_name = "hash-v1"

    if embedder_dim is None:
        dim_from_meta = metadata.get("embedder_dim")
        embedder_dim = dim_from_meta if isinstance(dim_from_meta, int) else HashEmbedder().dim

    existing_embedder = metadata.get("embedder_name")
    if (
        state_path.exists()
        and embedder_dim is not None
        and index._vectors
        and existing_embedder != "hash-v1"
    ):
        for node_id, vector in index._vectors.items():
            if len(vector) != embedder_dim:
                raise ValueError(
                    f"index vector dimension mismatch for node {node_id}: "
                    f"expected={embedder_dim}, actual={len(vector)}"
                )

    metadata.setdefault("schema_version", 1)
    metadata.setdefault("created_at", datetime.now(timezone.utc).isoformat())
    metadata["node_count"] = graph.node_count()
    metadata["embedder_name"] = embedder_name
    metadata["embedder_dim"] = embedder_dim

    payload = {
        "graph": {
            "nodes": [
                {
                    "id": node.id,
                    "content": node.content,
                    "summary": node.summary,
                    "metadata": node.metadata,
                }
                for node in graph.nodes()
            ],
            "edges": [
                {
                    "source": edge.source,
                    "target": edge.target,
                    "weight": edge.weight,
                    "kind": edge.kind,
                    "metadata": edge.metadata,
                }
                for source_edges in graph._edges.values()
                for edge in source_edges.values()
            ],
        },
        "index": index._vectors,
        "meta": metadata,
    }
    Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_state(path: str) -> tuple[Graph, VectorIndex, dict[str, object]]:
    """load state."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    graph = Graph()
    if not isinstance(payload, dict):
        raise SystemExit("state payload must be an object")
    graph_payload = payload.get("graph", payload)
    for node_data in graph_payload.get("nodes", []):
        graph.add_node(
            Node(
                id=node_data["id"],
                content=node_data["content"],
                summary=node_data.get("summary", ""),
                metadata=node_data.get("metadata", {}),
            )
        )

    for edge_data in graph_payload.get("edges", []):
        graph.add_edge(
            Edge(
                source=edge_data["source"],
                target=edge_data["target"],
                weight=edge_data.get("weight", 0.5),
                kind=edge_data.get("kind", "sibling"),
                metadata=edge_data.get("metadata", {}),
            )
        )

    index = VectorIndex()
    index_payload = payload.get("index", {})
    if "index" in payload and not isinstance(index_payload, dict):
        raise SystemExit("index payload must be an object")
    if isinstance(index_payload, dict):
        for node_id, vector in index_payload.items():
            if not isinstance(vector, list):
                raise SystemExit("index payload vectors must be arrays")
            index.upsert(node_id, vector)
    meta = payload.get("meta", {}) if isinstance(payload.get("meta", {}), dict) else {}
    return graph, index, meta
