from __future__ import annotations

import importlib
import sys
import types


class _Vector(list):
    def tolist(self):  # type: ignore[override]
        """tolist."""
        return list(self)


def _install_fake_sentence_transformers(monkeypatch, encode_fn):
    """ install fake sentence transformers."""
    module = types.ModuleType("sentence_transformers")

    class FakeSentenceTransformer:
        init_calls = 0

        def __init__(self, model_name: str) -> None:
            """  init  ."""
            self.model_name = model_name
            FakeSentenceTransformer.init_calls += 1

        def encode(self, values):
            """encode."""
            return encode_fn(values)

    module.SentenceTransformer = FakeSentenceTransformer
    monkeypatch.setitem(sys.modules, "sentence_transformers", module)
    sys.modules.pop("crabpath.embeddings", None)
    return module, FakeSentenceTransformer


def test_local_embed_fn(monkeypatch) -> None:
    """test local embed fn."""
    module, transformer_cls = _install_fake_sentence_transformers(
        monkeypatch,
        lambda text: _Vector([float(len(text)), 0.0]),
    )
    importlib.invalidate_caches()
    embeddings = importlib.import_module("crabpath.embeddings")
    if hasattr(embeddings.local_embed_fn, "_model"):
        delattr(embeddings.local_embed_fn, "_model")

    result_one = embeddings.local_embed_fn("hello")
    result_two = embeddings.local_embed_fn("world")

    assert result_one == [5.0, 0.0]
    assert result_two == [5.0, 0.0]
    assert transformer_cls.init_calls == 1
    assert embeddings.local_embed_fn._model.model_name == "all-MiniLM-L6-v2"


def test_local_embed_batch_fn(monkeypatch) -> None:
    """test local embed batch fn."""
    _, transformer_cls = _install_fake_sentence_transformers(
        monkeypatch,
        lambda texts: _Vector([_Vector([float(len(text)), 1.0]) for text in texts]),
    )
    importlib.invalidate_caches()
    embeddings = importlib.import_module("crabpath.embeddings")
    if hasattr(embeddings.local_embed_batch_fn, "_model"):
        delattr(embeddings.local_embed_batch_fn, "_model")

    result = embeddings.local_embed_batch_fn([("a", "abc"), ("b", "de")])

    assert transformer_cls.init_calls == 1
    assert result == {"a": [3.0, 1.0], "b": [2.0, 1.0]}
