from __future__ import annotations

import asyncio
import os
import platform
import sqlite3
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from portal.backend.app.auth import require_session
from portal.backend.app.db_roots import allowed_db_roots_as_strings, path_within_allowed_roots
from portal.backend.app.db_resolver import (
    candidates_as_dict,
    inspect_db,
    now_ms,
    resolve_current_db,
    resolve_effective_db,
    resolved_as_dict,
)
from portal.backend.app.portal_secrets import (
    clear_brave_api_key,
    clear_searxng_base_url,
    clear_serper_api_key,
    secrets_status,
    set_brave_api_key,
    set_searxng_base_url,
    set_serper_api_key,
)
from portal.backend.app.portal_state import set_selected_db_path
from portal.backend.app.vault_exec import run_vault


router = APIRouter(prefix="/system", dependencies=[Depends(require_session)])


def _sqlite_uri_readonly(path: str) -> str:
    return "file:" + quote(path, safe="/") + "?mode=ro"


def _safe_id_part(raw: str) -> str:
    import re

    return re.sub(r"[^a-zA-Z0-9_-]", "_", (raw or "").strip())


def _make_branch_id(project_id: str, branch_name: str) -> str:
    return f"br_{_safe_id_part(project_id)}_{_safe_id_part(branch_name)}"


def _table_exists(cursor: sqlite3.Cursor, table: str) -> bool:
    cursor.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1", (table,))
    return cursor.fetchone() is not None


def _allowed_db_path(p: Path) -> bool:
    return path_within_allowed_roots(p)


class DbSelectRequest(BaseModel):
    path: Optional[str] = Field(default=None, description="Absolute or ~-relative path to a SQLite DB file.")


class BraveKeyRequest(BaseModel):
    api_key: str = Field(min_length=10, max_length=500)

class SerperKeyRequest(BaseModel):
    api_key: str = Field(min_length=10, max_length=500)


class SearxngBaseUrlRequest(BaseModel):
    base_url: str = Field(min_length=4, max_length=500)


def _secret_write_response(fn):
    try:
        return fn()
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dbs")
def system_list_dbs():
    resolved, candidates = resolve_current_db()
    return {
        "now_ms": now_ms(),
        "current": resolved_as_dict(resolved),
        "candidates": candidates_as_dict(candidates),
    }


@router.get("/secrets/status")
def system_secrets_status():
    st = secrets_status()
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/brave")
def system_set_brave_key(req: BraveKeyRequest):
    st = _secret_write_response(lambda: set_brave_api_key(req.api_key))
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/brave/clear")
def system_clear_brave_key():
    st = _secret_write_response(clear_brave_api_key)
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/serper")
def system_set_serper_key(req: SerperKeyRequest):
    st = _secret_write_response(lambda: set_serper_api_key(req.api_key))
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/serper/clear")
def system_clear_serper_key():
    st = _secret_write_response(clear_serper_api_key)
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/searxng")
def system_set_searxng_base_url(req: SearxngBaseUrlRequest):
    st = _secret_write_response(lambda: set_searxng_base_url(req.base_url))
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/secrets/searxng/clear")
def system_clear_searxng_base_url():
    st = _secret_write_response(clear_searxng_base_url)
    return {
        "brave_api_key_configured": bool(st.brave_api_key_configured),
        "brave_api_key_source": st.brave_api_key_source,
        "serper_api_key_configured": bool(st.serper_api_key_configured),
        "serper_api_key_source": st.serper_api_key_source,
        "searxng_base_url_configured": bool(st.searxng_base_url_configured),
        "searxng_base_url_source": st.searxng_base_url_source,
        "searxng_base_url": st.searxng_base_url,
    }


@router.post("/db/select")
def system_select_db(req: DbSelectRequest):
    if req.path:
        p = Path(os.path.expanduser(req.path))
        if p.is_dir():
            raise HTTPException(status_code=400, detail="DB path must be a file, not a directory.")
        if not _allowed_db_path(p):
            raise HTTPException(
                status_code=400,
                detail="DB path is outside allowed roots. Update RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS to include the path.",
            )

    set_selected_db_path(req.path)
    resolved, candidates = resolve_current_db()
    return {
        "now_ms": now_ms(),
        "current": resolved_as_dict(resolved),
        "candidates": candidates_as_dict(candidates),
    }


@router.get("/diagnostics")
def system_diagnostics():
    resolved, candidates = resolve_current_db()
    dbc = inspect_db(resolved.path)
    secrets = secrets_status()

    # CLI probe: if this fails, the Portal isn't actually talking to the vault CLI.
    cli = run_vault(["list", "--format", "json"], timeout_s=30, db_path=resolved.path)
    cli_ok = cli.exit_code == 0
    cli_projects = None
    cli_parse_error = None
    if cli_ok:
        try:
            import json

            rows = json.loads(cli.stdout or "[]")
            cli_projects = len(rows) if isinstance(rows, list) else None
        except Exception as e:
            cli_parse_error = str(e)

    # Heuristic: if current DB looks empty but another candidate has data, recommend switching.
    best = None
    best_score = -1
    for c in candidates:
        if not c.exists or not c.stats:
            continue
        score = int(c.stats.counts.get("projects", 0)) * 1_000_000 + int(c.stats.counts.get("findings", 0)) * 10_000
        if score > best_score:
            best_score = score
            best = c

    hints: List[Dict[str, Any]] = []
    current_projects = (dbc.stats.counts.get("projects", 0) if dbc.stats else None) if dbc.exists else None
    current_findings = (dbc.stats.counts.get("findings", 0) if dbc.stats else None) if dbc.exists else None
    if best and best.path != resolved.path:
        if (current_projects or 0) == 0 and int(best.stats.counts.get("projects", 0)) > 0:
            hints.append(
                {
                    "type": "db_split",
                    "severity": "high",
                    "title": "Portal appears to be reading an empty DB",
                    "detail": "Another vault DB on disk contains projects. Switch the active DB to match your CLI research.",
                    "recommend_db_path": best.path,
                }
            )

    if cli_ok and cli_projects is not None and dbc.stats:
        db_projects = int(dbc.stats.counts.get("projects", 0))
        if abs(db_projects - cli_projects) > 0:
            # This should not happen because we force RESEARCHVAULT_DB in vault_exec.
            hints.append(
                {
                    "type": "cli_db_mismatch",
                    "severity": "high",
                    "title": "CLI output does not match direct DB counts",
                    "detail": "This suggests the CLI and backend are reading different DB paths. Check env and selection.",
                    "db_projects": db_projects,
                    "cli_projects": cli_projects,
                }
            )

    # If no "strong" provider is configured, searches will fall back to best-effort providers.
    if (not secrets.brave_api_key_configured) and (not secrets.serper_api_key_configured) and (not secrets.searxng_base_url_configured):
        needs_search = False
        if dbc.stats:
            needs_search = bool(
                dbc.stats.counts.get("watch_targets", 0)
                or dbc.stats.counts.get("verification_missions", 0)
            )
        if needs_search:
            hints.append(
                {
                    "type": "search_provider_setup",
                    "severity": "medium",
                    "title": "No API-backed search provider configured",
                    "detail": "The vault will fall back to best-effort providers (DuckDuckGo/Wikipedia). Configure Brave (or Serper/SearxNG) for higher quality and consistency.",
                }
            )

    return {
        "now_ms": now_ms(),
        "backend": {
            "python": sys.version.split(" ")[0],
            "platform": platform.platform(),
            "pid": os.getpid(),
        },
        "env": {
            "RESEARCHVAULT_DB": os.getenv("RESEARCHVAULT_DB"),
            "RESEARCHVAULT_SEARCH_PROVIDERS": os.getenv("RESEARCHVAULT_SEARCH_PROVIDERS"),
            "RESEARCHVAULT_WATCHDOG_INGEST_TOP": os.getenv("RESEARCHVAULT_WATCHDOG_INGEST_TOP"),
            "RESEARCHVAULT_VERIFY_INGEST_TOP": os.getenv("RESEARCHVAULT_VERIFY_INGEST_TOP"),
            "RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS": os.getenv("RESEARCHVAULT_PORTAL_ALLOWED_DB_ROOTS"),
            "RESEARCHVAULT_PORTAL_TOKEN_set": bool(os.getenv("RESEARCHVAULT_PORTAL_TOKEN")),
            "BRAVE_API_KEY_set": bool(os.getenv("BRAVE_API_KEY")),
            "SERPER_API_KEY_set": bool(os.getenv("SERPER_API_KEY")),
            "SEARXNG_BASE_URL_set": bool(os.getenv("SEARXNG_BASE_URL")),
            "effective_allowed_db_roots": allowed_db_roots_as_strings(),
        },
        "providers": {
            "brave": {
                "configured": bool(secrets.brave_api_key_configured),
                "source": secrets.brave_api_key_source,
            },
            "serper": {
                "configured": bool(secrets.serper_api_key_configured),
                "source": secrets.serper_api_key_source,
            },
            "searxng": {
                "configured": bool(secrets.searxng_base_url_configured),
                "source": secrets.searxng_base_url_source,
                "base_url": secrets.searxng_base_url,
            },
            "duckduckgo": {"configured": True, "source": "built_in"},
            "wikipedia": {"configured": True, "source": "built_in"},
        },
        "db": {
            "current": resolved_as_dict(resolved),
            "candidates": candidates_as_dict(candidates),
        },
        "cli": {
            "ok": cli_ok,
            "exit_code": cli.exit_code,
            "stderr": cli.stderr,
            "truncated": cli.truncated,
            "projects_parsed": cli_projects,
            "parse_error": cli_parse_error,
        },
        "hints": hints,
        "snapshot": {
            "current_projects": current_projects,
            "current_findings": current_findings,
        },
    }


def _sse_event(event: str, data: Any) -> str:
    import json

    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'), default=str)}\n\n"


@router.get("/stream")
async def system_stream(
    interval_s: float = Query(default=2.0, ge=0.5, le=30.0),
):
    async def gen():
        last_signature = None
        last_candidates_at = 0.0

        while True:
            resolved = resolve_effective_db()
            info = inspect_db(resolved.path)

            signature = (
                resolved.path,
                resolved.source,
                info.exists,
                info.size_bytes,
                info.mtime_s,
                (tuple(sorted((info.stats.counts or {}).items())) if info.stats else None),
            )

            payload = {
                "now_ms": now_ms(),
                "db": resolved_as_dict(resolved),
            }

            # Always send a pulse on first connect; afterward only when something changes.
            if last_signature is None:
                yield _sse_event("hello", payload)
                last_signature = signature
            elif signature != last_signature:
                yield _sse_event("pulse", payload)
                last_signature = signature
            else:
                # Keep the connection alive with a lightweight pulse.
                yield _sse_event("keepalive", {"now_ms": now_ms()})

            # Periodically send a candidate rescan snapshot (useful when users move DBs around).
            if time.time() - last_candidates_at > 15.0:
                res, cands = resolve_current_db()
                yield _sse_event(
                    "dbs",
                    {"now_ms": now_ms(), "current": resolved_as_dict(res), "candidates": candidates_as_dict(cands)},
                )
                last_candidates_at = time.time()

            await asyncio.sleep(float(interval_s))

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/graph")
def system_graph(
    project_id: str = Query(min_length=1, max_length=200),
    branch: Optional[str] = Query(default=None, max_length=200),
    limit: int = Query(default=250, ge=10, le=2_000),
):
    resolved = resolve_effective_db()
    dbc = inspect_db(resolved.path)
    if not dbc.exists:
        return {
            "ok": False,
            "reason": "db_missing",
            "db": resolved_as_dict(resolved),
            "project_id": project_id,
            "branch": branch or "main",
            "nodes": [],
            "edges": [],
        }

    branch_name = (branch or "main").strip() or "main"
    branch_id = _make_branch_id(project_id, branch_name)

    conn = sqlite3.connect(_sqlite_uri_readonly(resolved.path), uri=True, timeout=1.0)
    c = conn.cursor()

    nodes: List[Dict[str, Any]] = []
    node_ids: List[str] = []

    if _table_exists(c, "findings"):
        c.execute(
            """SELECT id, title, confidence, tags, created_at
               FROM findings
               WHERE project_id=? AND branch_id=?
               ORDER BY created_at DESC
               LIMIT ?""",
            (project_id, branch_id, int(limit)),
        )
        for fid, title, conf, tags, created_at in c.fetchall():
            node_ids.append(fid)
            nodes.append(
                {
                    "id": fid,
                    "type": "finding",
                    "label": title or fid,
                    "confidence": conf,
                    "tags": tags or "",
                    "created_at": created_at,
                }
            )

    if _table_exists(c, "artifacts") and len(node_ids) < int(limit):
        c.execute(
            """SELECT id, type, path, metadata, created_at
               FROM artifacts
               WHERE project_id=? AND branch_id=?
               ORDER BY created_at DESC
               LIMIT ?""",
            (project_id, branch_id, int(limit) - len(node_ids)),
        )
        for aid, atype, path, metadata, created_at in c.fetchall():
            node_ids.append(aid)
            label = (os.path.basename(path or "") or aid) if path else aid
            nodes.append(
                {
                    "id": aid,
                    "type": "artifact",
                    "subtype": atype,
                    "label": label,
                    "path": path or "",
                    "metadata": metadata or "",
                    "created_at": created_at,
                }
            )

    edges: List[Dict[str, Any]] = []
    if node_ids and _table_exists(c, "links"):
        placeholders = ",".join(["?"] * len(node_ids))
        q = f"""SELECT id, source_id, target_id, link_type, metadata, created_at
                FROM links
                WHERE source_id IN ({placeholders}) OR target_id IN ({placeholders})
                ORDER BY created_at DESC"""
        c.execute(q, node_ids + node_ids)
        keep = set(node_ids)
        for lid, sid, tid, ltype, meta, created_at in c.fetchall():
            if sid not in keep or tid not in keep:
                continue
            edges.append(
                {
                    "id": lid,
                    "source": sid,
                    "target": tid,
                    "type": ltype or "LINK",
                    "metadata": meta or "",
                    "created_at": created_at,
                }
            )

    conn.close()

    return {
        "ok": True,
        "db": resolved_as_dict(resolved),
        "project_id": project_id,
        "branch": branch_name,
        "branch_id": branch_id,
        "nodes": nodes,
        "edges": edges,
    }
