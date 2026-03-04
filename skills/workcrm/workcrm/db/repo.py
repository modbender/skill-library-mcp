from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ..types import ProjectStage
from .migrate import apply_migrations

_ALLOWED_STAGES: set[str] = {"intake", "active", "waiting", "blocked", "paused", "done"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class WorkCRMRepo:
    def __init__(self, db_path: str | Path):
        self._db_path = str(db_path)

    def create_organisation(self, name: str, *, notes: str | None = None) -> dict:
        now = _utc_now()
        oid = str(uuid.uuid4())
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO organisation(id,name,notes,created_at,updated_at,archived_at) VALUES (?,?,?,?,?,NULL)",
                (oid, name, notes, now, now),
            )
        return {"id": oid, "name": name, "notes": notes, "created_at": now, "updated_at": now}

    def create_contact(
        self,
        name: str,
        *,
        org_id: str | None = None,
        notes: str | None = None,
        channel_handles: dict | None = None,
    ) -> dict:
        now = _utc_now()
        cid = str(uuid.uuid4())
        ch = json.dumps(channel_handles or {}, sort_keys=True) if channel_handles is not None else None
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO contact(id,company_id,org_id,name,role,email,phone,wechat,channel_handles,notes,created_at,updated_at,archived_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,NULL)",
                (cid, None, org_id, name, None, None, None, None, ch, notes, now, now),
            )
        return {
            "id": cid,
            "org_id": org_id,
            "name": name,
            "channel_handles": json.loads(ch) if ch else {},
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }

    def _insert_participants(
        self,
        conn: sqlite3.Connection,
        *,
        parent_kind: str,
        parent_id: str,
        participants: list[dict],
    ) -> None:
        now = _utc_now()
        for idx, p in enumerate(participants):
            label = (p.get("label") or "").strip()
            if not label:
                continue
            pid = str(uuid.uuid4())
            ref = p.get("ref") or {}
            ref_kind = ref.get("kind")
            ref_id = ref.get("id")
            conn.execute(
                "INSERT OR IGNORE INTO participant(id,parent_kind,parent_id,ordinal,label,ref_kind,ref_id,created_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (pid, parent_kind, parent_id, idx, label, ref_kind, ref_id, now),
            )

    def create_draft(self, *, kind: str, preview: dict, payload: dict) -> dict:
        now = _utc_now()
        did = str(uuid.uuid4())
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO draft(id,kind,status,preview,payload,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
                (
                    did,
                    kind,
                    "pending",
                    json.dumps(preview, sort_keys=True),
                    json.dumps(payload, sort_keys=True),
                    now,
                    now,
                ),
            )
        return {"id": did, "kind": kind, "status": "pending", "created_at": now, "updated_at": now}

    def set_draft_status(self, draft_id: str, status: str) -> None:
        now = _utc_now()
        with self.connect() as conn:
            conn.execute(
                "UPDATE draft SET status=?, updated_at=? WHERE id=?",
                (status, now, draft_id),
            )

    def list_drafts(self, *, status: str | None = None) -> list[dict]:
        with self.connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT id,kind,status,created_at,updated_at FROM draft WHERE status=? "
                    "ORDER BY created_at, kind, id",
                    (status,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id,kind,status,created_at,updated_at FROM draft ORDER BY created_at, kind, id"
                ).fetchall()
        return [dict(r) for r in rows]

    def get_activity(self, activity_id: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM activity WHERE id=?", (activity_id,)).fetchone()
            if not row:
                return None
        return dict(row)

    def get_task(self, task_id: str) -> dict | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM task WHERE id=?", (task_id,)).fetchone()
            if not row:
                return None
        return dict(row)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        apply_migrations(conn)
        return conn

    def create_company(self, name: str, *, domain: str | None = None, notes: str | None = None) -> dict:
        now = _utc_now()
        cid = str(uuid.uuid4())
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO company(id,name,domain,notes,created_at,updated_at,archived_at) VALUES (?,?,?,?,?,?,NULL)",
                (cid, name, domain, notes, now, now),
            )
        return {"id": cid, "name": name, "domain": domain, "notes": notes, "created_at": now, "updated_at": now}

    def list_companies(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM company WHERE archived_at IS NULL ORDER BY created_at, id").fetchall()
        return [dict(r) for r in rows]

    def create_project(
        self,
        company_id: str,
        name: str,
        *,
        stage: ProjectStage = "active",
        notes: str | None = None,
    ) -> dict:
        if stage not in _ALLOWED_STAGES:
            raise ValueError(f"invalid project stage: {stage}")
        now = _utc_now()
        pid = str(uuid.uuid4())
        with self.connect() as conn:
            conn.execute(
                "INSERT INTO project(id,company_id,name,stage,notes,created_at,updated_at,archived_at) VALUES (?,?,?,?,?,?,?,NULL)",
                (pid, company_id, name, stage, notes, now, now),
            )
        return {
            "id": pid,
            "company_id": company_id,
            "name": name,
            "stage": stage,
            "notes": notes,
            "created_at": now,
            "updated_at": now,
        }

    def list_projects(self, *, company_id: Optional[str] = None) -> list[dict]:
        with self.connect() as conn:
            if company_id:
                rows = conn.execute(
                    "SELECT * FROM project WHERE archived_at IS NULL AND company_id=? ORDER BY created_at, id",
                    (company_id,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM project WHERE archived_at IS NULL ORDER BY created_at, id").fetchall()
        return [dict(r) for r in rows]

    def _get_or_create_company(self, conn: sqlite3.Connection, name: str) -> str:
        row = conn.execute("SELECT id FROM company WHERE name=? AND archived_at IS NULL", (name,)).fetchone()
        if row:
            return row[0]
        now = _utc_now()
        cid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO company(id,name,domain,notes,created_at,updated_at,archived_at) VALUES (?,?,?,?,?,?,NULL)",
            (cid, name, None, None, now, now),
        )
        return cid

    def _get_or_create_project(self, conn: sqlite3.Connection, company_id: str, name: str) -> str:
        row = conn.execute(
            "SELECT id FROM project WHERE company_id=? AND name=? AND archived_at IS NULL",
            (company_id, name),
        ).fetchone()
        if row:
            return row[0]
        now = _utc_now()
        pid = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO project(id,company_id,name,stage,notes,created_at,updated_at,archived_at) VALUES (?,?,?,?,?,?,?,NULL)",
            (pid, company_id, name, "active", None, now, now),
        )
        return pid

    def log_activity(
        self,
        *,
        company_name: str | None,
        project_name: str | None,
        summary: str,
        ts: str | None,
        source_text: str | None,
        participants: list[dict] | None = None,
    ) -> dict:
        now = _utc_now()
        aid = str(uuid.uuid4())
        with self.connect() as conn:
            company_id = self._get_or_create_company(conn, company_name) if company_name else None
            project_id = None
            if project_name and company_id:
                project_id = self._get_or_create_project(conn, company_id, project_name)
            act_ts = ts or now
            conn.execute(
                "INSERT INTO activity(id,company_id,project_id,contact_id,ts,channel,summary,details,source_text,created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?)",
                (aid, company_id, project_id, None, act_ts, "chat", summary, None, source_text, now),
            )
            if participants:
                self._insert_participants(conn, parent_kind="activity", parent_id=aid, participants=participants)
        return {"id": aid, "company_id": company_id, "project_id": project_id, "ts": act_ts, "summary": summary}

    def create_task(
        self,
        *,
        company_name: str | None,
        project_name: str | None,
        title: str,
        due_at: str | None,
        assignee: str | None = None,
        participants: list[dict] | None = None,
    ) -> dict:
        now = _utc_now()
        tid = str(uuid.uuid4())
        with self.connect() as conn:
            company_id = self._get_or_create_company(conn, company_name) if company_name else None
            project_id = None
            if project_name and company_id:
                project_id = self._get_or_create_project(conn, company_id, project_name)
            conn.execute(
                "INSERT INTO task(id,company_id,project_id,contact_id,created_from_activity_id,title,assignee,notes,due_at,status,priority,created_at,updated_at,done_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (tid, company_id, project_id, None, None, title, assignee, None, due_at, "open", 0, now, now, None),
            )
            if participants:
                self._insert_participants(conn, parent_kind="task", parent_id=tid, participants=participants)
        return {"id": tid, "company_id": company_id, "project_id": project_id, "title": title, "due_at": due_at}

    def get_project_review(self, project_id: str, *, limit_activities: int = 5) -> dict:
        with self.connect() as conn:
            proj = conn.execute("SELECT * FROM project WHERE id=?", (project_id,)).fetchone()
            if not proj:
                raise KeyError("project not found")
            acts = conn.execute(
                "SELECT * FROM activity WHERE project_id=? ORDER BY ts DESC, id DESC LIMIT ?",
                (project_id, limit_activities),
            ).fetchall()
            tasks = conn.execute(
                "SELECT * FROM task WHERE project_id=? AND status='open' ORDER BY due_at IS NULL, due_at, created_at, id",
                (project_id,),
            ).fetchall()
        return {"project": dict(proj), "recent_activities": [dict(a) for a in acts], "open_tasks": [dict(t) for t in tasks]}

    def followup_digest(self, *, now: str, days_ahead: int = 0) -> list[dict]:
        """Return open tasks due up to cutoff (inclusive). Ordered deterministically."""
        # MVP: treat due_at as ISO8601 date-time string; lexical order matches chronological.
        cutoff = now
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM task WHERE status='open' AND due_at IS NOT NULL AND due_at<=? "
                "ORDER BY due_at, created_at, id",
                (cutoff,),
            ).fetchall()
        return [dict(r) for r in rows]

    def export_json(self) -> dict[str, Any]:
        with self.connect() as conn:
            def q(table: str) -> list[dict]:
                rows = conn.execute(
                    f"SELECT * FROM {table} ORDER BY created_at, parent_kind, parent_id, ordinal, id"
                    if table == "participant"
                    else f"SELECT * FROM {table} ORDER BY created_at, id"
                ).fetchall()
                return [dict(r) for r in rows]

            data = {
                "schema_version": 2,
                "exported_at": _utc_now(),
                "companies": q("company"),
                "projects": q("project"),
                "organisations": q("organisation"),
                "contacts": q("contact"),
                "activities": q("activity"),
                "tasks": q("task"),
                "participants": q("participant"),
                "drafts": q("draft"),
            }
        # Ensure JSON-serializable
        json.dumps(data, sort_keys=True)
        return data
