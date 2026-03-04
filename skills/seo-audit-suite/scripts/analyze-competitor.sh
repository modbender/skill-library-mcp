#!/usr/bin/env bash
# Competitor analysis for a target keyword
set -euo pipefail

KEYWORD=""
COMPETITORS=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --keyword) KEYWORD="$2"; shift 2 ;;
    --competitors) COMPETITORS="$2"; shift 2 ;;
    *) shift ;;
  esac
done

[ -z "$KEYWORD" ] && { echo "Usage: analyze-competitor.sh --keyword \"target keyword\" [--competitors \"site1.com,site2.com\"]"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"
COMP_DIR="$BASE_DIR/sites/competitors"
mkdir -p "$COMP_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SLUG=$(echo "$KEYWORD" | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
OUTPUT="$COMP_DIR/$SLUG-$TIMESTAMP.json"

echo "🔍 Competitor Analysis: \"$KEYWORD\""
echo "   Analyzing top results..."

python3 << PYEOF
import json, sys, os, re
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip3 install requests beautifulsoup4 lxml")
    sys.exit(1)

keyword = "$KEYWORD"
manual_competitors = "$COMPETITORS"
headers = {"User-Agent": "ReighlanSEOBot/1.0"}

# Discover competitors via Brave Search if not specified
competitors = []
if manual_competitors:
    competitors = [{"url": f"https://{c.strip()}", "domain": c.strip()} for c in manual_competitors.split(",")]
else:
    # Use Brave Search API if available
    brave_key = os.environ.get("BRAVE_API_KEY", "")
    if brave_key:
        try:
            search_resp = requests.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": brave_key},
                params={"q": keyword, "count": 10},
                timeout=10
            )
            if search_resp.status_code == 200:
                results = search_resp.json().get("web", {}).get("results", [])
                for r in results[:10]:
                    from urllib.parse import urlparse
                    domain = urlparse(r["url"]).netloc
                    competitors.append({"url": r["url"], "domain": domain, "title": r.get("title", ""), "position": len(competitors) + 1})
        except Exception as e:
            print(f"   ⚠️  Brave Search failed: {e}")
    
    if not competitors:
        print("   ⚠️  No Brave API key. Specify competitors with --competitors or set BRAVE_API_KEY")
        sys.exit(1)

print(f"   Found {len(competitors)} competitors")

# Analyze each competitor
analyses = []
for comp in competitors:
    try:
        resp = requests.get(comp["url"], headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")
        
        text = soup.get_text(separator=" ", strip=True)
        word_count = len(text.split())
        
        title = soup.find("title")
        title_text = title.get_text(strip=True) if title else ""
        
        h_tags = soup.find_all(re.compile(r'^h[1-6]$'))
        headers_list = [{"level": int(h.name[1]), "text": h.get_text(strip=True)[:80]} for h in h_tags]
        
        # Check keyword in key locations
        kw_lower = keyword.lower()
        kw_in_title = kw_lower in title_text.lower()
        kw_in_h1 = any(kw_lower in h.get_text().lower() for h in soup.find_all("h1"))
        kw_in_text = text.lower().count(kw_lower)
        
        # Schema
        schemas = soup.find_all("script", type="application/ld+json")
        schema_types = []
        for s in schemas:
            try:
                data = json.loads(s.string)
                if isinstance(data, dict):
                    schema_types.append(data.get("@type", ""))
            except:
                pass
        
        analysis = {
            "url": comp["url"],
            "domain": comp["domain"],
            "position": comp.get("position"),
            "title": title_text[:100],
            "word_count": word_count,
            "headers_count": len(h_tags),
            "headers": headers_list[:10],
            "keyword_in_title": kw_in_title,
            "keyword_in_h1": kw_in_h1,
            "keyword_frequency": kw_in_text,
            "keyword_density": round(kw_in_text / max(word_count, 1) * 100, 2),
            "schema_types": schema_types,
            "images": len(soup.find_all("img")),
            "internal_links": len([a for a in soup.find_all("a", href=True) if comp["domain"] in a.get("href", "")]),
            "external_links": len([a for a in soup.find_all("a", href=True) if a.get("href", "").startswith("http") and comp["domain"] not in a.get("href", "")]),
        }
        analyses.append(analysis)
        print(f"   ✅ {comp['domain']}: {word_count} words, {len(h_tags)} headers")
    except Exception as e:
        print(f"   ❌ {comp['domain']}: {e}")

# Summary stats
if analyses:
    avg_words = sum(a["word_count"] for a in analyses) / len(analyses)
    avg_headers = sum(a["headers_count"] for a in analyses) / len(analyses)
    kw_in_title_pct = sum(1 for a in analyses if a["keyword_in_title"]) / len(analyses) * 100
    
    summary = {
        "keyword": keyword,
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
        "competitor_count": len(analyses),
        "averages": {
            "word_count": round(avg_words),
            "headers": round(avg_headers),
            "keyword_in_title_pct": round(kw_in_title_pct),
        },
        "competitors": analyses,
        "insights": []
    }
    
    # Generate insights
    if avg_words > 2000:
        summary["insights"].append(f"Competitive keyword — average content is {avg_words:.0f} words. You need 2000+ words to compete.")
    elif avg_words > 1000:
        summary["insights"].append(f"Moderate competition — average {avg_words:.0f} words. Aim for {avg_words*1.2:.0f}+ words.")
    else:
        summary["insights"].append(f"Low competition — average only {avg_words:.0f} words. Opportunity to dominate with comprehensive content.")
    
    if kw_in_title_pct > 70:
        summary["insights"].append("Most competitors have keyword in title — you should too.")
    
    schema_usage = sum(1 for a in analyses if a["schema_types"]) / len(analyses) * 100
    if schema_usage < 50:
        summary["insights"].append(f"Only {schema_usage:.0f}% of competitors use schema — easy win with structured data.")
    
    with open("$OUTPUT", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n📊 Summary:")
    print(f"   Avg word count: {avg_words:.0f}")
    print(f"   Avg headers: {avg_headers:.0f}")
    print(f"   Keyword in title: {kw_in_title_pct:.0f}%")
    print(f"\n   💡 Insights:")
    for insight in summary["insights"]:
        print(f"      → {insight}")
    print(f"\n   Full analysis: $OUTPUT")
PYEOF
