from __future__ import annotations

import json
from pathlib import Path

from crabpath import VectorIndex
from crabpath.cli import main
from crabpath.graph import Graph, Node
from crabpath.hasher import default_embed
from crabpath.inject import inject_batch, inject_correction, inject_node


def _write_state(path: Path) -> None:
    """Write a minimal state payload."""
    graph_payload = {
        "nodes": [
            {"id": "a", "content": "alpha", "summary": "", "metadata": {"file": "a.md"}},
            {"id": "b", "content": "beta", "summary": "", "metadata": {"file": "b.md"}},
        ],
        "edges": [
            {"source": "a", "target": "b", "weight": 0.7, "kind": "sibling", "metadata": {}},
            {"source": "b", "target": "a", "weight": 0.4, "kind": "sibling", "metadata": {}},
        ],
    }
    index_payload = {
        "a": default_embed("alpha"),
        "b": default_embed("beta"),
    }
    meta = {"embedder_name": "hash-v1", "embedder_dim": 1024}
    path.write_text(json.dumps({"graph": graph_payload, "index": index_payload, "meta": meta}), encoding="utf-8")


def test_inject_node_basic() -> None:
    """test inject node basic."""
    graph = Graph()
    index = VectorIndex()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "beta", metadata={"file": "b.md"}))
    index.upsert("a", default_embed("alpha"))
    index.upsert("b", default_embed("beta"))

    result = inject_node(
        graph,
        index,
        "learning::42",
        "Always run tests before shipping",
        embed_fn=default_embed,
        connect_top_k=2,
        connect_min_sim=0.0,
    )

    assert result["node_id"] == "learning::42"
    assert result["edges_added"] == 4
    assert set(result["connected_to"]) == {"a", "b"}
    assert graph.get_node("learning::42") is not None
    assert len(graph.outgoing("learning::42")) == 2
    assert any(edge.kind == "cross_file" for _, edge in graph.outgoing("learning::42"))
    assert any(target.id == "learning::42" for target, _ in graph.incoming("a"))


def test_inject_node_with_vector() -> None:
    """test inject node with vector."""
    graph = Graph()
    index = VectorIndex()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index.upsert("a", default_embed("alpha"))

    result = inject_node(
        graph,
        index,
        "learning::43",
        "Never forget to commit",
        embed_fn=default_embed,
        connect_top_k=1,
        connect_min_sim=0.0,
    )

    assert result["connected_to"] == ["a"]
    assert index._vectors["learning::43"] == default_embed("Never forget to commit")


def test_inject_correction_creates_inhibitory() -> None:
    """test inject correction creates inhibitory edges."""
    graph = Graph()
    index = VectorIndex()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    index.upsert("a", default_embed("alpha"))

    result = inject_correction(
        graph,
        index,
        "learning::99",
        "Never do X",
        embed_fn=default_embed,
        inhibition_strength=-0.7,
        connect_top_k=1,
        connect_min_sim=0.0,
    )

    assert result["inhibitory_edges_created"] >= 1
    edge = graph._edges["learning::99"]["a"]
    assert edge.kind == "inhibitory"
    assert edge.weight <= 0.0


def test_inject_batch() -> None:
    """test inject batch."""
    graph = Graph()
    index = VectorIndex()
    graph.add_node(Node("base", "base content", metadata={"file": "base.md"}))
    index.upsert("base", default_embed("base content"))

    result = inject_batch(
        graph=graph,
        index=index,
        nodes=[
            {"id": "learning::1", "content": "Teaching rule one", "type": "TEACHING", "summary": "teach"},
            {"id": "learning::2", "content": "Correction rule two", "type": "CORRECTION", "summary": "correct"},
            {"id": "learning::3", "content": "Plain directive", "type": "DIRECTIVE", "summary": "dir"},
            {"id": "dup", "content": "", "type": "TEACHING"},
            {"id": "learning::1", "content": "Duplicate", "type": "TEACHING", "summary": "duplicate"},
        ],
        vectors={
            "learning::1": default_embed("base content"),
            "learning::2": default_embed("base content"),
            "learning::3": default_embed("base content"),
        },
        connect_top_k=1,
        connect_min_sim=0.0,
    )

    assert result["injected"] == 3
    assert result["skipped"] == 2
    assert result["inhibitory"] >= 1
    assert result["edges_added"] >= 6
    assert graph.get_node("learning::2") is not None


def test_inject_duplicate_skips() -> None:
    """test inject duplicate skips."""
    graph = Graph()
    index = VectorIndex()
    graph.add_node(Node("a", "a", metadata={"file": "a.md"}))
    index.upsert("a", default_embed("a"))

    first = inject_node(
        graph,
        index,
        "learning::dup",
        "first",
        embed_fn=default_embed,
        connect_top_k=1,
        connect_min_sim=0.0,
    )
    second = inject_node(
        graph,
        index,
        "learning::dup",
        "second",
        embed_fn=default_embed,
        connect_top_k=1,
        connect_min_sim=0.0,
    )

    assert first["edges_added"] == 2
    assert second["edges_added"] == 0
    assert second["connected_to"] == []
    assert graph.get_node("learning::dup").content == "first"
    assert index._vectors["learning::dup"] == default_embed("first")


def test_inject_cli(tmp_path) -> None:
    """test inject cli."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    code = main(
        [
            "inject",
            "--state",
            str(state_path),
            "--id",
            "learning::55",
            "--content",
            "Never skip CI for hotfixes",
            "--type",
            "CORRECTION",
            "--json",
            "--connect-min-sim",
            "0.0",
        ]
    )
    assert code == 0
    payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert payload["graph"]["nodes"]
    assert any(node["id"] == "learning::55" for node in payload["graph"]["nodes"])
    assert any(
        edge["source"] == "learning::55" and edge["kind"] == "inhibitory"
        for edge in payload["graph"]["edges"]
    )
