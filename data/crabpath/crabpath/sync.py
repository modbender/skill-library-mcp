"""Incremental workspace sync helpers."""

from __future__ import annotations

import hashlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from collections.abc import Callable

from ._batch import batch_or_single_embed
from .graph import Edge, Graph, Node
from .hasher import default_embed, default_embed_batch
from .journal import log_event
from ._util import _first_line
from .split import split_workspace, _sibling_weight
from .store import load_state, save_state


DEFAULT_AUTHORITY_MAP = {
    "SOUL.md": "constitutional",
    "AGENTS.md": "constitutional",
    "USER.md": "canonical",
    "TOOLS.md": "canonical",
    "MEMORY.md": "canonical",
    "IDENTITY.md": "canonical",
    "HEARTBEAT.md": "canonical",
}


PROTECTED_AUTHORITIES = {"constitutional", "canonical"}


@dataclass
class SyncReport:
    nodes_added: int
    nodes_updated: int
    nodes_removed: int
    nodes_unchanged: int
    embeddings_computed: int
    authority_set: dict[str, int]


def _hash_content(content: str) -> str:
    """Hash node text for change detection."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _split_node_id(node_id: str) -> tuple[str | None, int | None]:
    """Split ``file::chunk`` style node IDs."""
    if "::" not in node_id:
        return None, None
    file_name, chunk_text = node_id.rsplit("::", 1)
    try:
        return file_name, int(chunk_text)
    except ValueError:
        return None, None


def _node_file(node: Node) -> str | None:
    """Resolve source file for a node."""
    file_name, _ = _split_node_id(node.id)
    metadata_file = node.metadata.get("file") if isinstance(node.metadata, dict) else None
    if isinstance(metadata_file, str) and metadata_file:
        return metadata_file
    return file_name


def _is_workspace_node(node: Node) -> bool:
    """Return True for nodes produced by workspace splitting."""
    file_name, _ = _split_node_id(node.id)
    if file_name is None:
        return False
    return isinstance(node.metadata, dict) and file_name == node.metadata.get("file")


def _is_protected(authority: str | None) -> bool:
    """Check if this node should be preserved even if removed from the workspace."""
    return isinstance(authority, str) and authority.lower() in PROTECTED_AUTHORITIES


def _resolve_authority(file_name: str, authority_map: dict[str, str] | None) -> str | None:
    """Look up authority by path basename and exact path."""
    if authority_map is None:
        return None
    if file_name in authority_map:
        value = authority_map[file_name]
        return value
    return authority_map.get(Path(file_name).name)


def _group_by_file(node_ids: set[str] | list[str]) -> dict[str, list[tuple[int, str]]]:
    """Group node IDs by source file and chunk index."""
    grouped: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for node_id in node_ids:
        file_name, chunk_idx = _split_node_id(node_id)
        if file_name is None or chunk_idx is None:
            continue
        grouped[file_name].append((chunk_idx, node_id))
    for file_name, entries in grouped.items():
        entries.sort(key=lambda item: item[0])
    return grouped


def _remove_file_sibling_edges(graph: Graph, file_name: str) -> None:
    """Remove sibling edges between nodes that belong to the same file."""
    for source_id in list(graph._edges):
        source_file, _ = _split_node_id(source_id)
        if source_file != file_name:
            continue
        for edge in list(graph._edges[source_id].values()):
            target_file, _ = _split_node_id(edge.target)
            if edge.kind == "sibling" and target_file == file_name:
                graph.remove_edge(edge.source, edge.target)


def _add_file_sibling_edges(graph: Graph, file_name: str, ordered_node_ids: list[str]) -> None:
    """Add bi-directional sibling edges for ordered file nodes."""
    for offset, (left, right) in enumerate(zip(ordered_node_ids, ordered_node_ids[1:])):
        weight = _sibling_weight(file_name, offset)
        graph.add_edge(Edge(source=left, target=right, weight=weight, kind="sibling"))
        graph.add_edge(Edge(source=right, target=left, weight=weight, kind="sibling"))


def sync_workspace(
    state_path: str,
    workspace_dir: str,
    *,
    embed_fn: Callable[[str], list[float]] | None = None,
    embed_batch_fn: Callable[[list[tuple[str, str]]], dict[str, list[float]]] | None = None,
    journal_path: str | None = None,
    authority_map: dict[str, str] | None = None,
) -> SyncReport:
    """Sync workspace chunks against persisted state and re-embed changed/new nodes."""
    state_path_obj = Path(state_path).expanduser()
    graph, index, meta = load_state(str(state_path_obj))
    _, current_texts = split_workspace(workspace_dir)

    if embed_fn is None and embed_batch_fn is None:
        embed_fn = default_embed
        embed_batch_fn = default_embed_batch

    existing_nodes: dict[str, Node] = {node.id: node for node in graph.nodes()}
    existing_hashes: dict[str, str] = {node_id: _hash_content(node.content) for node_id, node in existing_nodes.items()}
    current_ids = set(current_texts.keys())
    existing_ids = set(existing_nodes.keys())

    added_ids = sorted(current_ids - existing_ids)
    unchanged_ids: list[str] = []
    changed_ids: list[str] = []
    removed_ids: list[str] = []

    for node_id in sorted(current_ids & existing_ids):
        if existing_hashes.get(node_id) != _hash_content(current_texts[node_id]):
            changed_ids.append(node_id)
        else:
            unchanged_ids.append(node_id)

    current_file_ids = _group_by_file(current_ids)

    workspace_nodes: list[tuple[str, Node]] = []
    for node in graph.nodes():
        if not _is_workspace_node(node):
            continue
        workspace_nodes.append((node.id, node))

    affected_files: set[str] = set(current_file_ids.keys())

    for node_id, node in workspace_nodes:
        if node_id in current_ids:
            continue
        authority = node.metadata.get("authority") if isinstance(node.metadata, dict) else None
        if _is_protected(authority):
            continue
        removed_ids.append(node_id)
        file_name = _node_file(node)
        if file_name is not None:
            affected_files.add(file_name)

    for node_id in changed_ids + added_ids:
        file_name, _ = _split_node_id(node_id)
        if file_name is not None:
            affected_files.add(file_name)

    embed_targets = [(node_id, current_texts[node_id]) for node_id in sorted(changed_ids + added_ids)]
    vectors: dict[str, list[float]] = {}
    if embed_targets:
        vectors = batch_or_single_embed(embed_targets, embed_fn=embed_fn, embed_batch_fn=embed_batch_fn)

    if authority_map is None:
        authority_map = DEFAULT_AUTHORITY_MAP
    else:
        authority_map = dict(authority_map)

    authority_set: dict[str, int] = {}
    for node_id in changed_ids + added_ids:
        file_name, chunk_idx = _split_node_id(node_id)
        if file_name is None:
            continue
        content = current_texts[node_id]
        vector = vectors.get(node_id)
        if vector is None:
            raise SystemExit(f"embedding missing for node: {node_id}")

        old_node = existing_nodes.get(node_id)
        metadata: dict[str, Any] = dict(old_node.metadata) if old_node is not None else {}
        metadata["file"] = file_name
        metadata["chunk"] = chunk_idx
        metadata["kind"] = metadata.get("kind", "markdown")
        authority = _resolve_authority(file_name, authority_map)
        if authority is not None:
            metadata["authority"] = authority
            authority_set[authority] = authority_set.get(authority, 0) + 1
        node = Node(
            id=node_id,
            content=content,
            summary=_first_line(content),
            metadata=metadata,
        )
        graph.add_node(node)
        index.upsert(node_id, vector)

    for node_id in removed_ids:
        graph.remove_node(node_id)
        index.remove(node_id)

    for file_name in sorted(affected_files):
        ordered = [node_id for _, node_id in current_file_ids.get(file_name, [])]
        _remove_file_sibling_edges(graph, file_name)
        if ordered:
            _add_file_sibling_edges(graph, file_name, ordered)

    report = SyncReport(
        nodes_added=len(added_ids),
        nodes_updated=len(changed_ids),
        nodes_removed=len(removed_ids),
        nodes_unchanged=len(unchanged_ids),
        embeddings_computed=len(vectors),
        authority_set=authority_set,
    )

    save_state(graph=graph, index=index, path=str(state_path_obj), meta=meta)

    if journal_path is not None:
        log_event(
            {
                "type": "sync",
                "state_path": str(state_path_obj),
                "workspace_dir": str(Path(workspace_dir).expanduser()),
                "nodes_added": report.nodes_added,
                "nodes_updated": report.nodes_updated,
                "nodes_removed": report.nodes_removed,
                "nodes_unchanged": report.nodes_unchanged,
                "embeddings_computed": report.embeddings_computed,
                "authority_set": report.authority_set,
            },
            journal_path=journal_path,
        )

    return report
