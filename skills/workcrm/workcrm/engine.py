from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from typing import Optional

from .intent import detect_intent
from .parse import parse_freeform
from .types import EngineResponse, ProposedAction


_FAMILY_PREFIXES = ("family:", "家里:", "个人:")


class WorkCRMEngine:
    """Pure logic engine for intent -> propose -> confirm -> write."""

    def __init__(self, repo):
        # repo can be a single repo (work only) or a mapping: {"work": repo, "family": repo}
        self._repo = repo
        self._pending: Optional[ProposedAction] = None

    @property
    def pending(self) -> Optional[ProposedAction]:
        return self._pending

    def _select_repo_and_text(self, text: str):
        t = (text or "").strip()
        if isinstance(self._repo, dict):
            tl = t.lower()
            for p in _FAMILY_PREFIXES:
                if tl.startswith(p):
                    return self._repo["family"], t[len(p) :].lstrip()
            return self._repo["work"], t
        return self._repo, t

    def handle(self, text: str, *, now: Optional[datetime] = None) -> EngineResponse:
        repo, t = self._select_repo_and_text(text)

        if t in {"记", "不记"}:
            return self._handle_confirm(t)

        if t in {"草稿", "drafts", "待确认"}:
            rows = repo.list_drafts(status="pending")
            return EngineResponse(message=_fmt_pending_drafts(rows), wrote=False, result={"drafts": rows})

        intent = detect_intent(t)
        if intent.kind in {"log", "task"}:
            parsed = parse_freeform(t, now=now)
            preview = {
                "kind": intent.kind,
                "company": parsed.company,
                "project": parsed.project,
                "summary": parsed.summary if intent.kind == "log" else None,
                "title": parsed.title if intent.kind == "task" else None,
                "due_at": parsed.due_at,
                "assignee": parsed.assignee if intent.kind == "task" else None,
            }
            payload = {"intent": intent.kind, **asdict(parsed)}
            if isinstance(self._repo, dict):
                payload["_profile"] = "family" if repo is self._repo["family"] else "work"
            if payload.get("participants"):
                preview["participants"] = payload["participants"]
            draft = repo.create_draft(kind=intent.kind, preview=preview, payload=payload)
            self._pending = ProposedAction(
                kind=intent.kind,
                preview=preview,
                payload=payload,
                participants=payload.get("participants"),
                draft_id=draft["id"],
            )
            return EngineResponse(
                message=(
                    f"Draft {draft['id']} pending. Proposed {intent.kind}: {preview}. "
                    "Reply `记` to write, or `不记` to reject."
                ),
                pending=self._pending,
                wrote=False,
            )

        if intent.kind == "query":
            return EngineResponse(message="Query intent detected (MVP). No write performed.", wrote=False)

        return EngineResponse(message="No clear intent detected (MVP).", wrote=False)

    def _handle_confirm(self, token: str) -> EngineResponse:
        if not self._pending:
            return EngineResponse(message="Nothing pending.", wrote=False)

        if token == "不记":
            pa = self._pending
            self._pending = None
            r = self._repo
            if isinstance(r, dict):
                prof = pa.payload.get("_profile") or "work"
                r = r[prof]
            if pa.draft_id:
                r.set_draft_status(pa.draft_id, "rejected")
            return EngineResponse(message="Rejected draft.", wrote=False)

        assert token == "记"
        pa = self._pending
        self._pending = None

        r = self._repo
        if isinstance(r, dict):
            prof = pa.payload.get("_profile") or "work"
            r = r[prof]

        if pa.kind == "log":
            res = r.log_activity(
                company_name=pa.payload.get("company"),
                project_name=pa.payload.get("project"),
                summary=pa.payload.get("summary") or "",
                ts=now_utc(),
                source_text=None,
                participants=pa.payload.get("participants"),
            )
            if pa.draft_id:
                r.set_draft_status(pa.draft_id, "committed")
            return EngineResponse(message=f"Written activity {res['id']}.", wrote=True, result=res)

        if pa.kind == "task":
            res = r.create_task(
                company_name=pa.payload.get("company"),
                project_name=pa.payload.get("project"),
                title=pa.payload.get("title") or "",
                due_at=pa.payload.get("due_at"),
                assignee=pa.payload.get("assignee"),
                participants=pa.payload.get("participants"),
            )
            if pa.draft_id:
                r.set_draft_status(pa.draft_id, "committed")
            return EngineResponse(message=f"Written task {res['id']}.", wrote=True, result=res)

        return EngineResponse(message="Unknown pending action.", wrote=False)


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fmt_pending_drafts(rows: list[dict]) -> str:
    if not rows:
        return "No pending drafts."
    parts: list[str] = ["Pending drafts:"]
    for r in rows:
        parts.append(f"- {r['id']} {r['kind']} created_at={r['created_at']}")
    return "\n".join(parts)
