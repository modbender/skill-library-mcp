from __future__ import annotations

from pathlib import Path

from workcrm import WorkCRMEngine, WorkCRMRepo


def test_task_assignee_persist_on_confirm(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    eng = WorkCRMEngine(repo)

    r1 = eng.handle('task company=Acme project=Site title="Email" assignee=Alice due=today')
    assert r1.pending is not None

    r2 = eng.handle("记")
    assert r2.wrote
    assert r2.result and "id" in r2.result

    task = repo.get_task(r2.result["id"])
    assert task is not None
    assert task["assignee"] == "Alice"
