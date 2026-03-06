from __future__ import annotations

from dataclasses import dataclass

from workcrm import WorkCRMEngine, WorkCRMRepo


@dataclass(frozen=True)
class StubIntent:
    kind: str
    score: int = 100


def test_family_prefix_routes_to_family_repo(tmp_path, monkeypatch) -> None:
    # Force engine to treat messages as 'log' regardless of content.
    import workcrm.engine as eng_mod

    monkeypatch.setattr(eng_mod, "detect_intent", lambda _t: StubIntent(kind="log"))

    work_repo = WorkCRMRepo(tmp_path / "work.sqlite")
    family_repo = WorkCRMRepo(tmp_path / "family.sqlite")

    eng = WorkCRMEngine({"work": work_repo, "family": family_repo})

    eng.handle('family: log company=Acme project=Site summary="Call"')
    eng.handle("记")

    assert work_repo.export_json()["activities"] == []
    assert len(family_repo.export_json()["activities"]) == 1


def test_chinese_prefix_routes_to_family_repo(tmp_path, monkeypatch) -> None:
    import workcrm.engine as eng_mod

    monkeypatch.setattr(eng_mod, "detect_intent", lambda _t: StubIntent(kind="task"))

    work_repo = WorkCRMRepo(tmp_path / "work.sqlite")
    family_repo = WorkCRMRepo(tmp_path / "family.sqlite")

    eng = WorkCRMEngine({"work": work_repo, "family": family_repo})

    eng.handle('家里: task company=Acme project=Site title="Ping" due=today')
    eng.handle("记")

    assert work_repo.export_json()["tasks"] == []
    assert len(family_repo.export_json()["tasks"]) == 1
