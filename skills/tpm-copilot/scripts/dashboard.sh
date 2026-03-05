#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
[ "$1" = "--program" ] && PROGRAM="$2" || PROGRAM="${1:-}"

[ -z "$PROGRAM" ] && { echo "Usage: dashboard.sh --program <name>"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$PROGRAM"

[ ! -d "$PROG_DIR" ] && { echo "❌ Program not found: $PROGRAM"; exit 1; }

export TPM_BASE_DIR="$BASE_DIR"
export TPM_PROG_DIR="$PROG_DIR"

python3 << 'PYEOF'
import json, os, glob
from datetime import datetime

base_dir = os.environ["TPM_BASE_DIR"]
prog_dir = os.environ["TPM_PROG_DIR"]

prog_config = {}
pc_path = os.path.join(prog_dir, "config.json")
if os.path.exists(pc_path):
    with open(pc_path) as f: prog_config = json.load(f)

name = prog_config.get("name", "Unknown")
now = datetime.now()

# Risks
risks = []
register_path = os.path.join(prog_dir, "risks", "register.json")
if os.path.exists(register_path):
    with open(register_path) as f: risks = json.load(f)
open_risks = [r for r in risks if r.get("status") == "open"]
critical = len([r for r in open_risks if r.get("severity") in ("critical", "high")])

# Actions
actions = []
actions_path = os.path.join(base_dir, "meetings", "actions.json")
if os.path.exists(actions_path):
    with open(actions_path) as f: actions = json.load(f)
overdue = len([a for a in actions if a.get("status") != "done" and a.get("due_date", "9999") < now.strftime("%Y-%m-%d")])

# Reports
reports = glob.glob(os.path.join(prog_dir, "reports", "*.md"))

# Dependencies
deps = []
deps_path = os.path.join(prog_dir, "dependencies", "deps.json")
if os.path.exists(deps_path):
    with open(deps_path) as f: deps = json.load(f)
at_risk_deps = len([d for d in deps if d.get("from_status", "").lower() not in ("done", "closed", "resolved")])

# State
state = {}
state_path = os.path.join(base_dir, "state.json")
if os.path.exists(state_path):
    with open(state_path) as f: state = json.load(f)

W = 48
print("┌" + "─" * W + "┐")
print(f"│{'📊 ' + name:^{W+1}s}│")
print(f"│{now.strftime('%A, %B %d, %Y'):^{W}s}│")
print("├" + "─" * W + "┤")

# Workstreams
ws_list = prog_config.get("workstreams", [])
if ws_list:
    print(f"│  {'Workstreams':40s}      │")
    print(f"│  {'─' * 42}      │")
    for ws in ws_list:
        lead = ws.get("team_lead", "TBD")
        repos = len(ws.get("github_repos", []))
        tracker_key = ws.get("jira_project") or ws.get("linear_team_id") or "?"
        line = f"{ws.get('name', '?')} ({tracker_key}) — {lead}"
        print(f"│  {line:44s}    │")

print("├" + "─" * W + "┤")

# Risks
risk_color = "🔴" if critical > 0 else "🟡" if open_risks else "🟢"
print(f"│  {risk_color} Risks: {len(open_risks)} open ({critical} high/critical)       │")

# Actions
action_color = "🔴" if overdue > 0 else "🟢"
open_actions = len([a for a in actions if a.get("status") != "done"])
print(f"│  {action_color} Actions: {open_actions} open ({overdue} overdue)             │")

# Dependencies
dep_color = "🔴" if at_risk_deps > 0 else "🟢"
print(f"│  {dep_color} Dependencies: {len(deps)} tracked ({at_risk_deps} at risk)     │")

# Milestones
milestones = prog_config.get("milestones", [])
upcoming = [m for m in milestones if m.get("date", "") >= now.strftime("%Y-%m-%d")]
if upcoming:
    print("├" + "─" * W + "┤")
    print(f"│  {'Upcoming Milestones':44s}    │")
    for m in upcoming[:3]:
        status = m.get("status", "TBD")
        emoji = "🟢" if status == "on-track" else "🟡" if status == "at-risk" else "🔴" if status == "behind" else "⚪"
        days = (datetime.strptime(m["date"], "%Y-%m-%d") - now).days
        line = f"{emoji} {m['name']} — {m['date']} ({days}d)"
        print(f"│  {line:46s}  │")

print("├" + "─" * W + "┤")
last_report = state.get("last_status_report", "never")
last_scan = state.get("last_risk_scan", "never")
if last_report != "never":
    last_report = datetime.fromisoformat(last_report).strftime("%b %d %H:%M")
if last_scan != "never":
    last_scan = datetime.fromisoformat(last_scan).strftime("%b %d %H:%M")
print(f"│  Last report: {last_report:14s} Last scan: {last_scan:11s} │")
print(f"│  Reports generated: {len(reports):<27d} │")
print("└" + "─" * W + "┘")
PYEOF
