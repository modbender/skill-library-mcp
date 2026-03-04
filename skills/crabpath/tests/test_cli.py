from __future__ import annotations

import json
from io import StringIO
from pathlib import Path

import pytest

from crabpath.cli import main
from crabpath.hasher import default_embed
from crabpath.journal import read_journal


def _write_graph_payload(path: Path) -> None:
    """ write graph payload."""
    payload = {
        "graph": {
            "nodes": [
                {"id": "a", "content": "alpha", "summary": "", "metadata": {"file": "a.md"}},
                {"id": "b", "content": "beta", "summary": "", "metadata": {"file": "b.md"}},
            ],
            "edges": [
                {"source": "a", "target": "b", "weight": 0.7, "kind": "sibling", "metadata": {}},
            ],
        }
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_index(path: Path, payload: dict[str, list[float]] | None = None) -> None:
    """ write index."""
    if payload is None:
        payload = {"a": [1.0, 0.0], "b": [0.0, 1.0]}
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_state(
    path: Path,
    graph_payload: dict | None = None,
    index_payload: dict[str, list[float]] | None = None,
    meta: dict[str, object] | None = None,
) -> None:
    """ write state."""
    if graph_payload is None:
        graph_payload = {
            "nodes": [
                {"id": "a", "content": "alpha", "summary": "", "metadata": {"file": "a.md"}},
                {"id": "b", "content": "beta", "summary": "", "metadata": {"file": "b.md"}},
            ],
            "edges": [
                {"source": "a", "target": "b", "weight": 0.7, "kind": "sibling", "metadata": {}},
            ],
        }
    if index_payload is None:
        index_payload = {
            "a": default_embed("alpha"),
            "b": default_embed("beta"),
        }
    if meta is None:
        meta = {"embedder_name": "hash-v1", "embedder_dim": 1024}
    path.write_text(json.dumps({"graph": graph_payload, "index": index_payload, "meta": meta}), encoding="utf-8")


def test_init_command_creates_workspace_graph(tmp_path) -> None:
    """test init command creates workspace graph."""
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "a.md").write_text("## A\nHello", encoding="utf-8")
    output = tmp_path

    code = main(["init", "--workspace", str(workspace), "--output", str(output)])
    assert code == 0

    graph_path = output / "graph.json"
    texts_path = output / "texts.json"
    index_path = output / "index.json"
    assert graph_path.exists()
    assert texts_path.exists()
    assert index_path.exists()
    graph_data = json.loads(graph_path.read_text(encoding="utf-8"))
    graph_payload = graph_data["graph"] if "graph" in graph_data else graph_data
    assert len(graph_payload["nodes"]) == 1
    assert graph_data.get("meta", {}).get("embedder_name") == "hash-v1"
    state_data = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert state_data["meta"]["embedder_name"] == "hash-v1"
    texts_data = json.loads(texts_path.read_text(encoding="utf-8"))
    assert len(texts_data) == 1


def test_init_command_with_empty_workspace(tmp_path) -> None:
    """test init command with empty workspace."""
    workspace = tmp_path / "empty"
    workspace.mkdir()
    output = tmp_path / "out"
    output.mkdir()

    code = main(["init", "--workspace", str(workspace), "--output", str(output)])
    assert code == 0
    graph_file = json.loads((output / "graph.json").read_text(encoding="utf-8"))
    graph_data = graph_file["graph"] if "graph" in graph_file else graph_file
    assert graph_data["nodes"] == []
    assert graph_data["edges"] == []
    assert (output / "index.json").exists()


def test_query_command_returns_json_with_fired_nodes(tmp_path, capsys) -> None:
    """test query command returns json with fired nodes."""
    graph_path = tmp_path / "graph.json"
    index_path = tmp_path / "index.json"
    _write_graph_payload(graph_path)
    _write_index(
        index_path,
        {
            "a": default_embed("alpha"),
            "b": default_embed("beta"),
        },
    )

    code = main(
        [
            "query",
            "alpha",
            "--graph",
            str(graph_path),
            "--index",
            str(index_path),
            "--top",
            "2",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["fired"]
    assert "a" in out["fired"]
    assert out["tier_thresholds"] == {
        "reflex": ">= 0.6",
        "habitual": "0.2 - 0.6",
        "dormant": "< 0.2",
        "inhibitory": "< -0.01",
    }


def test_query_auto_embeds(tmp_path, capsys) -> None:
    """test query auto embeds."""
    graph_path = tmp_path / "graph.json"
    index_path = tmp_path / "index.json"
    _write_graph_payload(graph_path)
    _write_index(
        index_path,
        {
            "a": default_embed("alpha"),
            "b": default_embed("completely different text"),
        },
    )

    code = main(
        [
            "query",
            "alpha",
            "--graph",
            str(graph_path),
            "--index",
            str(index_path),
            "--top",
            "2",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["fired"]
    assert out["fired"][0] == "a"


def test_query_uses_vector_from_stdin(tmp_path, capsys, monkeypatch) -> None:
    """test query uses vector from stdin."""
    graph_path = tmp_path / "graph.json"
    index_path = tmp_path / "index.json"
    _write_graph_payload(graph_path)
    _write_index(index_path)

    monkeypatch.setattr("sys.stdin", StringIO(json.dumps([1.0, 0.0])))

    code = main(
        [
            "query",
            "seed",
            "--graph",
            str(graph_path),
            "--index",
            str(index_path),
            "--top",
            "1",
            "--query-vector-stdin",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["fired"][0] == "a"


def test_cli_state_flag_query(tmp_path, capsys) -> None:
    """test cli state flag query."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    code = main(
        [
            "query",
            "alpha",
            "--state",
            str(state_path),
            "--top",
            "2",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["fired"]
    assert "a" in out["fired"]


def test_query_max_context_chars_cap_in_query_command(tmp_path, capsys) -> None:
    """test query max context chars cap in query command."""
    state_path = tmp_path / "state.json"
    graph_payload = {
        "nodes": [
            {"id": "a", "content": "alpha " * 80, "summary": "", "metadata": {"file": "a.md"}},
            {"id": "b", "content": "zeta " * 80, "summary": "", "metadata": {"file": "b.md"}},
        ],
        "edges": [{"source": "a", "target": "b", "weight": 0.95, "kind": "sibling", "metadata": {}}],
    }
    _write_state(state_path, graph_payload=graph_payload)

    code = main(
        [
            "query",
            "alpha",
            "--state",
            str(state_path),
            "--top",
            "1",
            "--max-context-chars",
            "120",
            "--json",
        ]
    )
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert len(out["context"]) <= 120


def test_query_journal_written_to_state_directory(tmp_path) -> None:
    """test query journal written to state directory."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    main(
        [
            "query",
            "alpha",
            "--state",
            str(state_path),
            "--json",
        ]
    )
    journal_path = tmp_path / "journal.jsonl"
    assert journal_path.exists()

    entries = read_journal(journal_path=str(journal_path))
    assert entries
    assert entries[-1]["type"] == "query"


def test_cli_state_replay_uses_last_replayed_ts(tmp_path, capsys) -> None:
    """test cli state replay uses last replayed ts."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    sessions = tmp_path / "sessions.jsonl"
    sessions.write_text(
        "\n".join(
            [
                json.dumps({"role": "user", "content": "alpha", "ts": 1.0}),
                json.dumps({"role": "user", "content": "alpha", "ts": 2.0}),
                json.dumps({"role": "user", "content": "alpha", "ts": 3.0}),
            ]
        ),
        encoding="utf-8",
    )

    code = main(["replay", "--state", str(state_path), "--sessions", str(sessions), "--json"])
    assert code == 0
    first = json.loads(capsys.readouterr().out.strip())
    assert first["queries_replayed"] == 3
    assert json.loads(state_path.read_text(encoding="utf-8"))["meta"]["last_replayed_ts"] == 3.0

    sessions.write_text(
        "\n".join(
            [
                json.dumps({"role": "user", "content": "alpha", "ts": 4.0}),
                json.dumps({"role": "user", "content": "alpha", "ts": 5.0}),
            ]
        ),
        encoding="utf-8",
    )
    code = main(["replay", "--state", str(state_path), "--sessions", str(sessions), "--json"])
    assert code == 0
    second = json.loads(capsys.readouterr().out.strip())
    assert second["queries_replayed"] == 2
    assert json.loads(state_path.read_text(encoding="utf-8"))["meta"]["last_replayed_ts"] == 5.0


def test_query_command_text_output_includes_node_ids(tmp_path, capsys) -> None:
    """test query text output includes node ids."""
    graph_path = tmp_path / "graph.json"
    index_path = tmp_path / "index.json"
    graph_payload = {
        "graph": {
            "nodes": [
                {
                    "id": "deploy.md::0",
                    "content": "How to create a hotfix",
                    "summary": "",
                    "metadata": {"file": "deploy.md"},
                },
                {
                    "id": "deploy.md::1",
                    "content": "CI must pass for hotfixes",
                    "summary": "",
                    "metadata": {"file": "deploy.md"},
                },
            ],
            "edges": [
                {
                    "source": "deploy.md::0",
                    "target": "deploy.md::1",
                    "weight": 0.85,
                    "kind": "sibling",
                    "metadata": {},
                }
            ],
        }
    }
    graph_path.write_text(json.dumps(graph_payload), encoding="utf-8")
    _write_index(index_path, {"deploy.md::0": default_embed("deploy"), "deploy.md::1": default_embed("hotfix")})

    code = main(
        [
            "query",
            "deploy hotfix",
            "--graph",
            str(graph_path),
            "--index",
            str(index_path),
            "--top",
            "2",
        ]
    )
    assert code == 0
    out = capsys.readouterr().out
    assert "deploy.md::0" in out
    assert "deploy.md::1" in out


def test_cli_dimension_mismatch_error(tmp_path) -> None:
    """test cli dimension mismatch error."""
    state_path = tmp_path / "state.json"
    _write_state(
        state_path,
        index_payload={"a": [1.0, 0.0] * 768, "b": [0.0, 1.0] * 768},
        meta={"embedder_name": "openai-text-embedding-3-small", "embedder_dim": 1536},
    )

    with pytest.raises(SystemExit, match=r"Index was built with openai-text-embedding-3-small \(dim=1536\). CLI hash embedder uses dim=1024. Dimension mismatch. Use --query-vector-stdin with matching embedder."):
        main(["query", "alpha", "--state", str(state_path), "--embedder", "hash", "--top", "2", "--json"])
        main(["query", "alpha", "--state", str(state_path), "--top", "2", "--json"])


def test_query_command_error_on_missing_graph(tmp_path) -> None:
    """test query command error on missing graph."""
    index_path = tmp_path / "index.json"
    _write_index(index_path)
    with pytest.raises(SystemExit):
        main(["query", "seed", "--graph", str(tmp_path / "missing.json"), "--index", str(index_path)])


def test_query_command_keywords_without_index(tmp_path, capsys) -> None:
    """test query command keywords without index."""
    graph_path = tmp_path / "graph.json"
    _write_graph_payload(graph_path)

    code = main(["query", "alpha", "--graph", str(graph_path), "--top", "2", "--json"])
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert out["fired"]
    assert out["fired"][0] == "a"


def test_learn_command_updates_graph_weights(tmp_path) -> None:
    """test learn command updates graph weights."""
    graph_path = tmp_path / "graph.json"
    _write_graph_payload(graph_path)

    code = main(["learn", "--graph", str(graph_path), "--outcome", "1.0", "--fired-ids", "a,b"])
    assert code == 0

    payload = json.loads(graph_path.read_text(encoding="utf-8"))
    assert payload["graph"]["edges"][0]["weight"] > 0.7


def test_cli_state_flag_learn(tmp_path) -> None:
    """test cli state flag learn."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    original = json.loads(state_path.read_text(encoding="utf-8"))
    original_weight = original["graph"]["edges"][0]["weight"]
    code = main(
        [
            "learn",
            "--state",
            str(state_path),
            "--outcome",
            "1.0",
            "--fired-ids",
            "a,b",
        ]
    )
    assert code == 0

    updated = json.loads(state_path.read_text(encoding="utf-8"))
    assert updated["graph"]["edges"][0]["weight"] > original_weight


def test_cli_state_flag_health(tmp_path, capsys) -> None:
    """test cli state flag health."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    code = main(["health", "--state", str(state_path), "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    expected = {
        "dormant_pct",
        "habitual_pct",
        "reflex_pct",
        "cross_file_edge_pct",
        "orphan_nodes",
        "nodes",
        "edges",
    }
    assert expected.issubset(set(payload.keys()))


def test_learn_command_supports_json_output(tmp_path, capsys) -> None:
    """test learn command supports json output."""
    graph_path = tmp_path / "graph.json"
    _write_graph_payload(graph_path)

    code = main(["learn", "--graph", str(graph_path), "--outcome", "-1.0", "--fired-ids", "a,b", "--json"])
    assert code == 0
    data = json.loads(capsys.readouterr().out.strip())
    assert data["edges_updated"] == 1
    assert data["max_weight_delta"] >= 0.0


def test_merge_command_suggests_and_applies(tmp_path, capsys) -> None:
    """test merge command suggests and applies."""
    graph_path = tmp_path / "graph.json"
    payload = {
        "graph": {
            "nodes": [
                {"id": "a", "content": "alpha", "summary": "", "metadata": {}},
                {"id": "b", "content": "beta", "summary": "", "metadata": {}},
                {"id": "c", "content": "gamma", "summary": "", "metadata": {}},
            ],
            "edges": [
                {"source": "a", "target": "b", "weight": 0.95, "kind": "sibling", "metadata": {}},
                {"source": "b", "target": "a", "weight": 0.95, "kind": "sibling", "metadata": {}},
                {"source": "a", "target": "c", "weight": 0.2, "kind": "sibling", "metadata": {}},
                {"source": "c", "target": "a", "weight": 0.1, "kind": "sibling", "metadata": {}},
            ],
        }
    }
    graph_path.write_text(json.dumps(payload), encoding="utf-8")

    code = main(["merge", "--graph", str(graph_path), "--json"])
    assert code == 0
    out = json.loads(capsys.readouterr().out.strip())
    assert "suggestions" in out
    assert out["suggestions"]

    updated = json.loads(graph_path.read_text(encoding="utf-8"))
    if "graph" in updated:
        graph_payload = updated["graph"]
    else:
        graph_payload = updated
    assert "nodes" in graph_payload
    assert len(graph_payload["nodes"]) <= 3


def test_health_command_outputs_all_metrics(tmp_path, capsys) -> None:
    """test health command outputs all metrics."""
    graph_path = tmp_path / "graph.json"
    _write_graph_payload(graph_path)
    code = main(["health", "--graph", str(graph_path), "--json"])
    assert code == 0
    payload = json.loads(capsys.readouterr().out.strip())
    expected = {
        "dormant_pct",
        "habitual_pct",
        "reflex_pct",
        "cross_file_edge_pct",
        "orphan_nodes",
        "nodes",
        "edges",
    }
    assert expected.issubset(set(payload.keys()))


def test_health_command_text_output_is_readable(tmp_path, capsys) -> None:
    """test health command has human-readable non-json output."""
    graph_path = tmp_path / "graph.json"
    _write_graph_payload(graph_path)

    code = main(["health", "--graph", str(graph_path)])
    assert code == 0
    out = capsys.readouterr().out
    assert "Brain health:" in out
    assert "Nodes:" in out
    assert "Edges:" in out
    assert "Cross-file edges:" in out


def test_cli_help_text_for_commands() -> None:
    """test cli help text for commands."""
    for command in ["init", "query", "learn", "merge", "health", "connect", "replay", "journal", "sync"]:
        with pytest.raises(SystemExit):
            main([command, "--help"])


def test_inject_command_defaults_connect_min_sim_for_hash_embedder(tmp_path, capsys) -> None:
    """test inject uses a zero min similarity threshold by default for hash embeds."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    code = main(
        [
            "inject",
            "--state",
            str(state_path),
            "--id",
            "fix::ci",
            "--content",
            "alpha",
            "--type",
            "CORRECTION",
            "--json",
        ]
    )
    assert code == 0

    out = json.loads(capsys.readouterr().out.strip())
    assert out["connected_to"]
    assert out["inhibitory_edges_created"] > 0
