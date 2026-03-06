#!/usr/bin/env bash
set -euo pipefail

THRESHOLD=70

while [[ $# -gt 0 ]]; do
  case $1 in
    --threshold) THRESHOLD="$2"; shift 2 ;;
    *) shift ;;
  esac
done

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"

export LEAD_BASE_DIR="$BASE_DIR"
export SCORE_THRESHOLD="$THRESHOLD"

python3 << 'PYEOF'
import json, os, glob

base_dir = os.environ["LEAD_BASE_DIR"]
threshold = int(os.environ["SCORE_THRESHOLD"])

config_path = os.path.join(base_dir, "config.json")
config = {}
if os.path.exists(config_path):
    with open(config_path) as f:
        config = json.load(f)

scoring = config.get("scoring", {})
weights = scoring.get("weights", {
    "company_size_fit": 25,
    "industry_match": 25,
    "email_available": 20,
    "web_presence": 15,
    "tech_signals": 15,
})
target_industries = [i.lower() for i in scoring.get("target_industries", [])]
target_sizes = scoring.get("target_company_sizes", ["1-10", "11-50", "51-200"])

enriched_dir = os.path.join(base_dir, "leads", "enriched")
qualified_dir = os.path.join(base_dir, "leads", "qualified")
os.makedirs(qualified_dir, exist_ok=True)

files = glob.glob(os.path.join(enriched_dir, "*.json"))
qualified = 0
total = 0

print(f"📊 Scoring {len(files)} enriched leads (threshold: {threshold})")
print()

for f in files:
    with open(f) as fh:
        lead = json.load(fh)
    
    scores = {}
    
    # Company size fit
    size = lead.get("company_size", "unknown")
    if size in target_sizes:
        scores["company_size_fit"] = weights["company_size_fit"]
    elif size != "unknown":
        scores["company_size_fit"] = weights["company_size_fit"] * 0.5
    else:
        scores["company_size_fit"] = weights["company_size_fit"] * 0.3
    
    # Industry match
    industry = lead.get("industry", "unknown").lower()
    if target_industries and industry in target_industries:
        scores["industry_match"] = weights["industry_match"]
    elif target_industries:
        scores["industry_match"] = weights["industry_match"] * 0.2
    else:
        scores["industry_match"] = weights["industry_match"] * 0.5  # No filter = medium score
    
    # Email available
    contacts = lead.get("contacts", [])
    emails = lead.get("emails_found", [])
    if contacts and any(c.get("confidence", 0) > 80 for c in contacts):
        scores["email_available"] = weights["email_available"]
    elif emails:
        scores["email_available"] = weights["email_available"] * 0.7
    else:
        scores["email_available"] = 0
    
    # Web presence
    has_website = bool(lead.get("domain"))
    has_social = bool(lead.get("social_profiles"))
    web_score = 0
    if has_website: web_score += 0.6
    if has_social: web_score += 0.4
    scores["web_presence"] = weights["web_presence"] * web_score
    
    # Tech signals
    tech = lead.get("tech_stack", [])
    if len(tech) >= 3:
        scores["tech_signals"] = weights["tech_signals"]
    elif tech:
        scores["tech_signals"] = weights["tech_signals"] * 0.5
    else:
        scores["tech_signals"] = weights["tech_signals"] * 0.2
    
    total_score = round(sum(scores.values()))
    lead["score"] = total_score
    lead["score_breakdown"] = {k: round(v, 1) for k, v in scores.items()}
    
    total += 1
    
    if total_score >= threshold:
        lead["status"] = "qualified"
        dest = os.path.join(qualified_dir, f"{lead['id']}.json")
        with open(dest, "w") as fh:
            json.dump(lead, fh, indent=2)
        if os.path.exists(f):
            os.remove(f)
        qualified += 1
        print(f"   ✅ {lead.get('company_name', lead['id'])}: {total_score}/100 — QUALIFIED")
    else:
        with open(f, "w") as fh:
            json.dump(lead, fh, indent=2)
        print(f"   ⬜ {lead.get('company_name', lead['id'])}: {total_score}/100")

print(f"\n📊 Results: {qualified}/{total} qualified (threshold: {threshold})")
print(f"   Next: Run push-to-crm.sh --batch qualified")
PYEOF
