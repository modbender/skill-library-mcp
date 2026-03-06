#!/usr/bin/env bash
# Track keyword rankings over time
set -euo pipefail

SITE=""
KEYWORDS=""
REPORT=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --site) SITE="$2"; shift 2 ;;
    --keywords) KEYWORDS="$2"; shift 2 ;;
    --report) REPORT=true; shift ;;
    *) shift ;;
  esac
done

[ -z "$SITE" ] && { echo "Usage: track-keywords.sh --site <domain> --keywords \"kw1,kw2\" | --report"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"
KW_DIR="$BASE_DIR/sites/$SITE/keywords"
mkdir -p "$KW_DIR"

if [ "$REPORT" = true ]; then
  echo "📈 Keyword Rankings: $SITE"
  echo "========================="
  python3 << PYEOF
import json, glob, os
from datetime import datetime

kw_dir = "$KW_DIR"
files = sorted(glob.glob(f"{kw_dir}/tracking-*.json"), reverse=True)

if not files:
    print("   No tracking data yet. Run with --keywords first.")
    exit(0)

# Load last two checks for comparison
latest = json.load(open(files[0]))
previous = json.load(open(files[1])) if len(files) > 1 else None

prev_rankings = {}
if previous:
    for kw in previous.get("rankings", []):
        prev_rankings[kw["keyword"]] = kw.get("position")

print(f"   Last checked: {latest['checked_at']}")
print()
for kw in latest.get("rankings", []):
    pos = kw.get("position", "N/A")
    prev_pos = prev_rankings.get(kw["keyword"])
    
    change = ""
    if prev_pos and pos != "N/A":
        diff = prev_pos - pos  # positive = improved
        if diff > 0:
            change = f" ↑{diff} 🟢"
        elif diff < 0:
            change = f" ↓{abs(diff)} 🔴"
        else:
            change = " ─"
    
    print(f"   #{pos if pos != 'N/A' else '100+':<4} {kw['keyword']}{change}")
PYEOF
  exit 0
fi

[ -z "$KEYWORDS" ] && { echo "Provide --keywords or --report"; exit 1; }

echo "🔍 Checking rankings for $SITE..."

python3 << PYEOF
import json, os, sys
from datetime import datetime

try:
    import requests
except ImportError:
    print("pip3 install requests")
    sys.exit(1)

site = "$SITE"
keywords = [k.strip() for k in "$KEYWORDS".split(",")]
brave_key = os.environ.get("BRAVE_API_KEY", "")

if not brave_key:
    print("❌ BRAVE_API_KEY required for ranking checks")
    sys.exit(1)

rankings = []
for kw in keywords:
    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers={"X-Subscription-Token": brave_key},
            params={"q": kw, "count": 10},
            timeout=10
        )
        position = None
        if resp.status_code == 200:
            results = resp.json().get("web", {}).get("results", [])
            for i, r in enumerate(results):
                if site.lower() in r.get("url", "").lower():
                    position = i + 1
                    break
        
        rankings.append({
            "keyword": kw,
            "position": position if position else "N/A",
            "url": r["url"] if position and i < len(results) else None
        })
        
        status = f"#{position}" if position else "Not in top 10"
        print(f"   {kw}: {status}")
    except Exception as e:
        print(f"   {kw}: Error — {e}")
        rankings.append({"keyword": kw, "position": "N/A", "error": str(e)})

# Save tracking data
tracking = {
    "site": site,
    "checked_at": datetime.utcnow().isoformat() + "Z",
    "rankings": rankings
}

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
output = f"$KW_DIR/tracking-{timestamp}.json"
with open(output, "w") as f:
    json.dump(tracking, f, indent=2)

print(f"\n   Saved: {output}")
PYEOF
