#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
CHECK=false
ALERT=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --program) PROGRAM="$2"; shift 2 ;;
    --check) CHECK=true; shift ;;
    --alert) ALERT=true; shift ;;
    *) shift ;;
  esac
done

[ -z "$PROGRAM" ] && { echo "Usage: dependency-map.sh --program <name> [--check] [--alert]"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$PROGRAM"

[ ! -d "$PROG_DIR" ] && { echo "❌ Program not found: $PROGRAM"; exit 1; }

export TPM_BASE_DIR="$BASE_DIR"
export TPM_PROG_DIR="$PROG_DIR"
export TPM_CHECK="$CHECK"
export TPM_ALERT="$ALERT"

python3 << 'PYEOF'
import json, os, sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests"); sys.exit(1)

base_dir = os.environ["TPM_BASE_DIR"]
prog_dir = os.environ["TPM_PROG_DIR"]
do_check = os.environ["TPM_CHECK"] == "true"
do_alert = os.environ["TPM_ALERT"] == "true"

global_config = {}
gc_path = os.path.join(base_dir, "config.json")
if os.path.exists(gc_path):
    with open(gc_path) as f: global_config = json.load(f)

prog_config = {}
pc_path = os.path.join(prog_dir, "config.json")
if os.path.exists(pc_path):
    with open(pc_path) as f: prog_config = json.load(f)

deps_dir = os.path.join(prog_dir, "dependencies")
os.makedirs(deps_dir, exist_ok=True)
deps_file = os.path.join(deps_dir, "deps.json")

# Load manual dependencies
dependencies = []
if os.path.exists(deps_file):
    with open(deps_file) as f: dependencies = json.load(f)

# Auto-discover from Jira issue links
jira_config = global_config.get("jira", {})
jira_url = jira_config.get("base_url", "") or os.environ.get("JIRA_BASE_URL", "")
jira_email = jira_config.get("email", "") or os.environ.get("JIRA_EMAIL", "")
jira_token = jira_config.get("api_token", "") or os.environ.get("JIRA_API_TOKEN", "")

if jira_url and jira_email and jira_token:
    auth = (jira_email, jira_token)
    for ws in prog_config.get("workstreams", []):
        project = ws.get("jira_project", "")
        if not project: continue
        try:
            resp = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={
                    "jql": f'project = {project} AND issuefunction in linkedIssuesOf("project = {project}", "is blocked by")',
                    "maxResults": 50,
                    "fields": "summary,issuelinks,status"
                },
                timeout=15
            )
            if resp.status_code == 200:
                for issue in resp.json().get("issues", []):
                    for link in issue["fields"].get("issuelinks", []):
                        if link.get("type", {}).get("name") == "Blocks":
                            blocker = link.get("inwardIssue", {})
                            if blocker:
                                dep = {
                                    "from_ticket": blocker.get("key", "?"),
                                    "from_summary": blocker.get("fields", {}).get("summary", ""),
                                    "from_status": blocker.get("fields", {}).get("status", {}).get("name", "?"),
                                    "to_ticket": issue["key"],
                                    "to_summary": issue["fields"].get("summary", ""),
                                    "to_status": issue["fields"].get("status", {}).get("name", "?"),
                                    "type": "blocks",
                                    "source": "jira_link",
                                }
                                # Deduplicate
                                if not any(d.get("from_ticket") == dep["from_ticket"] and d.get("to_ticket") == dep["to_ticket"] for d in dependencies):
                                    dependencies.append(dep)
        except:
            pass

program_name = prog_config.get("name", "Unknown")
print(f"🔗 Dependency Map — {program_name}")
print("=" * 50)

if not dependencies:
    print("   No dependencies found.")
    print("   Add manually to: dependencies/deps.json")
    print('   Format: [{"from_ticket": "X-1", "to_ticket": "Y-2", "type": "blocks", "from_status": "In Progress"}]')
    sys.exit(0)

# Display
at_risk = []
for d in dependencies:
    from_status = d.get("from_status", "?")
    blocked = from_status.lower() not in ("done", "closed", "resolved")
    
    if blocked:
        icon = "🔴"
        at_risk.append(d)
    else:
        icon = "🟢"
    
    print(f"\n   {icon} {d.get('from_ticket', '?')} → blocks → {d.get('to_ticket', '?')}")
    print(f"      Upstream: {d.get('from_summary', '?')[:60]} [{from_status}]")
    print(f"      Blocked:  {d.get('to_summary', '?')[:60]} [{d.get('to_status', '?')}]")

print(f"\n   Total: {len(dependencies)} dependencies | At risk: {len(at_risk)}")

if do_check and at_risk:
    print(f"\n   ⚠️ {len(at_risk)} dependency(ies) at risk — upstream not complete:")
    for d in at_risk:
        print(f"      • {d['from_ticket']} [{d.get('from_status', '?')}] blocking {d['to_ticket']}")

# Save discovered dependencies
with open(deps_file, "w") as f:
    json.dump(dependencies, f, indent=2)

# Alert
if do_alert and at_risk:
    webhook = global_config.get("slack", {}).get("webhook_url", "") or os.environ.get("SLACK_WEBHOOK_URL", "")
    if webhook:
        text = f"🔗 *Dependency Alert — {program_name}*\n\n{len(at_risk)} at-risk dependencies:\n\n"
        for d in at_risk:
            text += f"• {d['from_ticket']} [{d.get('from_status','?')}] → blocks → {d['to_ticket']}\n"
        try:
            requests.post(webhook, json={"text": text}, timeout=10)
            print("\n   📤 Alert sent to Slack")
        except:
            pass
PYEOF
