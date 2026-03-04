from __future__ import annotations

import json

from crabpath.decay import DecayConfig
from crabpath.graph import Edge, Graph, Node
from crabpath.index import VectorIndex
from crabpath.maintain import MaintenanceReport, prune_edges, prune_orphan_nodes, run_maintenance
from crabpath.cli import main
from crabpath.store import save_state


def _write_state(path, graph: Graph, index_payload: dict[str, list[float]] | None = None) -> None:
    if index_payload is None:
        index_payload = {}
        for idx, node in enumerate(graph.nodes()):
            index_payload[node.id] = [float(idx), 1.0]

    index = VectorIndex()
    for node_id, vector in index_payload.items():
        index.upsert(node_id, vector)
    save_state(graph=graph, index=index, path=str(path), meta={"embedder_name": "hash-v1", "embedder_dim": 2})


def test_run_maintenance_default_tasks_on_small_graph(tmp_path) -> None:
    """test run maintenance default tasks on a small graph."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "c", 0.005))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    report = run_maintenance(
        state_path=str(state_path),
        tasks=None,
        prune_below=0.01,
        decay_config=DecayConfig(half_life=1, min_weight=0.0),
    )

    assert report.tasks_run == ["health", "decay", "prune", "merge"]
    assert report.edges_before == 2
    assert report.edges_after == 1
    assert report.pruned_edges >= 1
    assert "nodes" in report.health_before
    assert "nodes" in report.health_after


def test_dry_run_does_not_modify_state(tmp_path) -> None:
    """test dry run does not modify graph state."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.2))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)
    before = json.loads(state_path.read_text(encoding="utf-8"))

    report = run_maintenance(
        state_path=str(state_path),
        tasks=["decay", "prune", "merge"],
        dry_run=True,
        prune_below=0.01,
        decay_config=DecayConfig(half_life=1, min_weight=0.0),
    )

    after = json.loads(state_path.read_text(encoding="utf-8"))
    assert report.tasks_run == ["decay", "prune", "merge"]
    assert before == after
    assert "dry_run=True; no state write performed" in report.notes


def test_prune_edges_removes_low_weight_edges() -> None:
    """test prune edges removes low-weight edges."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_edge(Edge("a", "b", 0.2))
    graph.add_edge(Edge("b", "a", 0.005))

    removed = prune_edges(graph, below=0.01)
    assert removed == 1
    assert graph.edge_count() == 1
    assert graph._edges["a"]["b"].weight == 0.2


def test_prune_orphan_nodes_removes_disconnected_nodes() -> None:
    """test prune orphan nodes removes disconnected nodes."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_edge(Edge("a", "b", 0.2))

    removed = prune_orphan_nodes(graph)
    assert removed == 1
    assert graph.get_node("c") is None


def test_prune_skips_constitutional_nodes() -> None:
    """test prune skips constitutional and canonical nodes."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"authority": "constitutional"}))
    graph.add_node(Node("b", "B", metadata={"authority": "canonical"}))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))

    removed = prune_orphan_nodes(graph)
    assert removed == 2
    assert graph.get_node("a") is not None
    assert graph.get_node("b") is not None
    assert graph.get_node("c") is None
    assert graph.get_node("d") is None


def test_prune_skips_constitutional_edges() -> None:
    """test prune skips constitutional edges."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"authority": "constitutional"}))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C", metadata={"authority": "constitutional"}))
    graph.add_node(Node("d", "D"))

    graph.add_edge(Edge("a", "b", 0.005))
    graph.add_edge(Edge("b", "a", 0.005))
    graph.add_edge(Edge("c", "d", 0.005))
    graph.add_edge(Edge("d", "c", 0.005))
    graph.add_edge(Edge("b", "d", 0.005))

    removed = prune_edges(graph, below=0.01)
    assert removed == 1
    assert graph.edge_count() == 4
    assert ("a" in graph._edges and "b" in graph._edges["a"])
    assert ("c" in graph._edges and "d" in graph._edges["c"])


def test_merge_skips_constitutional_pairs(tmp_path) -> None:
    """test merge task skips constitutional node pairs."""
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"authority": "constitutional"}))
    graph.add_node(Node("b", "beta", metadata={"authority": "constitutional"}))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "a", 0.95))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    before = json.loads(state_path.read_text(encoding="utf-8"))
    before_nodes = len(before["graph"]["nodes"])
    report = run_maintenance(
        state_path=str(state_path),
        tasks=["merge"],
        max_merges=1,
    )

    after = json.loads(state_path.read_text(encoding="utf-8"))
    after_nodes = len(after["graph"]["nodes"])
    assert report.merges_proposed == 0
    assert report.merges_applied == 0
    assert after_nodes == before_nodes


def test_decay_skips_constitutional_edges(tmp_path) -> None:
    """test decay skips edges from constitutional sources."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"authority": "constitutional"}))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))
    graph.add_edge(Edge("a", "b", 1.0))
    graph.add_edge(Edge("c", "d", 1.0))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    run_maintenance(
        state_path=str(state_path),
        tasks=["decay"],
        decay_config=DecayConfig(half_life=1, min_weight=0.0),
    )

    payload = json.loads(state_path.read_text(encoding="utf-8"))
    edges = payload["graph"]["edges"]
    edge_ab = next(edge["weight"] for edge in edges if edge["source"] == "a" and edge["target"] == "b")
    edge_cd = next(edge["weight"] for edge in edges if edge["source"] == "c" and edge["target"] == "d")
    assert edge_ab == 1.0
    assert edge_cd == 0.5


def test_canonical_nodes_get_slower_decay(tmp_path) -> None:
    """test canonical nodes decay more slowly."""
    graph = Graph()
    graph.add_node(Node("a", "A", metadata={"authority": "canonical"}))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))
    graph.add_edge(Edge("a", "b", 0.8))
    graph.add_edge(Edge("c", "d", 0.8))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    run_maintenance(
        state_path=str(state_path),
        tasks=["decay"],
        decay_config=DecayConfig(half_life=1, min_weight=0.0),
    )

    payload = json.loads(state_path.read_text(encoding="utf-8"))
    edges = payload["graph"]["edges"]
    canonical_edge = next(edge["weight"] for edge in edges if edge["source"] == "a" and edge["target"] == "b")
    overlay_edge = next(edge["weight"] for edge in edges if edge["source"] == "c" and edge["target"] == "d")
    assert canonical_edge > overlay_edge


def test_anchor_cli_sets_authority(tmp_path) -> None:
    """test anchor cli sets and removes node authority."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    main(["anchor", "--state", str(state_path), "--node-id", "a", "--authority", "constitutional", "--json"])
    set_payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert set_payload["graph"]["nodes"][0]["metadata"]["authority"] == "constitutional"

    main(["anchor", "--state", str(state_path), "--node-id", "a", "--remove", "--json"])
    removed_payload = json.loads(state_path.read_text(encoding="utf-8"))
    assert "authority" not in removed_payload["graph"]["nodes"][0]["metadata"]


def test_merge_task_reduces_node_count(tmp_path) -> None:
    """test merge task reduces node count."""
    graph = Graph()
    graph.add_node(Node("a", "alpha"))
    graph.add_node(Node("b", "beta"))
    graph.add_node(Node("c", "gamma"))
    graph.add_edge(Edge("a", "b", 0.95))
    graph.add_edge(Edge("b", "a", 0.95))
    graph.add_edge(Edge("b", "c", 0.1))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    before = json.loads(state_path.read_text(encoding="utf-8"))
    before_nodes = len(before["graph"]["nodes"])
    report = run_maintenance(
        state_path=str(state_path),
        tasks=["merge"],
        max_merges=1,
    )

    after = json.loads(state_path.read_text(encoding="utf-8"))
    after_nodes = len(after["graph"]["nodes"])
    assert report.merges_proposed >= 1
    assert report.merges_applied == 1
    assert after_nodes < before_nodes


def test_maintenance_report_tracks_before_and_after_counts(tmp_path) -> None:
    """test maintenance report tracks before and after counts."""
    graph = Graph()
    graph.add_node(Node("a", "A"))
    graph.add_node(Node("b", "B"))
    graph.add_node(Node("c", "C"))
    graph.add_node(Node("d", "D"))
    graph.add_edge(Edge("a", "b", 0.2))
    graph.add_edge(Edge("b", "c", 0.005))
    graph.add_edge(Edge("c", "a", 0.2))

    state_path = tmp_path / "state.json"
    _write_state(state_path, graph)

    report = run_maintenance(
        state_path=str(state_path),
        tasks=["decay", "prune"],
        prune_below=0.01,
        decay_config=DecayConfig(half_life=1, min_weight=0.0),
    )

    assert report.edges_before == 3
    assert report.edges_after == 2
    assert "dormant_pct" in report.health_before
    assert "dormant_pct" in report.health_after
    assert report.pruned_edges >= 1
    assert isinstance(report.__dict__, dict)
