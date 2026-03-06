#!/usr/bin/env python3
"""
crawl.py — Crawl a business website and extract structured BusinessInfo JSON.

Usage:
    python3 crawl.py <url> [extra_url1 extra_url2 ...]

Output:
    JSON to stdout

2-level crawl only:
  Level 1: homepage + any user-provided extra URLs
  Level 2: up to 4 links discovered from Level 1, filtered by keyword relevance
  Never guesses paths. Never goes deeper than Level 2.
"""

import sys
import json
import re
import time
from urllib.parse import urljoin, urlparse

try:
    import httpx
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependencies. Run: pip install httpx beautifulsoup4 lxml", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; llms-txt-generator/1.0; +https://github.com/ngm9/llms-txt-generator)"
}
TIMEOUT = 15
MAX_TEXT_LENGTH = 3000        # Pass 1 default
MAX_TEXT_LENGTH_DEEP = 8000   # Pass 2 — more raw text for LLM extraction

# ── Link keyword filters ──────────────────────────────────────────────────────

TEAM_KEYWORDS     = ["about", "team", "founder", "founders", "people", "who-we-are", "leadership"]
CLIENT_KEYWORDS   = ["customer", "customers", "client", "clients", "testimonial", "testimonials",
                     "case-study", "case-studies", "review", "reviews", "story", "stories", "wall-of-love"]
PRICING_KEYWORDS  = ["pricing", "plans", "price"]
API_KEYWORDS      = ["api", "docs", "developer", "developers", "integration", "integrations", "openapi", "swagger"]


def keyword_match(text: str, keywords: list) -> bool:
    text = text.lower()
    return any(kw in text for kw in keywords)


# ── Fetching ──────────────────────────────────────────────────────────────────

def fetch(url: str):
    """Fetch URL, return (html_text, final_url) or (None, None) on failure."""
    try:
        r = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        if r.status_code == 200 and "text/html" in r.headers.get("content-type", ""):
            return r.text, str(r.url)
        else:
            print(f"  [skip] {url} → HTTP {r.status_code}", file=sys.stderr)
            return None, None
    except Exception as e:
        print(f"  [error] {url} → {e}", file=sys.stderr)
        return None, None


def fetch_text_file(url: str):
    """Fetch a plain text file (e.g. existing llms.txt)."""
    try:
        r = httpx.get(url, headers=HEADERS, timeout=TIMEOUT, follow_redirects=True)
        if r.status_code == 200:
            return r.text
        return None
    except Exception:
        return None


# ── Parsing ───────────────────────────────────────────────────────────────────

def extract_page(html: str, base_url: str) -> dict:
    """Extract structured info from a single HTML page."""
    soup = BeautifulSoup(html, "lxml")
    base_domain = ".".join(urlparse(base_url).netloc.split(".")[-2:])

    # ── Links: extract BEFORE stripping nav/footer ──
    # Nav and footer often contain the best discovery links (Team, Pricing, Case Studies, etc.)
    links = []
    seen_link_urls = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        text = a.get_text(strip=True)
        if not href or href.startswith(("javascript:", "tel:", "mailto:")):
            continue
        abs_url = urljoin(base_url, href)
        parsed = urlparse(abs_url)
        link_domain = ".".join(parsed.netloc.split(".")[-2:])
        # Accept same domain or subdomain; must have a real path
        if link_domain == base_domain and parsed.path and abs_url not in seen_link_urls:
            links.append({"text": text, "url": abs_url})
            seen_link_urls.add(abs_url)

    # ── Emails ──
    emails = list(set(re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", html)))
    emails = [e for e in emails if not any(x in e.lower() for x in ["example", "test@", "@sentry", "@email"])]

    # ── Strip script/style noise for text extraction ──
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    # ── Title ──
    title = ""
    if soup.title:
        title = soup.title.string or ""
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)

    # ── Meta description ──
    meta_desc = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta_desc = meta.get("content", "")

    # ── Headings (skip nav/footer/header elements) ──
    headings = []
    for tag in soup.find_all(["h1", "h2", "h3"]):
        if tag.find_parent(["nav", "footer", "header"]):
            continue
        t = tag.get_text(strip=True)
        if t:
            headings.append(t)

    # ── Body text (skip nav/footer/header) ──
    paragraphs = []
    for tag in soup.find_all(["p", "li", "blockquote"]):
        if tag.find_parent(["nav", "footer", "header"]):
            continue
        t = tag.get_text(strip=True)
        if len(t) > 30:
            paragraphs.append(t)

    raw_text = " ".join(paragraphs)

    return {
        "title": title,
        "meta_desc": meta_desc,
        "headings": headings,
        "raw_text": raw_text,  # caller truncates based on mode
        "links": links,
        "emails": emails,
    }


# ── Heuristics ────────────────────────────────────────────────────────────────

def detect_pricing(text: str) -> bool:
    patterns = [r'\$\d', r'₹\d', r'/month', r'/mo\b', r'/user', r'/seat',
                r'per candidate', r'per assessment', r'per seat', r'starting at']
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def extract_team_snippets(text: str) -> list:
    snippets = []
    patterns = [
        r'([A-Z][a-z]+ [A-Z][a-z]+),\s*(CEO|CTO|COO|CPO|Founder|Co-founder|Head of|VP|Director)',
        r'([A-Z][a-z]+ [A-Z][a-z]+) is (the |our )?(founder|co-founder|CEO|CTO)',
    ]
    for p in patterns:
        for m in re.finditer(p, text):
            snippets.append(m.group(0))
    return snippets[:5]


def extract_testimonial_snippets(text: str) -> list:
    quotes = re.findall(r'["\u201c\u201d]([^"\u201c\u201d]{30,200})["\u201c\u201d]', text)
    return quotes[:3]


# ── Level 2 link selection ────────────────────────────────────────────────────

def score_link(link: dict, keywords: list) -> int:
    """Score a link's relevance: URL path match scores higher than text match."""
    score = 0
    path = urlparse(link["url"]).path.lower()
    text = link["text"].lower()
    for kw in keywords:
        if kw in path:
            score += 2  # URL path match = strong signal
        elif kw in text:
            score += 1  # Text match = weaker signal
    return score


def select_level2_links(links: list) -> list:
    """
    Select up to 4 links to crawl at Level 2.
    Priority order: team > clients/testimonials > pricing > api/docs
    Scores links by relevance — URL path matches rank higher than text matches.
    Only follows links actually found on the page — never guesses paths.
    """
    selected = []
    seen_urls = set()

    def add(link):
        url = link["url"]
        parsed = urlparse(url)
        # Skip pure anchor-only links (e.g. /#section)
        if parsed.fragment and parsed.path in ("/", ""):
            return
        if url not in seen_urls and len(selected) < 4:
            selected.append(link)
            seen_urls.add(url)

    for category_keywords in [TEAM_KEYWORDS, CLIENT_KEYWORDS, PRICING_KEYWORDS, API_KEYWORDS]:
        # Score all links for this category, pick the best
        scored = [(score_link(l, category_keywords), l) for l in links]
        scored = [(s, l) for s, l in scored if s > 0]
        scored.sort(key=lambda x: -x[0])
        if scored:
            add(scored[0][1])

    return selected


# ── Main ──────────────────────────────────────────────────────────────────────

def crawl(root_url: str, extra_urls: list = [], deep: bool = False) -> dict:
    domain = urlparse(root_url).netloc
    text_limit = MAX_TEXT_LENGTH_DEEP if deep else MAX_TEXT_LENGTH
    print(f"🔍 Crawling {root_url} (mode={'deep' if deep else 'fast'})", file=sys.stderr)

    # ── Level 1 ──────────────────────────────────────────────────────────────
    level1_urls = [root_url] + extra_urls
    level1_pages = {}

    for url in level1_urls:
        html, final_url = fetch(url)
        if html:
            level1_pages[final_url or url] = extract_page(html, final_url or url)
            print(f"  ✓ {url}", file=sys.stderr)
        time.sleep(0.5)

    if not level1_pages:
        print("ERROR: Could not fetch any pages.", file=sys.stderr)
        sys.exit(1)

    # Merge Level 1 data
    all_links = []
    all_emails = []
    all_headings = []
    all_text = ""
    title = ""
    meta_desc = ""
    pages_crawled = []

    pages_raw = {}  # deep mode: full text per page keyed by url

    for url, page in level1_pages.items():
        pages_crawled.append(url)
        all_links.extend(page["links"])
        all_emails.extend(page["emails"])
        all_headings.extend(page["headings"])
        all_text += " " + page["raw_text"]
        if not title:
            title = page["title"]
        if not meta_desc:
            meta_desc = page["meta_desc"]
        if deep:
            pages_raw[url] = page["raw_text"][:text_limit]

    # Deduplicate links
    seen = set()
    unique_links = []
    for l in all_links:
        key = l["url"].rstrip("/")
        if key not in seen and l["text"]:
            unique_links.append(l)
            seen.add(key)

    print(f"  Found {len(unique_links)} unique links", file=sys.stderr)

    # ── Level 2 ──────────────────────────────────────────────────────────────
    level2_targets = select_level2_links(unique_links)
    print(f"  Level 2 targets: {[l['text'] for l in level2_targets]}", file=sys.stderr)

    level2_data = {"team": {}, "clients": {}, "pricing": {}, "api": {}}

    for link in level2_targets:
        print(f"  → Crawling: {link['text']} ({link['url']})", file=sys.stderr)
        html, final_url = fetch(link["url"])
        if html:
            page = extract_page(html, final_url or link["url"])
            page_url = final_url or link["url"]
            pages_crawled.append(page_url)
            all_emails.extend(page["emails"])
            all_text += " " + page["raw_text"]
            all_headings.extend(page["headings"])
            if deep:
                pages_raw[page_url] = page["raw_text"][:text_limit]

            combined = (link["text"] + " " + link["url"]).lower()
            # Always try to extract testimonials from any Level 2 page
            testimonials = extract_testimonial_snippets(page["raw_text"])

            if keyword_match(combined, TEAM_KEYWORDS):
                level2_data["team"] = {
                    "url": link["url"],
                    "snippets": extract_team_snippets(page["raw_text"]),
                    "raw": page["raw_text"][:1000],
                }
                # Team pages sometimes have testimonials too
                if testimonials and not level2_data["clients"]:
                    level2_data["clients"] = {"url": link["url"], "testimonials": testimonials, "raw": page["raw_text"][:500]}
            elif keyword_match(combined, CLIENT_KEYWORDS):
                level2_data["clients"] = {
                    "url": link["url"],
                    "testimonials": testimonials,
                    "raw": page["raw_text"][:1000],
                }
            elif keyword_match(combined, PRICING_KEYWORDS):
                level2_data["pricing"] = {
                    "url": link["url"],
                    "raw": page["raw_text"][:500],
                }
                # Pricing pages often have testimonials
                if testimonials and not level2_data["clients"]:
                    level2_data["clients"] = {"url": link["url"], "testimonials": testimonials, "raw": page["raw_text"][:500]}
            elif keyword_match(combined, API_KEYWORDS):
                level2_data["api"] = {
                    "url": link["url"],
                    "raw": page["raw_text"][:500],
                }
        time.sleep(0.5)

    # ── Check for existing llms.txt ───────────────────────────────────────────
    llms_txt_url = f"https://{domain}/llms.txt"
    existing_llms_txt = fetch_text_file(llms_txt_url)
    if existing_llms_txt:
        print(f"  ℹ️  Existing llms.txt found at {llms_txt_url}", file=sys.stderr)

    # ── Assemble output ───────────────────────────────────────────────────────
    all_emails = list(set(all_emails))

    nav_noise = ["login", "signin", "sign-in", "logout", "cart", "cookie", "privacy", "terms", "javascript"]
    important_links = [
        {"text": l["text"], "url": l["url"]}
        for l in unique_links
        if not keyword_match(l["url"].lower() + " " + l["text"].lower(), nav_noise) and l["text"]
    ][:15]

    output = {
        "domain": domain,
        "title": title,
        "meta_desc": meta_desc,
        "headings": all_headings[:20],
        "raw_text_summary": all_text[:text_limit],
        "emails": all_emails,
        "important_links": important_links,
        # Pass 1 heuristic signals (used by agent for gap report)
        "pricing_found": detect_pricing(all_text),
        "pricing_data": level2_data.get("pricing") or {},
        "api_found": bool(level2_data.get("api")),
        "api_data": level2_data.get("api") or {},
        "team_found": bool(level2_data.get("team") and level2_data["team"].get("snippets")),
        "team_data": level2_data.get("team") or {},
        "testimonials_found": bool(level2_data.get("clients") and level2_data["clients"].get("testimonials")),
        "testimonials_data": level2_data.get("clients") or {},
        "existing_llms_txt": existing_llms_txt,
        "pages_crawled": pages_crawled,
        "deep": deep,
    }

    # Pass 2 only: include full raw text per page for LLM extraction
    if deep:
        output["pages_raw"] = pages_raw

    return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: crawl.py <url> [extra_url1 extra_url2 ...]", file=sys.stderr)
        sys.exit(1)

    args = sys.argv[1:]
    deep = "--deep" in args
    args = [a for a in args if a != "--deep"]

    root_url = args[0]
    extra_urls = args[1:] if len(args) > 1 else []

    if not root_url.startswith("http"):
        root_url = "https://" + root_url

    result = crawl(root_url, extra_urls, deep=deep)
    print(json.dumps(result, indent=2))
