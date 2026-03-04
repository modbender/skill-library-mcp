from __future__ import annotations

from pathlib import Path

from workcrm import WorkCRMEngine, WorkCRMRepo


def test_no_write_without_confirm(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    eng = WorkCRMEngine(repo)

    # Propose a log
    r1 = eng.handle('log company=Acme project=Site summary="Call"')
    assert r1.pending is not None
    assert not r1.wrote

    # Random text should not write
    r2 = eng.handle("ok")
    assert not r2.wrote

    exported = repo.export_json()
    assert exported["activities"] == []

    # Cancel should discard
    r3 = eng.handle("不记")
    assert not r3.wrote
    assert eng.pending is None

    # Draft should be retained but marked rejected
    exported = repo.export_json()
    assert len(exported["drafts"]) == 1
    assert exported["drafts"][0]["status"] == "rejected"


def test_write_on_confirm(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    eng = WorkCRMEngine(repo)

    r1 = eng.handle('log company=Acme project=Site summary="Call"')
    assert r1.pending is not None

    r2 = eng.handle("记")
    assert r2.wrote
    assert r2.result and "id" in r2.result

    exported = repo.export_json()
    assert len(exported["activities"]) == 1

    # Draft should be retained and committed
    assert len(exported["drafts"]) == 1
    assert exported["drafts"][0]["status"] == "committed"
