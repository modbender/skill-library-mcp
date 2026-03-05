"""Tests for OpenAI embedding integration and CLI embedder resolution."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
import types

from crabpath.cli import _resolve_embedder
from crabpath.cli import _resolve_llm
from crabpath.cli import main


def _install_fake_openai(monkeypatch, vector_fn):
    """Install a fake openai module."""
    calls: list[tuple[str, object]] = []

    class FakeEmbedding:
        def __init__(self, vector: list[float]) -> None:
            self.embedding = vector

    class FakeResponse:
        def __init__(self, vectors: list[list[float]]) -> None:
            self.data = [FakeEmbedding(vector) for vector in vectors]

    class FakeEmbeddings:
        def create(self, model: str, input: str | list[str]) -> FakeResponse:
            calls.append((model, input))
            values = [input] if isinstance(input, str) else input
            vectors = [vector_fn(value) for value in values]
            return FakeResponse(vectors)

    class FakeOpenAI:
        def __init__(self, api_key: str | None = None) -> None:
            self.embeddings = FakeEmbeddings()
            self.api_key = api_key

    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    module_name = "crabpath.openai_embeddings"
    sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)
    return calls, module


def _install_fake_openai_llm(monkeypatch, responses):
    """Install a fake openai module for LLM calls."""
    calls: list[tuple[str, list[dict[str, str]]]] = []
    response_items = responses.copy()

    class FakeMessage:
        def __init__(self, content: str) -> None:
            self.content = content

    class FakeChoice:
        def __init__(self, content: str) -> None:
            self.message = FakeMessage(content)

    class FakeResponse:
        def __init__(self, content: str) -> None:
            self.choices = [FakeChoice(content)]

    class FakeChatCompletions:
        def create(self, model: str, messages: list[dict[str, str]]) -> FakeResponse:
            calls.append((model, messages))
            system = messages[0]["content"] if len(messages) > 0 else ""
            user = messages[1]["content"] if len(messages) > 1 else ""
            content = response_items.pop(0)
            return FakeResponse(content(system, user) if callable(content) else str(content))

    class FakeChat:
        def __init__(self) -> None:
            self.completions = FakeChatCompletions()

    class FakeOpenAI:
        def __init__(self, api_key: str | None = None) -> None:
            self.chat = FakeChat()
            self.api_key = api_key

    fake_openai = types.ModuleType("openai")
    fake_openai.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", fake_openai)

    module_name = "crabpath.openai_llm"
    sys.modules.pop(module_name, None)
    module = importlib.import_module(module_name)
    module._client = None
    return calls, module


def test_openai_llm_fn_calls_chat_completion(monkeypatch) -> None:
    """test openai llm fn."""
    calls, module = _install_fake_openai_llm(
        monkeypatch,
        [lambda _, __: "reply one"],
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    response = module.openai_llm_fn("system prompt", "user prompt")

    assert response == "reply one"
    assert calls == [
        (
            "gpt-5-mini",
            [
                {"role": "system", "content": "system prompt"},
                {"role": "user", "content": "user prompt"},
            ],
        )
    ]


def test_openai_llm_batch_fn_runs_sequentially(monkeypatch) -> None:
    """test openai llm batch fn."""
    calls, module = _install_fake_openai_llm(
        monkeypatch,
        [lambda _, __: "reply one", lambda _, __: "reply two"],
    )
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    output = module.openai_llm_batch_fn(
        [
            {"system": "system 1", "user": "user 1", "id": "r1"},
            {"system": "system 2", "user": "user 2", "id": "r2"},
        ]
    )

    assert output == [
        {"id": "r1", "response": "reply one"},
        {"id": "r2", "response": "reply two"},
    ]
    assert len(calls) == 2


def test_resolve_llm_none_returns_no_callbacks(monkeypatch) -> None:
    """test resolve llm none."""
    _install_fake_openai_llm(monkeypatch, [lambda _, __: "ignored"])
    llm_fn, llm_batch_fn = _resolve_llm(argparse.Namespace(llm=None))
    assert llm_fn is None
    assert llm_batch_fn is None


def test_resolve_llm_openai_returns_callbacks(monkeypatch) -> None:
    """test resolve llm openai."""
    _install_fake_openai_llm(monkeypatch, [lambda _, __: "ok"])
    llm_fn, llm_batch_fn = _resolve_llm(argparse.Namespace(llm="openai"))

    assert llm_fn is not None
    assert llm_batch_fn is not None


def test_openai_embedder_embed(monkeypatch) -> None:
    """test openai embedder embed."""
    embedding = [1.0] * 1536
    calls, module = _install_fake_openai(monkeypatch, lambda text: embedding if text == "hello" else [0.0] * 1536)

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    embedder = module.OpenAIEmbedder()
    vector = embedder.embed("hello")

    assert vector == embedding
    assert calls == [("text-embedding-3-small", "hello")]


def test_openai_embedder_embed_batch(monkeypatch) -> None:
    """test openai embedder embed batch."""
    vectors = {
        "first": [1.0] * 1536,
        "second": [0.0] * 1535 + [1.0],
    }

    calls, module = _install_fake_openai(monkeypatch, lambda text: vectors[text])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    embedder = module.OpenAIEmbedder()
    vectors_by_id = embedder.embed_batch([("a", "first"), ("b", "second")])

    assert vectors_by_id == {"a": vectors["first"], "b": vectors["second"]}
    assert calls == [("text-embedding-3-small", ["first", "second"])]


def test_resolve_embedder_chooses_by_arg_and_meta(monkeypatch) -> None:
    """test resolve embedder."""
    _install_fake_openai(monkeypatch, lambda text: [1.0] * 1536)

    hash_fn, hash_batch_fn, hash_name, hash_dim = _resolve_embedder(argparse.Namespace(embedder="hash"), {})
    assert hash_name == "hash-v1"
    assert hash_dim == 1024
    assert isinstance(hash_fn("alpha"), list)
    assert isinstance(hash_batch_fn([("a", "alpha")]), dict)

    default_fn, _, default_name, _ = _resolve_embedder(argparse.Namespace(embedder=None), {})
    assert default_name == "hash-v1"
    assert isinstance(default_fn("alpha"), list)

    openai_fn, openai_batch_fn, openai_name, openai_dim = _resolve_embedder(
        argparse.Namespace(embedder="openai"), {}
    )
    assert openai_name == "openai-text-embedding-3-small"
    assert openai_dim == 1536
    assert openai_fn("query") == [1.0] * 1536
    assert openai_batch_fn([("a", "query")]) == {"a": [1.0] * 1536}

    auto_fn, _, auto_name, _ = _resolve_embedder(
        argparse.Namespace(embedder=None),
        {"embedder_name": "openai-text-embedding-3-small", "embedder_dim": 1536},
    )
    assert auto_name == "openai-text-embedding-3-small"
    assert auto_fn("query") == [1.0] * 1536


def test_cmd_init_stores_openai_metadata(tmp_path, monkeypatch) -> None:
    """test cmd init stores openai metadata."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "note.md").write_text("alpha", encoding="utf-8")

    _install_fake_openai(monkeypatch, lambda text: [1.0] * 1536)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    code = main(["init", "--workspace", str(workspace), "--output", str(tmp_path), "--embedder", "openai"])
    assert code == 0

    state_data = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert state_data["meta"]["embedder_name"] == "openai-text-embedding-3-small"
    assert state_data["meta"]["embedder_dim"] == 1536


def test_cmd_query_auto_detects_openai_embedder(tmp_path, monkeypatch, capsys) -> None:
    """test cli query auto-detects openai metadata."""
    state_path = tmp_path / "state.json"
    state_path.write_text(
        json.dumps(
            {
                "graph": {
                    "nodes": [
                        {"id": "a", "content": "alpha", "summary": "", "metadata": {"file": "a.md"}},
                        {"id": "b", "content": "beta", "summary": "", "metadata": {"file": "b.md"}},
                    ],
                    "edges": [],
                },
                "index": {
                    "a": [1.0] * 1536,
                    "b": [0.0] * 1535 + [1.0],
                },
                "meta": {
                    "embedder_name": "openai-text-embedding-3-small",
                    "embedder_dim": 1536,
                },
            }
        ),
        encoding="utf-8",
    )

    _install_fake_openai(monkeypatch, lambda text: [1.0] * 1536 if text == "alpha" else [0.0] * 1536)
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    code = main(["query", "alpha", "--state", str(state_path), "--top", "2", "--json"])
    assert code == 0
    output = json.loads(capsys.readouterr().out.strip())
    assert output["fired"][0] == "a"
