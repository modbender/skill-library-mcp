from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from crabpath import Edge, Graph, HashEmbedder, Node, VectorIndex, save_state
from crabpath.store import load_state


def _write_state(path: Path) -> None:
    graph = Graph()
    graph.add_node(Node("a", "alpha", metadata={"file": "a.md"}))
    graph.add_node(Node("b", "beta", metadata={"file": "b.md"}))
    graph.add_edge(Edge("a", "b", weight=0.5, kind="sibling", metadata={"source": "unit"}))

    embedder = HashEmbedder()
    index = VectorIndex()
    index.upsert("a", embedder.embed("alpha"))
    index.upsert("b", embedder.embed("beta"))

    save_state(
        graph=graph,
        index=index,
        path=path,
        meta={"embedder_name": "hash-v1", "embedder_dim": embedder.dim},
    )


def _start_daemon(state_path: Path, auto_save_interval: int = 10) -> subprocess.Popen:
    env = os.environ.copy()
    env.pop("OPENAI_API_KEY", None)
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "crabpath",
            "daemon",
            "--state",
            str(state_path),
            "--auto-save-interval",
            str(auto_save_interval),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1,
        env=env,
    )


def _call(proc: subprocess.Popen, method: str, params: dict | None = None, req_id: str = "1") -> dict:
    assert proc.stdin is not None
    assert proc.stdout is not None
    req = {"id": req_id, "method": method, "params": params or {}}
    proc.stdin.write(json.dumps(req) + "\n")
    proc.stdin.flush()
    response = proc.stdout.readline()
    assert response
    return json.loads(response)


def _shutdown_daemon(proc: subprocess.Popen) -> dict:
    if proc.poll() is not None:
        return {"result": {"shutdown": True}}
    response = _call(proc, "shutdown", {}, req_id="shutdown")
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=2)
    return response


def test_daemon_responds_to_health(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    proc = _start_daemon(state_path)
    try:
        response = _call(proc, "health", req_id="health-1")
        assert response["id"] == "health-1"
        assert "result" in response
        assert "dormant_pct" in response["result"]
        assert "nodes" in response["result"]
        assert response["result"]["nodes"] == 2
    finally:
        _shutdown_daemon(proc)


def test_daemon_responds_to_info(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    proc = _start_daemon(state_path)
    try:
        response = _call(proc, "info", req_id="info-1")
        assert response["id"] == "info-1"
        result = response["result"]
        assert result["nodes"] == 2
        assert result["edges"] == 1
        assert result["embedder"] == "hash-v1"
    finally:
        _shutdown_daemon(proc)


def test_daemon_query_returns_fired_nodes(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    proc = _start_daemon(state_path)
    try:
        response = _call(proc, "query", {"query": "alpha", "top_k": 2}, req_id="query-1")
        result = response["result"]
        assert response["id"] == "query-1"
        assert "fired_nodes" in result
        assert result["fired_nodes"]
        assert "a" in result["fired_nodes"]
        assert result["seeds"]
        assert isinstance(result["embed_query_ms"], float)
        assert isinstance(result["traverse_ms"], float)
        assert isinstance(result["total_ms"], float)
    finally:
        _shutdown_daemon(proc)


def test_daemon_unknown_method_returns_error(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    proc = _start_daemon(state_path)
    try:
        response = _call(proc, "no-such-method", req_id="bad-1")
        assert "error" in response
        assert response["error"]["code"] == -32601
    finally:
        _shutdown_daemon(proc)


def test_daemon_shutdown_saves_state(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    graph, _, _ = load_state(str(state_path))
    before_weight = graph._edges["a"]["b"].weight

    proc = _start_daemon(state_path)
    try:
        learn = _call(proc, "learn", {"fired_nodes": ["a", "b"], "outcome": 1.0}, req_id="learn-1")
        assert learn["result"]["edges_updated"] == 1
        shutdown = _shutdown_daemon(proc)
        assert shutdown["result"]["shutdown"]

    finally:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=1)

    graph_after, _, _ = load_state(str(state_path))
    after_weight = graph_after._edges["a"]["b"].weight
    assert after_weight > before_weight
