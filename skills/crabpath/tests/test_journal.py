from __future__ import annotations

from pathlib import Path

from crabpath.journal import journal_stats, log_learn, log_query, read_journal


def test_log_query_appends(tmp_path: Path) -> None:
    """test log query appends."""
    path = tmp_path / "journal.jsonl"
    log_query(query_text="deploy", fired_ids=["a", "b", "c"], node_count=3, journal_path=str(path))

    entries = read_journal(journal_path=str(path))
    assert len(entries) == 1
    assert entries[0]["type"] == "query"
    assert entries[0]["query"] == "deploy"
    assert entries[0]["fired"] == ["a", "b", "c"]
    assert entries[0]["fired_count"] == 3
    assert "ts" in entries[0]
    assert "iso" in entries[0]


def test_log_query_defaults_node_count_to_fired_ids_length(tmp_path: Path) -> None:
    """test log query defaults node_count to len(fired_ids)."""
    path = tmp_path / "journal.jsonl"
    log_query(query_text="deploy", fired_ids=["a", "b", "c"], journal_path=str(path))

    entries = read_journal(journal_path=str(path))
    assert len(entries) == 1
    assert entries[0]["fired_count"] == 3
    assert entries[0]["node_count"] == 3


def test_log_learn_appends(tmp_path: Path) -> None:
    """test log learn appends."""
    path = tmp_path / "journal.jsonl"
    log_learn(fired_ids=["a"], outcome=0.75, journal_path=str(path))

    entries = read_journal(journal_path=str(path))
    assert len(entries) == 1
    assert entries[0]["type"] == "learn"
    assert entries[0]["fired"] == ["a"]
    assert entries[0]["outcome"] == 0.75


def test_log_query_and_learn_include_metadata(tmp_path: Path) -> None:
    """test log query and learn include metadata."""
    path = tmp_path / "journal.jsonl"
    log_query(
        query_text="deploy",
        fired_ids=["a"],
        node_count=1,
        journal_path=str(path),
        metadata={"session_id": "abc"},
    )
    log_learn(fired_ids=["a"], outcome=1.0, journal_path=str(path), metadata={"session_id": "abc"})

    entries = read_journal(journal_path=str(path))
    assert entries[0]["metadata"] == {"session_id": "abc"}
    assert entries[1]["metadata"] == {"session_id": "abc"}


def test_read_journal_last_n(tmp_path: Path) -> None:
    """test read journal last n."""
    path = tmp_path / "journal.jsonl"
    for idx in range(5):
        log_query(query_text=f"q{idx}", fired_ids=[f"n{idx}"], node_count=10, journal_path=str(path))

    entries = read_journal(journal_path=str(path), last_n=2)
    assert len(entries) == 2
    assert entries[0]["query"] == "q3"
    assert entries[1]["query"] == "q4"


def test_journal_stats(tmp_path: Path) -> None:
    """test journal stats."""
    path = tmp_path / "journal.jsonl"
    log_query(query_text="q1", fired_ids=["a", "b"], node_count=2, journal_path=str(path))
    log_query(query_text="q2", fired_ids=["c"], node_count=2, journal_path=str(path))
    log_learn(fired_ids=["a"], outcome=1.0, journal_path=str(path))
    log_learn(fired_ids=["a"], outcome=-1.0, journal_path=str(path))

    stats = journal_stats(journal_path=str(path))
    assert stats["total_entries"] == 4
    assert stats["queries"] == 2
    assert stats["learns"] == 2
    assert stats["positive_outcomes"] == 1
    assert stats["negative_outcomes"] == 1
    assert stats["avg_fired_per_query"] == 1.5


def test_empty_journal(tmp_path: Path) -> None:
    """test empty journal."""
    path = tmp_path / "missing-journal.jsonl"
    assert read_journal(journal_path=str(path)) == []
    assert journal_stats(journal_path=str(path)) == {
        "total_entries": 0,
        "queries": 0,
        "learns": 0,
        "positive_outcomes": 0,
        "negative_outcomes": 0,
        "avg_fired_per_query": 0,
    }
