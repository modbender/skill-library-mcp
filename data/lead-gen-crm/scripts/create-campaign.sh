#!/usr/bin/env bash
set -euo pipefail

NAME=""
TEMPLATE=""
LEADS="qualified"

while [[ $# -gt 0 ]]; do
  case $1 in
    --name) NAME="$2"; shift 2 ;;
    --template) TEMPLATE="$2"; shift 2 ;;
    --leads) LEADS="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$NAME" ] || [ -z "$TEMPLATE" ] && { echo "Usage: create-campaign.sh --name <name> --template <template-name> --leads <qualified|enriched>"; exit 1; }

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"
CAMPAIGN_DIR="$BASE_DIR/campaigns"
TEMPLATE_FILE="$BASE_DIR/templates/$TEMPLATE.json"
LEADS_DIR="$BASE_DIR/leads/$LEADS"

mkdir -p "$CAMPAIGN_DIR"

[ ! -f "$TEMPLATE_FILE" ] && { echo "❌ Template not found: $TEMPLATE_FILE"; exit 1; }

export CAMP_NAME="$NAME"
export CAMP_BASE_DIR="$BASE_DIR"
export CAMP_TEMPLATE="$TEMPLATE_FILE"
export CAMP_LEADS_DIR="$LEADS_DIR"
export CAMP_DIR="$CAMPAIGN_DIR"

python3 << 'PYEOF'
import json, os, glob
from datetime import datetime

name = os.environ["CAMP_NAME"]
base_dir = os.environ["CAMP_BASE_DIR"]
template_path = os.environ["CAMP_TEMPLATE"]
leads_dir = os.environ["CAMP_LEADS_DIR"]
campaign_dir = os.environ["CAMP_DIR"]

with open(template_path) as f:
    template = json.load(f)

lead_files = glob.glob(os.path.join(leads_dir, "*.json"))
recipients = []

for lf in lead_files:
    with open(lf) as f:
        lead = json.load(f)
    
    contacts = lead.get("contacts", [])
    email = contacts[0]["email"] if contacts else (lead.get("emails_found", [None])[0])
    if not email:
        continue
    
    recipients.append({
        "lead_id": lead["id"],
        "email": email,
        "first_name": contacts[0].get("first_name", "") if contacts else "",
        "last_name": contacts[0].get("last_name", "") if contacts else "",
        "company_name": lead.get("company_name", ""),
        "domain": lead.get("domain", ""),
        "status": "pending",
        "step": 0,
        "sent_at": [],
    })

campaign = {
    "name": name,
    "template": template,
    "recipients": recipients,
    "created_at": datetime.utcnow().isoformat() + "Z",
    "status": "draft",
    "total_recipients": len(recipients),
    "sent": 0,
    "replied": 0,
    "bounced": 0,
}

output = os.path.join(campaign_dir, f"{name}.json")
with open(output, "w") as f:
    json.dump(campaign, f, indent=2)

print(f"✅ Campaign created: {name}")
print(f"   Template: {template.get('name', 'unknown')}")
print(f"   Recipients: {len(recipients)}")
print(f"   Steps: 1 initial + {len(template.get('follow_ups', []))} follow-ups")
print(f"   File: {output}")
print(f"\n   ⚠️  Run send-campaign.sh --campaign {name} --dry-run before sending!")
PYEOF
