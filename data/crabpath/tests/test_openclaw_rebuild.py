from __future__ import annotations

import importlib.util
import json
import types
from pathlib import Path
import sys

from crabpath import Graph, Node, VectorIndex, load_state, save_state


def _load_module(path: Path, name: str):
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))

    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _build_seeded_state(path: Path, *, node_id: str, inject_hash: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    graph = Graph()
    graph.add_node(Node("workspace::1", "workspace note", metadata={"file": "notes.md"}))
    graph.add_node(Node(node_id, "Never answer this", metadata={"source": "learn_correction", "chat_id": "chat-1"}))

    index = VectorIndex()
    index.upsert("workspace::1", [0.1] * 1536)
    index.upsert(node_id, [0.2] * 1536)

    save_state(
        graph=graph,
        index=index,
        path=path,
        embedder_name="openai-text-embedding-3-small",
        embedder_dim=1536,
        meta={"rebuild_test": True},
    )

    log_path = path.parent / "injected_corrections.jsonl"
    log_path.write_text(json.dumps({"content_hash": inject_hash, "node_id": node_id, "chat_id": "chat-1"}) + "\n", encoding="utf-8")


def _health_stub():
    return types.SimpleNamespace(dormant_pct=0.1, habitual_pct=0.2, reflex_pct=0.3, cross_file_edge_pct=0.4, orphan_nodes=0)


def test_rebuild_preserves_injected_corrections_init_agent(tmp_path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.md").write_text("# notes", encoding="utf-8")
    output = tmp_path / "brain"
    state_path = output / "state.json"

    correction_id = "correction::abc123"
    _build_seeded_state(state_path, node_id=correction_id, inject_hash="abc123")

    init_agent_brain = _load_module(Path("examples/openclaw_adapter/init_agent_brain.py"), "oc_init_agent_brain_test")
    sessions = tmp_path / "sessions.jsonl"
    sessions.write_text('{"role":"user","content":"hello"}\\n', encoding="utf-8")

    monkeypatch.setattr(init_agent_brain, "require_api_key", lambda: "test")
    monkeypatch.setattr(init_agent_brain, "batch_or_single_embed", lambda items, embed_batch_fn: {node_id: [0.3] * 1536 for node_id, _ in items})
    monkeypatch.setattr(
        init_agent_brain,
        "replay_queries",
        lambda graph, queries, verbose=False: {"queries_replayed": 0, "edges_reinforced": 0, "cross_file_edges_created": 0, "last_replayed_ts": None},
    )
    monkeypatch.setattr(init_agent_brain, "measure_health", lambda graph: _health_stub())

    init_agent_brain.run(
        workspace=workspace,
        sessions=sessions,
        output=output,
        learning_db=None,
        do_connect_learnings=False,
        preserve_injected=True,
    )

    graph, _, _ = load_state(str(state_path))
    assert graph.get_node(correction_id) is not None


def test_rebuild_all_preserves_injected_corrections(tmp_path, monkeypatch) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "notes.md").write_text("# notes", encoding="utf-8")
    output = tmp_path / "agent"
    output.mkdir()
    sessions = tmp_path / "sessions"
    sessions.mkdir()

    state_path = output / "state.json"
    correction_id = "correction::def456"
    _build_seeded_state(state_path, node_id=correction_id, inject_hash="def456")

    rebuild = _load_module(Path("examples/openclaw_adapter/rebuild_all_brains.py"), "oc_rebuild_all_brains_test")
    monkeypatch.setattr(rebuild, "_load_learnings", lambda agent_id, skip_node_ids=None: [])
    monkeypatch.setattr(rebuild, "_embed_new_nodes", lambda new_texts, batch_size=50: {node_id: [0.4] * 1536 for node_id, _ in new_texts.items()})
    monkeypatch.setattr(
        rebuild,
        "replay_queries",
        lambda graph, queries: {"queries_replayed": 0, "edges_reinforced": 0, "cross_file_edges_created": 0, "last_replayed_ts": None},
    )
    monkeypatch.setattr(rebuild, "measure_health", lambda graph: _health_stub())
    monkeypatch.setitem(
        sys.modules,
        "subprocess",
        types.SimpleNamespace(run=lambda *args, **kwargs: types.SimpleNamespace(stdout="", returncode=0)),
    )

    rebuild.rebuild_agent(
        "main",
        {
            "workspace": workspace,
            "sessions": sessions,
            "output": output,
            "cache": tmp_path / "cache.json",
        },
        preserve_injected=True,
    )

    rebuilt_state_path = output / "state.json"
    graph, _, _ = load_state(str(rebuilt_state_path))
    assert graph.get_node(correction_id) is not None
