#!/usr/bin/env bash
set -euo pipefail

CAMPAIGN=""
DRY_RUN=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --campaign) CAMPAIGN="$2"; shift 2 ;;
    --dry-run) DRY_RUN=true; shift ;;
    *) shift ;;
  esac
done

[ -z "$CAMPAIGN" ] && { echo "Usage: send-campaign.sh --campaign <name> [--dry-run]"; exit 1; }

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"
CAMPAIGN_FILE="$BASE_DIR/campaigns/$CAMPAIGN.json"

[ ! -f "$CAMPAIGN_FILE" ] && { echo "❌ Campaign not found: $CAMPAIGN"; exit 1; }

export CAMP_FILE="$CAMPAIGN_FILE"
export CAMP_DRY_RUN="$DRY_RUN"
export CAMP_BASE_DIR="$BASE_DIR"

python3 << 'PYEOF'
import json, os, sys, time
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

campaign_file = os.environ["CAMP_FILE"]
dry_run = os.environ["CAMP_DRY_RUN"] == "true"
base_dir = os.environ["CAMP_BASE_DIR"]

with open(campaign_file) as f:
    campaign = json.load(f)

config = {}
config_path = os.path.join(base_dir, "config.json")
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)

email_config = config.get("email", {})
sendgrid_key = email_config.get("sendgrid_api_key") or os.environ.get("SENDGRID_API_KEY", "")
from_email = email_config.get("from_email", "")
from_name = email_config.get("from_name", "")
daily_limit = email_config.get("daily_limit", 50)
delay = email_config.get("delay_between_emails_sec", 30)

template = campaign.get("template", {})
recipients = campaign.get("recipients", [])

pending = [r for r in recipients if r["status"] == "pending"]

if dry_run:
    print(f"🔍 DRY RUN — Campaign: {campaign['name']}")
    print(f"   Recipients: {len(pending)} pending / {len(recipients)} total")
    print()
    for r in pending[:5]:
        subject = template["subject"].replace("{company_name}", r.get("company_name", ""))
        body = template["body"]
        for key in ["first_name", "last_name", "company_name", "domain"]:
            body = body.replace(f"{{{key}}}", r.get(key, f"[{key}]"))
        
        print(f"   To: {r['email']}")
        print(f"   Subject: {subject}")
        print(f"   Body preview: {body[:150]}...")
        print()
    
    if len(pending) > 5:
        print(f"   ... and {len(pending) - 5} more")
    
    print("   ⚠️  Remove --dry-run to send for real")
    sys.exit(0)

# Actual sending
if not sendgrid_key:
    print("❌ SENDGRID_API_KEY required for sending. Set in config.json or environment.")
    print("   Alternatively, configure SMTP in config.json")
    sys.exit(1)

if not from_email:
    print("❌ from_email not configured. Set in config.json under email.from_email")
    sys.exit(1)

print(f"📧 Sending campaign: {campaign['name']}")
print(f"   {len(pending)} emails to send (limit: {daily_limit}/day)")
print()

sent = 0
for r in pending:
    if sent >= daily_limit:
        print(f"\n   ⚠️ Daily limit reached ({daily_limit}). Remaining will send tomorrow.")
        break
    
    subject = template["subject"]
    body = template["body"]
    for key in ["first_name", "last_name", "company_name", "domain"]:
        subject = subject.replace(f"{{{key}}}", r.get(key, ""))
        body = body.replace(f"{{{key}}}", r.get(key, ""))
    
    try:
        resp = requests.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {sendgrid_key}",
                "Content-Type": "application/json",
            },
            json={
                "personalizations": [{"to": [{"email": r["email"]}]}],
                "from": {"email": from_email, "name": from_name},
                "subject": subject,
                "content": [{"type": "text/plain", "value": body}],
            },
            timeout=10,
        )
        
        if resp.status_code in (200, 202):
            r["status"] = "sent"
            r["step"] = 1
            r["sent_at"].append(datetime.utcnow().isoformat() + "Z")
            sent += 1
            print(f"   ✅ {r['email']}")
        else:
            print(f"   ❌ {r['email']}: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ {r['email']}: {e}")
    
    time.sleep(delay)

campaign["sent"] = sum(1 for r in recipients if r["status"] == "sent")
campaign["status"] = "active"

with open(campaign_file, "w") as f:
    json.dump(campaign, f, indent=2)

print(f"\n📊 Sent {sent} emails. Campaign status: active")
PYEOF
