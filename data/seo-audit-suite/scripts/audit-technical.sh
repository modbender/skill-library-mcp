#!/usr/bin/env bash
# Technical SEO audit
set -euo pipefail

URL="${1:-}"
[ -z "$URL" ] && { echo "Usage: audit-technical.sh <url>"; exit 1; }

BASE_DIR="${SEO_AUDIT_DIR:-$HOME/.openclaw/workspace/seo-audit}"
DOMAIN=$(python3 -c "from urllib.parse import urlparse; print(urlparse('$URL').netloc)")
SITE_DIR="$BASE_DIR/sites/$DOMAIN/audits"
mkdir -p "$SITE_DIR"

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTPUT="$SITE_DIR/technical-$TIMESTAMP.json"

python3 << 'PYEOF'
import json, sys, os
from urllib.parse import urlparse, urljoin
from datetime import datetime

try:
    import requests
except ImportError:
    print("Missing requests. Run: pip3 install requests")
    sys.exit(1)

url = os.environ.get("AUDIT_URL", "") or """" + URL + """"
parsed = urlparse(url)
base_url = f"{parsed.scheme}://{parsed.netloc}"
headers = {"User-Agent": "ReighlanSEOBot/1.0"}
issues = []
scores = {}

def safe_get(check_url, **kwargs):
    try:
        return requests.get(check_url, headers=headers, timeout=10, allow_redirects=True, **kwargs)
    except:
        return None

# --- HTTPS ---
if parsed.scheme != "https":
    issues.append({"severity": "critical", "check": "https", "message": "Not using HTTPS"})
    scores["https"] = 0
else:
    scores["https"] = 100

# --- Response Time ---
try:
    resp = requests.get(url, headers=headers, timeout=15)
    response_time = resp.elapsed.total_seconds()
    if response_time > 3:
        issues.append({"severity": "critical", "check": "speed", "message": f"Slow response: {response_time:.1f}s (should be <1s)"})
        scores["speed"] = 20
    elif response_time > 1:
        issues.append({"severity": "warning", "check": "speed", "message": f"Response time: {response_time:.1f}s (aim for <1s)"})
        scores["speed"] = 60
    else:
        scores["speed"] = 100
except Exception as e:
    issues.append({"severity": "critical", "check": "speed", "message": f"Could not reach site: {e}"})
    scores["speed"] = 0

# --- Robots.txt ---
robots_resp = safe_get(f"{base_url}/robots.txt")
if robots_resp and robots_resp.status_code == 200:
    robots_text = robots_resp.text
    if "Disallow: /" in robots_text and "Disallow: /\n" not in robots_text:
        issues.append({"severity": "critical", "check": "robots", "message": "robots.txt blocks all crawling"})
        scores["robots"] = 0
    else:
        scores["robots"] = 100
else:
    issues.append({"severity": "warning", "check": "robots", "message": "No robots.txt found"})
    scores["robots"] = 50

# --- Sitemap ---
sitemap_found = False
sitemap_url = f"{base_url}/sitemap.xml"
sitemap_resp = safe_get(sitemap_url)
if sitemap_resp and sitemap_resp.status_code == 200 and "<?xml" in sitemap_resp.text[:100]:
    sitemap_found = True
    scores["sitemap"] = 100
else:
    # Check robots.txt for sitemap directive
    if robots_resp and robots_resp.status_code == 200:
        for line in robots_resp.text.split("\n"):
            if line.lower().startswith("sitemap:"):
                alt_url = line.split(":", 1)[1].strip()
                alt_resp = safe_get(alt_url)
                if alt_resp and alt_resp.status_code == 200:
                    sitemap_found = True
                    scores["sitemap"] = 100
                    break

    if not sitemap_found:
        issues.append({"severity": "warning", "check": "sitemap", "message": "No XML sitemap found"})
        scores["sitemap"] = 0

# --- Redirect Chains ---
try:
    check_resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
    redirects = len(check_resp.history)
    if redirects > 2:
        issues.append({"severity": "warning", "check": "redirects", "message": f"Redirect chain: {redirects} hops (max 2)"})
        scores["redirects"] = 40
    elif redirects > 0:
        scores["redirects"] = 80
    else:
        scores["redirects"] = 100
except:
    scores["redirects"] = 50

# --- PageSpeed Insights (if API key available) ---
pagespeed_key = os.environ.get("PAGESPEED_API_KEY", "")
cwv = {}
if pagespeed_key:
    try:
        ps_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={pagespeed_key}&strategy=mobile"
        ps_resp = requests.get(ps_url, timeout=30)
        if ps_resp.status_code == 200:
            ps_data = ps_resp.json()
            perf_score = ps_data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0)
            scores["core_web_vitals"] = int((perf_score or 0) * 100)
            
            metrics = ps_data.get("lighthouseResult", {}).get("audits", {})
            cwv = {
                "lcp": metrics.get("largest-contentful-paint", {}).get("displayValue", "N/A"),
                "cls": metrics.get("cumulative-layout-shift", {}).get("displayValue", "N/A"),
                "fcp": metrics.get("first-contentful-paint", {}).get("displayValue", "N/A"),
            }
            
            if scores["core_web_vitals"] < 50:
                issues.append({"severity": "critical", "check": "core_web_vitals", "message": f"Poor Core Web Vitals score: {scores['core_web_vitals']}/100"})
            elif scores["core_web_vitals"] < 90:
                issues.append({"severity": "warning", "check": "core_web_vitals", "message": f"Core Web Vitals needs improvement: {scores['core_web_vitals']}/100"})
    except:
        pass

# --- Overall ---
overall = sum(scores.values()) / len(scores) if scores else 0
grade = "A" if overall >= 90 else "B" if overall >= 80 else "C" if overall >= 70 else "D" if overall >= 60 else "F"

result = {
    "url": url,
    "domain": parsed.netloc,
    "audit_type": "technical",
    "audited_at": datetime.utcnow().isoformat() + "Z",
    "overall_score": round(overall, 1),
    "grade": grade,
    "scores": {k: round(v, 1) for k, v in scores.items()},
    "issues": sorted(issues, key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 3)),
    "core_web_vitals": cwv,
    "meta": {
        "has_robots": scores.get("robots", 0) > 0,
        "has_sitemap": sitemap_found,
        "redirect_hops": redirects if 'redirects' in dir() else 0,
        "response_time_s": response_time if 'response_time' in dir() else None,
    }
}

output_path = """" + OUTPUT + """"
with open(output_path, "w") as f:
    json.dump(result, f, indent=2)

print(f"⚙️  Technical SEO Audit: {url}")
print(f"   Score: {overall:.0f}/100 ({grade})")
if cwv:
    print(f"   Core Web Vitals — LCP: {cwv.get('lcp', 'N/A')} | CLS: {cwv.get('cls', 'N/A')} | FCP: {cwv.get('fcp', 'N/A')}")

criticals = [i for i in issues if i["severity"] == "critical"]
warnings = [i for i in issues if i["severity"] == "warning"]

if criticals:
    print("   🔴 Critical:")
    for i in criticals:
        print(f"      • {i['message']}")
if warnings:
    print("   🟡 Warnings:")
    for i in warnings:
        print(f"      • {i['message']}")

print(f"\n   Full report: {output_path}")
PYEOF
