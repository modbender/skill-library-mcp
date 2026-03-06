from __future__ import annotations

from pathlib import Path

import pytest

from crabpath import Edge, Graph, ManagedState, Node, VectorIndex, load_state, save_state


def test_save_load_state_with_meta(tmp_path: Path) -> None:
    """test save load state with meta."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "beta", metadata={"file": "b.md"}))
    graph.add_edge(Edge("a", "b", 0.5, kind="sibling", metadata={"source": "test"}))

    index = VectorIndex()
    index.upsert("a", [1.0, 0.0])
    index.upsert("b", [0.0, 1.0])

    state_path = tmp_path / "state.json"
    save_state(
        graph=graph,
        index=index,
        path=state_path,
        embedder_name="hash-v1",
        embedder_dim=1024,
    )

    loaded_graph, loaded_index, meta = load_state(str(state_path))
    assert loaded_graph.get_node("a").content == "alpha"
    assert loaded_index._vectors["a"] == [1.0, 0.0]
    assert meta["embedder_name"] == "hash-v1"
    assert meta["embedder_dim"] == 1024
    assert meta["schema_version"] == 1
    assert meta["node_count"] == 2
    assert "created_at" in meta


def test_save_state_preserves_custom_metadata(tmp_path: Path) -> None:
    """test save state preserves custom metadata."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index = VectorIndex()
    index.upsert("a", [1.0, 0.0])

    state_path = tmp_path / "state.json"
    save_state(
        graph=graph,
        index=index,
        path=state_path,
        meta={"last_replayed_ts": 123.45, "custom": "value"},
    )

    _, _, meta = load_state(str(state_path))
    assert meta["last_replayed_ts"] == 123.45
    assert meta["custom"] == "value"
    assert meta["embedder_name"] == "hash-v1"


def test_save_state_preserves_existing_embedder_meta(tmp_path: Path) -> None:
    """test save state preserves embedder metadata from existing state when no override is provided."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "beta", metadata={"file": "b.md"}))

    index = VectorIndex()
    index.upsert("a", [1.0] * 1536)
    index.upsert("b", [0.0] * 1536)

    state_path = tmp_path / "state.json"
    save_state(
        graph=graph,
        index=index,
        path=state_path,
        embedder_name="openai-text-embedding-3-small",
        embedder_dim=1536,
    )

    graph2 = Graph()
    graph2.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    graph2.add_node(Node("b", "beta", metadata={"file": "b.md"}))
    graph2.add_node(Node("c", "gamma", metadata={"file": "c.md"}))

    index2 = VectorIndex()
    index2.upsert("a", [0.5] * 1536)
    index2.upsert("b", [0.5] * 1536)
    index2.upsert("c", [0.5] * 1536)

    save_state(graph=graph2, index=index2, path=state_path)

    _, _, meta = load_state(str(state_path))
    assert meta["embedder_name"] == "openai-text-embedding-3-small"
    assert meta["embedder_dim"] == 1536


def test_save_state_raises_on_dimension_mismatch(tmp_path: Path) -> None:
    """test save state raises when vector dimension mismatches embedded metadata."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index = VectorIndex()
    index.upsert("a", [1.0] * 1024)

    state_path = tmp_path / "state.json"
    save_state(graph=graph, index=index, path=state_path, embedder_name="openai-text-embedding-3-small", embedder_dim=1024)

    mismatched_index = VectorIndex()
    mismatched_index.upsert("a", [0.5] * 1536)
    with pytest.raises(ValueError, match=r"dimension mismatch"):
        save_state(graph=graph, index=mismatched_index, path=state_path)


def test_save_state_explicit_meta_overrides(tmp_path: Path) -> None:
    """test save state explicit meta overrides existing metadata."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index = VectorIndex()
    index.upsert("a", [1.0] * 1024)

    state_path = tmp_path / "state.json"
    save_state(graph=graph, index=index, path=state_path, embedder_name="openai-text-embedding-3-small", embedder_dim=1536)

    override = {
        "embedder_name": "hash-v1",
        "embedder_dim": 2,
        "custom_note": "override",
    }
    override_index = VectorIndex()
    override_index.upsert("a", [1.0, 2.0])
    save_state(graph=graph, index=override_index, path=state_path, meta=override)

    _, _, meta = load_state(str(state_path))
    assert meta["embedder_name"] == "hash-v1"
    assert meta["embedder_dim"] == 2
    assert meta["custom_note"] == "override"


def test_managed_state_context_manager_autosaves_and_context_enter_exit(tmp_path: Path) -> None:
    """test managed state context manager autosaves and context enter exit."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index = VectorIndex()
    index.upsert("a", [1.0, 0.0])
    state_path = tmp_path / "state.json"
    save_state(graph=graph, index=index, path=state_path)

    with ManagedState(state_path, auto_save_every=1) as state:
        state.graph.add_node(Node("b", "beta", metadata={"file": "b.md"}))
        state.index.upsert("b", [0.0, 1.0])
        state.tick()

    reloaded_graph, _, _ = load_state(str(state_path))
    assert reloaded_graph.get_node("b") is not None
