#!/usr/bin/env python3
"""Budget audit — run from Loki's heartbeat to check agent budgets.

Resets daily counters at midnight AEST. Flags warnings and demotions.

Usage:
  python3 scripts/budget_audit.py [--reset-only] [--json]
"""

import sys, os, json, glob
from datetime import datetime
from zoneinfo import ZoneInfo

AEST = ZoneInfo("Australia/Sydney")
AGENTS_DIR = os.path.expanduser("~/.openclaw/workspace/agents")
GOV_LOG = os.path.join(AGENTS_DIR, "governance", "log.jsonl")

# Agent directory name → agent id mapping
AGENT_MAP = {
    "analyst": "archie",
    "sara": "sara",
    "kit": "kit",
    "liv": "liv",
    "belle": "belle",
}

WARN_THRESHOLD = 0.80  # 80%
RED_THRESHOLD = 1.00   # 100%
DEMOTION_CONSECUTIVE_DAYS = 3
EMERGENCY_MULTIPLIER = 2.0  # 200% in one day = immediate demotion


def log_event(agent: str, event: str, details: dict):
    """Append to governance log."""
    os.makedirs(os.path.dirname(GOV_LOG), exist_ok=True)
    entry = {
        "ts": datetime.now(AEST).isoformat(),
        "agent": agent,
        "event": event,
        "details": details,
    }
    with open(GOV_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def audit_agent(agent_dir: str, agent_name: str, today: str) -> dict:
    """Audit one agent's budget. Returns report dict."""
    budget_path = os.path.join(agent_dir, "BUDGET.json")
    if not os.path.exists(budget_path):
        return {"agent": agent_name, "status": "no_budget_file"}

    with open(budget_path) as f:
        budget = json.load(f)

    report = {
        "agent": agent_name,
        "dir": os.path.basename(agent_dir),
        "limit": budget.get("daily_limit_output_tokens", 50000),
        "used": budget.get("used_output_tokens", 0),
        "status": budget.get("status", "active"),
        "consecutive_overbudget": budget.get("consecutive_overbudget_days", 0),
        "spawns_today": len(budget.get("spawns", [])),
        "actions": [],
    }

    # Check if we need to reset (new day)
    budget_day = budget.get("today", "")
    if budget_day != today:
        previous_used = budget.get("used_output_tokens", 0)
        previous_limit = budget.get("daily_limit_output_tokens", 50000)
        was_over = previous_used > previous_limit

        # Update consecutive overbudget counter
        consecutive = budget.get("consecutive_overbudget_days", 0)
        if was_over:
            consecutive += 1
            log_event(agent_name, "overbudget_day", {
                "day": budget_day,
                "used": previous_used,
                "limit": previous_limit,
                "pct": round(previous_used / previous_limit * 100, 1),
                "consecutive": consecutive,
            })
        else:
            consecutive = 0

        # Reset for new day
        budget["today"] = today
        budget["used_output_tokens"] = 0
        budget["spawns"] = []
        budget["warnings"] = []
        budget["consecutive_overbudget_days"] = consecutive

        # Check for demotion
        if consecutive >= DEMOTION_CONSECUTIVE_DAYS and budget["status"] != "demoted":
            budget["status"] = "demoted"
            report["actions"].append(f"DEMOTED: {consecutive} consecutive days over budget")
            log_event(agent_name, "demotion", {
                "reason": f"{consecutive} consecutive days over budget",
            })
        elif budget["status"] == "demoted":
            pass  # Stay demoted until manually reinstated
        else:
            budget["status"] = "active"

        log_event(agent_name, "daily_reset", {
            "previous_day": budget_day,
            "previous_used": previous_used,
            "was_over": was_over,
            "consecutive": consecutive,
        })

        report["actions"].append(f"Daily reset (prev: {previous_used} tokens)")

        with open(budget_path, "w") as f:
            json.dump(budget, f, indent=2)

        report["used"] = 0
        report["status"] = budget["status"]
        report["consecutive_overbudget"] = consecutive
        return report

    # Same day — check thresholds
    limit = budget.get("daily_limit_output_tokens", 50000)
    used = budget.get("used_output_tokens", 0)
    pct = used / limit if limit > 0 else 0

    report["pct"] = round(pct * 100, 1)

    if pct >= EMERGENCY_MULTIPLIER and budget["status"] != "demoted":
        budget["status"] = "demoted"
        report["actions"].append(f"EMERGENCY DEMOTION: {report['pct']}% of daily budget")
        log_event(agent_name, "demotion", {
            "reason": f"Emergency: {report['pct']}% in single day",
            "used": used,
            "limit": limit,
        })
    elif pct >= RED_THRESHOLD and budget["status"] == "active":
        budget["status"] = "red"
        report["actions"].append(f"RED: Over budget at {report['pct']}%")
        log_event(agent_name, "red", {"used": used, "limit": limit, "pct": report["pct"]})
    elif pct >= WARN_THRESHOLD and "yellow_warned" not in budget.get("warnings", []):
        budget.setdefault("warnings", []).append("yellow_warned")
        report["actions"].append(f"YELLOW: Approaching budget at {report['pct']}%")
        log_event(agent_name, "warning", {"used": used, "limit": limit, "pct": report["pct"]})

    report["status"] = budget["status"]

    with open(budget_path, "w") as f:
        json.dump(budget, f, indent=2)

    return report


def main():
    json_output = "--json" in sys.argv
    today = datetime.now(AEST).strftime("%Y-%m-%d")

    reports = []
    agent_dirs = sorted(glob.glob(os.path.join(AGENTS_DIR, "*")))

    for agent_dir in agent_dirs:
        if not os.path.isdir(agent_dir):
            continue
        dirname = os.path.basename(agent_dir)
        if dirname == "governance":
            continue
        agent_name = AGENT_MAP.get(dirname, dirname)
        budget_path = os.path.join(agent_dir, "BUDGET.json")
        if not os.path.exists(budget_path):
            continue

        report = audit_agent(agent_dir, agent_name, today)
        reports.append(report)

    if json_output:
        print(json.dumps(reports, indent=2))
        return

    # Human-readable output
    alerts = []
    print(f"📊 Budget Audit — {today}")
    print(f"{'Agent':<10} {'Status':<10} {'Used':>8} {'Limit':>8} {'%':>6} {'Spawns':>6}  Actions")
    print("-" * 75)
    for r in reports:
        pct_str = f"{r.get('pct', 0):.0f}%" if "pct" in r else "—"
        status_emoji = {
            "active": "🟢",
            "red": "🔴",
            "demoted": "⛔",
            "no_budget_file": "❓",
        }.get(r["status"], "⚪")

        print(f"{r['agent']:<10} {status_emoji} {r['status']:<8} "
              f"{r.get('used', 0):>8,} {r.get('limit', 0):>8,} {pct_str:>6} "
              f"{r.get('spawns_today', 0):>6}  {'; '.join(r.get('actions', []))}")

        if r.get("actions"):
            alerts.extend(r["actions"])

    if alerts:
        print(f"\n⚠️ {len(alerts)} action(s) taken")
    else:
        print("\n✅ All agents within budget")


if __name__ == "__main__":
    main()
