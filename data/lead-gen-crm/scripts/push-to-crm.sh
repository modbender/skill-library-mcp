#!/usr/bin/env bash
set -euo pipefail

LEAD_ID=""
BATCH=""
CRM=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --batch) BATCH="$2"; shift 2 ;;
    --crm) CRM="$2"; shift 2 ;;
    *) LEAD_ID="$1"; shift ;;
  esac
done

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"
export LEAD_BASE_DIR="$BASE_DIR"
export PUSH_LEAD_ID="$LEAD_ID"
export PUSH_BATCH="$BATCH"
export PUSH_CRM="$CRM"

python3 << 'PYEOF'
import json, os, sys, glob
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

base_dir = os.environ["LEAD_BASE_DIR"]
lead_id = os.environ.get("PUSH_LEAD_ID", "")
batch = os.environ.get("PUSH_BATCH", "")
crm_override = os.environ.get("PUSH_CRM", "")

config = {}
config_path = os.path.join(base_dir, "config.json")
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)

crm_name = crm_override or config.get("default_crm", "hubspot")
crm_config = config.get("crm", {}).get(crm_name, {})

def push_lead(lead):
    company = lead.get("company_name", "Unknown")
    contacts = lead.get("contacts", [])
    email = contacts[0]["email"] if contacts else lead.get("emails_found", [""])[0]
    first_name = contacts[0].get("first_name", "") if contacts else ""
    last_name = contacts[0].get("last_name", "") if contacts else ""
    
    if crm_name == "hubspot":
        api_key = crm_config.get("api_key") or os.environ.get("HUBSPOT_API_KEY", "")
        if not api_key:
            print(f"   ⚠️ HUBSPOT_API_KEY not set — skipping CRM push")
            return False
        
        # Create contact
        try:
            resp = requests.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={
                    "properties": {
                        "email": email,
                        "firstname": first_name,
                        "lastname": last_name,
                        "company": company,
                        "website": f"https://{lead.get('domain', '')}",
                        "lead_source": "reighlan_lead_gen",
                    }
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                contact_id = resp.json().get("id")
                print(f"   ✅ HubSpot contact created: {email} (ID: {contact_id})")
                lead["crm_id"] = contact_id
                lead["crm"] = "hubspot"
                return True
            elif resp.status_code == 409:
                print(f"   ℹ️  Contact already exists in HubSpot: {email}")
                return True
            else:
                print(f"   ❌ HubSpot error: {resp.status_code} — {resp.text[:200]}")
                return False
        except Exception as e:
            print(f"   ❌ HubSpot error: {e}")
            return False
    
    elif crm_name == "pipedrive":
        api_key = crm_config.get("api_key") or os.environ.get("PIPEDRIVE_API_KEY", "")
        domain = crm_config.get("domain") or os.environ.get("PIPEDRIVE_DOMAIN", "")
        if not api_key or not domain:
            print(f"   ⚠️ PIPEDRIVE_API_KEY/DOMAIN not set")
            return False
        
        try:
            resp = requests.post(
                f"https://{domain}.pipedrive.com/api/v1/persons",
                params={"api_token": api_key},
                json={
                    "name": f"{first_name} {last_name}".strip() or company,
                    "email": [{"value": email, "primary": True}],
                    "org_id": None,
                },
                timeout=10,
            )
            if resp.status_code in (200, 201):
                person_id = resp.json().get("data", {}).get("id")
                print(f"   ✅ Pipedrive person created: {email} (ID: {person_id})")
                lead["crm_id"] = str(person_id)
                lead["crm"] = "pipedrive"
                return True
            else:
                print(f"   ❌ Pipedrive error: {resp.status_code}")
                return False
        except Exception as e:
            print(f"   ❌ Pipedrive error: {e}")
            return False
    
    elif crm_name == "csv":
        csv_path = os.path.join(base_dir, "reports", "leads-export.csv")
        import csv
        file_exists = os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["company", "email", "first_name", "last_name", "domain", "score", "industry"])
            writer.writerow([company, email, first_name, last_name, lead.get("domain", ""), lead.get("score", ""), lead.get("industry", "")])
        print(f"   ✅ Exported to CSV: {email}")
        return True
    
    else:
        print(f"   ⚠️ Unknown CRM: {crm_name}. Use csv as fallback.")
        return False

print(f"📤 Pushing to {crm_name.upper()}")

if batch:
    batch_dir = os.path.join(base_dir, "leads", batch)
    files = glob.glob(os.path.join(batch_dir, "*.json"))
    pushed = 0
    for f in files:
        with open(f) as fh:
            lead = json.load(fh)
        if push_lead(lead):
            lead["pushed_to_crm"] = True
            lead["pushed_at"] = datetime.utcnow().isoformat() + "Z"
            with open(f, "w") as fh:
                json.dump(lead, fh, indent=2)
            pushed += 1
    print(f"\n📊 Pushed {pushed}/{len(files)} leads to {crm_name}")
elif lead_id:
    for subdir in ["qualified", "enriched", "raw"]:
        path = os.path.join(base_dir, "leads", subdir, f"{lead_id}.json")
        if os.path.exists(path):
            with open(path) as f:
                lead = json.load(f)
            push_lead(lead)
            break
    else:
        print(f"❌ Lead not found: {lead_id}")
else:
    print("Usage: push-to-crm.sh <lead-id> | --batch qualified")
PYEOF
