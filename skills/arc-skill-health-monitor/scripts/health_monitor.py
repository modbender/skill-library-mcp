#!/usr/bin/env python3
"""Skill Health Monitor — Track deployed skill performance, detect drift, alert on issues."""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

HEALTH_DIR = Path.home() / ".openclaw" / "health"
HEALTH_DIR.mkdir(parents=True, exist_ok=True)


def _health_file(skill_name):
    return HEALTH_DIR / f"{skill_name}.json"


def _load_health(skill_name):
    path = _health_file(skill_name)
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {"skill": skill_name, "checks": [], "thresholds": {}, "created_at": datetime.now(timezone.utc).isoformat()}


def _save_health(skill_name, data):
    with open(_health_file(skill_name), 'w') as f:
        json.dump(data, f, indent=2)


SHELL_METACHARACTERS = set('|;&$`(){}!><\n')


def _sanitize_skill_name(name):
    """Validate skill name contains only safe characters."""
    import re
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValueError(f"Invalid skill name: {name!r} — only alphanumeric, dash, underscore allowed")
    return name


def _validate_cmd(cmd):
    """Reject commands containing shell metacharacters."""
    for char in cmd:
        if char in SHELL_METACHARACTERS:
            raise ValueError(f"Shell metacharacter '{char}' in command — rejected for safety")


def check_skill(skill_name, cmd, timeout=30):
    """Execute a skill command and record health metrics."""
    _sanitize_skill_name(skill_name)
    if isinstance(cmd, str):
        _validate_cmd(cmd)
    health = _load_health(skill_name)

    start_time = time.time()
    try:
        import shlex
        cmd_parts = shlex.split(cmd) if isinstance(cmd, str) else cmd
        result = subprocess.run(
            cmd_parts, shell=False, capture_output=True, text=True, timeout=timeout
        )
        elapsed_ms = int((time.time() - start_time) * 1000)
        success = result.returncode == 0
        output_hash = hash(result.stdout[:1000]) if result.stdout else 0
        error_msg = result.stderr[:500] if result.stderr and not success else ""
    except subprocess.TimeoutExpired:
        elapsed_ms = timeout * 1000
        success = False
        output_hash = 0
        error_msg = f"Timeout after {timeout}s"
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        success = False
        output_hash = 0
        error_msg = str(e)[:500]

    check = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "latency_ms": elapsed_ms,
        "success": success,
        "output_hash": output_hash,
        "error": error_msg,
    }

    health["checks"].append(check)

    # Keep last 1000 checks
    if len(health["checks"]) > 1000:
        health["checks"] = health["checks"][-1000:]

    _save_health(skill_name, health)

    # Check thresholds
    alerts = []
    thresholds = health.get("thresholds", {})
    if thresholds.get("max_latency_ms") and elapsed_ms > thresholds["max_latency_ms"]:
        alerts.append(f"LATENCY ALERT: {elapsed_ms}ms > {thresholds['max_latency_ms']}ms threshold")
    if not success:
        # Count recent errors
        recent = [c for c in health["checks"][-10:] if not c["success"]]
        max_errors = thresholds.get("max_errors", 5)
        if len(recent) >= max_errors:
            alerts.append(f"ERROR RATE ALERT: {len(recent)} errors in last 10 checks (threshold: {max_errors})")

    # Detect output drift
    recent_hashes = [c["output_hash"] for c in health["checks"][-5:] if c["success"]]
    if len(recent_hashes) >= 3 and len(set(recent_hashes)) > 1:
        if recent_hashes[-1] != recent_hashes[-2]:
            alerts.append("OUTPUT DRIFT: Output changed from previous execution")

    return {
        "skill": skill_name,
        "check": check,
        "alerts": alerts,
        "total_checks": len(health["checks"]),
    }


def set_threshold(skill_name, max_latency_ms=None, max_errors=None):
    """Set alerting thresholds for a skill."""
    _sanitize_skill_name(skill_name)
    health = _load_health(skill_name)
    if max_latency_ms is not None:
        health["thresholds"]["max_latency_ms"] = max_latency_ms
    if max_errors is not None:
        health["thresholds"]["max_errors"] = max_errors
    _save_health(skill_name, health)
    return health["thresholds"]


def get_trend(skill_name, period_hours=24):
    """Get health trends for a skill over a time period."""
    _sanitize_skill_name(skill_name)
    health = _load_health(skill_name)
    checks = health.get("checks", [])

    cutoff = datetime.now(timezone.utc) - timedelta(hours=period_hours)
    recent = []
    for c in checks:
        try:
            ts = datetime.fromisoformat(c["timestamp"])
            if ts >= cutoff:
                recent.append(c)
        except (ValueError, KeyError):
            continue

    if not recent:
        return {"skill": skill_name, "period_hours": period_hours, "message": "No data in this period"}

    latencies = [c["latency_ms"] for c in recent]
    successes = sum(1 for c in recent if c["success"])
    errors = len(recent) - successes

    latencies_sorted = sorted(latencies)
    p50 = latencies_sorted[len(latencies_sorted) // 2]
    p95 = latencies_sorted[int(len(latencies_sorted) * 0.95)]
    p99 = latencies_sorted[int(len(latencies_sorted) * 0.99)]

    return {
        "skill": skill_name,
        "period_hours": period_hours,
        "total_checks": len(recent),
        "successes": successes,
        "errors": errors,
        "error_rate": f"{(errors / len(recent) * 100):.1f}%",
        "latency": {
            "min": min(latencies),
            "max": max(latencies),
            "avg": int(sum(latencies) / len(latencies)),
            "p50": p50,
            "p95": p95,
            "p99": p99,
        },
        "uptime": f"{(successes / len(recent) * 100):.1f}%",
    }


def dashboard():
    """Show health dashboard for all monitored skills."""
    skills = []
    for f in sorted(HEALTH_DIR.glob("*.json")):
        skill_name = f.stem
        health = _load_health(skill_name)
        checks = health.get("checks", [])
        if not checks:
            continue

        recent = checks[-10:]
        latencies = [c["latency_ms"] for c in recent]
        errors = sum(1 for c in recent if not c["success"])

        last_check = checks[-1]
        status = "OK" if last_check["success"] else "ERROR"

        skills.append({
            "name": skill_name,
            "status": status,
            "last_check": last_check["timestamp"],
            "last_latency_ms": last_check["latency_ms"],
            "avg_latency_ms": int(sum(latencies) / len(latencies)),
            "recent_errors": errors,
            "total_checks": len(checks),
        })

    return skills


def report(json_output=False):
    """Generate a full health report."""
    skills = dashboard()
    if json_output:
        print(json.dumps({"skills": skills, "generated_at": datetime.now(timezone.utc).isoformat()}, indent=2))
    else:
        if not skills:
            print("No skills being monitored. Use 'check' to start monitoring.")
            return
        print(f"Health Dashboard — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"{'Skill':<30} {'Status':<8} {'Latency':<12} {'Errors':<8} {'Checks':<8}")
        print("-" * 66)
        for s in skills:
            status_icon = "OK" if s["status"] == "OK" else "ERR"
            print(f"{s['name']:<30} {status_icon:<8} {s['avg_latency_ms']}ms{'':>6} {s['recent_errors']}/10{'':>3} {s['total_checks']}")


def main():
    parser = argparse.ArgumentParser(description="Skill Health Monitor")
    sub = parser.add_subparsers(dest="command")

    p_check = sub.add_parser("check", help="Check a skill's health")
    p_check.add_argument("--skill", required=True, help="Skill name")
    p_check.add_argument("--cmd", required=True, help="Command to execute")
    p_check.add_argument("--timeout", type=int, default=30, help="Timeout in seconds")

    p_dash = sub.add_parser("dashboard", help="Show health dashboard")

    p_thresh = sub.add_parser("threshold", help="Set alert thresholds")
    p_thresh.add_argument("--skill", required=True)
    p_thresh.add_argument("--max-latency", type=int, help="Max latency in ms")
    p_thresh.add_argument("--max-errors", type=int, help="Max errors in last 10 checks")

    p_report = sub.add_parser("report", help="Generate health report")
    p_report.add_argument("--json", action="store_true")

    p_trend = sub.add_parser("trend", help="View trends")
    p_trend.add_argument("--skill", required=True)
    p_trend.add_argument("--period", default="24h", help="Time period (e.g., 1h, 24h, 7d)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        result = check_skill(args.skill, args.cmd, args.timeout)
        if result["alerts"]:
            for alert in result["alerts"]:
                print(f"[ALERT] {alert}")
        check = result["check"]
        status = "OK" if check["success"] else "ERROR"
        print(f"[{status}] {args.skill}: {check['latency_ms']}ms")
        if check["error"]:
            print(f"  Error: {check['error']}")

    elif args.command == "dashboard":
        report()

    elif args.command == "threshold":
        thresholds = set_threshold(args.skill, args.max_latency, args.max_errors)
        print(f"Thresholds for {args.skill}: {json.dumps(thresholds)}")

    elif args.command == "report":
        report(json_output=args.json)

    elif args.command == "trend":
        period_str = args.period.lower()
        if period_str.endswith('h'):
            hours = int(period_str[:-1])
        elif period_str.endswith('d'):
            hours = int(period_str[:-1]) * 24
        else:
            hours = int(period_str)
        trend = get_trend(args.skill, hours)
        print(json.dumps(trend, indent=2))


if __name__ == "__main__":
    main()
