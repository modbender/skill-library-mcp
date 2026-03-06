from __future__ import annotations

from pathlib import Path

from workcrm import WorkCRMEngine, WorkCRMRepo


def test_participants_persist_on_confirm(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    eng = WorkCRMEngine(repo)

    r1 = eng.handle(
        'log company=Acme project=Site summary="Call" participants="Alice#c:123,Bob"'
    )
    assert r1.pending is not None

    r2 = eng.handle("记")
    assert r2.wrote

    data = repo.export_json()
    assert len(data["activities"]) == 1
    assert len(data["participants"]) == 2
    labels = [p["label"] for p in data["participants"]]
    assert labels == ["Alice", "Bob"]


def test_list_pending_drafts_deterministic(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    eng = WorkCRMEngine(repo)

    eng.handle('log company=Acme project=Site summary="One"')
    eng.handle('task company=Acme project=Site title="Two" due=today')

    r = eng.handle("草稿")
    assert not r.wrote
    assert r.result and "drafts" in r.result
    drafts = r.result["drafts"]
    assert [d["status"] for d in drafts] == ["pending", "pending"]
    assert [d["kind"] for d in drafts] == ["log", "task"]
