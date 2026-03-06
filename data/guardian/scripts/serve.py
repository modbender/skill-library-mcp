#!/usr/bin/env python3
"""Guardian standalone HTTP API server (stdlib only)."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import shlex
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_CONFIG_PATH = Path(os.environ.get("GUARDIAN_CONFIG") or (SKILL_ROOT / "config.json"))
if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from core.api import GuardianScanner
from core.settings import load_config as load_guardian_config
from scripts.audit_export import export_dir as audit_export_dir
from scripts.audit_export import list_export_files as list_audit_export_files
from scripts.egress_scanner import ensure_egress_table
from scripts.runtime_monitor import ensure_runtime_table


_OPENCLAW_CFG_PATH = Path.home() / ".openclaw" / "openclaw.json"

_AUDIT_ISSUES = [
    {
        "key": ("gateway", "rateLimit", "enabled"),
        "severity": "critical",
        "title": "Rate Limiting",
        "description": "No rate limit — API vulnerable to DoS",
        "fix": "openclaw config set gateway.rateLimit.enabled true",
        "points": 20,
    },
    {
        "key": ("tools", "allowlist"),
        "severity": "critical",
        "title": "Tool Execution",
        "description": "External tool execution unrestricted",
        "fix": "Set tools.allowlist in openclaw.json",
        "points": 20,
    },
    {
        "key": ("models", "allowlist"),
        "severity": "medium",
        "title": "Model Allowlist",
        "description": "Any model can be used",
        "fix": "Set models.allowlist in openclaw.json",
        "points": 10,
    },
    {
        "key": ("sessions", "timeout"),
        "severity": "medium",
        "title": "Session Timeout",
        "description": "Sessions never expire",
        "fix": "Set sessions.timeout in openclaw.json",
        "points": 10,
    },
    {
        "key": ("logging", "audit"),
        "severity": "medium",
        "title": "Audit Logging",
        "description": "No forensic trail",
        "fix": "Enable logging.audit in openclaw.json",
        "points": 10,
    },
]


def _get_nested(d: Dict[str, Any], *keys: str) -> Any:
    """Traverse nested dict with multiple keys."""
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)  # type: ignore[assignment]
    return d


def _is_configured(cfg: Dict[str, Any], key_path: tuple) -> bool:
    """Return True if the config key is set to a truthy / non-empty value."""
    val = _get_nested(cfg, *key_path)
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (list, dict)):
        return len(val) > 0
    return bool(val)


def build_config_audit_payload() -> Dict[str, Any]:
    """Read ~/.openclaw/openclaw.json and produce a config audit report."""
    openclaw_cfg: Dict[str, Any] = {}
    try:
        if _OPENCLAW_CFG_PATH.exists():
            openclaw_cfg = json.loads(_OPENCLAW_CFG_PATH.read_text(encoding="utf-8"))
    except Exception:
        pass

    # Check Guardian-side config for passing items
    guardian_active = True  # if the server is running, Guardian is active
    try:
        g_cfg = load_guardian_config(config_path=str(DEFAULT_CONFIG_PATH))
        scan_interval = g_cfg.get("scan_interval_minutes", 2)
    except Exception:
        scan_interval = 2

    # Count signatures
    def_count = 0
    def_dir = SKILL_ROOT / "definitions"
    if def_dir.exists():
        for f in def_dir.glob("*.json"):
            try:
                data = json.loads(f.read_text())
                def_count += len(data.get("signatures", []))
            except Exception:
                pass

    passing = []
    if guardian_active:
        passing.append("Guardian active")
    if def_count > 0:
        passing.append(f"Signatures loaded ({def_count})")
    if scan_interval:
        passing.append(f"Scan interval set ({scan_interval}min)")

    issues = []
    score = 100
    for issue_def in _AUDIT_ISSUES:
        if not _is_configured(openclaw_cfg, issue_def["key"]):
            score -= issue_def["points"]
            issues.append({
                "severity": issue_def["severity"],
                "title": issue_def["title"],
                "description": issue_def["description"],
                "fix": issue_def["fix"],
                "points": issue_def["points"],
            })

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 45:
        grade = "D"
    else:
        grade = "F"

    return {"score": score, "grade": grade, "issues": issues, "passing": passing}


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
        (table,),
    ).fetchone()
    return row is not None


def _today_bounds_utc() -> Tuple[str, str]:
    now = datetime.now(timezone.utc)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start.isoformat(), end.isoformat()


def list_runtime_events_payload(scanner: GuardianScanner, query: str) -> Dict[str, Any]:
    """Return runtime monitor events."""
    db = scanner._scanner.db
    if not db:
        return {"events": [], "count": 0}
    ensure_runtime_table(db.conn)
    qs = parse_qs(query)
    limit = int((qs.get("limit", ["20"]) or ["20"])[0])
    rows = db.conn.execute(
        "SELECT * FROM runtime_events ORDER BY timestamp DESC LIMIT ?",
        (max(1, min(limit, 500)),),
    ).fetchall()
    return {"events": [dict(row) for row in rows], "count": len(rows)}


def list_egress_events_payload(scanner: GuardianScanner, query: str) -> Dict[str, Any]:
    """Return egress scanner events."""
    db = scanner._scanner.db
    if not db:
        return {"events": [], "count": 0}
    ensure_egress_table(db.conn)
    qs = parse_qs(query)
    limit = int((qs.get("limit", ["20"]) or ["20"])[0])
    rows = db.conn.execute(
        "SELECT * FROM egress_events ORDER BY timestamp DESC LIMIT ?",
        (max(1, min(limit, 500)),),
    ).fetchall()
    return {"events": [dict(row) for row in rows], "count": len(rows)}


def build_layer_status_payload(scanner: GuardianScanner) -> Dict[str, Any]:
    """Return status for all Guardian security layers."""
    db = scanner._scanner.db
    layers: Dict[str, Any] = {
        "layer0": {
            "name": "OpenClaw Native",
            "active": True,
            "event_count_today": 0,
            "last_scan": None,
            "status": "active",
            "description": "Capability restrictions and approval gates.",
        }
    }
    if not db:
        layers.update(
            {
                "layer1": {"name": "Pre-Scan", "active": False, "event_count_today": 0, "last_scan": None, "status": "inactive"},
                "layer2": {"name": "Runtime Monitor", "active": False, "event_count_today": 0, "last_scan": None, "status": "inactive"},
                "layer3": {"name": "Egress Control", "active": False, "event_count_today": 0, "last_scan": None, "status": "inactive"},
                "layer4": {"name": "Audit Trail", "active": False, "event_count_today": 0, "last_scan": None, "status": "inactive"},
            }
        )
        return {"layers": layers}

    conn = db.conn
    start_day, end_day = _today_bounds_utc()

    pre_scan_count = 0
    pre_scan_total = 0
    if _table_exists(conn, "threats"):
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM threats WHERE detected_at >= ? AND detected_at <= ?",
            (start_day, end_day),
        ).fetchone()
        pre_scan_count = int(row["cnt"]) if row else 0
        row_total = conn.execute("SELECT COUNT(*) AS cnt FROM threats").fetchone()
        pre_scan_total = int(row_total["cnt"] or 0) if row_total else 0
    metrics_last = None
    if _table_exists(conn, "metrics"):
        row = conn.execute("SELECT MAX(period_start) AS last_scan FROM metrics").fetchone()
        metrics_last = row["last_scan"] if row else None

    layers["layer1"] = {
        "name": "Pre-Scan",
        "active": _table_exists(conn, "threats"),
        "event_count_today": pre_scan_count,
        "total_events": pre_scan_total,
        "last_scan": metrics_last,
        "status": "active" if _table_exists(conn, "threats") else "inactive",
        "description": "Signature matching on inbound content.",
    }

    ensure_runtime_table(conn)
    runtime_count = 0
    runtime_total = 0
    runtime_last = None
    row = conn.execute(
        "SELECT COUNT(*) AS cnt, MAX(timestamp) AS last_scan FROM runtime_events WHERE timestamp >= ? AND timestamp <= ?",
        (start_day, end_day),
    ).fetchone()
    if row:
        runtime_count = int(row["cnt"] or 0)
        runtime_last = row["last_scan"]
    row_total = conn.execute("SELECT COUNT(*) AS cnt FROM runtime_events").fetchone()
    runtime_total = int(row_total["cnt"] or 0) if row_total else 0
    layers["layer2"] = {
        "name": "Runtime Monitor",
        "active": True,
        "event_count_today": runtime_count,
        "total_events": runtime_total,
        "last_scan": runtime_last,
        "status": "active" if runtime_total > 0 else "partial",
        "description": "Post-processing behavioral analysis.",
    }

    ensure_egress_table(conn)
    egress_count = 0
    egress_total = 0
    egress_last = None
    row = conn.execute(
        "SELECT COUNT(*) AS cnt, MAX(timestamp) AS last_scan FROM egress_events WHERE timestamp >= ? AND timestamp <= ?",
        (start_day, end_day),
    ).fetchone()
    if row:
        egress_count = int(row["cnt"] or 0)
        egress_last = row["last_scan"]
    row_total = conn.execute("SELECT COUNT(*) AS cnt FROM egress_events").fetchone()
    egress_total = int(row_total["cnt"] or 0) if row_total else 0
    layers["layer3"] = {
        "name": "Egress Control",
        "active": True,
        "event_count_today": egress_count,
        "total_events": egress_total,
        "last_scan": egress_last,
        "status": "active" if egress_total > 0 else "partial",
        "description": "Outbound content scanning.",
    }

    workspace = Path(os.environ.get("GUARDIAN_WORKSPACE", os.getcwd())).expanduser().resolve()
    exports_root = audit_export_dir(workspace)
    files = list_audit_export_files(exports_root)
    today_count = 0
    for fpath in files:
        try:
            if fpath.stat().st_mtime >= datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp():
                today_count += 1
        except OSError:
            continue
    last_scan = datetime.fromtimestamp(files[-1].stat().st_mtime, tz=timezone.utc).isoformat() if files else None
    layers["layer4"] = {
        "name": "Audit Trail",
        "active": exports_root.exists(),
        "event_count_today": today_count,
        "total_events": len(files),
        "last_scan": last_scan,
        "status": "active" if files else "partial",
        "description": "Tamper-evident decision log.",
    }

    return {"layers": layers}


def build_status_payload(scanner: GuardianScanner) -> Dict[str, Any]:
    """Build status payload from DB summary and health estimate."""
    db = scanner._scanner.db
    summary = db.get_threat_summary(hours=24) if db else {"total": 0, "blocked": 0, "categories": {}}
    health = max(0, 100 - min(100, int(summary.get("blocked", 0) * 5)))
    return {
        "ok": True,
        "health_score": health,
        "threats_24h": summary.get("total", 0),
        "blocked_24h": summary.get("blocked", 0),
        "categories": summary.get("categories", {}),
    }


def _save_guardian_config(cfg: Dict[str, Any], path: Path | None = None) -> None:
    target = Path(path) if path else DEFAULT_CONFIG_PATH
    target.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")


_RATING_CTA = "\n\n⭐ Guardian just blocked a threat! Rate us → https://clawhub.ai/bluemax30001/guardian (one-time ask)"


def _ensure_guardian_state(conn: sqlite3.Connection) -> None:
    """Create guardian_state singleton table and add first_notification_sent column safely."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS guardian_state (
            id INTEGER PRIMARY KEY DEFAULT 1,
            first_notification_sent INTEGER DEFAULT 0
        )
        """
    )
    conn.execute("INSERT OR IGNORE INTO guardian_state (id, first_notification_sent) VALUES (1, 0)")
    # Safe ALTER TABLE: add column if it doesn't exist
    cols = [row[1] for row in conn.execute("PRAGMA table_info(guardian_state)").fetchall()]
    if "first_notification_sent" not in cols:
        conn.execute("ALTER TABLE guardian_state ADD COLUMN first_notification_sent INTEGER DEFAULT 0")
    conn.commit()


def _get_first_notification_sent(conn: sqlite3.Connection) -> bool:
    _ensure_guardian_state(conn)
    row = conn.execute("SELECT first_notification_sent FROM guardian_state WHERE id=1").fetchone()
    return bool(row and row[0])


def _set_first_notification_sent(conn: sqlite3.Connection) -> None:
    _ensure_guardian_state(conn)
    conn.execute("UPDATE guardian_state SET first_notification_sent=1 WHERE id=1")
    conn.commit()


def _notify_primary_channel(scanner: GuardianScanner, result: Dict[str, Any], channel: str, approval_token: str | None = None) -> None:
    """Optional local notifier for blocked content.

    Configure via `alerts.primary_notify_command` in config.json.
    The command receives one argument: a compact JSON payload string.
    """
    try:
        cfg = scanner._scanner.config or {}
        cmd = (((cfg.get("alerts") or {}).get("primary_notify_command")) or "").strip()
        if not cmd:
            # Fallback: read directly from config file
            try:
                file_cfg = load_guardian_config(config_path=str(DEFAULT_CONFIG_PATH))
                cmd = (((file_cfg.get("alerts") or {}).get("primary_notify_command")) or "").strip()
            except Exception:
                pass
        if not cmd:
            return
        top = result.get("top_threat") or {}
        raw_evidence = str(top.get("evidence") or "").strip()
        summary = result.get("summary")

        # BL-047C: append one-time rating CTA on first notification
        db = scanner._scanner.db
        is_first = False
        if db:
            try:
                is_first = not _get_first_notification_sent(db.conn)
            except Exception:
                pass
        if is_first and summary is not None:
            summary = str(summary) + _RATING_CTA
        elif is_first and summary is None:
            summary = _RATING_CTA.strip()

        payload = {
            "event": "guardian_blocked",
            "severity": top.get("severity"),
            "sig_id": top.get("id"),
            "channel": channel,
            "summary": summary,
            "threat_count": len(result.get("threats") or []),
            "evidence": raw_evidence[:300] if raw_evidence else "",
            "approval_token": approval_token,
            "approval_hint": "Approve via /approve-request?token=<token> endpoint or dashboard pending approvals",
        }
        cmd_parts = shlex.split(cmd)
        if not cmd_parts:
            return
        subprocess.run(cmd_parts + [json.dumps(payload)], check=False, timeout=5)
        if is_first and db:
            try:
                _set_first_notification_sent(db.conn)
            except Exception:
                pass
    except Exception:
        # Notifications are best-effort only
        pass


def handle_scan_payload(scanner: GuardianScanner, data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Validate and process /scan payload."""
    text = str(data.get("text", ""))
    channel = str(data.get("channel", "api"))
    if not text.strip():
        return HTTPStatus.BAD_REQUEST, {"error": "text is required"}

    result = scanner.scan(text=text, channel=channel)
    payload = result.to_dict()
    if payload.get("blocked"):
        db = scanner._scanner.db
        approval_token = None
        if db:
            top = payload.get("top_threat") or {}
            evidence = top.get("evidence") or ""
            # BL-039: resolve threat_id from DB (most-recent match for this sig+channel)
            threat_id: Optional[int] = None
            try:
                row = db.conn.execute(
                    "SELECT id FROM threats WHERE sig_id=? AND channel=? ORDER BY detected_at DESC LIMIT 1",
                    (top.get("id"), channel),
                ).fetchone()
                if row:
                    threat_id = int(row["id"])
            except Exception:
                pass
            approval_token = secrets.token_urlsafe(16)
            db.create_approval_request(
                threat_id=threat_id,
                token=approval_token,
                channel=channel,
                source=channel,
                sig_id=top.get("id"),
                severity=top.get("severity"),
                evidence=str(evidence)[:240],
            )
        _notify_primary_channel(scanner, payload, channel, approval_token)
        payload["approval_token"] = approval_token
    status = HTTPStatus.FORBIDDEN if result.blocked else HTTPStatus.OK
    return status, payload


def handle_dismiss_payload(scanner: GuardianScanner, data: Dict[str, Any]) -> Tuple[int, Dict[str, Any]]:
    """Validate and process /dismiss payload."""
    raw_id = data.get("id")
    if raw_id is None:
        return HTTPStatus.BAD_REQUEST, {"error": "id is required"}

    try:
        threat_id = int(raw_id)
    except (TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"}

    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}

    db.dismiss_threat(threat_id)
    return HTTPStatus.OK, {"ok": True, "dismissed": threat_id}


def handle_ignore_signature_payload(
    scanner: GuardianScanner, data: Dict[str, Any], config_path: Path | None = None
) -> Tuple[int, Dict[str, Any]]:
    """Add a signature to dismissed_signatures and dismiss existing matches."""
    raw_sig = str(data.get("sig_id") or data.get("signature") or "").strip()
    if not raw_sig:
        return HTTPStatus.BAD_REQUEST, {"error": "sig_id is required"}

    cfg = load_guardian_config(config_path=str(config_path or DEFAULT_CONFIG_PATH))
    dismissed = cfg.setdefault("dismissed_signatures", [])
    updated = False
    if raw_sig not in dismissed:
        dismissed.append(raw_sig)
        updated = True
    _save_guardian_config(cfg, path=config_path)

    db = scanner._scanner.db
    dismissed_count = 0
    if db:
        cur = db.conn.execute("UPDATE threats SET dismissed=1 WHERE sig_id=?", (raw_sig,))
        db.conn.commit()
        dismissed_count = int(cur.rowcount)

    # Refresh in-memory patterns so the ignore takes effect immediately
    try:
        scanner._scanner.config = cfg
        scanner._scanner.patterns = scanner._scanner._load_patterns()
    except Exception:
        pass

    return HTTPStatus.OK, {
        "ok": True,
        "sig_id": raw_sig,
        "updated_config": updated,
        "dismissed": dismissed_count,
    }


def extract_allowlist_pattern(evidence: str) -> str:
    """Extract a reasonable allowlist pattern from threat evidence.
    
    Strategy:
    - Escape special regex chars
    - Keep key identifying words intact
    - Use word boundaries for safety
    - Prefer exact match over wildcards
    """
    import re
    
    # Clean and normalize
    clean = evidence.strip()
    
    # Escape special regex characters
    escaped = re.escape(clean)
    
    # For short messages (< 30 chars), use exact match
    if len(clean) < 30:
        return escaped
    
    # For longer messages, extract key phrases (first ~40 chars of unique content)
    # This creates a narrow pattern that's unlikely to match other content
    if len(clean) > 40:
        # Take first significant chunk
        key_part = clean[:40]
        escaped = re.escape(key_part)
        return escaped + ".*"  # Allow continuation but anchor start
    
    return escaped


def handle_approve_payload(
    scanner: GuardianScanner, data: Dict[str, Any], config_path: Path | None = None
) -> Tuple[int, Dict[str, Any]]:
    """Approve a threat as safe, add allowlist pattern, dismiss threat, and log override event."""
    raw_id = data.get("id")
    if raw_id is None:
        return HTTPStatus.BAD_REQUEST, {"error": "id is required"}
    
    try:
        threat_id = int(raw_id)
    except (TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"}
    
    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}
    
    # Get the threat details
    cursor = db.conn.execute(
        "SELECT evidence, description, sig_id, channel, source_file FROM threats WHERE id=?",
        (threat_id,)
    )
    row = cursor.fetchone()
    if not row:
        return HTTPStatus.NOT_FOUND, {"error": f"Threat {threat_id} not found"}
    
    evidence, description, sig_id, channel, source_file = row
    
    # Extract pattern from evidence (the actual matched text)
    if not evidence or not evidence.strip():
        return HTTPStatus.BAD_REQUEST, {"error": "Cannot extract pattern: no evidence text"}
    
    pattern = extract_allowlist_pattern(evidence)
    
    # Load config and add pattern to allowlist
    cfg = load_guardian_config(config_path=str(config_path or DEFAULT_CONFIG_PATH))
    
    # Ensure false_positive_suppression section exists
    if "false_positive_suppression" not in cfg:
        cfg["false_positive_suppression"] = {}
    
    fps = cfg["false_positive_suppression"]
    if "allowlist_patterns" not in fps:
        fps["allowlist_patterns"] = []
    
    allowlist = fps["allowlist_patterns"]
    
    scope = str(data.get("scope", "once")).strip() or "once"
    actor = str(data.get("actor", "dashboard")).strip() or "dashboard"
    reason = str(data.get("reason", "Approved from dashboard")).strip()

    # Check if pattern already exists
    if pattern in allowlist:
        # Still dismiss the threat even if pattern exists
        db.dismiss_threat(threat_id)
        event_id = db.log_override_event(
            threat_id=threat_id,
            action="approve",
            scope=scope,
            actor=actor,
            reason=reason,
            channel=channel,
            source=source_file,
            sig_id=sig_id,
            evidence=evidence,
        )
        return HTTPStatus.OK, {
            "ok": True,
            "pattern": pattern,
            "already_exists": True,
            "dismissed": threat_id,
            "override_event_id": event_id,
        }
    
    # Add pattern to allowlist
    allowlist.append(pattern)
    _save_guardian_config(cfg, path=config_path)
    
    # Dismiss this threat
    db.dismiss_threat(threat_id)
    event_id = db.log_override_event(
        threat_id=threat_id,
        action="approve",
        scope=scope,
        actor=actor,
        reason=reason,
        channel=channel,
        source=source_file,
        sig_id=sig_id,
        evidence=evidence,
    )
    
    # Refresh in-memory patterns so the allowlist takes effect immediately
    try:
        scanner._scanner.config = cfg
        scanner._scanner.patterns = scanner._scanner._load_patterns()
    except Exception:
        pass
    
    return HTTPStatus.OK, {
        "ok": True,
        "pattern": pattern,
        "dismissed": threat_id,
        "evidence": evidence,
        "override_event_id": event_id,
    }


def handle_block_sender_payload(
    scanner: GuardianScanner, data: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    """Block a sender/source from generating future threats."""
    raw_id = data.get("id")
    if raw_id is None:
        return HTTPStatus.BAD_REQUEST, {"error": "id is required"}
    
    try:
        threat_id = int(raw_id)
    except (TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"}
    
    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}
    
    # Get the threat to extract source
    cursor = db.conn.execute(
        "SELECT source_file, channel FROM threats WHERE id=?",
        (threat_id,)
    )
    row = cursor.fetchone()
    if not row:
        return HTTPStatus.NOT_FOUND, {"error": f"Threat {threat_id} not found"}
    
    source = row["source_file"] or row["channel"] or "unknown"
    channel = row["channel"]
    
    # Add to blocklist
    reason = data.get("reason", "Blocked via dashboard action")
    entry_id = db.add_blocklist_entry(source, channel, "dashboard", reason)
    
    # Dismiss the threat
    db.dismiss_threat(threat_id)
    
    return HTTPStatus.OK, {
        "ok": True,
        "blocked": source,
        "channel": channel,
        "entry_id": entry_id,
        "dismissed": threat_id,
    }


def handle_escalate_payload(
    scanner: GuardianScanner, data: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    """Escalate a threat for human review."""
    raw_id = data.get("id")
    if raw_id is None:
        return HTTPStatus.BAD_REQUEST, {"error": "id is required"}
    
    try:
        threat_id = int(raw_id)
    except (TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"}
    
    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}
    
    # Escalate the threat
    db.escalate_threat(threat_id)
    
    return HTTPStatus.OK, {
        "ok": True,
        "escalated": threat_id,
        "note": "Flagged for human review",
    }


def handle_report_false_positive_payload(
    scanner: GuardianScanner, data: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    """Report a threat as a false positive."""
    raw_id = data.get("id")
    if raw_id is None:
        return HTTPStatus.BAD_REQUEST, {"error": "id is required"}
    
    try:
        threat_id = int(raw_id)
    except (TypeError, ValueError):
        return HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"}
    
    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}
    
    comment = data.get("comment", "Reported via dashboard")
    reported_by = data.get("reported_by", "dashboard")
    
    # Create the report
    report_id = db.report_false_positive(threat_id, reported_by, comment)
    
    # Dismiss the threat
    db.dismiss_threat(threat_id)
    
    return HTTPStatus.OK, {
        "ok": True,
        "report_id": report_id,
        "threat_id": threat_id,
        "dismissed": threat_id,
        "note": "Thank you for the feedback. This helps improve Guardian.",
    }


def handle_approve_override_payload(
    scanner: GuardianScanner, data: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    """Process a primary-channel approve-override action (BL-039).

    Accepts either ``token`` (from notification) or ``threat_id`` directly.
    Records the approval in the DB:
      - Updates approval_request status → 'approved_override'
      - Sets threats.approved_override=1, approved_by, approved_at
      - Logs to override_events for full audit trail
    """
    token = str(data.get("token", "")).strip()
    raw_id = data.get("threat_id")
    actor = str(data.get("actor", "primary-channel")).strip() or "primary-channel"
    reason = str(data.get("reason", "user-approved")).strip() or "user-approved"

    db = scanner._scanner.db
    if not db:
        return HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"}

    threat_id: Optional[int] = None
    req: Optional[Dict[str, Any]] = None

    if token:
        req = db.get_approval_request_by_token(token)
        if not req or req.get("status") != "pending":
            return HTTPStatus.NOT_FOUND, {"error": "pending approval request not found for token"}
        threat_id = req.get("threat_id")
        db.decide_approval_request(token, "approved_override", actor, reason)
    elif raw_id is not None:
        try:
            threat_id = int(raw_id)
        except (TypeError, ValueError):
            return HTTPStatus.BAD_REQUEST, {"error": "threat_id must be an integer"}
    else:
        return HTTPStatus.BAD_REQUEST, {"error": "token or threat_id is required"}

    # Update the threat record with approved_override audit columns
    if threat_id is not None:
        db.approve_override_threat(threat_id, approved_by=actor, reason=reason)

    # Log override event for audit trail
    req_data = req or {}
    event_id = db.log_override_event(
        threat_id=threat_id,
        action="approved_override",
        scope="once",
        actor=actor,
        reason=reason,
        channel=req_data.get("channel"),
        source=req_data.get("source"),
        sig_id=req_data.get("sig_id"),
        evidence=req_data.get("evidence"),
    )

    approved_at = db._now()
    return HTTPStatus.OK, {
        "ok": True,
        "status": "approved_override",
        "token": token or None,
        "threat_id": threat_id,
        "approved_by": actor,
        "approved_at": approved_at,
        "override_event_id": event_id,
        "reason": reason,
    }


def list_threats_payload(scanner: GuardianScanner, query: str) -> Dict[str, Any]:
    """Return filtered threats payload for /threats route."""
    db = scanner._scanner.db
    if not db:
        return {"threats": []}

    qs = parse_qs(query)
    hours = int((qs.get("hours", ["24"]) or ["24"])[0])
    limit = int((qs.get("limit", ["50"]) or ["50"])[0])
    rows = db.get_threats(hours=hours, limit=limit)

    channel = (qs.get("channel", [None]) or [None])[0]
    category = (qs.get("category", [None]) or [None])[0]
    if channel:
        rows = [row for row in rows if row.get("channel") == channel]
    if category:
        rows = [row for row in rows if row.get("category") == category]
    return {"threats": rows, "count": len(rows)}


class GuardianHTTPHandler(BaseHTTPRequestHandler):
    """HTTP handler exposing scan/status/health/dismiss/threat endpoints."""

    scanner: GuardianScanner

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    def _json_response(self, status: int, payload: Dict[str, Any]) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json_body(self) -> Tuple[Dict[str, Any], str]:
        length = int(self.headers.get("Content-Length", "0") or 0)
        if length <= 0:
            return {}, "Request body is required"
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError:
            return {}, "Request body must be valid JSON"
        if not isinstance(data, dict):
            return {}, "JSON body must be an object"
        return data, ""

    def do_OPTIONS(self) -> None:  # noqa: N802
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self._json_response(HTTPStatus.OK, {"ok": True})
            return

        if parsed.path == "/status":
            self._json_response(HTTPStatus.OK, build_status_payload(self.scanner))
            return

        if parsed.path == "/threats":
            self._json_response(HTTPStatus.OK, list_threats_payload(self.scanner, parsed.query))
            return

        if parsed.path == "/runtime-events":
            self._json_response(HTTPStatus.OK, list_runtime_events_payload(self.scanner, parsed.query))
            return

        if parsed.path == "/egress-events":
            self._json_response(HTTPStatus.OK, list_egress_events_payload(self.scanner, parsed.query))
            return

        if parsed.path == "/layer-status":
            self._json_response(HTTPStatus.OK, build_layer_status_payload(self.scanner))
            return

        if parsed.path == "/threats-lite":
            payload = list_threats_payload(self.scanner, parsed.query)
            rows = payload.get("threats", [])
            lite = []
            for t in rows[:80]:
                lite.append({
                    "id": t.get("id"),
                    "severity": t.get("severity"),
                    "source": t.get("source") or t.get("channel"),
                    "channel": t.get("channel"),
                    "description": t.get("description"),
                    "sig_id": t.get("sig_id"),
                    "blocked": t.get("blocked"),
                    "dismissed": t.get("dismissed"),
                    "detected_at": t.get("detected_at") or t.get("timestamp"),
                    "evidence": (t.get("evidence") or "")[:400],
                    "context": (t.get("context") or "")[:3000],
                    # BL-039: approved_override audit fields
                    "approved_override": t.get("approved_override", 0),
                    "approved_by": t.get("approved_by"),
                    "approved_at": t.get("approved_at"),
                })
            self._json_response(HTTPStatus.OK, {
                "generated_at": payload.get("generated_at"),
                "threats": lite,
                "count": len(lite),
            })
            return

        if parsed.path == "/allowlist":
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            rules = db.get_allowlist_rules(active_only=True)
            self._json_response(HTTPStatus.OK, {"rules": rules})
            return

        if parsed.path == "/blocklist":
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            entries = db.get_blocklist(active_only=True)
            self._json_response(HTTPStatus.OK, {"entries": entries})
            return

        if parsed.path.startswith("/similar"):
            qs = parse_qs(parsed.query)
            raw_id = (qs.get("id", [None]) or [None])[0]
            if not raw_id:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "id parameter is required"})
                return
            try:
                threat_id = int(raw_id)
            except (TypeError, ValueError):
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "id must be an integer"})
                return
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            similar = db.get_similar_threats(threat_id, limit=20)
            self._json_response(HTTPStatus.OK, {"threats": similar, "count": len(similar)})
            return

        if parsed.path == "/false-positive-reports":
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            reports = db.get_false_positive_reports(days=30)
            self._json_response(HTTPStatus.OK, {"reports": reports})
            return

        if parsed.path == "/overrides":
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            qs = parse_qs(parsed.query)
            limit = int((qs.get("limit", ["50"]) or ["50"])[0])
            events = db.get_override_events(limit=limit)
            self._json_response(HTTPStatus.OK, {"events": events, "count": len(events)})
            return

        if parsed.path == "/approval-requests":
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            qs = parse_qs(parsed.query)
            limit = int((qs.get("limit", ["50"]) or ["50"])[0])
            status_filter = str((qs.get("status", ["pending"]) or ["pending"])[0])
            events = db.list_approval_requests(status=status_filter, limit=limit)
            self._json_response(HTTPStatus.OK, {"requests": events, "count": len(events)})
            return

        if parsed.path == "/approved-overrides":
            # BL-039: Return threats with approved_override=1 for dashboard audit trail
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            qs = parse_qs(parsed.query)
            limit = int((qs.get("limit", ["50"]) or ["50"])[0])
            overrides = db.get_approved_overrides(limit=limit)
            self._json_response(HTTPStatus.OK, {"overrides": overrides, "count": len(overrides)})
            return

        if parsed.path == "/config-audit":
            self._json_response(HTTPStatus.OK, build_config_audit_payload())
            return

        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)

        if parsed.path == "/scan":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_scan_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        if parsed.path == "/approve-request":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return
            token = str(data.get("token", "")).strip()
            actor = str(data.get("actor", "primary-channel")).strip() or "primary-channel"
            reason = str(data.get("reason", "Approved from primary channel")).strip()
            if not token:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "token is required"})
                return
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            req = db.get_approval_request_by_token(token)
            if not req or req.get("status") != "pending":
                self._json_response(HTTPStatus.NOT_FOUND, {"error": "pending approval request not found"})
                return
            db.decide_approval_request(token, "approved", actor, reason)
            db.log_override_event(
                threat_id=req.get("threat_id"),
                action="approve",
                scope="once",
                actor=actor,
                reason=reason,
                channel=req.get("channel"),
                source=req.get("source"),
                sig_id=req.get("sig_id"),
                evidence=req.get("evidence"),
            )
            self._json_response(HTTPStatus.OK, {"ok": True, "token": token, "status": "approved"})
            return

        if parsed.path == "/deny-request":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return
            token = str(data.get("token", "")).strip()
            actor = str(data.get("actor", "primary-channel")).strip() or "primary-channel"
            reason = str(data.get("reason", "Denied from primary channel")).strip()
            if not token:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "token is required"})
                return
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            req = db.get_approval_request_by_token(token)
            if not req or req.get("status") != "pending":
                self._json_response(HTTPStatus.NOT_FOUND, {"error": "pending approval request not found"})
                return
            db.decide_approval_request(token, "denied", actor, reason)
            self._json_response(HTTPStatus.OK, {"ok": True, "token": token, "status": "denied"})
            return

        if parsed.path in {"/api/approve-override", "/approve-override"}:
            # BL-039: Primary-channel approve-override endpoint (legacy alias: /approve-override)
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return
            status, payload = handle_approve_override_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        if parsed.path == "/dismiss":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_dismiss_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        if parsed.path == "/allowlist":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return
            db = self.scanner._scanner.db
            if not db:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "DB persistence disabled"})
                return
            action = str(data.get("action", "add")).strip()
            if action == "add":
                sig_id = str(data.get("signature_id", "")).strip()
                scope = str(data.get("scope", "all")).strip()
                scope_value = str(data.get("scope_value", "") or "").strip()
                reason = str(data.get("reason", "") or "").strip()
                if not sig_id:
                    self._json_response(HTTPStatus.BAD_REQUEST, {"error": "signature_id is required"})
                    return
                rule_id = db.add_allowlist_rule(sig_id, scope, scope_value or None, "user", reason)
                self._json_response(HTTPStatus.OK, {"ok": True, "rule_id": rule_id, "signature_id": sig_id, "scope": scope})
            elif action == "remove":
                raw_id = data.get("rule_id")
                if raw_id is None:
                    self._json_response(HTTPStatus.BAD_REQUEST, {"error": "rule_id is required"})
                    return
                db.remove_allowlist_rule(int(raw_id))
                self._json_response(HTTPStatus.OK, {"ok": True, "removed": int(raw_id)})
            else:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": f"Unknown action: {action}"})
            return

        if parsed.path in {"/ignore", "/ignore-signature"}:
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_ignore_signature_payload(self.scanner, data, config_path=DEFAULT_CONFIG_PATH)
            self._json_response(status, payload)
            return

        if parsed.path == "/approve":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_approve_payload(self.scanner, data, config_path=DEFAULT_CONFIG_PATH)
            self._json_response(status, payload)
            return

        if parsed.path == "/block-sender":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_block_sender_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        if parsed.path == "/escalate":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_escalate_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        if parsed.path == "/report-false-positive":
            data, err = self._read_json_body()
            if err:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": err})
                return

            status, payload = handle_report_false_positive_payload(self.scanner, data)
            self._json_response(status, payload)
            return

        self._json_response(HTTPStatus.NOT_FOUND, {"error": "Not found"})


def create_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    severity: str = "medium",
    db_path: str | None = None,
    server_class: type[ThreadingHTTPServer] = ThreadingHTTPServer,
) -> ThreadingHTTPServer:
    """Create configured Guardian HTTP server instance."""
    effective_db = db_path or str((Path.cwd() / "guardian.db").resolve())
    scanner = GuardianScanner(severity=severity, db_path=effective_db, record_to_db=True, config_path=str(DEFAULT_CONFIG_PATH))

    class _ConfiguredHandler(GuardianHTTPHandler):
        pass

    _ConfiguredHandler.scanner = scanner
    server = server_class((host, port), _ConfiguredHandler)
    return server


def main() -> None:
    """CLI entrypoint for guardian-serve."""
    parser = argparse.ArgumentParser(description="Guardian HTTP API server")
    parser.add_argument("--host", default="0.0.0.0", help="Bind host")
    parser.add_argument("--port", type=int, default=8080, help="Bind port")
    parser.add_argument("--severity", default="medium", help="low|medium|high|critical")
    parser.add_argument("--db", dest="db_path", help="SQLite DB path")
    args = parser.parse_args()

    try:
        server = create_server(host=args.host, port=args.port, severity=args.severity, db_path=args.db_path)
    except PermissionError as exc:
        raise SystemExit(f"Unable to bind HTTP server on {args.host}:{args.port}: {exc}") from exc
    print(f"Guardian server listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        server.server_close()
        server.RequestHandlerClass.scanner.close()


if __name__ == "__main__":
    main()
