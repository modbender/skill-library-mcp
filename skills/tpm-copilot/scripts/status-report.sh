#!/usr/bin/env bash
set -euo pipefail

PROGRAM=""
AUDIENCE="full"
DELIVER="stdout"

while [[ $# -gt 0 ]]; do
  case $1 in
    --program) PROGRAM="$2"; shift 2 ;;
    --audience) AUDIENCE="$2"; shift 2 ;;
    --deliver) DELIVER="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$PROGRAM" ] && { echo "Usage: status-report.sh --program <name> [--audience exec|eng|full] [--deliver stdout|slack|email|file]"; exit 1; }

BASE_DIR="${TPM_DIR:-$HOME/.openclaw/workspace/tpm}"
PROG_DIR="$BASE_DIR/programs/$PROGRAM"

[ ! -d "$PROG_DIR" ] && { echo "❌ Program not found: $PROGRAM. Run add-program.sh first."; exit 1; }

export TPM_BASE_DIR="$BASE_DIR"
export TPM_PROG_DIR="$PROG_DIR"
export TPM_AUDIENCE="$AUDIENCE"
export TPM_DELIVER="$DELIVER"

python3 << 'PYEOF'
import json, os, sys, subprocess, re
from datetime import datetime, timedelta
from urllib.parse import urljoin

base_dir = os.environ["TPM_BASE_DIR"]
prog_dir = os.environ["TPM_PROG_DIR"]
audience = os.environ["TPM_AUDIENCE"]
deliver = os.environ["TPM_DELIVER"]

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

# Load configs
global_config = {}
gc_path = os.path.join(base_dir, "config.json")
if os.path.exists(gc_path):
    with open(gc_path) as f:
        global_config = json.load(f)

prog_config = {}
pc_path = os.path.join(prog_dir, "config.json")
if os.path.exists(pc_path):
    with open(pc_path) as f:
        prog_config = json.load(f)

program_name = prog_config.get("name", "Unknown Program")
tracker = prog_config.get("tracker", global_config.get("tracker", "jira"))
workstreams = prog_config.get("workstreams", [])
milestones = prog_config.get("milestones", [])

# ========== DATA COLLECTION ==========

data = {
    "jira": {},
    "github": {},
    "milestones": milestones,
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
}

# --- JIRA DATA ---
jira_config = global_config.get("jira", {})
jira_url = jira_config.get("base_url", "") or os.environ.get("JIRA_BASE_URL", "")
jira_email = jira_config.get("email", "") or os.environ.get("JIRA_EMAIL", "")
jira_token = jira_config.get("api_token", "") or os.environ.get("JIRA_API_TOKEN", "")

if jira_url and jira_email and jira_token and tracker == "jira":
    auth = (jira_email, jira_token)
    headers = {"Accept": "application/json"}
    
    for ws in workstreams:
        project = ws.get("jira_project", "")
        if not project:
            continue
        
        ws_name = ws.get("name", project)
        ws_data = {"name": ws_name, "tickets": {}, "blockers": [], "recent_completions": [], "stale": []}
        
        try:
            # Get ticket counts by status
            jql = f'project = {project} AND sprint in openSprints()'
            resp = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth, headers=headers,
                params={"jql": jql, "maxResults": 100, "fields": "status,summary,assignee,updated,priority,labels"},
                timeout=15
            )
            
            if resp.status_code == 200:
                issues = resp.json().get("issues", [])
                status_counts = {}
                stale_days = prog_config.get("settings", {}).get("stale_ticket_days", 5)
                cutoff = datetime.utcnow() - timedelta(days=stale_days)
                
                for issue in issues:
                    fields = issue.get("fields", {})
                    status = fields.get("status", {}).get("name", "Unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                    
                    # Check for blockers
                    labels = [l for l in fields.get("labels", [])]
                    if status.lower() in ("blocked", "impediment") or "blocked" in [l.lower() for l in labels]:
                        ws_data["blockers"].append({
                            "key": issue["key"],
                            "summary": fields.get("summary", ""),
                            "assignee": (fields.get("assignee") or {}).get("displayName", "Unassigned"),
                        })
                    
                    # Check for stale tickets
                    updated = fields.get("updated", "")
                    if updated:
                        updated_dt = datetime.fromisoformat(updated.replace("Z", "+00:00")).replace(tzinfo=None)
                        if updated_dt < cutoff and status.lower() not in ("done", "closed", "resolved"):
                            ws_data["stale"].append({
                                "key": issue["key"],
                                "summary": fields.get("summary", ""),
                                "days_stale": (datetime.utcnow() - updated_dt).days,
                            })
                
                ws_data["tickets"] = status_counts
                ws_data["total"] = len(issues)
                ws_data["done"] = sum(v for k, v in status_counts.items() if k.lower() in ("done", "closed", "resolved"))
                
            # Recent completions (last 7 days)
            jql_done = f'project = {project} AND status changed to Done AFTER -7d ORDER BY updated DESC'
            resp2 = requests.get(
                f"{jira_url}/rest/api/3/search",
                auth=auth, headers=headers,
                params={"jql": jql_done, "maxResults": 10, "fields": "summary,assignee"},
                timeout=10
            )
            if resp2.status_code == 200:
                for issue in resp2.json().get("issues", []):
                    ws_data["recent_completions"].append({
                        "key": issue["key"],
                        "summary": issue["fields"].get("summary", ""),
                    })
                    
        except Exception as e:
            ws_data["error"] = str(e)
        
        data["jira"][ws_name] = ws_data

# --- LINEAR DATA ---
linear_key = global_config.get("linear", {}).get("api_key", "") or os.environ.get("LINEAR_API_KEY", "")

if linear_key and tracker == "linear":
    for ws in workstreams:
        team_id = ws.get("linear_team_id", "")
        if not team_id:
            continue
        
        ws_name = ws.get("name", team_id)
        ws_data = {"name": ws_name, "tickets": {}, "blockers": [], "recent_completions": [], "stale": []}
        
        try:
            query = """
            query($teamId: String!) {
              team(id: $teamId) {
                activeCycle {
                  issues { nodes { title identifier state { name } assignee { name } updatedAt labels { nodes { name } } } }
                  progress
                  endsAt
                }
              }
            }
            """
            resp = requests.post(
                "https://api.linear.app/graphql",
                headers={"Authorization": linear_key, "Content-Type": "application/json"},
                json={"query": query, "variables": {"teamId": team_id}},
                timeout=15
            )
            if resp.status_code == 200:
                cycle = resp.json().get("data", {}).get("team", {}).get("activeCycle", {})
                if cycle:
                    issues = cycle.get("issues", {}).get("nodes", [])
                    status_counts = {}
                    for issue in issues:
                        state = issue.get("state", {}).get("name", "Unknown")
                        status_counts[state] = status_counts.get(state, 0) + 1
                        
                        labels = [n.get("name", "").lower() for n in issue.get("labels", {}).get("nodes", [])]
                        if "blocked" in labels or state.lower() == "blocked":
                            ws_data["blockers"].append({
                                "key": issue.get("identifier", ""),
                                "summary": issue.get("title", ""),
                                "assignee": (issue.get("assignee") or {}).get("name", "Unassigned"),
                            })
                    
                    ws_data["tickets"] = status_counts
                    ws_data["total"] = len(issues)
                    ws_data["progress"] = cycle.get("progress", 0)
                    ws_data["ends_at"] = cycle.get("endsAt", "")
        except Exception as e:
            ws_data["error"] = str(e)
        
        data["jira"][ws_name] = ws_data  # Same structure regardless of tracker

# --- GITHUB DATA ---
for ws in workstreams:
    repos = ws.get("github_repos", [])
    for repo in repos:
        if not repo:
            continue
        
        gh_data = {"repo": repo, "prs_open": [], "prs_merged_7d": 0, "ci_status": "unknown"}
        
        try:
            # Open PRs
            result = subprocess.run(
                ["gh", "pr", "list", "--repo", repo, "--state", "open", "--json", "number,title,author,createdAt,reviewDecision,url", "--limit", "20"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                prs = json.loads(result.stdout)
                threshold = timedelta(hours=prog_config.get("settings", {}).get("pr_review_threshold_hours", 48))
                now = datetime.utcnow()
                
                for pr in prs:
                    created = datetime.fromisoformat(pr["createdAt"].replace("Z", "+00:00")).replace(tzinfo=None)
                    age_hours = (now - created).total_seconds() / 3600
                    gh_data["prs_open"].append({
                        "number": pr["number"],
                        "title": pr["title"],
                        "author": pr.get("author", {}).get("login", "unknown"),
                        "age_hours": round(age_hours),
                        "needs_review": pr.get("reviewDecision") != "APPROVED" and age_hours > threshold.total_seconds() / 3600,
                        "url": pr.get("url", ""),
                    })
            
            # Merged PRs last 7 days
            result2 = subprocess.run(
                ["gh", "pr", "list", "--repo", repo, "--state", "merged", "--json", "number", "--limit", "50",
                 "--search", f"merged:>{(datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d')}"],
                capture_output=True, text=True, timeout=10
            )
            if result2.returncode == 0:
                gh_data["prs_merged_7d"] = len(json.loads(result2.stdout))
            
            # CI status on main
            result3 = subprocess.run(
                ["gh", "run", "list", "--repo", repo, "--branch", "main", "--limit", "1", "--json", "conclusion"],
                capture_output=True, text=True, timeout=10
            )
            if result3.returncode == 0:
                runs = json.loads(result3.stdout)
                if runs:
                    gh_data["ci_status"] = runs[0].get("conclusion", "unknown")
                    
        except Exception as e:
            gh_data["error"] = str(e)
        
        data["github"][repo] = gh_data

# ========== REPORT GENERATION ==========

now = datetime.now()
report = ""

def rag_status(ws_data):
    """Determine RAG status for a workstream."""
    blockers = len(ws_data.get("blockers", []))
    stale = len(ws_data.get("stale", []))
    total = ws_data.get("total", 0)
    done = ws_data.get("done", 0)
    
    if blockers >= 3 or (total > 0 and done / total < 0.3):
        return "🔴 RED"
    elif blockers >= 1 or stale >= 3 or (total > 0 and done / total < 0.6):
        return "🟡 AMBER"
    else:
        return "🟢 GREEN"

if audience == "exec":
    report += f"# {program_name} — Executive Summary\n"
    report += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    # Overall RAG
    all_ws = list(data["jira"].values())
    total_blockers = sum(len(ws.get("blockers", [])) for ws in all_ws)
    
    report += "## Program Status\n\n"
    for ws_data in all_ws:
        rag = rag_status(ws_data)
        total = ws_data.get("total", 0)
        done = ws_data.get("done", 0)
        pct = f"{done}/{total}" if total else "N/A"
        report += f"- {rag} **{ws_data['name']}** — {pct} sprint items complete\n"
    
    report += "\n## Key Highlights\n\n"
    total_completed = sum(len(ws.get("recent_completions", [])) for ws in all_ws)
    report += f"- {total_completed} items completed in the last 7 days\n"
    
    for repo, gh in data["github"].items():
        report += f"- {gh.get('prs_merged_7d', 0)} PRs merged ({repo})\n"
    
    if total_blockers > 0:
        report += f"\n## ⚠️ Risks & Blockers ({total_blockers})\n\n"
        for ws_data in all_ws:
            for b in ws_data.get("blockers", []):
                report += f"- **{b['key']}**: {b['summary']} (owner: {b['assignee']})\n"
    
    # Milestones
    upcoming = [m for m in milestones if m.get("date", "") >= now.strftime("%Y-%m-%d")]
    if upcoming:
        report += "\n## Upcoming Milestones\n\n"
        for m in upcoming[:5]:
            report += f"- **{m['name']}** — {m['date']} ({m.get('status', 'TBD')})\n"
    
    report += "\n## Decisions Needed\n\n"
    report += "- *(Add decisions requiring exec input)*\n"

elif audience == "eng":
    report += f"# {program_name} — Engineering Update\n"
    report += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    for ws_data in all_ws if 'all_ws' in dir() else data["jira"].values():
        report += f"## {ws_data['name']}\n\n"
        report += f"**Sprint Progress:** "
        tickets = ws_data.get("tickets", {})
        if tickets:
            report += " | ".join(f"{status}: {count}" for status, count in sorted(tickets.items()))
        report += "\n\n"
        
        # Recent completions
        completions = ws_data.get("recent_completions", [])
        if completions:
            report += "**Completed (7d):**\n"
            for c in completions[:8]:
                report += f"- ✅ {c['key']}: {c['summary']}\n"
            report += "\n"
        
        # Blockers
        blockers = ws_data.get("blockers", [])
        if blockers:
            report += "**🚫 Blockers:**\n"
            for b in blockers:
                report += f"- {b['key']}: {b['summary']} → {b['assignee']}\n"
            report += "\n"
        
        # Stale tickets
        stale = ws_data.get("stale", [])
        if stale:
            report += f"**⚠️ Stale ({len(stale)} tickets, no update in {prog_config.get('settings', {}).get('stale_ticket_days', 5)}+ days):**\n"
            for s in stale[:5]:
                report += f"- {s['key']}: {s['summary']} ({s['days_stale']}d stale)\n"
            report += "\n"
    
    # GitHub
    for repo, gh in data["github"].items():
        report += f"## GitHub: {repo}\n\n"
        report += f"- PRs merged (7d): {gh.get('prs_merged_7d', 0)}\n"
        report += f"- PRs open: {len(gh.get('prs_open', []))}\n"
        report += f"- CI (main): {gh.get('ci_status', 'unknown')}\n"
        
        needs_review = [pr for pr in gh.get("prs_open", []) if pr.get("needs_review")]
        if needs_review:
            report += f"\n**🔍 Needs Review ({len(needs_review)}):**\n"
            for pr in needs_review:
                report += f"- #{pr['number']}: {pr['title']} ({pr['age_hours']}h old) — {pr['author']}\n"
        report += "\n"

else:  # full
    report += f"# {program_name} — Program Status Report\n"
    report += f"**{now.strftime('%B %d, %Y')}**\n\n"
    
    report += "## Overall Status\n\n"
    for ws_data in data["jira"].values():
        rag = rag_status(ws_data)
        report += f"- {rag} **{ws_data['name']}**\n"
    report += "\n"
    
    # Full details per workstream
    for ws_data in data["jira"].values():
        report += f"## {ws_data['name']}\n\n"
        tickets = ws_data.get("tickets", {})
        if tickets:
            report += "| Status | Count |\n|--------|-------|\n"
            for status, count in sorted(tickets.items()):
                report += f"| {status} | {count} |\n"
            report += "\n"
        
        completions = ws_data.get("recent_completions", [])
        if completions:
            report += "**Completed (7d):**\n"
            for c in completions:
                report += f"- ✅ {c['key']}: {c['summary']}\n"
            report += "\n"
        
        blockers = ws_data.get("blockers", [])
        if blockers:
            report += "**Blockers:**\n"
            for b in blockers:
                report += f"- 🚫 {b['key']}: {b['summary']} → {b['assignee']}\n"
            report += "\n"
        
        stale = ws_data.get("stale", [])
        if stale:
            report += f"**Stale Tickets:**\n"
            for s in stale:
                report += f"- ⚠️ {s['key']}: {s['summary']} ({s['days_stale']}d)\n"
            report += "\n"
    
    # GitHub
    for repo, gh in data["github"].items():
        report += f"## GitHub: {repo}\n\n"
        report += f"- Merged (7d): {gh.get('prs_merged_7d', 0)} | Open: {len(gh.get('prs_open', []))} | CI: {gh.get('ci_status', 'unknown')}\n\n"
        
        for pr in gh.get("prs_open", []):
            flag = "🔍" if pr.get("needs_review") else "  "
            report += f"  {flag} #{pr['number']}: {pr['title']} ({pr['age_hours']}h) — @{pr['author']}\n"
        report += "\n"
    
    # Milestones
    if milestones:
        report += "## Milestones\n\n"
        for m in milestones:
            emoji = "✅" if m.get("status") == "complete" else "🟢" if m.get("status") == "on-track" else "🟡" if m.get("status") == "at-risk" else "🔴"
            report += f"- {emoji} **{m['name']}** — {m['date']} ({m.get('status', 'TBD')})\n"
        report += "\n"
    
    # Risks summary
    all_blockers = []
    for ws_data in data["jira"].values():
        all_blockers.extend(ws_data.get("blockers", []))
    if all_blockers:
        report += "## Risk Register\n\n"
        for b in all_blockers:
            report += f"- **{b['key']}**: {b['summary']} (owner: {b['assignee']})\n"
        report += "\n"

report += f"\n---\n*Generated by TPM Copilot — {now.strftime('%Y-%m-%d %H:%M')}*\n"

# ========== DELIVERY ==========

if deliver == "stdout":
    print(report)

elif deliver == "file":
    timestamp = now.strftime("%Y%m%d-%H%M")
    report_path = os.path.join(prog_dir, "reports", f"{audience}-{timestamp}.md")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"✅ Report saved: {report_path}")

elif deliver == "slack":
    webhook = global_config.get("slack", {}).get("webhook_url", "") or os.environ.get("SLACK_WEBHOOK_URL", "")
    if webhook:
        try:
            # Truncate for Slack
            text = report if len(report) < 3500 else report[:3500] + "\n\n... [truncated]"
            resp = requests.post(webhook, json={"text": text}, timeout=10)
            print(f"✅ Delivered to Slack ({resp.status_code})")
        except Exception as e:
            print(f"❌ Slack delivery failed: {e}")
            print(report)
    else:
        print("⚠️ No SLACK_WEBHOOK_URL configured. Printing to stdout.")
        print(report)

elif deliver == "email":
    email_config = global_config.get("email", {})
    resend_key = email_config.get("api_key", "") or os.environ.get("RESEND_API_KEY", "")
    stakeholders = prog_config.get("stakeholders", {}).get(audience, [])
    
    if resend_key and stakeholders:
        for recipient in stakeholders:
            if "@" in recipient:
                try:
                    resp = requests.post(
                        "https://api.resend.com/emails",
                        headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                        json={
                            "from": f"TPM Copilot <{email_config.get('from', 'delivered@resend.dev')}>",
                            "to": [recipient],
                            "subject": f"{program_name} — {audience.title()} Status Update ({now.strftime('%b %d')})",
                            "text": report,
                        },
                        timeout=10
                    )
                    print(f"✅ Emailed to {recipient}")
                except Exception as e:
                    print(f"❌ Email failed for {recipient}: {e}")
    else:
        print("⚠️ Email not configured or no stakeholders set. Printing to stdout.")
        print(report)

# Save state
state_path = os.path.join(base_dir, "state.json")
state = {}
if os.path.exists(state_path):
    with open(state_path) as f:
        state = json.load(f)
state["last_status_report"] = now.isoformat()
with open(state_path, "w") as f:
    json.dump(state, f, indent=2)
PYEOF
