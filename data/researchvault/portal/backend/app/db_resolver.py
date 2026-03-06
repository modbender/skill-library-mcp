from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

import scripts.db as vault_db

from portal.backend.app.db_roots import allowed_db_roots, path_within_allowed_roots
from portal.backend.app.portal_state import get_selected_db_path

def _expand_abs(p: str) -> str:
    return str(Path(os.path.expanduser(p)).resolve())


def _sqlite_uri_readonly(path: str) -> str:
    # Keep '/' unescaped; escape spaces and other unsafe chars.
    return "file:" + quote(path, safe="/") + "?mode=ro"


def _table_exists(cursor: sqlite3.Cursor, table: str) -> bool:
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,))
    return cursor.fetchone() is not None


def _safe_int(v: Any) -> Optional[int]:
    try:
        return int(v)
    except Exception:
        return None


@dataclass(frozen=True)
class DbStats:
    schema_version: Optional[int]
    counts: Dict[str, int]
    last_finding_at: Optional[str]
    last_event_at: Optional[str]


@dataclass(frozen=True)
class DbCandidate:
    path: str
    exists: bool
    size_bytes: Optional[int]
    mtime_s: Optional[float]
    stats: Optional[DbStats]
    error: Optional[str]


@dataclass(frozen=True)
class ResolvedDb:
    path: str
    source: str  # selected|env|auto
    note: str


def inspect_db(path: str) -> DbCandidate:
    p = _expand_abs(path)
    pp = Path(p)
    if not pp.exists():
        return DbCandidate(path=p, exists=False, size_bytes=None, mtime_s=None, stats=None, error=None)

    try:
        st = pp.stat()
        size_bytes = int(st.st_size)
        mtime_s = float(st.st_mtime)
    except Exception:
        size_bytes = None
        mtime_s = None

    try:
        uri = _sqlite_uri_readonly(p)
        conn = sqlite3.connect(uri, uri=True, timeout=1.0)
        c = conn.cursor()

        schema_version = None
        if _table_exists(c, "schema_version"):
            c.execute("SELECT version FROM schema_version")
            row = c.fetchone()
            schema_version = _safe_int(row[0]) if row else None

        counts: Dict[str, int] = {}
        for t in [
            "projects",
            "findings",
            "events",
            "artifacts",
            "links",
            "branches",
            "hypotheses",
            "verification_missions",
            "watch_targets",
        ]:
            if _table_exists(c, t):
                c.execute(f"SELECT COUNT(*) FROM {t}")
                counts[t] = int(c.fetchone()[0])
            else:
                counts[t] = 0

        last_finding_at = None
        if _table_exists(c, "findings"):
            c.execute("SELECT MAX(created_at) FROM findings")
            row = c.fetchone()
            last_finding_at = str(row[0]) if row and row[0] else None

        last_event_at = None
        if _table_exists(c, "events"):
            c.execute("SELECT MAX(timestamp) FROM events")
            row = c.fetchone()
            last_event_at = str(row[0]) if row and row[0] else None

        conn.close()
        return DbCandidate(
            path=p,
            exists=True,
            size_bytes=size_bytes,
            mtime_s=mtime_s,
            stats=DbStats(
                schema_version=schema_version,
                counts=counts,
                last_finding_at=last_finding_at,
                last_event_at=last_event_at,
            ),
            error=None,
        )
    except Exception as e:
        return DbCandidate(
            path=p,
            exists=True,
            size_bytes=size_bytes,
            mtime_s=mtime_s,
            stats=None,
            error=str(e),
        )


def _dedup_paths(paths: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    out: List[str] = []
    for p in paths:
        ap = _expand_abs(p)
        if ap in seen:
            continue
        seen.add(ap)
        out.append(ap)
    return out


def _allowed_path(path: str) -> bool:
    return path_within_allowed_roots(Path(os.path.expanduser(path)))


def _fallback_default_db_path() -> str:
    default = _expand_abs(vault_db.DEFAULT_DB_PATH)
    if _allowed_path(default):
        return default
    roots = allowed_db_roots()
    if roots:
        return str((roots[0] / Path(default).name).resolve())
    return default


def discover_candidate_paths() -> List[str]:
    paths: List[str] = []

    selected = get_selected_db_path()
    if selected and _allowed_path(selected):
        paths.append(selected)

    env = os.getenv("RESEARCHVAULT_DB")
    if env and _allowed_path(env):
        paths.append(env)

    # Known defaults (kept in scripts.db for consistency) if allowed by root policy.
    if _allowed_path(vault_db.DEFAULT_DB_PATH):
        paths.append(vault_db.DEFAULT_DB_PATH)

    # "Nearby" vaults (lightweight globbing; do not recurse).
    paths.extend([str(p) for p in Path(os.path.expanduser("~/.researchvault")).glob("*.db")])
    paths.extend([str(p) for p in Path(os.path.expanduser("~/.researchvault")).glob("*.sqlite*")])

    return [p for p in _dedup_paths(paths) if _allowed_path(p)]


def list_db_candidates() -> List[DbCandidate]:
    return [inspect_db(p) for p in discover_candidate_paths()]


def _activity_score(c: DbCandidate) -> Tuple[int, float]:
    # Prefer DBs that actually contain projects/findings; fall back to mtime.
    if not c.exists or not c.stats:
        return (0, 0.0)
    counts = c.stats.counts
    projects = int(counts.get("projects", 0))
    findings = int(counts.get("findings", 0))
    events = int(counts.get("events", 0))
    artifacts = int(counts.get("artifacts", 0))
    missions = int(counts.get("verification_missions", 0))
    links = int(counts.get("links", 0))
    score = projects * 1_000_000 + findings * 10_000 + artifacts * 1_000 + events * 100 + missions * 10 + links
    return (int(score), float(c.mtime_s or 0.0))


def resolve_current_db() -> Tuple[ResolvedDb, List[DbCandidate]]:
    candidates = list_db_candidates()

    return (resolve_effective_db(), candidates)


def resolve_effective_db() -> ResolvedDb:
    """Resolve the effective DB path without doing a full candidate scan."""
    selected = get_selected_db_path()
    if selected and _allowed_path(selected):
        p = _expand_abs(selected)
        exists = Path(p).exists()
        note = "User-selected DB path (persisted)."
        if not exists:
            note += " (DB file does not exist yet; it will be created on first write.)"
        return ResolvedDb(path=p, source="selected", note=note)

    env = os.getenv("RESEARCHVAULT_DB")
    if env and _allowed_path(env):
        p = _expand_abs(env)
        exists = Path(p).exists()
        note = "From RESEARCHVAULT_DB environment variable."
        if not exists:
            note += " (DB file does not exist yet; it will be created on first write.)"
        return ResolvedDb(path=p, source="env", note=note)

    default = inspect_db(vault_db.DEFAULT_DB_PATH) if _allowed_path(vault_db.DEFAULT_DB_PATH) else inspect_db(_fallback_default_db_path())

    if default.exists:
        return ResolvedDb(path=default.path, source="auto", note="Only default DB exists.")

    return ResolvedDb(
        path=_fallback_default_db_path(),
        source="auto",
        note="No existing DB found; default path will be created on first write.",
    )


def candidates_as_dict(cands: List[DbCandidate]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for c in cands:
        out.append(
            {
                "path": c.path,
                "exists": c.exists,
                "size_bytes": c.size_bytes,
                "mtime_s": c.mtime_s,
                "error": c.error,
                "schema_version": c.stats.schema_version if c.stats else None,
                "counts": c.stats.counts if c.stats else None,
                "last_finding_at": c.stats.last_finding_at if c.stats else None,
                "last_event_at": c.stats.last_event_at if c.stats else None,
            }
        )
    return out


def resolved_as_dict(res: ResolvedDb) -> Dict[str, Any]:
    # Keep a stable wire format for the frontend.
    cand = inspect_db(res.path)
    return {
        "path": res.path,
        "source": res.source,
        "note": res.note,
        "exists": cand.exists,
        "size_bytes": cand.size_bytes,
        "mtime_s": cand.mtime_s,
        "schema_version": cand.stats.schema_version if cand.stats else None,
        "counts": cand.stats.counts if cand.stats else None,
        "last_finding_at": cand.stats.last_finding_at if cand.stats else None,
        "last_event_at": cand.stats.last_event_at if cand.stats else None,
    }


def now_ms() -> int:
    return int(time.time() * 1000)
