from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_state(path: Path, *, with_openai_meta: bool = False) -> None:
    embedder_dim = 3
    payload = {
        "graph": {
            "nodes": [
                {"id": "a", "content": "alpha", "summary": "alpha", "metadata": {}},
                {"id": "b", "content": "beta", "summary": "beta", "metadata": {}},
            ],
            "edges": [
                {"source": "a", "target": "b", "weight": 0.5, "kind": "sibling", "metadata": {}},
            ],
        },
        "index": {"a": [1.0, 0.0, 0.0], "b": [0.0, 1.0, 0.0]},
        "meta": {"embedder_name": "text-embedding-3-small" if with_openai_meta else "hash-v1", "embedder_dim": embedder_dim},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _load_module_query() -> object:
    return _load_module(Path("examples/openclaw_adapter/query_brain.py"), "oc_query")


def _load_module_learn() -> object:
    return _load_module(Path("examples/openclaw_adapter/learn_correction.py"), "oc_learn")


def test_query_brain_logs_fired_nodes_by_chat_id(tmp_path, capsys, monkeypatch):
    state_path = tmp_path / "state.json"
    _write_state(state_path)
    now = 2_000_000.0

    query = _load_module_query()
    monkeypatch.setattr(query, "require_api_key", lambda: "test")
    monkeypatch.setattr(query, "embed_query", lambda _client, _text: [1.0, 0.0, 0.0])
    monkeypatch.setattr(query.time, "time", lambda: now)

    old_entry = {"chat_id": "chat-1", "query": "old", "fired_nodes": ["x"], "ts": now - 8 * 24 * 60 * 60}
    old_log = (tmp_path / "fired_log.jsonl")
    old_log.write_text(json.dumps(old_entry), encoding="utf-8")

    monkeypatch.setattr(sys, "argv", ["query_brain.py", str(state_path), "alpha", "--chat-id", "chat-1", "--top", "1", "--json"])
    query.main()

    output = json.loads(capsys.readouterr().out.strip())
    assert output["fired_nodes"][0] == "a"

    lines = [json.loads(line) for line in (tmp_path / "fired_log.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 1
    assert lines[0]["chat_id"] == "chat-1"
    assert lines[0]["ts"] == now


def test_learn_correction_reads_fired_log_and_runs_learn(tmp_path, capsys):
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    log = tmp_path / "fired_log.jsonl"
    log.write_text(json.dumps({"chat_id": "chat-1", "fired_nodes": ["a", "b"], "ts": 2_000_000.0}) + "\n")

    learn = _load_module_learn()
    learn.main(["--state", str(state_path), "--chat-id", "chat-1", "--outcome", "-1.0"])
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["fired_ids_penalized"] == ["a", "b"]
    assert summary["edges_updated"] == 1

    payload = json.loads(state_path.read_text(encoding="utf-8"))
    edge = payload["graph"]["edges"][0]
    assert edge["source"] == "a"
    assert edge["target"] == "b"
    assert edge["weight"] < 0.5


def test_prune_removes_older_fired_log_entries(tmp_path):
    query = _load_module_query()
    now = 2_000_000.0
    rows = [
        {"ts": now - 8 * 24 * 60 * 60, "chat_id": "chat-1", "fired_nodes": ["a"]},
        {"ts": now - 6 * 24 * 60 * 60, "chat_id": "chat-1", "fired_nodes": ["b"]},
    ]

    kept = query._prune_fired_log(rows, now)
    assert len(kept) == 1
    assert kept[0]["fired_nodes"] == ["b"]
