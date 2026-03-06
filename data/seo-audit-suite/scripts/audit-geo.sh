#!/usr/bin/env bash
# GEO (Generative Engine Optimization) audit
set -euo pipefail

URL="${1:-}"
[ -z "$URL" ] && { echo "Usage: audit-geo.sh <url>"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"
DOMAIN=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$URL').netloc)")
SITE_DIR="$BASE_DIR/sites/$DOMAIN/audits"
mkdir -p "$SITE_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT="$SITE_DIR/geo-$TIMESTAMP.json"

python3 << 'PYEOF'
import json, sys, re, os
from urllib.parse import urlparse
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip3 install requests beautifulsoup4 lxml")
    sys.exit(1)

url = os.environ.get("AUDIT_URL", "") or """" + URL + """"
headers = {"User-Agent": "ReighlanSEOBot/1.0"}

try:
    resp = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(resp.text, "lxml")
except Exception as e:
    print(f"❌ Failed to fetch {url}: {e}")
    sys.exit(1)

issues = []
scores = {}
recommendations = []

text = soup.get_text(separator="\n", strip=True)
paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 20]

# --- Content Structure (Q&A patterns) ---
qa_patterns = len(re.findall(r'\b(what|how|why|when|where|who|which|can|does|is|are)\b.*\?', text, re.IGNORECASE))
has_faq_headers = bool(re.search(r'<h[2-4][^>]*>.*?(FAQ|frequently asked|questions)', resp.text, re.IGNORECASE))

if qa_patterns >= 3 or has_faq_headers:
    scores["qa_structure"] = 100
elif qa_patterns >= 1:
    scores["qa_structure"] = 60
    recommendations.append("Add more Q&A formatted content — AI engines love extracting clear question-answer pairs")
else:
    scores["qa_structure"] = 20
    issues.append({"severity": "warning", "check": "qa_structure", "message": "No Q&A patterns found — add FAQ sections or question-based headers"})
    recommendations.append("Add FAQ section with common questions about your topic")

# --- Concise Answers (first sentences of sections) ---
h_tags = soup.find_all(re.compile(r'^h[1-6]$'))
concise_count = 0
for h in h_tags:
    next_p = h.find_next("p")
    if next_p:
        first_sentence = next_p.get_text(strip=True).split(".")[0]
        if 20 < len(first_sentence) < 200:
            concise_count += 1

if h_tags:
    concise_ratio = concise_count / len(h_tags)
    scores["concise_answers"] = min(100, int(concise_ratio * 100))
    if concise_ratio < 0.5:
        issues.append({"severity": "warning", "check": "concise_answers", "message": "Many sections lack concise opening sentences"})
        recommendations.append("Start each section with a direct, concise answer — AI engines extract these as snippets")
else:
    scores["concise_answers"] = 30

# --- Statistics & Data Points ---
stat_patterns = len(re.findall(r'\d+(?:\.\d+)?(?:%| percent|x |times|million|billion|thousand)', text, re.IGNORECASE))
if stat_patterns >= 5:
    scores["data_points"] = 100
elif stat_patterns >= 2:
    scores["data_points"] = 70
    recommendations.append("Add more specific statistics and data points — they increase citation likelihood")
else:
    scores["data_points"] = 30
    issues.append({"severity": "warning", "check": "data_points", "message": f"Only {stat_patterns} data points found — AI engines prefer content with specific stats"})
    recommendations.append("Include specific numbers, percentages, and statistics throughout your content")

# --- Schema Richness ---
schemas = soup.find_all("script", type="application/ld+json")
schema_types = []
for s in schemas:
    try:
        data = json.loads(s.string)
        if isinstance(data, dict):
            schema_types.append(data.get("@type", "unknown"))
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    schema_types.append(item.get("@type", "unknown"))
    except:
        pass

geo_schemas = {"FAQPage", "HowTo", "Article", "NewsArticle", "BlogPosting", "WebPage", "Organization", "Person"}
matched = set(schema_types) & geo_schemas

if len(matched) >= 3:
    scores["schema_richness"] = 100
elif len(matched) >= 1:
    scores["schema_richness"] = 60
    missing = geo_schemas - matched
    recommendations.append(f"Add more schema types. Consider: {', '.join(list(missing)[:3])}")
else:
    scores["schema_richness"] = 0
    issues.append({"severity": "warning", "check": "schema_richness", "message": "No GEO-relevant schema markup found"})
    recommendations.append("Add FAQPage, Article, or HowTo schema — critical for AI engine visibility")

# --- E-E-A-T Signals ---
eeat_score = 0
# Author info
has_author = bool(soup.find(string=re.compile(r'(written by|author|by\s)', re.IGNORECASE)))
if has_author: eeat_score += 25

# About page link
has_about = bool(soup.find("a", href=re.compile(r'/about', re.IGNORECASE)))
if has_about: eeat_score += 25

# Date/freshness
has_date = bool(soup.find("time") or re.search(r'\b(20[12]\d[-/]\d{2}[-/]\d{2}|January|February|March|April|May|June|July|August|September|October|November|December)\b', text))
if has_date: eeat_score += 25

# Sources/references
has_sources = len(soup.find_all("a", href=re.compile(r'^https?://'))) >= 3
if has_sources: eeat_score += 25

scores["eeat_signals"] = eeat_score
if eeat_score < 50:
    issues.append({"severity": "warning", "check": "eeat", "message": f"Weak E-E-A-T signals ({eeat_score}/100)"})
    if not has_author: recommendations.append("Add visible author attribution")
    if not has_about: recommendations.append("Link to an About page")
    if not has_date: recommendations.append("Add publish/update dates")
    if not has_sources: recommendations.append("Include outbound links to authoritative sources")

# --- Topical Depth ---
word_count = len(text.split())
unique_headers = len(set(h.get_text(strip=True).lower() for h in h_tags))

if word_count >= 2000 and unique_headers >= 5:
    scores["topical_depth"] = 100
elif word_count >= 1000 and unique_headers >= 3:
    scores["topical_depth"] = 70
else:
    scores["topical_depth"] = 40
    recommendations.append("Increase content depth — cover subtopics comprehensively with dedicated sections")

# --- Overall GEO Score ---
overall = sum(scores.values()) / len(scores) if scores else 0
grade = "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D" if overall >= 60 else "F"

result = {
    "url": url,
    "audit_type": "geo",
    "audited_at": datetime.utcnow().isoformat() + "Z",
    "geo_score": round(overall, 1),
    "grade": grade,
    "scores": {k: round(v, 1) for k, v in scores.items()},
    "issues": issues,
    "recommendations": recommendations,
    "meta": {
        "word_count": word_count,
        "qa_patterns": qa_patterns,
        "data_points": stat_patterns,
        "schema_types": schema_types,
        "headers_count": len(h_tags),
    }
}

output_path = """" + OUTPUT + """"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"🤖 GEO Audit: {url}")
print(f"   GEO Readiness Score: {overall:.0f}/100 ({grade})")
print()
print("   Scores:")
for k, v in sorted(scores.items(), key=lambda x: x[1]):
    bar = "█" * int(v/10) + "░" * (10 - int(v/10))
    print(f"      {k:20s} {bar} {v:.0f}")

if recommendations:
    print()
    print("   💡 Top Recommendations:")
    for r in recommendations[:5]:
        print(f"      → {r}")

print(f"\n   Full report: {output_path}")
PYEOF
