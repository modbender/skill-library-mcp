#!/usr/bin/env python3
"""
Lead Scorer — Analyze a domain and return a 0-100 score with detailed breakdown.
Scoring is customizable via JSON profiles that define which signals matter.

Dependencies: pip3 install dnspython
"""

import argparse
import csv
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from html.parser import HTMLParser
from xml.etree import ElementTree

# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

class SimpleHTMLParser(HTMLParser):
    """Extract text, links, meta tags, scripts from HTML."""

    def __init__(self):
        super().__init__()
        self.text = []
        self.links = []
        self.meta = {}
        self.scripts = []
        self.h1 = []
        self.h2 = []
        self._tag_stack = []
        self._capture = False

    def handle_starttag(self, tag, attrs):
        attrs_d = dict(attrs)
        self._tag_stack.append(tag)
        if tag == "a" and "href" in attrs_d:
            self.links.append(attrs_d["href"])
        if tag == "meta":
            name = attrs_d.get("name", attrs_d.get("property", "")).lower()
            content = attrs_d.get("content", "")
            if name and content:
                self.meta[name] = content
        if tag == "script":
            src = attrs_d.get("src", "")
            if src:
                self.scripts.append(src)
        if tag in ("h1", "h2"):
            self._capture = True
            self._capture_tag = tag
            self._capture_buf = []

    def handle_endtag(self, tag):
        if self._tag_stack:
            self._tag_stack.pop()
        if self._capture and tag == getattr(self, "_capture_tag", None):
            text = "".join(self._capture_buf).strip()
            if text:
                if tag == "h1":
                    self.h1.append(text)
                else:
                    self.h2.append(text)
            self._capture = False

    def handle_data(self, data):
        self.text.append(data)
        if self._capture:
            self._capture_buf.append(data)


def fetch_url(url, timeout=10):
    """Fetch a URL, return (status, body_text, headers) or None on error."""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (compatible; LeadScorer/1.0)"
        })
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        body = resp.read(512_000)  # 512KB max
        encoding = resp.headers.get_content_charset() or "utf-8"
        try:
            text = body.decode(encoding, errors="replace")
        except Exception:
            text = body.decode("utf-8", errors="replace")
        return resp.status, text, resp.headers
    except Exception:
        return None


def parse_html(html_text):
    """Parse HTML and return a SimpleHTMLParser with extracted data."""
    parser = SimpleHTMLParser()
    try:
        parser.feed(html_text)
    except Exception:
        pass
    return parser


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------

def gather_dns(domain):
    """Gather MX, SPF, DMARC records."""
    import dns.resolver
    data = {"mx_records": [], "mx_provider": None, "has_spf": False, "has_dmarc": False}
    try:
        answers = dns.resolver.resolve(domain, "MX")
        for r in answers:
            mx = str(r.exchange).lower().rstrip(".")
            data["mx_records"].append(mx)
        # Identify provider
        mx_str = " ".join(data["mx_records"])
        if "google" in mx_str or "gmail" in mx_str:
            data["mx_provider"] = "Google Workspace"
        elif "outlook" in mx_str or "microsoft" in mx_str:
            data["mx_provider"] = "Microsoft 365"
        elif "zoho" in mx_str:
            data["mx_provider"] = "Zoho Mail"
        elif "protonmail" in mx_str:
            data["mx_provider"] = "ProtonMail"
        elif data["mx_records"]:
            data["mx_provider"] = "Other"
    except Exception:
        pass
    # SPF
    try:
        answers = dns.resolver.resolve(domain, "TXT")
        for r in answers:
            txt = str(r).lower()
            if "v=spf1" in txt:
                data["has_spf"] = True
    except Exception:
        pass
    # DMARC
    try:
        answers = dns.resolver.resolve(f"_dmarc.{domain}", "TXT")
        for r in answers:
            if "v=dmarc1" in str(r).lower():
                data["has_dmarc"] = True
    except Exception:
        pass
    return data


def _find_elements(root, local_name):
    """Find elements by local name regardless of namespace."""
    # Try common namespace first
    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    found = root.findall(f".//{{{ns}}}{local_name}")
    if found:
        return found
    # Try no namespace
    found = root.findall(f".//{local_name}")
    if found:
        return found
    # Brute force: iterate all elements and match local name
    return [el for el in root.iter() if el.tag.split('}')[-1] == local_name]


def _parse_sitemap_xml(xml_text, delay=0.5, follow_index=True):
    """Parse a sitemap XML string, handling namespaced and non-namespaced variants."""
    urls = 0
    dates = []
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError:
        # Fall back to regex
        locs = re.findall(r"<loc[^>]*>(.+?)</loc>", xml_text, re.IGNORECASE)
        return len(locs), []

    # Check if it's a sitemap index (has <sitemap><loc> entries)
    index_locs = _find_elements(root, "sitemap")
    if index_locs and follow_index:
        child_locs = []
        for sitemap_el in index_locs:
            loc_el = sitemap_el.find(f"{{{sitemap_el.tag.split('}')[0][1:]}}}loc") if '}' in sitemap_el.tag else sitemap_el.find("loc")
            if loc_el is None:
                # Try any child named loc
                for child in sitemap_el:
                    if child.tag.split('}')[-1] == 'loc' and child.text:
                        child_locs.append(child.text.strip())
                        break
            elif loc_el is not None and loc_el.text:
                child_locs.append(loc_el.text.strip())

        if child_locs:
            # Fetch first child sitemap to count, estimate total
            time.sleep(delay)
            child_result = fetch_url(child_locs[0])
            if child_result and child_result[0] == 200:
                child_urls, child_dates = _parse_sitemap_xml(child_result[1], delay, follow_index=False)
                urls = child_urls * len(child_locs)  # estimate total
                dates = child_dates
            return urls, dates

    # Regular sitemap — count <url> elements
    url_elements = _find_elements(root, "url")
    urls = len(url_elements)

    # Also try <loc> directly if no <url> wrappers found
    if urls == 0:
        loc_elements = _find_elements(root, "loc")
        urls = len(loc_elements)

    # Gather lastmod dates
    lastmod_elements = _find_elements(root, "lastmod")
    for el in lastmod_elements:
        if el.text:
            dates.append(el.text.strip()[:10])

    return urls, dates


def gather_sitemap(domain, delay=0.5):
    """Parse sitemap.xml for URL count and dates."""
    data = {"sitemap_urls": 0, "sitemap_dates": [], "sitemap_found": False}
    urls_to_try = [
        f"https://{domain}/sitemap.xml",
        f"https://{domain}/sitemap_index.xml",
        f"https://www.{domain}/sitemap.xml",
        f"https://{domain}/sitemap.xml.gz",
    ]

    # Also check robots.txt for sitemap location
    robots_result = fetch_url(f"https://{domain}/robots.txt")
    if robots_result and robots_result[0] == 200:
        for line in robots_result[1].splitlines():
            if line.lower().startswith("sitemap:"):
                sitemap_url = line.split(":", 1)[1].strip()
                if sitemap_url and sitemap_url not in urls_to_try:
                    urls_to_try.insert(0, sitemap_url)

    for url in urls_to_try:
        result = fetch_url(url)
        if result and result[0] == 200 and result[1].strip():
            data["sitemap_found"] = True
            content = result[1]

            # Handle HTML pages returned for sitemap URLs (some servers redirect)
            if content.strip().lower().startswith("<!doctype") or "<html" in content[:200].lower():
                # Not a sitemap, skip
                time.sleep(delay)
                continue

            urls_count, dates = _parse_sitemap_xml(content, delay)

            # If XML parsing found nothing, fall back to regex
            if urls_count == 0:
                locs = re.findall(r"<loc[^>]*>(.+?)</loc>", content, re.IGNORECASE)
                urls_count = len(locs)

            data["sitemap_urls"] = urls_count
            data["sitemap_dates"] = dates
            break
        time.sleep(delay)
    return data


def gather_website(domain, delay=0.5):
    """Scrape homepage, /blog, /about for signals."""
    data = {
        "homepage_ok": False,
        "has_blog": False,
        "blog_path": None,
        "has_about": False,
        "tech_stack": [],
        "social_links": {"twitter": None, "linkedin": None, "youtube": None, "facebook": None},
        "has_meta_description": False,
        "has_contact_page": False,
        "emails_found": [],
        "homepage_text": "",
        "h1_tags": [],
        "h2_tags": [],
        "all_links": [],
    }

    # Homepage
    base = f"https://{domain}"
    result = fetch_url(base)
    if not result:
        result = fetch_url(f"https://www.{domain}")
        if result:
            base = f"https://www.{domain}"
    if not result:
        result = fetch_url(f"http://{domain}")
        if result:
            base = f"http://{domain}"

    if result and result[0] == 200:
        data["homepage_ok"] = True
        parsed = parse_html(result[1])
        full_text = " ".join(parsed.text).lower()
        data["homepage_text"] = full_text[:10000]
        data["h1_tags"] = parsed.h1[:5]
        data["h2_tags"] = parsed.h2[:10]
        data["has_meta_description"] = bool(parsed.meta.get("description"))
        data["all_links"] = parsed.links

        # Detect tech stack from scripts and meta
        page_lower = result[1].lower()
        if "wp-content" in page_lower or "wordpress" in page_lower:
            data["tech_stack"].append("WordPress")
        if "shopify" in page_lower:
            data["tech_stack"].append("Shopify")
        if "squarespace" in page_lower:
            data["tech_stack"].append("Squarespace")
        if "wix" in page_lower:
            data["tech_stack"].append("Wix")
        if "webflow" in page_lower:
            data["tech_stack"].append("Webflow")
        if "cloudflare" in page_lower:
            data["tech_stack"].append("Cloudflare")
        if "google-analytics" in page_lower or "gtag" in page_lower or "ga4" in page_lower:
            data["tech_stack"].append("Google Analytics")
        if "hubspot" in page_lower:
            data["tech_stack"].append("HubSpot")
        if "intercom" in page_lower:
            data["tech_stack"].append("Intercom")
        if "drift" in page_lower:
            data["tech_stack"].append("Drift")

        # Social links
        for href in parsed.links:
            href_lower = (href or "").lower()
            if "twitter.com/" in href_lower or "x.com/" in href_lower:
                data["social_links"]["twitter"] = href
            elif "linkedin.com/" in href_lower:
                data["social_links"]["linkedin"] = href
            elif "youtube.com/" in href_lower:
                data["social_links"]["youtube"] = href
            elif "facebook.com/" in href_lower:
                data["social_links"]["facebook"] = href

        # Check for blog/contact links
        for href in parsed.links:
            href_lower = (href or "").lower()
            if "/blog" in href_lower:
                data["has_blog"] = True
                data["blog_path"] = href
            if "/contact" in href_lower:
                data["has_contact_page"] = True

        # Extract emails
        emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", result[1]))
        # Filter out common false positives
        data["emails_found"] = [e for e in emails if not e.endswith((".png", ".jpg", ".js", ".css"))]

    # Check /blog if not found in links
    if not data["has_blog"]:
        time.sleep(delay)
        for path in ["/blog", "/blog/", "/articles", "/posts", "/news"]:
            blog_result = fetch_url(base + path)
            if blog_result and blog_result[0] == 200 and len(blog_result[1]) > 500:
                data["has_blog"] = True
                data["blog_path"] = path
                break

    # Check /about
    time.sleep(delay)
    about_result = fetch_url(base + "/about")
    if not about_result or about_result[0] != 200:
        about_result = fetch_url(base + "/about-us")
    if about_result and about_result[0] == 200:
        data["has_about"] = True
        about_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", about_result[1]))
        data["emails_found"].extend([e for e in about_emails if e not in data["emails_found"]])

    # Check /contact
    if not data["has_contact_page"]:
        time.sleep(delay)
        contact_result = fetch_url(base + "/contact")
        if not contact_result or contact_result[0] != 200:
            contact_result = fetch_url(base + "/contact-us")
        if contact_result and contact_result[0] == 200:
            data["has_contact_page"] = True
            contact_emails = set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", contact_result[1]))
            data["emails_found"].extend([e for e in contact_emails if e not in data["emails_found"]])

    return data


# ---------------------------------------------------------------------------
# Signal scoring
# ---------------------------------------------------------------------------

def score_has_blog(profile_signal, web_data, sitemap_data, dns_data):
    """Score blog existence and quality."""
    max_score = profile_signal["weight"]
    if not web_data.get("has_blog") and sitemap_data.get("sitemap_urls", 0) < 10:
        return 0, "No blog or content section found"

    score = max_score * 0.5  # Base for having a blog
    evidence_parts = []

    if web_data.get("has_blog"):
        evidence_parts.append(f"Blog found at {web_data.get('blog_path', '/blog')}")

    urls = sitemap_data.get("sitemap_urls", 0)
    if urls > 100:
        score = max_score
        evidence_parts.append(f"{urls} URLs in sitemap")
    elif urls > 50:
        score = max_score * 0.85
        evidence_parts.append(f"{urls} URLs in sitemap")
    elif urls > 20:
        score = max_score * 0.7
        evidence_parts.append(f"{urls} URLs in sitemap")
    elif urls > 0:
        evidence_parts.append(f"{urls} URLs in sitemap")

    return min(round(score), max_score), "; ".join(evidence_parts) or "Blog detected"


def score_business_legitimacy(profile_signal, web_data, sitemap_data, dns_data):
    """Score business legitimacy via DNS and website quality."""
    max_score = profile_signal["weight"]
    score = 0
    evidence = []

    provider = dns_data.get("mx_provider")
    if provider in ("Google Workspace", "Microsoft 365"):
        score += max_score * 0.4
        evidence.append(f"MX: {provider}")
    elif provider:
        score += max_score * 0.2
        evidence.append(f"MX: {provider}")

    if dns_data.get("has_spf"):
        score += max_score * 0.15
        evidence.append("SPF configured")
    if dns_data.get("has_dmarc"):
        score += max_score * 0.15
        evidence.append("DMARC configured")
    if web_data.get("has_about"):
        score += max_score * 0.15
        evidence.append("About page found")
    if web_data.get("has_meta_description"):
        score += max_score * 0.15
        evidence.append("Meta description present")

    return min(round(score), max_score), "; ".join(evidence) or "Limited business signals"


def score_content_velocity(profile_signal, web_data, sitemap_data, dns_data):
    """Score content publishing frequency and recency."""
    max_score = profile_signal["weight"]
    dates = sitemap_data.get("sitemap_dates", [])
    if not dates:
        urls = sitemap_data.get("sitemap_urls", 0)
        if urls > 50:
            return round(max_score * 0.4), f"Sitemap has {urls} URLs but no dates"
        return 0, "No content dates available"

    score = 0
    evidence = []
    now = datetime.now(timezone.utc)

    # Check recency
    try:
        sorted_dates = sorted(dates, reverse=True)
        latest = sorted_dates[0]
        latest_dt = datetime.fromisoformat(latest.replace("Z", "+00:00")) if "T" in latest else datetime.strptime(latest, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        days_ago = (now - latest_dt).days
        if days_ago < 30:
            score += max_score * 0.5
            evidence.append(f"Last updated {days_ago}d ago")
        elif days_ago < 90:
            score += max_score * 0.3
            evidence.append(f"Last updated {days_ago}d ago")
        elif days_ago < 365:
            score += max_score * 0.15
            evidence.append(f"Last updated {days_ago}d ago")
        else:
            evidence.append(f"Last updated {days_ago}d ago (stale)")
    except Exception:
        pass

    # Check volume of recent content
    recent = [d for d in dates if d >= (now.strftime("%Y") + "-01")]
    if len(recent) > 20:
        score += max_score * 0.5
        evidence.append(f"{len(recent)} pages updated this year")
    elif len(recent) > 5:
        score += max_score * 0.3
        evidence.append(f"{len(recent)} pages updated this year")
    elif len(recent) > 0:
        score += max_score * 0.15
        evidence.append(f"{len(recent)} pages updated this year")

    return min(round(score), max_score), "; ".join(evidence) or "Limited content activity"


def score_tech_stack(profile_signal, web_data, sitemap_data, dns_data):
    """Score tech stack sophistication."""
    max_score = profile_signal["weight"]
    stack = web_data.get("tech_stack", [])
    if not stack:
        return 0, "No tech stack detected"

    score = min(len(stack) * (max_score / 4), max_score)
    return min(round(score), max_score), f"Detected: {', '.join(stack)}"


def score_audience_size(profile_signal, web_data, sitemap_data, dns_data):
    """Score social media presence."""
    max_score = profile_signal["weight"]
    social = web_data.get("social_links", {})
    present = [k for k, v in social.items() if v]

    if not present:
        return 0, "No social media links found"

    score = min(len(present) * (max_score / 4), max_score * 0.8)
    # Bonus for having multiple platforms
    if len(present) >= 3:
        score = max_score
    evidence = f"Social presence: {', '.join(present)}"
    return min(round(score), max_score), evidence


def score_contact_findability(profile_signal, web_data, sitemap_data, dns_data):
    """Score how easy it is to find contact info."""
    max_score = profile_signal["weight"]
    score = 0
    evidence = []

    if web_data.get("has_contact_page"):
        score += max_score * 0.4
        evidence.append("Contact page found")
    if web_data.get("emails_found"):
        score += max_score * 0.4
        evidence.append(f"{len(web_data['emails_found'])} email(s) found")
    social = web_data.get("social_links", {})
    if social.get("linkedin"):
        score += max_score * 0.2
        evidence.append("LinkedIn link found")

    return min(round(score), max_score), "; ".join(evidence) or "No contact info found"


def score_seo_tools(profile_signal, web_data, sitemap_data, dns_data):
    """Score keyword presence (e.g., SEO tool mentions)."""
    max_score = profile_signal["weight"]
    keywords = profile_signal.get("keywords", [])
    if not keywords:
        return 0, "No keywords configured for this signal"

    text = web_data.get("homepage_text", "").lower()
    found = [kw for kw in keywords if kw.lower() in text]

    if not found:
        return 0, "No keyword matches found"

    ratio = len(found) / len(keywords)
    score = round(max_score * min(ratio * 2, 1.0))  # Finding half the keywords = full score
    return min(score, max_score), f"Keywords found: {', '.join(found)}"


# Signal name → scorer function mapping
SIGNAL_SCORERS = {
    "has_blog": score_has_blog,
    "business_legitimacy": score_business_legitimacy,
    "content_velocity": score_content_velocity,
    "tech_stack": score_tech_stack,
    "audience_size": score_audience_size,
    "contact_findability": score_contact_findability,
    "seo_tools": score_seo_tools,
}


def score_generic(profile_signal, web_data, sitemap_data, dns_data):
    """Fallback scorer for unknown signals — uses keywords if available."""
    keywords = profile_signal.get("keywords", [])
    if keywords:
        return score_seo_tools(profile_signal, web_data, sitemap_data, dns_data)
    return 0, "No scorer available for this signal"


# ---------------------------------------------------------------------------
# Main scoring
# ---------------------------------------------------------------------------

def get_grade(score):
    if score >= 80:
        return "A"
    elif score >= 60:
        return "B"
    elif score >= 40:
        return "C"
    elif score >= 20:
        return "D"
    return "F"


def generate_summary(signals_result, grade):
    """Generate a human-readable summary."""
    parts = []
    strong = [k for k, v in signals_result.items() if v["score"] >= v["max"] * 0.7]
    weak = [k for k, v in signals_result.items() if v["score"] < v["max"] * 0.3]

    if strong:
        parts.append(f"Strong in: {', '.join(s.replace('_', ' ') for s in strong)}.")
    if weak:
        parts.append(f"Weak in: {', '.join(s.replace('_', ' ') for s in weak)}.")

    priority_map = {"A": "High-priority lead.", "B": "Good lead, worth pursuing.", "C": "Moderate lead.", "D": "Low-priority lead.", "F": "Unlikely fit."}
    parts.append(priority_map.get(grade, ""))
    return " ".join(parts)


def score_domain(domain, profile, delay=0.5):
    """Score a single domain against a profile."""
    domain = domain.strip().lower()
    domain = re.sub(r"^https?://", "", domain)
    domain = domain.split("/")[0]

    sys.stderr.write(f"Scoring {domain}...\n")

    # Gather data
    sys.stderr.write("  Gathering DNS records...\n")
    dns_data = gather_dns(domain)
    time.sleep(delay)

    sys.stderr.write("  Fetching sitemap...\n")
    sitemap_data = gather_sitemap(domain, delay)
    time.sleep(delay)

    sys.stderr.write("  Scraping website...\n")
    web_data = gather_website(domain, delay)

    # Score each signal
    signals = profile.get("signals", {})
    total_weight = sum(s.get("weight", 0) for s in signals.values())
    signals_result = {}
    total_score = 0

    for signal_name, signal_config in signals.items():
        scorer = SIGNAL_SCORERS.get(signal_name, score_generic)
        score, evidence = scorer(signal_config, web_data, sitemap_data, dns_data)
        signals_result[signal_name] = {
            "score": score,
            "max": signal_config["weight"],
            "evidence": evidence,
        }
        total_score += score

    # Normalize to 0-100 if weights don't sum to 100
    if total_weight > 0 and total_weight != 100:
        normalized = round((total_score / total_weight) * 100)
    else:
        normalized = total_score

    grade = get_grade(normalized)

    raw_data = {
        "sitemap_urls": sitemap_data.get("sitemap_urls", 0),
        "sitemap_found": sitemap_data.get("sitemap_found", False),
        "mx_provider": dns_data.get("mx_provider"),
        "has_spf": dns_data.get("has_spf", False),
        "has_dmarc": dns_data.get("has_dmarc", False),
        "tech_stack": web_data.get("tech_stack", []),
        "social_links": {k: v for k, v in web_data.get("social_links", {}).items() if v},
        "emails_found": web_data.get("emails_found", []),
        "has_contact_page": web_data.get("has_contact_page", False),
        "homepage_ok": web_data.get("homepage_ok", False),
    }

    return {
        "domain": domain,
        "score": normalized,
        "grade": grade,
        "profile": profile.get("name", "unknown"),
        "signals": signals_result,
        "raw_data": raw_data,
        "summary": generate_summary(signals_result, grade),
    }


def load_profile(profile_path):
    """Load a scoring profile from JSON file."""
    if not os.path.isabs(profile_path):
        # Check relative to script's profiles dir
        script_dir = os.path.dirname(os.path.abspath(__file__))
        profiles_dir = os.path.join(script_dir, "profiles")
        candidate = os.path.join(profiles_dir, profile_path)
        if os.path.exists(candidate):
            profile_path = candidate
    with open(profile_path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Score leads by domain analysis")
    parser.add_argument("domains", nargs="*", help="Domain(s) to score")
    parser.add_argument("--profile", default="default.json", help="Scoring profile JSON file (default: default.json)")
    parser.add_argument("--csv", dest="csv_file", help="CSV file with domains to score")
    parser.add_argument("--domain-column", default="domain", help="Column name for domains in CSV (default: domain)")
    parser.add_argument("--scrape-delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    profile = load_profile(args.profile)

    domains = list(args.domains)
    if args.csv_file:
        with open(args.csv_file) as f:
            reader = csv.DictReader(f)
            col = args.domain_column
            for row in reader:
                if col in row and row[col].strip():
                    domains.append(row[col].strip())

    if not domains:
        parser.error("Provide at least one domain or --csv file")

    results = []
    for i, domain in enumerate(domains):
        if i > 0:
            time.sleep(args.scrape_delay)
        result = score_domain(domain, profile, args.scrape_delay)
        results.append(result)

    output = results if len(results) > 1 else results[0]
    json_out = json.dumps(output, indent=2, default=str)

    if args.output:
        with open(args.output, "w") as f:
            f.write(json_out + "\n")
        sys.stderr.write(f"Results written to {args.output}\n")
    else:
        print(json_out)


if __name__ == "__main__":
    main()
