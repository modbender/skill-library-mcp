from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from crabpath.compact import compact_daily_notes
from crabpath.hasher import default_embed
from crabpath.store import load_state


TODAY = date.today()


def _write_state(path: Path) -> None:
    """Write a minimal hash-v1 state for compact tests."""
    payload = {
        "graph": {
            "nodes": [
                {"id": "note::base", "content": "base memory", "summary": "base", "metadata": {"source": "memory"}
                }
            ],
            "edges": [],
        },
        "index": {
            "note::base": default_embed("base memory"),
        },
        "meta": {"embedder_name": "hash-v1", "embedder_dim": 1024},
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_note(path: Path, content: str) -> None:
    """Write a note file."""
    path.write_text(content, encoding="utf-8")


def _make_note_name(days_ago: int) -> str:
    return (TODAY - timedelta(days=days_ago)).isoformat()


def test_compact_skips_recent_files(tmp_path: Path) -> None:
    """test compact skips recent files."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    notes_dir = tmp_path / "memory"
    notes_dir.mkdir()
    note_path = notes_dir / f"{_make_note_name(0)}.md"
    content = "\n".join(f"line {idx}" for idx in range(30)) + "\n"
    _write_note(note_path, content)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=str(notes_dir),
        max_age_days=7,
        min_lines_to_compact=20,
        target_lines=15,
    )

    assert report.files_scanned == 1
    assert report.files_compacted == 0
    assert report.files_skipped == 1
    assert report.nodes_injected == 0
    assert note_path.read_text(encoding="utf-8") == content


def test_compact_skips_short_files(tmp_path: Path) -> None:
    """test compact skips files with too few lines."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    notes_dir = tmp_path / "memory"
    notes_dir.mkdir()
    note_path = notes_dir / f"{_make_note_name(10)}.md"
    content = "short\nline\nonly\n"
    _write_note(note_path, content)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=str(notes_dir),
        max_age_days=7,
        min_lines_to_compact=20,
        target_lines=15,
    )

    assert report.files_scanned == 1
    assert report.files_compacted == 0
    assert report.files_skipped == 1
    assert report.nodes_injected == 0
    assert note_path.read_text(encoding="utf-8") == content
    graph, _, _ = load_state(str(state_path))
    assert graph.node_count() == 1


def test_compact_reduces_line_count(tmp_path: Path) -> None:
    """test compact rewrites notes with reduced line count."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    notes_dir = tmp_path / "memory"
    notes_dir.mkdir()
    note_path = notes_dir / f"{_make_note_name(10)}.md"
    long_section = "\n".join(f"detail line {idx}" for idx in range(30))
    content = "## Header A\n" + long_section + "\n## Header B\n" + long_section + "\n"
    _write_note(note_path, content)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=str(notes_dir),
        max_age_days=7,
        min_lines_to_compact=20,
        target_lines=6,
    )

    compacted = note_path.read_text(encoding="utf-8")
    compact_lines = compacted.splitlines()
    assert report.files_compacted == 1
    assert report.files_skipped == 0
    assert len(compact_lines) <= 6
    assert len(compact_lines) < 60
    assert compact_lines[0].startswith("## Header A")


def test_compact_injects_nodes_into_graph(tmp_path: Path) -> None:
    """test compact injects nodes into graph."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)

    notes_dir = tmp_path / "memory"
    notes_dir.mkdir()
    note_path = notes_dir / f"{_make_note_name(10)}.md"
    content = "## Decisions\nAlways update docs before shipping.\nSecond line.\n## Corrections\nFix missing edge cases.\n"
    _write_note(note_path, content)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=str(notes_dir),
        max_age_days=7,
        min_lines_to_compact=3,
        target_lines=12,
    )

    graph, _, _ = load_state(str(state_path))
    injected_nodes = [
        node
        for node in graph.nodes()
        if node.id.startswith("learning::compact::") and node.metadata.get("source") == str(note_path)
    ]
    assert report.nodes_injected > 0
    assert injected_nodes
    assert all(node.metadata.get("authority") == "overlay" for node in injected_nodes)
    assert any("decisions" in node.content.lower() for node in injected_nodes)


def test_compact_dry_run(tmp_path: Path) -> None:
    """test compact dry-run does not mutate files or graph."""
    state_path = tmp_path / "state.json"
    _write_state(state_path)
    graph_before, index_before, _ = load_state(str(state_path))
    nodes_before = graph_before.node_count()
    vectors_before = dict(index_before._vectors)

    notes_dir = tmp_path / "memory"
    notes_dir.mkdir()
    note_path = notes_dir / f"{_make_note_name(10)}.md"
    content = "## Notes\n" + "\n".join(f"line {idx}" for idx in range(40)) + "\n"
    _write_note(note_path, content)

    report = compact_daily_notes(
        state_path=str(state_path),
        memory_dir=str(notes_dir),
        max_age_days=7,
        min_lines_to_compact=20,
        target_lines=8,
        dry_run=True,
    )

    graph_after, index_after, _ = load_state(str(state_path))
    assert report.files_compacted == 1
    assert report.nodes_injected == 0
    assert note_path.read_text(encoding="utf-8") == content
    assert graph_after.node_count() == nodes_before
    assert index_after._vectors == vectors_before
