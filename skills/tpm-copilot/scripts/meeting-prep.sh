#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
TYPE="standup"

while [[ $# -gt 0 ]]; do
  case $1 in
    --program) PROGRAM="$2"; shift 2 ;;
    --type) TYPE="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$PROGRAM" ] && { echo "Usage: meeting-prep.sh --program <name> --type <standup|sprint-review|exec-sync|program-review>"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$PROGRAM"

[ ! -d "$PROG_DIR" ] && { echo "❌ Program not found: $PROGRAM"; exit 1; }

export TPM_BASE_DIR="$BASE_DIR"
export TPM_PROG_DIR="$PROG_DIR"
export TPM_MEETING_TYPE="$TYPE"

python3 << 'PYEOF'
import json, os, sys, subprocess
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("pip3 install requests"); sys.exit(1)

base_dir = os.environ["TPM_BASE_DIR"]
prog_dir = os.environ["TPM_PROG_DIR"]
meeting_type = os.environ["TPM_MEETING_TYPE"]

global_config = {}
gc_path = os.path.join(base_dir, "config.json")
if os.path.exists(gc_path):
    with open(gc_path) as f: global_config = json.load(f)

prog_config = {}
pc_path = os.path.join(prog_dir, "config.json")
if os.path.exists(pc_path):
    with open(pc_path) as f: prog_config = json.load(f)

program_name = prog_config.get("name", "Unknown")
now = datetime.now()
agenda = ""

# Quick data pull (lighter than full status report)
jira_config = global_config.get("jira", {})
jira_url = jira_config.get("base_url", "") or os.environ.get("JIRA_BASE_URL", "")
jira_email = jira_config.get("email", "") or os.environ.get("JIRA_EMAIL", "")
jira_token = jira_config.get("api_token", "") or os.environ.get("JIRA_API_TOKEN", "")

recent = []
in_progress = []
blockers = []

if jira_url and jira_email and jira_token:
    auth = (jira_email, jira_token)
    for ws in prog_config.get("workstreams", []):
        project = ws.get("jira_project", "")
        if not project: continue
        try:
            # Recently completed
            resp = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND status changed to Done AFTER -1d', "maxResults": 10, "fields": "summary,assignee"},
                timeout=10
            )
            if resp.status_code == 200:
                for i in resp.json().get("issues", []):
                    recent.append({"key": i["key"], "summary": i["fields"]["summary"], "assignee": (i["fields"].get("assignee") or {}).get("displayName", "?")})
            
            # In progress
            resp2 = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND status = "In Progress" AND sprint in openSprints()', "maxResults": 20, "fields": "summary,assignee"},
                timeout=10
            )
            if resp2.status_code == 200:
                for i in resp2.json().get("issues", []):
                    in_progress.append({"key": i["key"], "summary": i["fields"]["summary"], "assignee": (i["fields"].get("assignee") or {}).get("displayName", "?")})
            
            # Blockers
            resp3 = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND (status = Blocked OR labels = blocked) AND status != Done', "maxResults": 10, "fields": "summary,assignee"},
                timeout=10
            )
            if resp3.status_code == 200:
                for i in resp3.json().get("issues", []):
                    blockers.append({"key": i["key"], "summary": i["fields"]["summary"], "assignee": (i["fields"].get("assignee") or {}).get("displayName", "?")})
        except:
            pass

# Check for overdue action items
actions_file = os.path.join(base_dir, "meetings", "actions.json")
overdue_actions = []
if os.path.exists(actions_file):
    with open(actions_file) as f:
        actions = json.load(f)
    for a in actions:
        if a.get("status") != "done" and a.get("due_date", "9999") < now.strftime("%Y-%m-%d"):
            overdue_actions.append(a)

# Risk register
register_path = os.path.join(prog_dir, "risks", "register.json")
open_risks = []
if os.path.exists(register_path):
    with open(register_path) as f:
        open_risks = [r for r in json.load(f) if r.get("status") == "open"]

if meeting_type == "standup":
    agenda += f"# Daily Standup — {program_name}\n"
    agenda += f"**{now.strftime('%A, %B %d, %Y')}**\n\n"
    
    agenda += "## ✅ Completed Yesterday\n\n"
    if recent:
        for r in recent:
            agenda += f"- {r['key']}: {r['summary']} ({r['assignee']})\n"
    else:
        agenda += "- *(Pull from team updates)*\n"
    
    agenda += "\n## 🔄 In Progress Today\n\n"
    if in_progress:
        for i in in_progress:
            agenda += f"- {i['key']}: {i['summary']} → {i['assignee']}\n"
    else:
        agenda += "- *(No items in progress)*\n"
    
    agenda += "\n## 🚫 Blockers\n\n"
    if blockers:
        for b in blockers:
            agenda += f"- {b['key']}: {b['summary']} → {b['assignee']}\n"
    else:
        agenda += "- None 🎉\n"
    
    if overdue_actions:
        agenda += f"\n## ⚠️ Overdue Action Items ({len(overdue_actions)})\n\n"
        for a in overdue_actions:
            agenda += f"- {a.get('description', '?')} → {a.get('owner', '?')} (due: {a.get('due_date', '?')})\n"

elif meeting_type == "sprint-review":
    agenda += f"# Sprint Review — {program_name}\n"
    agenda += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    agenda += "## Sprint Summary\n\n"
    agenda += "- Completed: *(auto-filled from Jira when connected)*\n"
    agenda += "- Carried over: *(tickets not done)*\n"
    agenda += "- Velocity: *(story points completed vs committed)*\n\n"
    
    agenda += "## Completed Work\n\n"
    if recent:
        for r in recent:
            agenda += f"- ✅ {r['key']}: {r['summary']}\n"
    
    agenda += "\n## Demos\n\n"
    agenda += "1. *(Add demo items)*\n\n"
    
    agenda += "## Carry-Over Items\n\n"
    if in_progress:
        for i in in_progress:
            agenda += f"- ⏳ {i['key']}: {i['summary']} → {i['assignee']}\n"
    
    agenda += "\n## Discussion\n\n"
    agenda += "- What went well?\n- What could improve?\n- Action items for next sprint?\n"

elif meeting_type == "exec-sync":
    agenda += f"# Executive Sync — {program_name}\n"
    agenda += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    agenda += "## Program Status (RAG)\n\n"
    agenda += "- *(Overall RAG — update from latest status report)*\n\n"
    
    agenda += "## Top Risks\n\n"
    if open_risks:
        for r in sorted(open_risks, key=lambda x: {"critical": 0, "high": 1, "medium": 2}.get(x.get("severity", "low"), 3))[:5]:
            sev = {"critical": "🔴", "high": "🟠", "medium": "🟡"}.get(r["severity"], "🔵")
            agenda += f"- {sev} {r['title']}\n"
    else:
        agenda += "- No active risks\n"
    
    agenda += "\n## Decisions Needed\n\n"
    agenda += "1. *(Add decisions requiring exec input)*\n\n"
    
    milestones = prog_config.get("milestones", [])
    upcoming = [m for m in milestones if m.get("date", "") >= now.strftime("%Y-%m-%d")]
    if upcoming:
        agenda += "## Upcoming Milestones\n\n"
        for m in upcoming[:3]:
            agenda += f"- **{m['name']}** — {m['date']} ({m.get('status', 'TBD')})\n"
    
    agenda += "\n## Resource / Dependency Asks\n\n"
    agenda += "- *(Any asks for exec help)*\n"

elif meeting_type == "program-review":
    agenda += f"# Program Review — {program_name}\n"
    agenda += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    agenda += "## Workstream Status\n\n"
    for ws in prog_config.get("workstreams", []):
        agenda += f"### {ws.get('name', '?')}\n"
        agenda += f"- Lead: {ws.get('team_lead', 'TBD')}\n"
        agenda += f"- Status: *(update)*\n"
        agenda += f"- Key accomplishments:\n- Upcoming work:\n- Risks:\n\n"
    
    agenda += "## Cross-Team Dependencies\n\n"
    agenda += "- *(Review dependency map)*\n\n"
    
    agenda += "## Risks & Mitigations\n\n"
    if open_risks:
        for r in open_risks:
            agenda += f"- {r['title']} — mitigation: {r.get('mitigation', 'TBD')}\n"
    
    agenda += "\n## Timeline Review\n\n"
    for m in prog_config.get("milestones", []):
        emoji = "✅" if m.get("status") == "complete" else "🟢" if m.get("status") == "on-track" else "🟡"
        agenda += f"- {emoji} {m['name']} — {m['date']}\n"
    
    agenda += "\n## Action Items\n\n"
    agenda += "- *(Capture during meeting)*\n"

agenda += f"\n---\n*Prepared by TPM Copilot — {now.strftime('%Y-%m-%d %H:%M')}*\n"

print(agenda)

# Save to meetings directory
meetings_dir = os.path.join(base_dir, "meetings")
os.makedirs(meetings_dir, exist_ok=True)
filename = f"{meeting_type}-{now.strftime('%Y%m%d')}.md"
with open(os.path.join(meetings_dir, filename), "w") as f:
    f.write(agenda)
print(f"\n📁 Saved: meetings/{filename}")
PYEOF
