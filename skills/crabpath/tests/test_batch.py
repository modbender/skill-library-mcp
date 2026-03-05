from __future__ import annotations

import json
from pathlib import Path

from crabpath._batch import batch_or_single, batch_or_single_embed
from crabpath.graph import Graph, Node
from crabpath.split import generate_summaries, split_workspace


def test_batch_or_single_uses_batch_fn() -> None:
    """test batch or single uses batch fn."""
    single_calls = {"count": 0}

    def llm_single(_system_prompt: str, _user_prompt: str) -> str:
        """llm single."""
        single_calls["count"] += 1
        return "single"

    def llm_batch_fn(requests: list[dict]) -> list[dict]:
        """llm batch fn."""
        return [{"id": request["id"], "response": request["user"]} for request in requests]

    requests = [
        {"id": "req_0", "system": "s", "user": "u0"},
        {"id": "req_1", "system": "s", "user": "u1"},
    ]

    responses = batch_or_single(requests, llm_fn=llm_single, llm_batch_fn=llm_batch_fn)
    assert responses == [
        {"id": "req_0", "response": "u0"},
        {"id": "req_1", "response": "u1"},
    ]
    assert single_calls["count"] == 0


def test_batch_or_single_falls_back_to_single() -> None:
    """test batch or single falls back to single."""
    single_calls = {"count": 0}

    def llm_single(_system_prompt: str, _user_prompt: str) -> str:
        """llm single."""
        single_calls["count"] += 1
        return "single"

    requests = [
        {"id": "req_0", "system": "s", "user": "u0"},
        {"id": "req_1", "system": "s", "user": "u1"},
    ]

    responses = batch_or_single(requests, llm_fn=llm_single, llm_batch_fn=None, max_workers=1)
    assert single_calls["count"] == len(requests)
    assert {item["id"]: item["response"] for item in responses} == {"req_0": "single", "req_1": "single"}


def test_batch_or_single_embed() -> None:
    """test batch or single embed."""
    def embed_fn(text: str) -> list[float]:
        """embed fn."""
        return [float(len(text))]

    def embed_batch_fn(texts: list[tuple[str, str]]) -> dict[str, list[float]]:
        """embed batch fn."""
        return {node_id: [float(len(text))] for node_id, text in texts}

    text_items = [("a", "hello"), ("b", "world")]

    result = batch_or_single_embed(text_items, embed_fn=embed_fn, embed_batch_fn=embed_batch_fn)
    assert result == {"a": [5.0], "b": [5.0]}


def test_split_with_llm_batch_fn(tmp_path: Path) -> None:
    """test split with llm batch fn."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "a.md").write_text("one one one", encoding="utf-8")
    (workspace / "b.md").write_text("two two two", encoding="utf-8")

    def llm_batch_fn(requests: list[dict]) -> list[dict]:
        """llm batch fn."""
        return [
            {
                "id": request["id"],
                "response": json.dumps({"sections": [f"{request['id']}-left", f"{request['id']}-right"]}),
            }
            for request in requests
        ]

    graph, texts = split_workspace(
        workspace,
        llm_fn=None,
        llm_batch_fn=llm_batch_fn,
        should_use_llm_for_file=lambda _path, _content: True,
    )

    assert len(graph.nodes()) == 4
    assert set(texts.values()) == {"a.md-left", "a.md-right", "b.md-left", "b.md-right"}


def test_generate_summaries_batch() -> None:
    """test generate summaries batch."""
    graph = Graph()
    graph.add_node(Node("a", "alpha text"))
    graph.add_node(Node("b", "beta text"))

    single_calls = {"count": 0}

    def llm_fn(_system_prompt: str, _user_prompt: str) -> str:
        """llm fn."""
        single_calls["count"] += 1
        raise RuntimeError("should not be called")

    def llm_batch_fn(requests: list[dict]) -> list[dict]:
        """llm batch fn."""
        return [
            {
                "id": request["id"],
                "response": json.dumps({"summary": f"summary-{request['id']}"}),
            }
            for request in requests
        ]

    summaries = generate_summaries(graph, llm_fn=llm_fn, llm_batch_fn=llm_batch_fn)
    assert single_calls["count"] == 0
    assert summaries == {"a": "summary-a", "b": "summary-b"}
