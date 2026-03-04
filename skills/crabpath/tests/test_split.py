from __future__ import annotations

from pathlib import Path
import json

from crabpath.split import split_workspace


def test_split_by_headers_creates_chunked_nodes(tmp_path: Path) -> None:
    """test split by headers creates chunked nodes."""
    workspace = tmp_path / "split_headers"
    workspace.mkdir()
    (workspace / "a.md").write_text(
        "## Intro\nThis is intro.\n\n## Body\nThis is body.",
        encoding="utf-8",
    )

    graph, texts = split_workspace(str(workspace))
    nodes = {node.id for node in graph.nodes()}
    assert len(nodes) == 2
    assert any(node_id.endswith("::0") for node_id in nodes)
    assert any(node_id.endswith("::1") for node_id in nodes)
    assert graph.outgoing("a.md::0")[0][1].kind == "sibling"
    assert texts["a.md::0"].startswith("## Intro")


def test_split_by_blank_lines_when_no_headers(tmp_path: Path) -> None:
    """test split by blank lines when no headers."""
    workspace = tmp_path / "split_blank"
    workspace.mkdir()
    (workspace / "a.md").write_text(
        "First paragraph.\n\nSecond paragraph.\n\nThird paragraph.",
        encoding="utf-8",
    )

    graph, texts = split_workspace(str(workspace))
    assert len(graph.nodes()) == 3
    assert graph.edge_count() == 4
    assert len(texts) == 3


def test_split_single_file_with_no_sections_is_one_node(tmp_path: Path) -> None:
    """test split single file with no sections is one node."""
    workspace = tmp_path / "split_single"
    workspace.mkdir()
    (workspace / "single.md").write_text("Just one paragraph only.", encoding="utf-8")

    graph, texts = split_workspace(str(workspace))
    assert graph.node_count() == 1
    assert graph.edge_count() == 0
    assert "single.md::0" in texts


def test_split_multiple_files_with_cross_references(tmp_path: Path) -> None:
    """test split multiple files with cross references."""
    workspace = tmp_path / "split_multi"
    workspace.mkdir()
    (workspace / "one.md").write_text(
        "## Alpha\nSee [file two](two.md).\n\n## Beta\n", encoding="utf-8"
    )
    (workspace / "two.md").write_text(
        "# Cross\nThis references [one.md](one.md) in the text.", encoding="utf-8"
    )

    graph, texts = split_workspace(str(workspace))
    node_ids = {node.id for node in graph.nodes()}
    assert len(node_ids) == 3
    assert "one.md::0" in node_ids
    assert "two.md::0" in node_ids
    assert any("file two" in text for text in texts.values())
    assert any("one.md" in text for text in texts.values())


def test_split_empty_workspace(tmp_path: Path) -> None:
    """test split empty workspace."""
    workspace = tmp_path / "split_empty"
    workspace.mkdir()
    graph, texts = split_workspace(str(workspace))

    assert graph.node_count() == 0
    assert texts == {}


def test_split_ignores_binary_files(tmp_path: Path) -> None:
    """test split ignores binary files."""
    workspace = tmp_path / "split_binary"
    workspace.mkdir()
    (workspace / "note.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (workspace / "text.md").write_text("## Section\nBody", encoding="utf-8")

    graph, texts = split_workspace(str(workspace))
    assert graph.node_count() == 1
    assert len(graph.nodes()) == 1
    assert list(texts.keys()) == ["text.md::0"]


def test_split_nested_directories_preserved(tmp_path: Path) -> None:
    """test split nested directories preserved."""
    workspace = tmp_path / "split_nested"
    nested = workspace / "a" / "b"
    nested.mkdir(parents=True)
    (workspace / "root.md").write_text("## R\nroot", encoding="utf-8")
    (nested / "nested.md").write_text("## N\nnested", encoding="utf-8")

    graph, _ = split_workspace(str(workspace))
    ids = {node.id for node in graph.nodes()}
    assert "root.md::0" in ids
    assert "a/b/nested.md::0" in ids


def test_split_long_file_splits_into_multiple_nodes(tmp_path: Path) -> None:
    """test split long file splits into multiple nodes."""
    workspace = tmp_path / "split_long"
    workspace.mkdir()
    paragraph = "word " * 20
    (workspace / "long.md").write_text(
        f"{paragraph}\n\n{paragraph}\n\n{paragraph}\n\n{paragraph}",
        encoding="utf-8",
    )

    graph, _ = split_workspace(str(workspace))
    assert graph.node_count() >= 4
    assert graph.edge_count() >= 3


def test_split_sibling_edge_weights_have_jitter(tmp_path: Path) -> None:
    """test split sibling edge weights have jitter."""
    workspace = tmp_path / "split_jitter"
    workspace.mkdir()
    (workspace / "file.md").write_text(
        "## A\na\n\n## B\nb\n\n## C\nc\n\n## D\nd",
        encoding="utf-8",
    )

    graph, _ = split_workspace(str(workspace))
    weights = [edge.weight for source in graph._edges.values() for edge in source.values()]
    assert len(set(round(w, 6) for w in weights)) >= 2
    assert all(0.4 <= w <= 0.6 for w in weights)


def test_split_file_with_title_only(tmp_path: Path) -> None:
    """test split file with title only."""
    workspace = tmp_path / "split_title"
    workspace.mkdir()
    (workspace / "title.md").write_text("# Just a title", encoding="utf-8")

    graph, texts = split_workspace(str(workspace))
    assert graph.node_count() == 1
    assert graph.incoming("title.md::0") == []
    assert texts["title.md::0"] == "# Just a title"


def test_split_with_llm_json_sections(tmp_path: Path) -> None:
    """test split with llm json sections."""
    workspace = tmp_path / "split_llm"
    workspace.mkdir()
    (workspace / "note.md").write_text("Intro paragraph.\n\nDeep dive.\n\nChecklist.\n")

    calls: list[tuple[str, str]] = []

    def fake_llm(system: str, user: str) -> str:
        """fake llm."""
        calls.append((system, user))
        return json.dumps({"sections": ["Section 1: Intro.", "Section 2: Deep dive.", "Section 3: Checklist."]})

    graph, texts = split_workspace(str(workspace), llm_fn=fake_llm)

    assert len(graph.nodes()) == 3
    assert list(texts.values()) == ["Section 1: Intro.", "Section 2: Deep dive.", "Section 3: Checklist."]
    assert calls


def test_split_with_llm(tmp_path: Path) -> None:
    """test split with llm."""
    test_split_with_llm_json_sections(tmp_path)


def test_split_without_llm(tmp_path: Path) -> None:
    """test split without llm."""
    workspace = tmp_path / "split_no_llm"
    workspace.mkdir()
    (workspace / "note.md").write_text("## Intro\nFirst\n\n## Body\nSecond")

    graph, texts = split_workspace(str(workspace))
    assert len(graph.nodes()) == 2
    assert texts["note.md::0"].startswith("## Intro")


def test_split_with_llm_parse_fallback_to_headers(tmp_path: Path) -> None:
    """test split with llm parse fallback to headers."""
    workspace = tmp_path / "split_bad_llm"
    workspace.mkdir()
    (workspace / "note.md").write_text("## Intro\nFirst\n\n## Body\nSecond")

    def bad_llm(_system: str, _user: str) -> str:
        """bad llm."""
        return "not-json"

    graph, texts = split_workspace(str(workspace), llm_fn=bad_llm)
    assert len(graph.nodes()) == 2
    assert texts["note.md::0"].startswith("## Intro")


def test_split_json_file_with_long_payload_handles_supported_extension(tmp_path: Path) -> None:
    """test split json file with long payload handles supported extension."""
    workspace = tmp_path / "split_json"
    workspace.mkdir()
    content = json.dumps({f"key{i}": list(range(100)) for i in range(30)}, ensure_ascii=False)
    (workspace / "payload.json").write_text(content, encoding="utf-8")

    graph, texts = split_workspace(str(workspace), file_extensions=(".json",))
    assert graph.node_count() == len(texts)
    assert graph.node_count() >= 1


def test_split_python_file_chunks_by_definitions(tmp_path: Path) -> None:
    """test split python file chunks by definitions."""
    workspace = tmp_path / "split_py"
    workspace.mkdir()
    (workspace / "sample.py").write_text(
        "import os\n\n\ndef first():\n    return 1\n\nclass Thing:\n    pass\n\n\ndef second():\n    return 2\n",
        encoding="utf-8",
    )

    graph, texts = split_workspace(str(workspace), file_extensions=(".py",))
    assert len(graph.nodes()) >= 2
    node_contents = list(texts.values())
    assert any(chunk.startswith("def first") for chunk in node_contents)
    assert any(chunk.startswith("class Thing") for chunk in node_contents)
    assert any(chunk.startswith("def second") for chunk in node_contents)


def test_split_text_file_uses_blank_line_split(tmp_path: Path) -> None:
    """test split text file uses blank line split."""
    workspace = tmp_path / "split_text"
    workspace.mkdir()
    (workspace / "notes.txt").write_text("First paragraph.\n\nSecond paragraph.\n\nThird paragraph.", encoding="utf-8")

    graph, texts = split_workspace(str(workspace), file_extensions=(".txt",))
    assert len(graph.nodes()) == 3
    assert len(texts) == 3
