#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
CREATE_TICKETS=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --program) PROGRAM="$2"; shift 2 ;;
    --create-tickets) CREATE_TICKETS=true; shift ;;
    *) shift ;;
  esac
done

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"

export TPM_BASE_DIR="$BASE_DIR"
export TPM_CREATE_TICKETS="$CREATE_TICKETS"

python3 << 'PYEOF'
import json, os, sys
from datetime import datetime

base_dir = os.environ["TPM_BASE_DIR"]
create_tickets = os.environ["TPM_CREATE_TICKETS"] == "true"

actions_file = os.path.join(base_dir, "meetings", "actions.json")
if not os.path.exists(actions_file):
    print("No action items tracked yet. Run process-notes.sh on meeting notes first.")
    sys.exit(0)

with open(actions_file) as f:
    actions = json.load(f)

now = datetime.now().strftime("%Y-%m-%d")

open_actions = [a for a in actions if a.get("status") != "done"]
overdue = [a for a in open_actions if a.get("due_date") and a["due_date"] < now]
due_today = [a for a in open_actions if a.get("due_date") == now]
upcoming = [a for a in open_actions if a.get("due_date", "9999") > now]
no_date = [a for a in open_actions if not a.get("due_date")]
done = [a for a in actions if a.get("status") == "done"]

print("📋 Action Item Tracker")
print("=" * 50)
print(f"   Total: {len(actions)} | Open: {len(open_actions)} | Done: {len(done)} | Overdue: {len(overdue)}")
print()

if overdue:
    print("🔴 OVERDUE:")
    for a in overdue:
        print(f"   ❗ {a['description']}")
        print(f"      Owner: {a.get('owner', '?')} | Due: {a['due_date']} | From: {os.path.basename(a.get('source_file', '?'))}")
    print()

if due_today:
    print("🟡 DUE TODAY:")
    for a in due_today:
        print(f"   ⏰ {a['description']}")
        print(f"      Owner: {a.get('owner', '?')}")
    print()

if upcoming:
    print("🟢 UPCOMING:")
    for a in sorted(upcoming, key=lambda x: x.get("due_date", "9999"))[:10]:
        print(f"   📌 {a['description']}")
        print(f"      Owner: {a.get('owner', '?')} | Due: {a.get('due_date', 'no date')}")
    print()

if no_date:
    print(f"⚪ NO DUE DATE ({len(no_date)}):")
    for a in no_date[:5]:
        print(f"   • {a['description']} → {a.get('owner', '?')}")
    if len(no_date) > 5:
        print(f"   ... and {len(no_date) - 5} more")
    print()

if create_tickets:
    print("🎫 Creating Jira tickets for open action items...")
    # Load global config for Jira
    gc_path = os.path.join(base_dir, "config.json")
    global_config = {}
    if os.path.exists(gc_path):
        with open(gc_path) as f: global_config = json.load(f)
    
    jira_config = global_config.get("jira", {})
    jira_url = jira_config.get("base_url", "") or os.environ.get("JIRA_BASE_URL", "")
    jira_email = jira_config.get("email", "") or os.environ.get("JIRA_EMAIL", "")
    jira_token = jira_config.get("api_token", "") or os.environ.get("JIRA_API_TOKEN", "")
    
    if not all([jira_url, jira_email, jira_token]):
        print("   ⚠️ Jira not configured. Set JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN")
    else:
        import requests
        auth = (jira_email, jira_token)
        created = 0
        for a in open_actions:
            if a.get("jira_ticket"):
                continue
            try:
                resp = requests.post(
                    f"{jira_url}/rest/api/3/issue",
                    auth=auth,
                    headers={"Content-Type": "application/json"},
                    json={
                        "fields": {
                            "project": {"key": a.get("project", "TASK")},
                            "summary": f"[Action Item] {a['description'][:200]}",
                            "issuetype": {"name": "Task"},
                            "description": {
                                "type": "doc", "version": 1,
                                "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"From meeting notes: {a.get('source_file', '?')}\nOwner: {a.get('owner', '?')}\nDue: {a.get('due_date', '?')}"}]}]
                            }
                        }
                    },
                    timeout=10
                )
                if resp.status_code in (200, 201):
                    ticket_key = resp.json().get("key", "?")
                    a["jira_ticket"] = ticket_key
                    created += 1
                    print(f"   ✅ {ticket_key}: {a['description'][:60]}")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Save updated actions
        with open(actions_file, "w") as f:
            json.dump(actions, f, indent=2)
        print(f"\n   Created {created} Jira tickets")
PYEOF
