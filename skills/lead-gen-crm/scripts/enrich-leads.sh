#!/usr/bin/env bash
set -euo pipefail

LEAD_ID=""
BATCH=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --batch) BATCH="$2"; shift 2 ;;
    *) LEAD_ID="$1"; shift ;;
  esac
done

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"

export LEAD_BASE_DIR="$BASE_DIR"
export LEAD_ID="$LEAD_ID"
export LEAD_BATCH="$BATCH"

python3 << 'PYEOF'
import json, os, sys, glob, re, time
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

base_dir = os.environ["LEAD_BASE_DIR"]
lead_id = os.environ.get("LEAD_ID", "")
batch = os.environ.get("LEAD_BATCH", "")
hunter_key = os.environ.get("HUNTER_API_KEY", "")

# Load config
config_path = os.path.join(base_dir, "config.json")
config = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)
    if not hunter_key:
        hunter_key = config.get("hunter_api_key", "")

def enrich_lead(lead_path):
    with open(lead_path) as f:
        lead = json.load(f)
    
    if lead.get("enriched"):
        return False
    
    domain = lead.get("domain", "")
    print(f"   Enriching: {lead.get('company_name', domain)}...")
    
    # Hunter.io domain search for emails
    if hunter_key and domain:
        try:
            resp = requests.get(
                "https://api.hunter.io/v2/domain-search",
                params={"domain": domain, "api_key": hunter_key},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                lead["organization"] = data.get("organization", lead.get("company_name", ""))
                lead["industry"] = data.get("industry") or lead.get("industry", "unknown")
                lead["company_size"] = data.get("company_size") or "unknown"
                lead["country"] = data.get("country") or lead.get("location", "unknown")
                
                emails = data.get("emails", [])
                if emails:
                    lead["contacts"] = []
                    for email in emails[:5]:
                        lead["contacts"].append({
                            "email": email.get("value", ""),
                            "first_name": email.get("first_name", ""),
                            "last_name": email.get("last_name", ""),
                            "position": email.get("position", ""),
                            "confidence": email.get("confidence", 0),
                        })
                    lead["emails_found"] = [e.get("value") for e in emails[:5]]
            time.sleep(1)  # Rate limit
        except Exception as e:
            print(f"      ⚠️ Hunter.io error: {e}")
    
    # Basic web scrape for additional signals
    if domain:
        try:
            resp = requests.get(f"https://{domain}", timeout=8, headers={"User-Agent": "ReighlanLeadBot/1.0"})
            if resp.status_code == 200:
                text = resp.text.lower()
                # Tech signals
                tech = []
                tech_checks = {
                    "shopify": "shopify", "wordpress": "wp-content",
                    "react": "react", "next.js": "_next",
                    "hubspot": "hubspot", "intercom": "intercom",
                    "google analytics": "google-analytics", "stripe": "stripe",
                }
                for name, sig in tech_checks.items():
                    if sig in text:
                        tech.append(name)
                lead["tech_stack"] = tech
                
                # Social links
                socials = {}
                linkedin = re.search(r'linkedin\.com/company/([^/"]+)', text)
                if linkedin: socials["linkedin"] = f"https://linkedin.com/company/{linkedin.group(1)}"
                twitter = re.search(r'(?:twitter|x)\.com/([^/"]+)', text)
                if twitter: socials["twitter"] = f"https://x.com/{twitter.group(1)}"
                lead["social_profiles"] = socials
        except:
            pass
    
    lead["enriched"] = True
    lead["enriched_at"] = datetime.utcnow().isoformat() + "Z"
    lead["status"] = "enriched"
    
    # Save to enriched directory
    enriched_path = os.path.join(base_dir, "leads", "enriched", f"{lead['id']}.json")
    with open(enriched_path, "w") as f:
        json.dump(lead, f, indent=2)
    
    # Remove from raw
    if os.path.exists(lead_path) and "/raw/" in lead_path:
        os.remove(lead_path)
    
    contacts = len(lead.get("contacts", []))
    print(f"      ✅ {contacts} contacts, tech: {lead.get('tech_stack', [])}")
    return True

if batch:
    batch_dir = os.path.join(base_dir, "leads", batch)
    files = glob.glob(os.path.join(batch_dir, "*.json"))
    enriched = 0
    for f in files:
        if enrich_lead(f):
            enriched += 1
    print(f"\n📊 Enriched {enriched}/{len(files)} leads")
elif lead_id:
    # Find the lead file
    for subdir in ["raw", "enriched"]:
        path = os.path.join(base_dir, "leads", subdir, f"{lead_id}.json")
        if os.path.exists(path):
            enrich_lead(path)
            break
    else:
        print(f"❌ Lead not found: {lead_id}")
else:
    print("Usage: enrich-leads.sh <lead-id> | --batch raw")
PYEOF
