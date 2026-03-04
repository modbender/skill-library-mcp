#!/usr/bin/env bash
set -euo pipefail

CLIENT=""
VIA="email"
LATEST=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --client) CLIENT="$2"; shift 2 ;;
    --via) VIA="$2"; shift 2 ;;
    --latest) LATEST=true; shift ;;
    *) shift ;;
  esac
done

[ -z "$CLIENT" ] && { echo "Usage: deliver-report.sh --client <name> --latest [--via email|slack]"; exit 1; }

BASE_DIR="${CLIENT_REPORTS_DIR:-$HOME/.openclaw/workspace/client-reports}"
CLIENT_DIR="$BASE_DIR/clients/$CLIENT"

[ ! -d "$CLIENT_DIR" ] && { echo "❌ Client not found: $CLIENT"; exit 1; }

export DLV_CLIENT_DIR="$CLIENT_DIR"
export DLV_BASE_DIR="$BASE_DIR"
export DLV_VIA="$VIA"

python3 << 'PYEOF'
import json, os, sys, glob
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

client_dir = os.environ["DLV_CLIENT_DIR"]
base_dir = os.environ["DLV_BASE_DIR"]
via = os.environ["DLV_VIA"]

# Load configs
client_config = {}
with open(os.path.join(client_dir, "config.json")) as f:
    client_config = json.load(f)

global_config = {}
gc_path = os.path.join(base_dir, "config.json")
if os.path.exists(gc_path):
    with open(gc_path) as f:
        global_config = json.load(f)

# Find latest report
reports_dir = os.path.join(client_dir, "reports")
reports = sorted(glob.glob(os.path.join(reports_dir, "*")), reverse=True)

if not reports:
    print("❌ No reports found. Run generate-report.sh first.")
    sys.exit(1)

latest_report = reports[0]
client_name = client_config.get("display_name", client_config.get("name", "Unknown"))

print(f"📧 Delivering report for {client_name}")
print(f"   Report: {os.path.basename(latest_report)}")
print(f"   Via: {via}")

if via == "email":
    sendgrid_key = global_config.get("sendgrid_api_key") or os.environ.get("SENDGRID_API_KEY", "")
    from_email = global_config.get("from_email", "")
    to_email = client_config.get("contact_email", "")
    
    if not sendgrid_key or not from_email or not to_email:
        print("   ❌ Email delivery requires: sendgrid_api_key, from_email (global config), contact_email (client config)")
        sys.exit(1)
    
    with open(latest_report) as f:
        content = f.read()
    
    is_html = latest_report.endswith(".html")
    content_type = "text/html" if is_html else "text/plain"
    
    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={"Authorization": f"Bearer {sendgrid_key}", "Content-Type": "application/json"},
            json={
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": from_email, "name": global_config.get("from_name", "Reighlan Reports")},
                "subject": f"{client_name} — {os.path.basename(latest_report).replace('.html', '').replace('.md', '').replace('-', ' ').title()}",
                "content": [{"type": content_type, "value": content}],
            },
            timeout=10,
        )
        if resp.status_code in (200, 202):
            print(f"   ✅ Sent to {to_email}")
        else:
            print(f"   ❌ SendGrid error: {resp.status_code} — {resp.text[:200]}")
    except Exception as e:
        print(f"   ❌ Email error: {e}")

elif via == "slack":
    webhook = client_config.get("slack_webhook", "") or os.environ.get("SLACK_WEBHOOK_URL", "")
    if not webhook:
        print("   ❌ Set slack_webhook in client config or SLACK_WEBHOOK_URL env")
        sys.exit(1)
    
    with open(latest_report) as f:
        content = f.read()
    
    # Truncate for Slack
    if len(content) > 3000:
        content = content[:3000] + "\n\n... [truncated — full report attached]"
    
    try:
        resp = requests.post(webhook, json={"text": f"📊 *{client_name} Report*\n\n{content}"}, timeout=10)
        if resp.status_code == 200:
            print("   ✅ Sent to Slack")
        else:
            print(f"   ❌ Slack error: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Slack error: {e}")

else:
    print(f"   ❌ Unknown delivery method: {via}")
PYEOF
