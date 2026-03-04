#!/usr/bin/env bash
set -euo pipefail

QUERY=""
COUNT=10
INDUSTRY=""
LOCATION=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --query) QUERY="$2"; shift 2 ;;
    --count) COUNT="$2"; shift 2 ;;
    --industry) INDUSTRY="$2"; shift 2 ;;
    --location) LOCATION="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$QUERY" ] && { echo "Usage: discover-leads.sh --query \"search terms\" [--count N] [--industry X] [--location Y]"; exit 1; }

BASE_DIR="${LEAD_GEN_DIR:-$HOME/.openclaw/workspace/lead-gen}"
RAW_DIR="$BASE_DIR/leads/raw"
mkdir -p "$RAW_DIR"

export LEAD_QUERY="$QUERY"
export LEAD_COUNT="$COUNT"
export LEAD_INDUSTRY="$INDUSTRY"
export LEAD_LOCATION="$LOCATION"
export LEAD_RAW_DIR="$RAW_DIR"

python3 << 'PYEOF'
import json, os, sys, re, hashlib
from datetime import datetime
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

query = os.environ["LEAD_QUERY"]
count = int(os.environ["LEAD_COUNT"])
industry = os.environ.get("LEAD_INDUSTRY", "")
location = os.environ.get("LEAD_LOCATION", "")
raw_dir = os.environ["LEAD_RAW_DIR"]

brave_key = os.environ.get("BRAVE_API_KEY", "")
if not brave_key:
    print("❌ BRAVE_API_KEY required for lead discovery")
    sys.exit(1)

# Build search query
search_query = query
if industry:
    search_query += f" {industry}"
if location:
    search_query += f" {location}"

print(f"🔍 Discovering leads: \"{search_query}\"")

try:
    resp = requests.get(
        "https://api.search.brave.com/res/v1/web/search",
        headers={"X-Subscription-Token": brave_key},
        params={"q": search_query, "count": min(count, 20)},
        timeout=15,
    )
    results = resp.json().get("web", {}).get("results", [])
except Exception as e:
    print(f"❌ Search failed: {e}")
    sys.exit(1)

leads_created = 0
for r in results:
    url = r.get("url", "")
    domain = urlparse(url).netloc
    title = r.get("title", "")
    description = r.get("description", "")

    # Skip social media, wikipedia, etc.
    skip_domains = ["wikipedia.org", "facebook.com", "twitter.com", "linkedin.com", "youtube.com", "reddit.com", "yelp.com"]
    if any(sd in domain for sd in skip_domains):
        continue

    # Generate stable ID from domain
    lead_id = hashlib.md5(domain.encode()).hexdigest()[:12]
    lead_file = os.path.join(raw_dir, f"{lead_id}.json")

    if os.path.exists(lead_file):
        continue

    # Extract any email patterns from description
    emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.]+', description)

    # Try to extract company name from title
    company_name = title.split(" - ")[0].split(" | ")[0].split(" — ")[0].strip()

    lead = {
        "id": lead_id,
        "company_name": company_name,
        "domain": domain,
        "url": url,
        "description": description[:300],
        "emails_found": emails,
        "industry": industry or "unknown",
        "location": location or "unknown",
        "source": "brave_search",
        "source_query": search_query,
        "discovered_at": datetime.utcnow().isoformat() + "Z",
        "status": "raw",
        "score": None,
        "enriched": False,
    }

    with open(lead_file, "w") as f:
        json.dump(lead, f, indent=2)
    leads_created += 1
    print(f"   ✅ {company_name} ({domain})")

print(f"\n📊 Discovered {leads_created} new leads")
print(f"   Saved to: {raw_dir}")
print(f"   Next: Run enrich-leads.sh --batch raw")
PYEOF
