#!/usr/bin/env bash
# On-page SEO audit for a single URL
set -euo pipefail

URL="${1:-}"
DEPTH="${3:-0}"
[ -z "$URL" ] && { echo "Usage: audit-page.sh <url> [--depth N]"; exit 1; }

while [[ $# -gt 1 ]]; do
  case $2 in
    --depth) DEPTH="$3"; shift 2 ;;
    *) shift ;;
  esac
done

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"
DOMAIN=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$URL').netloc)")
SITE_DIR="$BASE_DIR/sites/$DOMAIN/audits"
mkdir -p "$SITE_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT="$SITE_DIR/onpage-$TIMESTAMP.json"

export AUDIT_URL="$URL"
export OUTPUT_PATH="$OUTPUT"

python3 << 'PYEOF'
import json, sys, re, os
from urllib.parse import urlparse, urljoin
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip3 install requests beautifulsoup4 lxml")
    sys.exit(1)

url = sys.argv[1] if len(sys.argv) > 1 else ""
if not url:
    url = os.environ["AUDIT_URL"]

headers = {"User-Agent": "ReighlanSEOBot/1.0"}

try:
    resp = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
except Exception as e:
    print(f"❌ Failed to fetch {url}: {e}")
    sys.exit(1)

soup = BeautifulSoup(resp.text, "lxml")
issues = []
scores = {}

# --- Title Tag ---
title_tag = soup.find("title")
title = title_tag.get_text(strip=True) if title_tag else ""
if not title:
    issues.append({"severity": "critical", "check": "title", "message": "Missing title tag"})
    scores["title"] = 0
elif len(title) < 30:
    issues.append({"severity": "warning", "check": "title", "message": f"Title too short ({len(title)} chars, aim for 50-60)"})
    scores["title"] = 50
elif len(title) > 65:
    issues.append({"severity": "warning", "check": "title", "message": f"Title too long ({len(title)} chars, may truncate in SERPs)"})
    scores["title"] = 70
else:
    scores["title"] = 100

# --- Meta Description ---
meta_desc_tag = soup.find("meta", attrs={"name": "description"})
meta_desc = meta_desc_tag.get("content", "") if meta_desc_tag else ""
if not meta_desc:
    issues.append({"severity": "critical", "check": "meta_description", "message": "Missing meta description"})
    scores["meta_description"] = 0
elif len(meta_desc) < 120:
    issues.append({"severity": "warning", "check": "meta_description", "message": f"Meta description short ({len(meta_desc)} chars, aim for 150-160)"})
    scores["meta_description"] = 60
elif len(meta_desc) > 165:
    issues.append({"severity": "info", "check": "meta_description", "message": f"Meta description long ({len(meta_desc)} chars, may truncate)"})
    scores["meta_description"] = 80
else:
    scores["meta_description"] = 100

# --- H1 Tag ---
h1_tags = soup.find_all("h1")
if len(h1_tags) == 0:
    issues.append({"severity": "critical", "check": "h1", "message": "Missing H1 tag"})
    scores["h1"] = 0
elif len(h1_tags) > 1:
    issues.append({"severity": "warning", "check": "h1", "message": f"Multiple H1 tags found ({len(h1_tags)}), should have exactly one"})
    scores["h1"] = 60
else:
    scores["h1"] = 100

# --- Header Hierarchy ---
headers_found = []
for i in range(1, 7):
    for h in soup.find_all(f"h{i}"):
        headers_found.append({"level": i, "text": h.get_text(strip=True)[:80]})

hierarchy_ok = True
if headers_found:
    levels = [h["level"] for h in headers_found]
    for i in range(1, len(levels)):
        if levels[i] > levels[i-1] + 1:
            hierarchy_ok = False
            break

if not hierarchy_ok:
    issues.append({"severity": "warning", "check": "header_hierarchy", "message": "Header hierarchy has gaps (e.g., H1 → H3 skipping H2)"})
    scores["header_hierarchy"] = 60
else:
    scores["header_hierarchy"] = 100

# --- Images ---
images = soup.find_all("img")
images_without_alt = [img.get("src", "unknown")[:60] for img in images if not img.get("alt")]
if images_without_alt:
    issues.append({"severity": "warning", "check": "images", "message": f"{len(images_without_alt)}/{len(images)} images missing alt text"})
    scores["images"] = max(0, 100 - (len(images_without_alt) / max(len(images), 1) * 100))
else:
    scores["images"] = 100

# --- Links ---
internal_links = []
external_links = []
parsed_url = urlparse(url)
for a in soup.find_all("a", href=True):
    href = a["href"]
    resolved = urljoin(url, href)
    parsed_href = urlparse(resolved)
    if parsed_href.netloc == parsed_url.netloc:
        internal_links.append(resolved)
    elif parsed_href.scheme in ("http", "https"):
        external_links.append(resolved)

scores["internal_links"] = 100 if len(internal_links) >= 3 else 50
if len(internal_links) < 3:
    issues.append({"severity": "warning", "check": "internal_links", "message": f"Only {len(internal_links)} internal links (aim for 3+)"})

# --- Word Count ---
text = soup.get_text(separator=" ", strip=True)
word_count = len(text.split())
if word_count < 300:
    issues.append({"severity": "warning", "check": "word_count", "message": f"Thin content ({word_count} words, minimum 300 for ranking)"})
    scores["word_count"] = 30
elif word_count < 800:
    scores["word_count"] = 70
else:
    scores["word_count"] = 100

# --- Schema Markup ---
scripts = soup.find_all("script", type="application/ld+json")
if not scripts:
    issues.append({"severity": "warning", "check": "schema", "message": "No JSON-LD structured data found"})
    scores["schema"] = 0
else:
    scores["schema"] = 100

# --- Open Graph ---
og_title = soup.find("meta", property="og:title")
og_desc = soup.find("meta", property="og:description")
og_image = soup.find("meta", property="og:image")
og_score = sum([bool(og_title), bool(og_desc), bool(og_image)]) / 3 * 100
if og_score < 100:
    missing = []
    if not og_title: missing.append("og:title")
    if not og_desc: missing.append("og:description")
    if not og_image: missing.append("og:image")
    issues.append({"severity": "info", "check": "open_graph", "message": f"Missing OG tags: {', '.join(missing)}"})
scores["open_graph"] = og_score

# --- Canonical ---
canonical = soup.find("link", rel="canonical")
if not canonical:
    issues.append({"severity": "warning", "check": "canonical", "message": "Missing canonical tag"})
    scores["canonical"] = 0
else:
    scores["canonical"] = 100

# --- HTTPS ---
is_https = parsed_url.scheme == "https"
if not is_https:
    issues.append({"severity": "critical", "check": "https", "message": "Site not using HTTPS"})
    scores["https"] = 0
else:
    scores["https"] = 100

# --- Viewport (Mobile) ---
viewport = soup.find("meta", attrs={"name": "viewport"})
if not viewport:
    issues.append({"severity": "warning", "check": "mobile", "message": "Missing viewport meta tag"})
    scores["mobile"] = 0
else:
    scores["mobile"] = 100

# --- Overall Score ---
overall = sum(scores.values()) / len(scores) if scores else 0
grade = "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D" if overall >= 60 else "F"

result = {
    "url": url,
    "domain": parsed_url.netloc,
    "audited_at": datetime.utcnow().isoformat() + "Z",
    "status_code": resp.status_code,
    "overall_score": round(overall, 1),
    "grade": grade,
    "scores": {k: round(v, 1) for k, v in scores.items()},
    "issues": sorted(issues, key=lambda x: {"critical": 0, "warning": 1, "info": 2}[x["severity"]]),
    "meta": {
        "title": title,
        "meta_description": meta_desc[:200],
        "h1": [h.get_text(strip=True)[:80] for h in h1_tags],
        "word_count": word_count,
        "internal_links": len(internal_links),
        "external_links": len(external_links),
        "images": len(images),
        "images_without_alt": len(images_without_alt),
        "has_schema": bool(scripts),
        "has_canonical": bool(canonical),
        "is_https": is_https,
    }
}

output_path = os.environ["OUTPUT_PATH"]
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

# Print summary
print(f"🔍 SEO Audit: {url}")
print(f"   Score: {overall:.0f}/100 ({grade})")
print(f"   Title: {title[:60]}{'...' if len(title) > 60 else ''}")
print(f"   Words: {word_count} | Links: {len(internal_links)} int / {len(external_links)} ext | Images: {len(images)}")
print()

criticals = [i for i in issues if i["severity"] == "critical"]
warnings = [i for i in issues if i["severity"] == "warning"]
infos = [i for i in issues if i["severity"] == "info"]

if criticals:
    print("   🔴 Critical:")
    for i in criticals:
        print(f"      • {i['message']}")
if warnings:
    print("   🟡 Warnings:")
    for i in warnings:
        print(f"      • {i['message']}")
if infos:
    print("   🔵 Info:")
    for i in infos:
        print(f"      • {i['message']}")

print(f"\n   Full report: {output_path}")
PYEOF
