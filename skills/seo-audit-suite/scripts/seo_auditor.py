#!/usr/bin/env python3
"""Core SEO auditing engine. Analyzes a URL for on-page, technical, and GEO factors."""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse, urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip3 install beautifulsoup4 requests lxml")
    sys.exit(1)


def fetch_page(url, timeout=15):
    """Fetch a page and return response + timing."""
    headers = {"User-Agent": "ReighlanSEOBot/1.0 (+https://reighlan.dev)"}
    start = time.time()
    resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    load_time = time.time() - start
    return resp, load_time


def audit_title(soup):
    """Audit title tag."""
    issues = []
    score = 100
    title_tag = soup.find("title")

    if not title_tag or not title_tag.string:
        return {"score": 0, "value": None, "issues": [{"severity": "critical", "msg": "Missing title tag"}]}

    title = title_tag.string.strip()
    length = len(title)

    if length < 30:
        issues.append({"severity": "warning", "msg": f"Title too short ({length} chars, aim for 50-60)"})
        score -= 20
    elif length > 60:
        issues.append({"severity": "warning", "msg": f"Title may be truncated in SERPs ({length} chars, aim for 50-60)"})
        score -= 10

    if title.lower() in ["home", "homepage", "untitled", "welcome"]:
        issues.append({"severity": "critical", "msg": "Generic/non-descriptive title"})
        score -= 40

    return {"score": max(0, score), "value": title, "length": length, "issues": issues}


def audit_meta_description(soup):
    """Audit meta description."""
    issues = []
    score = 100
    meta = soup.find("meta", attrs={"name": "description"})

    if not meta or not meta.get("content"):
        return {"score": 0, "value": None, "issues": [{"severity": "critical", "msg": "Missing meta description"}]}

    desc = meta["content"].strip()
    length = len(desc)

    if length < 120:
        issues.append({"severity": "warning", "msg": f"Meta description short ({length} chars, aim for 150-160)"})
        score -= 15
    elif length > 160:
        issues.append({"severity": "info", "msg": f"Meta description may be truncated ({length} chars)"})
        score -= 5

    return {"score": max(0, score), "value": desc, "length": length, "issues": issues}


def audit_headings(soup):
    """Audit heading hierarchy."""
    issues = []
    score = 100

    h1s = soup.find_all("h1")
    h2s = soup.find_all("h2")

    if len(h1s) == 0:
        issues.append({"severity": "critical", "msg": "No H1 tag found"})
        score -= 40
    elif len(h1s) > 1:
        issues.append({"severity": "warning", "msg": f"Multiple H1 tags found ({len(h1s)})"})
        score -= 15

    if len(h2s) == 0:
        issues.append({"severity": "info", "msg": "No H2 tags — consider adding subheadings for structure"})
        score -= 10

    headings = []
    for level in range(1, 7):
        tags = soup.find_all(f"h{level}")
        for tag in tags:
            headings.append({"level": level, "text": tag.get_text(strip=True)[:100]})

    return {"score": max(0, score), "h1_count": len(h1s), "h2_count": len(h2s), "headings": headings[:20], "issues": issues}


def audit_images(soup):
    """Audit image alt text."""
    issues = []
    images = soup.find_all("img")
    total = len(images)
    missing_alt = [img.get("src", "unknown")[:80] for img in images if not img.get("alt")]

    if total == 0:
        return {"score": 100, "total": 0, "missing_alt": 0, "issues": []}

    missing_count = len(missing_alt)
    coverage = ((total - missing_count) / total) * 100

    if missing_count > 0:
        severity = "critical" if coverage < 50 else "warning"
        issues.append({"severity": severity, "msg": f"{missing_count}/{total} images missing alt text"})

    return {
        "score": int(coverage),
        "total": total,
        "missing_alt": missing_count,
        "missing_alt_srcs": missing_alt[:10],
        "issues": issues,
    }


def audit_links(soup, base_url):
    """Audit internal and external links."""
    issues = []
    links = soup.find_all("a", href=True)
    parsed_base = urlparse(base_url)

    internal = []
    external = []
    nofollow = []

    for link in links:
        href = link["href"]
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if parsed.netloc == parsed_base.netloc:
            internal.append(full_url)
        elif parsed.scheme in ("http", "https"):
            external.append(full_url)

        rel = link.get("rel", [])
        if "nofollow" in rel:
            nofollow.append(full_url)

    if len(internal) < 3:
        issues.append({"severity": "warning", "msg": f"Low internal linking ({len(internal)} links)"})

    return {
        "score": 100 if len(internal) >= 3 else 70,
        "internal_count": len(internal),
        "external_count": len(external),
        "nofollow_count": len(nofollow),
        "issues": issues,
    }


def audit_content(soup):
    """Audit content quality signals."""
    issues = []
    score = 100

    # Get main text content
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)
    words = text.split()
    word_count = len(words)

    if word_count < 300:
        issues.append({"severity": "warning", "msg": f"Thin content ({word_count} words, aim for 1000+)"})
        score -= 30
    elif word_count < 1000:
        issues.append({"severity": "info", "msg": f"Content could be deeper ({word_count} words)"})
        score -= 10

    return {"score": max(0, score), "word_count": word_count, "issues": issues}


def audit_schema(soup):
    """Check for structured data / schema markup."""
    issues = []
    score = 0

    # JSON-LD
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    schemas_found = []

    for script in jsonld_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                schemas_found.append(data.get("@type", "Unknown"))
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        schemas_found.append(item.get("@type", "Unknown"))
        except (json.JSONDecodeError, TypeError):
            pass

    # Microdata
    microdata = soup.find_all(attrs={"itemtype": True})
    for item in microdata:
        schemas_found.append(item["itemtype"].split("/")[-1])

    if schemas_found:
        score = min(100, 50 + len(schemas_found) * 15)
    else:
        issues.append({"severity": "warning", "msg": "No structured data found — add JSON-LD schema"})

    return {"score": score, "schemas": schemas_found, "issues": issues}


def audit_og_twitter(soup):
    """Check Open Graph and Twitter Card tags."""
    issues = []
    score = 100

    og_tags = {meta.get("property"): meta.get("content") for meta in soup.find_all("meta", property=re.compile(r"^og:"))}
    twitter_tags = {meta.get("name"): meta.get("content") for meta in soup.find_all("meta", attrs={"name": re.compile(r"^twitter:")})}

    if not og_tags.get("og:title"):
        issues.append({"severity": "warning", "msg": "Missing og:title"})
        score -= 15
    if not og_tags.get("og:description"):
        issues.append({"severity": "warning", "msg": "Missing og:description"})
        score -= 10
    if not og_tags.get("og:image"):
        issues.append({"severity": "info", "msg": "Missing og:image — social shares won't have a preview"})
        score -= 10

    if not twitter_tags.get("twitter:card"):
        issues.append({"severity": "info", "msg": "Missing twitter:card tag"})
        score -= 5

    return {"score": max(0, score), "og": og_tags, "twitter": twitter_tags, "issues": issues}


def audit_technical(resp, soup, load_time):
    """Basic technical checks."""
    issues = []
    score = 100

    # HTTPS
    if not resp.url.startswith("https"):
        issues.append({"severity": "critical", "msg": "Not using HTTPS"})
        score -= 30

    # Load time
    if load_time > 3.0:
        issues.append({"severity": "warning", "msg": f"Slow page load ({load_time:.1f}s)"})
        score -= 15
    elif load_time > 1.5:
        issues.append({"severity": "info", "msg": f"Page load could be faster ({load_time:.1f}s)"})
        score -= 5

    # Viewport
    viewport = soup.find("meta", attrs={"name": "viewport"})
    if not viewport:
        issues.append({"severity": "critical", "msg": "Missing viewport meta tag — not mobile-friendly"})
        score -= 25

    # Canonical
    canonical = soup.find("link", rel="canonical")
    if not canonical:
        issues.append({"severity": "warning", "msg": "Missing canonical URL"})
        score -= 10

    # Language
    html_tag = soup.find("html")
    if html_tag and not html_tag.get("lang"):
        issues.append({"severity": "info", "msg": "Missing lang attribute on <html>"})
        score -= 5

    # Redirect chain
    if len(resp.history) > 1:
        issues.append({"severity": "warning", "msg": f"Redirect chain detected ({len(resp.history)} redirects)"})
        score -= 10

    return {
        "score": max(0, score),
        "https": resp.url.startswith("https"),
        "load_time_s": round(load_time, 2),
        "status_code": resp.status_code,
        "redirects": len(resp.history),
        "has_viewport": viewport is not None,
        "has_canonical": canonical is not None,
        "canonical_url": canonical["href"] if canonical else None,
        "issues": issues,
    }


def audit_geo(soup):
    """GEO (Generative Engine Optimization) readiness audit."""
    issues = []
    score = 50  # Start at 50, add/subtract based on signals

    # Check for FAQ schema
    jsonld_scripts = soup.find_all("script", type="application/ld+json")
    has_faq = False
    has_howto = False
    for script in jsonld_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                t = data.get("@type", "")
                if t == "FAQPage":
                    has_faq = True
                if t == "HowTo":
                    has_howto = True
        except:
            pass

    if has_faq:
        score += 15
    else:
        issues.append({"severity": "info", "msg": "No FAQ schema — AI engines favor Q&A structured content"})

    if has_howto:
        score += 10

    # Check for clear first-paragraph answers
    first_p = soup.find("p")
    if first_p:
        first_text = first_p.get_text(strip=True)
        if len(first_text) > 50:
            score += 10  # Has substantive first paragraph
        else:
            issues.append({"severity": "info", "msg": "First paragraph is thin — lead with a direct answer"})

    # Check for author/date signals (E-E-A-T)
    has_author = bool(soup.find(attrs={"rel": "author"}) or soup.find("meta", attrs={"name": "author"}))
    has_date = bool(soup.find("time") or soup.find("meta", attrs={"property": "article:published_time"}))

    if has_author:
        score += 5
    else:
        issues.append({"severity": "info", "msg": "No author attribution found — reduces E-E-A-T signals"})

    if has_date:
        score += 5
    else:
        issues.append({"severity": "info", "msg": "No publish date found — freshness signals missing"})

    # Check robots.txt mentions for AI crawlers
    issues.append({"severity": "info", "msg": "Check robots.txt for GPTBot/PerplexityBot access (manual check needed)"})

    return {"score": min(100, max(0, score)), "has_faq_schema": has_faq, "has_howto_schema": has_howto, "has_author": has_author, "has_date": has_date, "issues": issues}


def calculate_overall_score(results):
    """Calculate weighted overall score."""
    weights = {"on_page": 0.30, "technical": 0.25, "content": 0.20, "geo": 0.15, "schema": 0.10}

    # On-page is average of title, meta, headings, images, links, og
    on_page_scores = [results["title"]["score"], results["meta_description"]["score"],
                      results["headings"]["score"], results["images"]["score"],
                      results["links"]["score"], results["og_twitter"]["score"]]
    on_page = sum(on_page_scores) / len(on_page_scores)

    category_scores = {
        "on_page": on_page,
        "technical": results["technical"]["score"],
        "content": results["content"]["score"],
        "geo": results["geo"]["score"],
        "schema": results["schema"]["score"],
    }

    overall = sum(category_scores[k] * weights[k] for k in weights)

    return {"overall": round(overall), "categories": {k: round(v) for k, v in category_scores.items()}}


def run_audit(url, output_dir=None):
    """Run a full audit on a URL."""
    print(f"🔍 Auditing: {url}")
    print()

    resp, load_time = fetch_page(url)
    soup = BeautifulSoup(resp.text, "lxml")
    # Keep a copy for content audit (which decomposes tags)
    soup_content = BeautifulSoup(resp.text, "lxml")

    results = {
        "url": url,
        "final_url": resp.url,
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "title": audit_title(soup),
        "meta_description": audit_meta_description(soup),
        "headings": audit_headings(soup),
        "images": audit_images(soup),
        "links": audit_links(soup, resp.url),
        "og_twitter": audit_og_twitter(soup),
        "schema": audit_schema(soup),
        "technical": audit_technical(resp, soup, load_time),
        "content": audit_content(soup_content),
        "geo": audit_geo(soup),
    }

    results["scores"] = calculate_overall_score(results)

    # Collect all issues
    all_issues = []
    for key, val in results.items():
        if isinstance(val, dict) and "issues" in val:
            for issue in val["issues"]:
                issue["category"] = key
                all_issues.append(issue)

    results["all_issues"] = sorted(all_issues, key=lambda x: {"critical": 0, "warning": 1, "info": 2}.get(x["severity"], 3))

    # Print summary
    scores = results["scores"]
    grade = "🟢" if scores["overall"] >= 80 else "🟡" if scores["overall"] >= 60 else "🔴"
    print(f"{grade} Overall Score: {scores['overall']}/100")
    print()
    for cat, sc in scores["categories"].items():
        indicator = "🟢" if sc >= 80 else "🟡" if sc >= 60 else "🔴"
        print(f"  {indicator} {cat.replace('_', ' ').title()}: {sc}/100")

    print()
    critical = [i for i in all_issues if i["severity"] == "critical"]
    warnings = [i for i in all_issues if i["severity"] == "warning"]
    info = [i for i in all_issues if i["severity"] == "info"]

    if critical:
        print(f"🔴 {len(critical)} Critical Issues:")
        for i in critical:
            print(f"   • {i['msg']}")
    if warnings:
        print(f"🟡 {len(warnings)} Warnings:")
        for i in warnings:
            print(f"   • {i['msg']}")
    if info:
        print(f"ℹ️  {len(info)} Info:")
        for i in info:
            print(f"   • {i['msg']}")

    # Save results
    if output_dir:
        domain = urlparse(url).netloc.replace(".", "_")
        domain_dir = os.path.join(output_dir, domain)
        os.makedirs(domain_dir, exist_ok=True)
        out_file = os.path.join(domain_dir, f"{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json")
        with open(out_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\n📄 Full results saved: {out_file}")

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SEO Page Auditor")
    parser.add_argument("--url", required=True, help="URL to audit")
    parser.add_argument("--output-dir", help="Directory to save results")
    args = parser.parse_args()

    run_audit(args.url, args.output_dir)
