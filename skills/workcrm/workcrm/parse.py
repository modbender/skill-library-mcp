from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Optional


@dataclass(frozen=True)
class ParsedMessage:
    company: Optional[str]
    project: Optional[str]
    summary: Optional[str]
    title: Optional[str]
    due_at: Optional[str]
    assignee: Optional[str]
    participants: list[dict]


def _iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_due_at(token: str, *, now: Optional[datetime] = None) -> Optional[str]:
    if not token:
        return None
    now_dt = now or datetime.now(timezone.utc)
    t = token.strip().lower()

    if t in {"today", "tod"}:
        d = now_dt.date()
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat()
    if t == "tomorrow":
        d = now_dt.date() + timedelta(days=1)
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat()

    m = re.fullmatch(r"(\d+)(d)", t)
    if m:
        days = int(m.group(1))
        d = now_dt.date() + timedelta(days=days)
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat()

    # YYYY-MM-DD
    try:
        d = date.fromisoformat(t)
        return datetime(d.year, d.month, d.day, tzinfo=timezone.utc).isoformat()
    except ValueError:
        return None


def _parse_participants(t: str) -> list[dict]:
    m = re.search(r"\bparticipants=([^\n]+)", t)
    if not m:
        return []
    raw = m.group(1).strip()
    if raw.startswith('"') and raw.endswith('"'):
        raw = raw[1:-1]
    if not raw:
        return []

    out: list[dict] = []
    for item in [x.strip() for x in raw.split(",") if x.strip()]:
        if "#" in item:
            label, ref = item.split("#", 1)
            label = label.strip()
            ref = ref.strip()
            if ref.startswith("c:"):
                out.append({"label": label or ref, "ref": {"kind": "contact", "id": ref[2:]}})
            elif ref.startswith("o:"):
                out.append({"label": label or ref, "ref": {"kind": "organisation", "id": ref[2:]}})
            else:
                out.append({"label": item})
        else:
            out.append({"label": item})
    return out


def parse_freeform(text: str, *, now: Optional[datetime] = None) -> ParsedMessage:
    t = (text or "").strip()

    company = None
    project = None
    participants = _parse_participants(t)
    # Pattern: Company/Project
    m = re.search(r"([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", t)
    if m:
        company = m.group(1)
        project = m.group(2)

    # key=value tokens (very small MVP)
    def get_kv(key: str) -> Optional[str]:
        km = re.search(rf"\b{re.escape(key)}=([^\s]+)", t)
        return km.group(1) if km else None

    company = get_kv("company") or company
    project = get_kv("project") or project

    summary = None
    title = None

    sm = re.search(r"\bsummary=\"([^\"]+)\"", t)
    if sm:
        summary = sm.group(1)

    tm = re.search(r"\btitle=\"([^\"]+)\"", t)
    if tm:
        title = tm.group(1)

    due_tok = get_kv("due")
    due_at = parse_due_at(due_tok, now=now) if due_tok else None

    am = re.search(r"\bassignee=([^\s]+)", t)
    assignee = am.group(1) if am else None

    if not summary and not title:
        # fallback: use full text
        summary = t[:280] if t else None
        title = summary

    return ParsedMessage(
        company=company,
        project=project,
        summary=summary,
        title=title,
        due_at=due_at,
        assignee=assignee,
        participants=participants,
    )


__all__ = ["ParsedMessage", "parse_freeform", "parse_due_at", "_iso_now"]
