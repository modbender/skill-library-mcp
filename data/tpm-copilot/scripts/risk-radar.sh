#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
ALERT=false
HISTORY=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --program) PROGRAM="$2"; shift 2 ;;
    --alert) ALERT=true; shift ;;
    --history) HISTORY=true; shift ;;
    *) shift ;;
  esac
done

[ -z "$PROGRAM" ] && { echo "Usage: risk-radar.sh --program <name> [--alert] [--history]"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$PROGRAM"

[ ! -d "$PROG_DIR" ] && { echo "❌ Program not found: $PROGRAM"; exit 1; }

export TPM_BASE_DIR="$BASE_DIR"
export TPM_PROG_DIR="$PROG_DIR"
export TPM_ALERT="$ALERT"
export TPM_HISTORY="$HISTORY"

python3 << 'PYEOF'
import json, os, sys, subprocess, hashlib
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    print("pip3 install requests"); sys.exit(1)

base_dir = os.environ["TPM_BASE_DIR"]
prog_dir = os.environ["TPM_PROG_DIR"]
do_alert = os.environ["TPM_ALERT"] == "true"
show_history = os.environ["TPM_HISTORY"] == "true"

global_config = {}
gc_path = os.path.join(base_dir, "config.json")
if os.path.exists(gc_path):
    with open(gc_path) as f: global_config = json.load(f)

prog_config = {}
pc_path = os.path.join(prog_dir, "config.json")
if os.path.exists(pc_path):
    with open(pc_path) as f: prog_config = json.load(f)

risks_dir = os.path.join(prog_dir, "risks")
os.makedirs(risks_dir, exist_ok=True)

# Load existing risk register
register_path = os.path.join(risks_dir, "register.json")
existing_risks = []
if os.path.exists(register_path):
    with open(register_path) as f: existing_risks = json.load(f)
existing_ids = {r["id"] for r in existing_risks}

if show_history:
    print(f"📊 Risk History — {prog_config.get('name', 'Unknown')}")
    print("=" * 50)
    if not existing_risks:
        print("   No risks recorded yet.")
    for r in sorted(existing_risks, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x.get("severity", "low"), 4)):
        status_icon = "🔴" if r["status"] == "open" else "🟢"
        sev = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(r.get("severity", "low"), "⚪")
        print(f"   {status_icon} {sev} {r['id']}: {r['title']}")
        print(f"      Category: {r.get('category', '?')} | Detected: {r.get('detected_at', '?')} | Source: {r.get('source', '?')}")
        if r.get("mitigation"):
            print(f"      Mitigation: {r['mitigation']}")
        print()
    sys.exit(0)

# ========== SCAN FOR NEW RISKS ==========

new_risks = []
now = datetime.utcnow()
settings = prog_config.get("settings", {})
stale_days = settings.get("stale_ticket_days", 5)
pr_threshold = settings.get("pr_review_threshold_hours", 48)
tracker = prog_config.get("tracker", global_config.get("tracker", "jira"))

def make_risk_id(source, key):
    return "RISK-" + hashlib.md5(f"{source}:{key}".encode()).hexdigest()[:8].upper()

# --- Jira Risks ---
jira_config = global_config.get("jira", {})
jira_url = jira_config.get("base_url", "") or os.environ.get("JIRA_BASE_URL", "")
jira_email = jira_config.get("email", "") or os.environ.get("JIRA_EMAIL", "")
jira_token = jira_config.get("api_token", "") or os.environ.get("JIRA_API_TOKEN", "")

if jira_url and jira_email and jira_token and tracker == "jira":
    auth = (jira_email, jira_token)
    
    for ws in prog_config.get("workstreams", []):
        project = ws.get("jira_project", "")
        if not project: continue
        
        try:
            # Blocked tickets
            resp = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND (status = Blocked OR labels = blocked) AND status != Done', "maxResults": 50, "fields": "summary,assignee,updated"},
                timeout=10
            )
            if resp.status_code == 200:
                for issue in resp.json().get("issues", []):
                    rid = make_risk_id("jira_blocked", issue["key"])
                    if rid not in existing_ids:
                        new_risks.append({
                            "id": rid, "severity": "high", "category": "blocker",
                            "title": f"{issue['key']}: {issue['fields'].get('summary', '')}",
                            "detected_at": now.strftime("%Y-%m-%d"), "source": "jira_blocked",
                            "ticket": issue["key"], "status": "open", "mitigation": "", "owner": ""
                        })
            
            # Stale tickets
            cutoff = (now - timedelta(days=stale_days)).strftime("%Y-%m-%d")
            resp2 = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND updated < "{cutoff}" AND status NOT IN (Done, Closed) AND sprint in openSprints()', "maxResults": 50, "fields": "summary,updated"},
                timeout=10
            )
            if resp2.status_code == 200:
                stale_count = len(resp2.json().get("issues", []))
                if stale_count >= 3:
                    rid = make_risk_id("stale_tickets", f"{project}_{now.strftime('%Y%W')}")
                    if rid not in existing_ids:
                        new_risks.append({
                            "id": rid, "severity": "medium", "category": "delivery",
                            "title": f"{stale_count} stale tickets in {project} (no update in {stale_days}+ days)",
                            "detected_at": now.strftime("%Y-%m-%d"), "source": "stale_scan",
                            "status": "open", "mitigation": "", "owner": ""
                        })
            
            # Sprint scope creep (tickets added after sprint start)
            resp3 = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth,
                params={"jql": f'project = {project} AND sprint in openSprints() AND created > -3d', "maxResults": 20, "fields": "summary"},
                timeout=10
            )
            if resp3.status_code == 200:
                added_count = len(resp3.json().get("issues", []))
                if added_count >= 5:
                    rid = make_risk_id("scope_creep", f"{project}_{now.strftime('%Y%W')}")
                    if rid not in existing_ids:
                        new_risks.append({
                            "id": rid, "severity": "medium", "category": "scope",
                            "title": f"Scope creep: {added_count} tickets added to active sprint in {project}",
                            "detected_at": now.strftime("%Y-%m-%d"), "source": "scope_creep",
                            "status": "open", "mitigation": "", "owner": ""
                        })
        except Exception as e:
            pass

# --- GitHub Risks ---
for ws in prog_config.get("workstreams", []):
    for repo in ws.get("github_repos", []):
        if not repo: continue
        try:
            # Stale PRs
            result = subprocess.run(
                ["gh", "pr", "list", "--repo", repo, "--state", "open", "--json", "number,title,createdAt,reviewDecision"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                stale_prs = []
                for pr in prs:
                    created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00")).replace(tzinfo=None)
                    age = (now - created).total_seconds() / 3600
                    if age > pr_threshold and pr.get("reviewDecision") != "APPROVED":
                        stale_prs.append(pr)
                
                if stale_prs:
                    rid = make_risk_id("pr_bottleneck", f"{repo}_{now.strftime('%Y%W')}")
                    if rid not in existing_ids:
                        new_risks.append({
                            "id": rid, "severity": "medium", "category": "review_bottleneck",
                            "title": f"{len(stale_prs)} PRs waiting review >{pr_threshold}h in {repo}",
                            "detected_at": now.strftime("%Y-%m-%d"), "source": "github_pr_scan",
                            "status": "open", "mitigation": "", "owner": ""
                        })
            
            # CI failures
            result2 = subprocess.run(
                ["gh", "run", "list", "--repo", repo, "--branch", "main", "--limit", "3", "--json", "conclusion"],
                capture_output=True, text=True, timeout=10
            )
            if result2.returncode == 0:
                runs = json.loads(result2.stdout)
                failures = [r for r in runs if r.get("conclusion") == "failure"]
                if len(failures) >= 2:
                    rid = make_risk_id("ci_failure", f"{repo}_{now.strftime('%Y%W')}")
                    if rid not in existing_ids:
                        new_risks.append({
                            "id": rid, "severity": "high", "category": "ci",
                            "title": f"CI repeatedly failing on main branch in {repo}",
                            "detected_at": now.strftime("%Y-%m-%d"), "source": "github_ci_scan",
                            "status": "open", "mitigation": "", "owner": ""
                        })
        except:
            pass

# ========== OUTPUT ==========

program_name = prog_config.get("name", "Unknown")
print(f"🛡️  Risk Radar — {program_name}")
print("=" * 50)

all_open = [r for r in existing_risks if r["status"] == "open"] + new_risks

if not all_open and not new_risks:
    print("   ✅ No active risks detected. All clear!")
else:
    if new_risks:
        print(f"\n   🆕 {len(new_risks)} new risk(s) detected:\n")
        for r in new_risks:
            sev = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(r["severity"], "⚪")
            print(f"   {sev} {r['id']}: {r['title']}")
    
    existing_open = [r for r in existing_risks if r["status"] == "open"]
    if existing_open:
        print(f"\n   📋 {len(existing_open)} existing open risk(s):\n")
        for r in existing_open:
            sev = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵"}.get(r["severity"], "⚪")
            print(f"   {sev} {r['id']}: {r['title']}")

    print(f"\n   Summary: {len(new_risks)} new | {len(existing_open)} existing | {len([r for r in existing_risks if r['status'] == 'resolved'])} resolved")

# Save updated register
updated_register = existing_risks + new_risks
with open(register_path, "w") as f:
    json.dump(updated_register, f, indent=2)

# Alert if requested
if do_alert and new_risks:
    webhook = global_config.get("slack", {}).get("webhook_url", "") or os.environ.get("SLACK_WEBHOOK_URL", "")
    if webhook:
        alert_text = f"🛡️ *Risk Radar Alert — {program_name}*\n\n{len(new_risks)} new risk(s) detected:\n\n"
        for r in new_risks:
            alert_text += f"• [{r['severity'].upper()}] {r['title']}\n"
        try:
            requests.post(webhook, json={"text": alert_text}, timeout=10)
            print(f"\n   📤 Alert sent to Slack")
        except:
            pass

# Update state
state_path = os.path.join(base_dir, "state.json")
state = {}
if os.path.exists(state_path):
    with open(state_path) as f: state = json.load(f)
state["last_risk_scan"] = now.isoformat()
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
PYEOF
