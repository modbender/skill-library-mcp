#!/usr/bin/env python3
"""
Production-Grade Health & Status Monitor for Intrusive Thoughts.
GitHub Issue #13 — Traffic light status, heartbeat tracking, self-healing.
"""

import json
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Resolve data directory from config or default
def _get_data_dir():
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text())
            d = cfg.get("system", {}).get("data_dir", "")
            if d:
                return Path(d).expanduser()
        except Exception:
            pass
    return Path(__file__).parent

DATA_DIR = _get_data_dir()
HEALTH_DIR = DATA_DIR / "health"
HEALTH_FILE = HEALTH_DIR / "status.json"
HEARTBEAT_LOG = HEALTH_DIR / "heartbeats.json"
INCIDENT_LOG = HEALTH_DIR / "incidents.json"


def _ensure_dirs():
    HEALTH_DIR.mkdir(parents=True, exist_ok=True)


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _load_json(path, default=None):
    if default is None:
        default = {}
    try:
        if path.exists():
            return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        pass
    return default


def _save_json(path, data):
    _ensure_dirs()
    path.write_text(json.dumps(data, indent=2, default=str))


# ---------------------------------------------------------------------------
# Status model
# ---------------------------------------------------------------------------

class Status:
    GREEN = "green"    # 🟢 All systems operational
    YELLOW = "yellow"  # 🟡 Issues detected, still functional
    RED = "red"        # 🔴 Critical — requires attention

EMOJI = {Status.GREEN: "🟢", Status.YELLOW: "🟡", Status.RED: "🔴"}


def _default_status():
    return {
        "overall": Status.GREEN,
        "last_updated": _now_iso(),
        "version": "1.0.0",
        "uptime_since": _now_iso(),
        "components": {
            "mood_system": {"status": Status.GREEN, "message": "OK", "last_check": None},
            "memory_system": {"status": Status.GREEN, "message": "OK", "last_check": None},
            "cron_jobs": {"status": Status.GREEN, "message": "OK", "last_check": None},
            "dashboard": {"status": Status.GREEN, "message": "OK", "last_check": None},
            "data_integrity": {"status": Status.GREEN, "message": "OK", "last_check": None},
        },
        "metrics": {
            "total_heartbeats": 0,
            "total_incidents": 0,
            "last_incident": None,
            "consecutive_healthy": 0,
            "mttr_seconds": None,  # mean time to recover
        }
    }


def get_status():
    """Get current system status."""
    return _load_json(HEALTH_FILE, _default_status())


def set_component_status(component, status, message="OK"):
    """Update a specific component's status."""
    data = get_status()
    if component not in data["components"]:
        data["components"][component] = {}
    data["components"][component] = {
        "status": status,
        "message": message,
        "last_check": _now_iso(),
    }
    # Recalculate overall status
    statuses = [c["status"] for c in data["components"].values()]
    if Status.RED in statuses:
        data["overall"] = Status.RED
    elif Status.YELLOW in statuses:
        data["overall"] = Status.YELLOW
    else:
        data["overall"] = Status.GREEN
    data["last_updated"] = _now_iso()
    _save_json(HEALTH_FILE, data)
    return data


# ---------------------------------------------------------------------------
# Health checks
# ---------------------------------------------------------------------------

def check_mood_system():
    """Verify mood system files are valid."""
    issues = []
    for fname in ["moods.json", "mood_history.json", "thoughts.json"]:
        p = DATA_DIR / fname
        if not p.exists():
            issues.append(f"{fname} missing")
            continue
        try:
            json.loads(p.read_text())
        except json.JSONDecodeError:
            issues.append(f"{fname} is corrupted JSON")

    # Check mood_history isn't stale (>48h since last entry)
    mh = DATA_DIR / "mood_history.json"
    if mh.exists():
        try:
            history = json.loads(mh.read_text())
            if history:
                last = history[-1] if isinstance(history, list) else None
                if last and "timestamp" in last:
                    ts = datetime.fromisoformat(last["timestamp"].replace("Z", "+00:00"))
                    age = datetime.now(timezone.utc) - ts
                    if age > timedelta(hours=48):
                        issues.append(f"No mood set in {age.days}d {age.seconds//3600}h")
        except Exception:
            pass

    if issues:
        severity = Status.RED if any("corrupted" in i or "missing" in i for i in issues) else Status.YELLOW
        return set_component_status("mood_system", severity, "; ".join(issues))
    return set_component_status("mood_system", Status.GREEN)


def check_data_integrity():
    """Verify key data files exist and are valid JSON."""
    critical_files = ["history.json", "streaks.json", "achievements.json"]
    issues = []
    for fname in critical_files:
        p = DATA_DIR / fname
        if not p.exists():
            issues.append(f"{fname} missing")
            continue
        try:
            data = json.loads(p.read_text())
            # Check file isn't empty
            if not data:
                issues.append(f"{fname} is empty")
        except json.JSONDecodeError:
            issues.append(f"{fname} corrupted")
        except OSError as e:
            issues.append(f"{fname}: {e}")

    if issues:
        severity = Status.RED if any("corrupted" in i for i in issues) else Status.YELLOW
        return set_component_status("data_integrity", severity, "; ".join(issues))
    return set_component_status("data_integrity", Status.GREEN)


def check_cron_jobs():
    """Check if expected cron jobs exist (requires OpenClaw cron access)."""
    # This is a lightweight check — just verify config mentions scheduling
    config = DATA_DIR / "config.json"
    if not config.exists():
        return set_component_status("cron_jobs", Status.YELLOW, "No config.json — cron jobs may not be configured")
    try:
        cfg = json.loads(config.read_text())
        scheduling = cfg.get("scheduling", {})
        if not scheduling:
            return set_component_status("cron_jobs", Status.YELLOW, "No scheduling config")
    except Exception as e:
        return set_component_status("cron_jobs", Status.YELLOW, f"Config error: {e}")
    return set_component_status("cron_jobs", Status.GREEN)


def check_dashboard():
    """Check if dashboard script exists."""
    dash = DATA_DIR / "dashboard.py"
    if not dash.exists():
        return set_component_status("dashboard", Status.YELLOW, "dashboard.py missing")
    return set_component_status("dashboard", Status.GREEN)


def check_memory_system():
    """Check memory system health."""
    mem_dir = DATA_DIR / "memory_store"
    if not mem_dir.exists():
        return set_component_status("memory_system", Status.YELLOW, "memory_store/ not initialized yet")
    
    issues = []
    for fname in ["episodic.json", "semantic.json", "procedural.json"]:
        p = mem_dir / fname
        if p.exists():
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError:
                issues.append(f"{fname} corrupted")
    
    if issues:
        return set_component_status("memory_system", Status.RED, "; ".join(issues))
    return set_component_status("memory_system", Status.GREEN)


def run_all_checks():
    """Run all health checks and return overall status."""
    check_mood_system()
    check_data_integrity()
    check_cron_jobs()
    check_dashboard()
    check_memory_system()
    status = get_status()
    return status


# ---------------------------------------------------------------------------
# Heartbeat tracking
# ---------------------------------------------------------------------------

def record_heartbeat(source="system"):
    """Record a heartbeat pulse."""
    _ensure_dirs()
    beats = _load_json(HEARTBEAT_LOG, [])
    beats.append({
        "timestamp": _now_iso(),
        "source": source,
        "status": get_status()["overall"],
    })
    # Keep last 1000 heartbeats
    beats = beats[-1000:]
    _save_json(HEARTBEAT_LOG, beats)

    # Update metrics
    status = get_status()
    status["metrics"]["total_heartbeats"] = status["metrics"].get("total_heartbeats", 0) + 1
    if status["overall"] == Status.GREEN:
        status["metrics"]["consecutive_healthy"] = status["metrics"].get("consecutive_healthy", 0) + 1
    else:
        status["metrics"]["consecutive_healthy"] = 0
    _save_json(HEALTH_FILE, status)


# ---------------------------------------------------------------------------
# Incident tracking
# ---------------------------------------------------------------------------

def log_incident(component, severity, description, auto_resolved=False):
    """Log a health incident."""
    _ensure_dirs()
    incidents = _load_json(INCIDENT_LOG, [])
    incident = {
        "id": f"INC-{len(incidents)+1:04d}",
        "timestamp": _now_iso(),
        "component": component,
        "severity": severity,
        "description": description,
        "resolved": auto_resolved,
        "resolved_at": _now_iso() if auto_resolved else None,
    }
    incidents.append(incident)
    # Keep last 500 incidents
    incidents = incidents[-500:]
    _save_json(INCIDENT_LOG, incidents)

    # Update metrics
    status = get_status()
    status["metrics"]["total_incidents"] = status["metrics"].get("total_incidents", 0) + 1
    status["metrics"]["last_incident"] = _now_iso()
    _save_json(HEALTH_FILE, status)
    return incident


def resolve_incident(incident_id):
    """Mark an incident as resolved."""
    incidents = _load_json(INCIDENT_LOG, [])
    for inc in incidents:
        if inc["id"] == incident_id:
            inc["resolved"] = True
            inc["resolved_at"] = _now_iso()
            break
    _save_json(INCIDENT_LOG, incidents)


# ---------------------------------------------------------------------------
# Dashboard-friendly output
# ---------------------------------------------------------------------------

def get_dashboard_data():
    """Return health data formatted for the dashboard."""
    status = run_all_checks()
    incidents = _load_json(INCIDENT_LOG, [])
    beats = _load_json(HEARTBEAT_LOG, [])

    return {
        "overall": status["overall"],
        "overall_emoji": EMOJI.get(status["overall"], "❓"),
        "components": {
            name: {
                "emoji": EMOJI.get(c["status"], "❓"),
                "status": c["status"],
                "message": c["message"],
            }
            for name, c in status["components"].items()
        },
        "metrics": status["metrics"],
        "recent_incidents": incidents[-5:],
        "heartbeat_count_24h": sum(
            1 for b in beats
            if _parse_ts(b.get("timestamp", "")) > datetime.now(timezone.utc) - timedelta(hours=24)
        ),
        "version": status.get("version", "unknown"),
    }


def _parse_ts(ts_str):
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except Exception:
        return datetime.min.replace(tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Pretty print
# ---------------------------------------------------------------------------

def print_status():
    """Print a human-readable status report."""
    data = get_dashboard_data()
    print(f"\n{'='*50}")
    print(f"  {data['overall_emoji']} Intrusive Thoughts Health Monitor")
    print(f"  Version: {data['version']}")
    print(f"{'='*50}\n")

    print("Components:")
    for name, comp in data["components"].items():
        print(f"  {comp['emoji']} {name:20s} {comp['message']}")

    print(f"\nMetrics:")
    m = data["metrics"]
    print(f"  Heartbeats: {m.get('total_heartbeats', 0)}")
    print(f"  Incidents: {m.get('total_incidents', 0)}")
    print(f"  Consecutive healthy: {m.get('consecutive_healthy', 0)}")
    if m.get("last_incident"):
        print(f"  Last incident: {m['last_incident']}")

    if data["recent_incidents"]:
        print(f"\nRecent Incidents:")
        for inc in data["recent_incidents"]:
            resolved = "✅" if inc.get("resolved") else "❌"
            print(f"  {resolved} [{inc['id']}] {inc['component']}: {inc['description']}")

    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]

    if not args or args[0] == "status":
        print_status()
    elif args[0] == "check":
        status = run_all_checks()
        overall = status["overall"]
        print(f"{EMOJI[overall]} {overall.upper()}")
        sys.exit(0 if overall == Status.GREEN else 1)
    elif args[0] == "heartbeat":
        source = args[1] if len(args) > 1 else "manual"
        record_heartbeat(source)
        print("💓 Heartbeat recorded")
    elif args[0] == "incident":
        if len(args) < 4:
            print("Usage: health_monitor.py incident <component> <severity> <description>")
            sys.exit(1)
        inc = log_incident(args[1], args[2], " ".join(args[3:]))
        print(f"📋 Incident logged: {inc['id']}")
    elif args[0] == "resolve":
        if len(args) < 2:
            print("Usage: health_monitor.py resolve <incident-id>")
            sys.exit(1)
        resolve_incident(args[1])
        print(f"✅ Resolved: {args[1]}")
    elif args[0] == "json":
        print(json.dumps(get_dashboard_data(), indent=2, default=str))
    else:
        print("Usage: health_monitor.py [status|check|heartbeat|incident|resolve|json]")
        sys.exit(1)
