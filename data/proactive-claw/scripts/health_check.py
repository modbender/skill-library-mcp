#!/usr/bin/env python3
"""
health_check.py — System health audit for proactive-claw.

Single command to check: DB integrity, config validity, daemon running,
calendar connectivity, feature flag consistency, stale data, disk usage.

Usage:
  python3 health_check.py                    # full report
  python3 health_check.py --check db
  python3 health_check.py --check daemon
  python3 health_check.py --check config
  python3 health_check.py --check calendar
  python3 health_check.py --check flags
  python3 health_check.py --check stale
  python3 health_check.py --check disk
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if sys.version_info < (3, 8):
    print(json.dumps({"error": "python_version_too_old", "detail": "Python 3.8+ required."}))
    sys.exit(1)

SKILL_DIR = Path.home() / ".openclaw/workspace/skills/proactive-claw"
CONFIG_FILE = SKILL_DIR / "config.json"
DB_FILE = SKILL_DIR / "memory.db"
STATE_FILE = SKILL_DIR / "daemon_state.json"
LOG_FILE = SKILL_DIR / "daemon.log"


def load_config() -> dict:
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def check_db_integrity() -> dict:
    """Run PRAGMA integrity_check on memory.db."""
    if not DB_FILE.exists():
        return {"status": "warning", "detail": "memory.db does not exist yet (no outcomes saved)."}
    try:
        conn = sqlite3.connect(str(DB_FILE))
        result = conn.execute("PRAGMA integrity_check").fetchone()[0]
        # Count tables
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        table_names = [t[0] for t in tables]
        conn.close()
        ok = result == "ok"
        return {
            "status": "ok" if ok else "error",
            "integrity": result,
            "tables": table_names,
            "table_count": len(table_names),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def check_config_validity() -> dict:
    """Validate config keys and types."""
    if not CONFIG_FILE.exists():
        return {"status": "error", "detail": "config.json not found. Run setup.sh first."}

    config = load_config()
    if not config:
        return {"status": "error", "detail": "config.json is empty or invalid JSON."}

    issues = []
    # Check required keys
    required = ["calendar_backend", "timezone"]
    for key in required:
        if key not in config:
            issues.append(f"Missing required key: {key}")

    # Check feature flags are boolean
    for key, val in config.items():
        if key.startswith("feature_") and not isinstance(val, bool):
            issues.append(f"{key} should be boolean, got {type(val).__name__}")

    # Check known enum values
    if config.get("calendar_backend") not in ("google", "nextcloud", None):
        issues.append(f"Unknown calendar_backend: {config.get('calendar_backend')}")

    if config.get("proactivity_mode") and config["proactivity_mode"] not in ("low", "balanced", "executive"):
        issues.append(f"Unknown proactivity_mode: {config['proactivity_mode']}")

    if config.get("max_autonomy_level") and config["max_autonomy_level"] not in ("advisory", "confirm", "autonomous"):
        issues.append(f"Unknown max_autonomy_level: {config['max_autonomy_level']}")

    return {
        "status": "ok" if not issues else "warning",
        "issues": issues,
        "keys_found": len(config),
    }


def check_daemon_running() -> dict:
    """Check if daemon process is active."""
    platform = sys.platform
    try:
        if platform == "darwin":
            result = subprocess.run(
                ["launchctl", "list", "ai.openclaw.proactive-claw"],
                capture_output=True, text=True
            )
            running = result.returncode == 0
            return {
                "status": "ok" if running else "warning",
                "running": running,
                "platform": "macOS (launchd)",
                "detail": result.stdout.strip()[:200] if running else "Daemon not loaded.",
            }
        elif platform.startswith("linux"):
            result = subprocess.run(
                ["systemctl", "--user", "is-active", "openclaw-proactive-claw.timer"],
                capture_output=True, text=True
            )
            running = result.stdout.strip() == "active"
            return {
                "status": "ok" if running else "warning",
                "running": running,
                "platform": "Linux (systemd)",
            }
        else:
            return {"status": "warning", "detail": f"Platform {platform} not supported for daemon check."}
    except Exception as e:
        return {"status": "warning", "detail": str(e)}


def check_calendar_connectivity() -> dict:
    """Try to connect to the calendar backend."""
    config = load_config()
    backend = config.get("calendar_backend", "google")
    try:
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from cal_backend import CalendarBackend
        b = CalendarBackend()
        cals = b.list_user_calendars()
        openclaw_id = b.get_openclaw_cal_id()
        return {
            "status": "ok",
            "backend": backend,
            "calendars_found": len(cals),
            "action_calendar_id": openclaw_id,
        }
    except Exception as e:
        return {
            "status": "error",
            "backend": backend,
            "detail": str(e),
        }


def check_feature_flag_consistency() -> dict:
    """Check for inconsistent feature flag combinations."""
    config = load_config()
    issues = []

    if config.get("feature_policy_engine") and not config.get("feature_calendar", True):
        issues.append("feature_policy_engine=true but feature_calendar=false — policies need calendar access.")

    if config.get("feature_orchestrator") and not config.get("feature_memory", True):
        issues.append("feature_orchestrator=true but feature_memory=false — orchestrator needs memory.")

    if config.get("feature_energy") and not config.get("feature_memory", True):
        issues.append("feature_energy=true but feature_memory=false — energy predictor needs outcome history.")

    if config.get("feature_team_awareness") and not config.get("feature_calendar", True):
        issues.append("feature_team_awareness=true but feature_calendar=false.")

    if config.get("feature_proactivity_engine") and not config.get("feature_calendar", True):
        issues.append("feature_proactivity_engine=true but feature_calendar=false.")

    return {
        "status": "ok" if not issues else "warning",
        "issues": issues,
    }


def check_stale_data() -> dict:
    """Check for stale or missing data."""
    warnings = []
    if not DB_FILE.exists():
        return {"status": "warning", "warnings": ["No memory.db — no outcomes saved yet."]}

    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row

    # Check last outcome
    try:
        row = conn.execute(
            "SELECT MAX(captured_at) as latest FROM outcomes"
        ).fetchone()
        if row and row["latest"]:
            latest = datetime.fromisoformat(row["latest"].replace("Z", "+00:00"))
            if latest.tzinfo is None:
                latest = latest.replace(tzinfo=timezone.utc)
            days_ago = (datetime.now(timezone.utc) - latest).days
            if days_ago > 30:
                warnings.append(f"No outcomes captured in {days_ago} days.")
        else:
            warnings.append("No outcomes in database.")
    except Exception:
        pass

    # Check daemon state
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text())
            last_run = state.get("last_run")
            if last_run:
                lr = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
                if lr.tzinfo is None:
                    lr = lr.replace(tzinfo=timezone.utc)
                hours_ago = (datetime.now(timezone.utc) - lr).total_seconds() / 3600
                if hours_ago > 2:
                    warnings.append(f"Daemon last ran {hours_ago:.0f}h ago (expected every 15min).")
        except Exception:
            pass
    else:
        warnings.append("No daemon state file — daemon may have never run.")

    conn.close()
    return {
        "status": "ok" if not warnings else "warning",
        "warnings": warnings,
    }


def check_disk_usage() -> dict:
    """Report file sizes."""
    sizes = {}
    for name, path in [("memory.db", DB_FILE), ("daemon.log", LOG_FILE),
                        ("config.json", CONFIG_FILE)]:
        if path.exists():
            sizes[name] = f"{path.stat().st_size / 1024:.1f} KB"
        else:
            sizes[name] = "not found"

    outcomes_dir = SKILL_DIR / "outcomes"
    if outcomes_dir.exists():
        total = sum(f.stat().st_size for f in outcomes_dir.glob("*.json"))
        sizes["outcomes/"] = f"{total / 1024:.1f} KB ({len(list(outcomes_dir.glob('*.json')))} files)"
    else:
        sizes["outcomes/"] = "not found"

    return {"status": "ok", "sizes": sizes}


def full_health_check() -> dict:
    """Run all checks and return comprehensive report."""
    checks = {
        "db": check_db_integrity(),
        "config": check_config_validity(),
        "daemon": check_daemon_running(),
        "calendar": check_calendar_connectivity(),
        "flags": check_feature_flag_consistency(),
        "stale": check_stale_data(),
        "disk": check_disk_usage(),
    }

    overall = "ok"
    for name, result in checks.items():
        if result.get("status") == "error":
            overall = "error"
            break
        if result.get("status") == "warning" and overall == "ok":
            overall = "warning"

    return {
        "overall": overall,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }


CHECK_MAP = {
    "db": check_db_integrity,
    "config": check_config_validity,
    "daemon": check_daemon_running,
    "calendar": check_calendar_connectivity,
    "flags": check_feature_flag_consistency,
    "stale": check_stale_data,
    "disk": check_disk_usage,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", choices=list(CHECK_MAP.keys()),
                        help="Run a specific check")
    args = parser.parse_args()

    if args.check:
        result = CHECK_MAP[args.check]()
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(full_health_check(), indent=2))


if __name__ == "__main__":
    main()
