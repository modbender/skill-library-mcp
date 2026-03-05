from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from workcrm import WorkCRMRepo


def test_schema_crud_basics(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    c = repo.create_company("Acme")
    p = repo.create_project(c["id"], "Website", stage="active")

    companies = repo.list_companies()
    projects = repo.list_projects(company_id=c["id"])

    assert [x["name"] for x in companies] == ["Acme"]
    assert [x["name"] for x in projects] == ["Website"]

    act = repo.log_activity(company_name="Acme", project_name="Website", summary="Kickoff", ts=None, source_text=None)
    task = repo.create_task(company_name="Acme", project_name="Website", title="Send proposal", due_at=None)

    assert act["company_id"] == c["id"]
    assert task["project_id"] == p["id"]


def test_digest_ordering(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")

    now = datetime(2026, 2, 14, 0, 0, 0, tzinfo=timezone.utc).isoformat()

    repo.create_task(company_name="Acme", project_name="Site", title="Overdue", due_at="2026-02-10T00:00:00+00:00")
    repo.create_task(company_name="Acme", project_name="Site", title="Due today", due_at="2026-02-14T00:00:00+00:00")
    repo.create_task(company_name="Acme", project_name="Site", title="Later", due_at="2026-02-20T00:00:00+00:00")

    digest = repo.followup_digest(now=now)
    assert [t["title"] for t in digest] == ["Overdue", "Due today"]


def test_export_json_valid(tmp_path: Path) -> None:
    repo = WorkCRMRepo(tmp_path / "wcrm.sqlite")
    repo.create_company("Acme")
    data = repo.export_json()
    json.dumps(data)
    for k in [
        "companies",
        "projects",
        "organisations",
        "contacts",
        "activities",
        "tasks",
        "participants",
        "drafts",
    ]:
        assert k in data
