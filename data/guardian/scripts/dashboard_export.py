#!/usr/bin/env python3
"""Export Guardian runtime status and metrics as JSON for dashboards."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def skill_root() -> Path:
    """Return Guardian skill root path."""
    return Path(__file__).resolve().parents[1]


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load Guardian config, preferring OpenClaw Control UI config."""
    sys.path.insert(0, str(skill_root() / "core"))
    from settings import load_config as shared_load_config  # type: ignore  # noqa: E402

    return shared_load_config(config_path)


def resolve_workspace() -> Path:
    """Resolve workspace location for default DB path."""
    import os

    guardian_workspace = os.environ.get("GUARDIAN_WORKSPACE")
    if guardian_workspace:
        return Path(guardian_workspace).expanduser().resolve()
    openclaw_workspace = os.environ.get("OPENCLAW_WORKSPACE")
    if openclaw_workspace:
        return Path(openclaw_workspace).expanduser().resolve()
    default_workspace = Path.home() / ".openclaw" / "workspace"
    if default_workspace.exists():
        return default_workspace.resolve()
    return Path.cwd().resolve()


def resolve_db_path(config: Dict[str, Any], db_path: Optional[str] = None) -> Path:
    """Resolve effective DB path from args and config."""
    if db_path:
        return Path(db_path).expanduser().resolve()
    raw = config.get("db_path", "auto")
    if not raw or raw == "auto":
        return resolve_workspace() / "guardian.db"
    return Path(str(raw)).expanduser().resolve()


def parse_iso(value: str) -> datetime:
    """Parse ISO datetime string with optional Z suffix."""
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def as_z(value: Optional[str]) -> Optional[str]:
    """Normalize datetime text to UTC with trailing Z."""
    if not value:
        return None
    return parse_iso(value).astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def determine_status(config: Dict[str, Any]) -> str:
    """Return active, bypass, or disabled status from config."""
    enabled = bool(config.get("enabled", True))
    if not enabled:
        return "disabled"
    if bool(config.get("admin_override", False)):
        return "bypass"
    return "active"


def _config_score(config: Dict[str, Any]) -> int:
    """Compute a simple config hygiene score when audit rows are unavailable."""
    score = 100
    if not config.get("enabled", True):
        score -= 30
    if config.get("admin_override", False):
        score -= 25
    admin = config.get("admin", {}) if isinstance(config.get("admin"), dict) else {}
    if admin.get("disable_until"):
        score -= 10
    channels = config.get("channels", {}) if isinstance(config.get("channels"), dict) else {}
    if channels.get("monitor_all") is not True:
        score -= 10
    alerts = config.get("alerts", {}) if isinstance(config.get("alerts"), dict) else {}
    if not alerts.get("notify_on_critical", False):
        score -= 15
    return max(0, score)


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def export_dashboard(config_path: Optional[str] = None, db_path: Optional[str] = None) -> Dict[str, Any]:
    """Build dashboard export payload."""
    config = load_config(config_path)
    status = determine_status(config)
    effective_db = resolve_db_path(config, db_path)

    if not effective_db.exists():
        return {
            "status": status,
            "health": 100,
            "scanned": 0,
            "threats_24h": 0,
            "blocked_24h": 0,
            "last_scan": None,
            "top_categories": {},
            "critical_pending": 0,
            "config_score": _config_score(config),
            "recent_threats": [],
            "admin_mode": status,
        }

    cutoff_24 = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()
    cutoff_7d = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()

    with _connect(effective_db) as conn:
        totals = conn.execute(
            "SELECT COALESCE(SUM(messages_scanned),0) AS scanned FROM metrics WHERE period='hourly'"
        ).fetchone()
        threat_24 = conn.execute(
            "SELECT COUNT(*) AS total, COALESCE(SUM(blocked),0) AS blocked FROM threats WHERE detected_at >= ? AND dismissed=0",
            (cutoff_24,),
        ).fetchone()
        top_categories = conn.execute(
            "SELECT category, COUNT(*) AS cnt FROM threats WHERE detected_at >= ? AND dismissed=0 GROUP BY category ORDER BY cnt DESC LIMIT 5",
            (cutoff_7d,),
        ).fetchall()
        recent_threats_rows = conn.execute(
            """
            SELECT id, detected_at, sig_id, category, severity, score, blocked, channel
            FROM threats
            WHERE dismissed=0
            ORDER BY detected_at DESC
            LIMIT 10
            """
        ).fetchall()
        last_scan_row = conn.execute("SELECT MAX(period_start) AS last_scan FROM metrics").fetchone()
        health_row = conn.execute(
            "SELECT health_score FROM metrics WHERE health_score IS NOT NULL ORDER BY period_start DESC LIMIT 1"
        ).fetchone()
        pending_critical = conn.execute(
            """
            SELECT COUNT(*) AS pending
            FROM threats
            WHERE detected_at >= ? AND dismissed=0 AND blocked=0 AND lower(severity)='critical'
            """,
            (cutoff_24,),
        ).fetchone()
        config_row = conn.execute(
            "SELECT score FROM config_audits ORDER BY audited_at DESC LIMIT 1"
        ).fetchone()

    recent_threats = []
    for row in recent_threats_rows:
        rec = dict(row)
        rec["detected_at"] = as_z(rec.get("detected_at"))
        recent_threats.append(rec)

    health_score = int(health_row["health_score"]) if health_row and health_row["health_score"] is not None else max(
        0,
        100 - int((threat_24["total"] if threat_24 else 0) * 2),
    )

    payload = {
        "status": status,
        "health": health_score,
        "scanned": int(totals["scanned"]) if totals and totals["scanned"] is not None else 0,
        "threats_24h": int(threat_24["total"]) if threat_24 else 0,
        "blocked_24h": int(threat_24["blocked"]) if threat_24 else 0,
        "last_scan": as_z(last_scan_row["last_scan"]) if last_scan_row else None,
        "top_categories": {str(row["category"]): int(row["cnt"]) for row in top_categories if row["category"]},
        "critical_pending": int(pending_critical["pending"]) if pending_critical else 0,
        "config_score": int(config_row["score"]) if config_row and config_row["score"] is not None else _config_score(config),
        "recent_threats": recent_threats,
        "admin_mode": status,
    }
    return payload


def main() -> int:
    """CLI entrypoint for dashboard JSON export."""
    parser = argparse.ArgumentParser(description="Export Guardian dashboard JSON")
    parser.add_argument("--config", dest="config_path", help="Path to config JSON")
    parser.add_argument("--db", dest="db_path", help="Path to guardian.db")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()

    payload = export_dashboard(config_path=args.config_path, db_path=args.db_path)
    if args.pretty:
        print(json.dumps(payload, indent=2))
    else:
        print(json.dumps(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
