#!/usr/bin/env python3
"""
smart-web-scraper: Extract structured data from web pages.
Supports CSS selectors, table auto-detection, link extraction, multi-page crawling.
Output formats: text, json, csv, markdown.
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from urllib.robotparser import RobotFileParser

try:
    from bs4 import BeautifulSoup, Tag
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    print("Error: beautifulsoup4 is required. Install with: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

try:
    import lxml  # noqa: F401
    PARSER = "lxml"
except ImportError:
    PARSER = "html.parser"

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 smart-web-scraper/1.0"
DEFAULT_DELAY = 1.0  # seconds between requests


def fetch(url: str, timeout: int = 30) -> str:
    """Fetch URL content with proper headers and error handling."""
    req = Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    try:
        with urlopen(req, timeout=timeout) as resp:
            encoding = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(encoding, errors="replace")
    except HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason} — {url}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"Connection Error: {e.reason} — {url}", file=sys.stderr)
        sys.exit(1)


def check_robots(url: str) -> bool:
    """Check if URL is allowed by robots.txt."""
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        return True  # If we can't read robots.txt, assume allowed


def clean_text(text: str) -> str:
    """Normalize whitespace in extracted text."""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def element_to_dict(el: Tag) -> dict:
    """Convert a BS4 element to a structured dict."""
    result = {
        "text": clean_text(el.get_text(separator=" ")),
        "tag": el.name,
    }
    if el.get("class"):
        result["class"] = " ".join(el["class"])
    if el.get("href"):
        result["href"] = el["href"]
    if el.get("src"):
        result["src"] = el["src"]
    # Include data-* attributes
    data_attrs = {k: v for k, v in el.attrs.items() if k.startswith("data-")}
    if data_attrs:
        result["data"] = data_attrs
    return result


# ─── Commands ────────────────────────────────────────────────

def cmd_extract(url: str, selector: str = None, fmt: str = "text", output: str = None):
    """Extract content from a URL, optionally filtered by CSS selector."""
    html = fetch(url)
    soup = BeautifulSoup(html, PARSER)

    # Remove noise elements
    for tag in soup(["script", "style", "noscript", "iframe"]):
        tag.decompose()

    if selector:
        elements = soup.select(selector)
        if not elements:
            print(f"No elements matched selector: {selector}", file=sys.stderr)
            sys.exit(1)
    else:
        elements = [soup.body] if soup.body else [soup]

    results = []
    for el in elements:
        if selector:
            results.append(element_to_dict(el))
        else:
            results.append({"text": clean_text(el.get_text(separator="\n"))})

    _output(results, fmt, output)


def cmd_tables(url: str, fmt: str = "text", output: str = None):
    """Auto-detect and extract all HTML tables."""
    html = fetch(url)
    soup = BeautifulSoup(html, PARSER)
    tables = soup.find_all("table")

    if not tables:
        print("No tables found on this page.", file=sys.stderr)
        sys.exit(1)

    all_tables = []
    for idx, table in enumerate(tables):
        rows = []
        headers = []

        # Extract headers
        thead = table.find("thead")
        if thead:
            headers = [clean_text(th.get_text()) for th in thead.find_all(["th", "td"])]

        # Extract rows
        for tr in table.find_all("tr"):
            cells = [clean_text(td.get_text()) for td in tr.find_all(["td", "th"])]
            if cells:
                # Skip header row if already captured
                if cells == headers:
                    continue
                if not headers and tr.find("th"):
                    headers = cells
                    continue
                rows.append(cells)

        all_tables.append({
            "table_index": idx,
            "headers": headers,
            "rows": rows,
            "row_count": len(rows),
        })

    if fmt == "csv":
        # For CSV, output first table with headers
        t = all_tables[0]
        buf = io.StringIO()
        writer = csv.writer(buf)
        if t["headers"]:
            writer.writerow(t["headers"])
        for row in t["rows"]:
            writer.writerow(row)
        _write_output(buf.getvalue(), output)
    elif fmt == "json":
        _write_output(json.dumps(all_tables, indent=2, ensure_ascii=False), output)
    elif fmt == "md":
        lines = []
        for t in all_tables:
            if t["headers"]:
                lines.append("| " + " | ".join(t["headers"]) + " |")
                lines.append("| " + " | ".join(["---"] * len(t["headers"])) + " |")
            for row in t["rows"]:
                lines.append("| " + " | ".join(row) + " |")
            lines.append("")
        _write_output("\n".join(lines), output)
    else:
        for t in all_tables:
            print(f"=== Table {t['table_index']} ({t['row_count']} rows) ===")
            if t["headers"]:
                print("  " + " | ".join(t["headers"]))
                print("  " + "-" * 60)
            for row in t["rows"]:
                print("  " + " | ".join(row))
            print()


def cmd_links(url: str, external: bool = False, internal: bool = False):
    """Extract all links from a page."""
    html = fetch(url)
    soup = BeautifulSoup(html, PARSER)
    base_domain = urlparse(url).netloc

    links = []
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        text = clean_text(a.get_text())
        link_domain = urlparse(href).netloc
        is_external = link_domain != base_domain

        if external and not is_external:
            continue
        if internal and is_external:
            continue

        # Skip anchors, javascript, mailto
        if href.startswith(("javascript:", "mailto:", "tel:", "#")):
            continue

        links.append({"url": href, "text": text or "[no text]", "external": is_external})

    # Deduplicate by URL
    seen = set()
    unique = []
    for link in links:
        if link["url"] not in seen:
            seen.add(link["url"])
            unique.append(link)

    print(json.dumps(unique, indent=2, ensure_ascii=False))


def cmd_structure(url: str):
    """Extract page structure: title, meta, headings, images, links."""
    html = fetch(url)
    soup = BeautifulSoup(html, PARSER)

    structure = {
        "url": url,
        "title": soup.title.string.strip() if soup.title and soup.title.string else None,
        "meta": {},
        "headings": [],
        "images": [],
        "link_count": len(soup.find_all("a", href=True)),
    }

    # Meta tags
    for meta in soup.find_all("meta"):
        name = meta.get("name") or meta.get("property")
        content = meta.get("content")
        if name and content:
            structure["meta"][name] = content

    # Headings hierarchy
    for level in range(1, 7):
        for h in soup.find_all(f"h{level}"):
            structure["headings"].append({
                "level": level,
                "text": clean_text(h.get_text()),
            })

    # Images
    for img in soup.find_all("img", src=True)[:20]:  # Limit to 20
        structure["images"].append({
            "src": urljoin(url, img["src"]),
            "alt": img.get("alt", ""),
        })

    print(json.dumps(structure, indent=2, ensure_ascii=False))


def cmd_crawl(url: str, pages: int = 5, selector: str = None, fmt: str = "text",
              output: str = None, delay: float = DEFAULT_DELAY, ignore_robots: bool = False):
    """Crawl multiple pages following pagination patterns."""
    all_results = []
    current_url = url

    for page_num in range(1, pages + 1):
        if not current_url:
            break

        if not ignore_robots and not check_robots(current_url):
            print(f"Blocked by robots.txt: {current_url}", file=sys.stderr)
            break

        print(f"[{page_num}/{pages}] Scraping: {current_url}", file=sys.stderr)
        html = fetch(current_url)
        soup = BeautifulSoup(html, PARSER)

        # Remove noise
        for tag in soup(["script", "style", "noscript", "iframe"]):
            tag.decompose()

        # Extract content
        if selector:
            elements = soup.select(selector)
            for el in elements:
                item = element_to_dict(el)
                item["_page"] = page_num
                item["_source_url"] = current_url
                all_results.append(item)
        else:
            body = soup.body or soup
            all_results.append({
                "text": clean_text(body.get_text(separator="\n")),
                "_page": page_num,
                "_source_url": current_url,
            })

        # Find next page link
        current_url = _find_next_page(soup, current_url, page_num)

        if page_num < pages and current_url:
            time.sleep(delay)

    print(f"\nExtracted {len(all_results)} items from {page_num} pages.", file=sys.stderr)
    _output(all_results, fmt, output)


def _find_next_page(soup: BeautifulSoup, current_url: str, current_page: int) -> str | None:
    """Heuristic to find the next page URL."""
    # Strategy 1: Look for rel="next"
    next_link = soup.find("a", rel="next")
    if next_link and next_link.get("href"):
        return urljoin(current_url, next_link["href"])

    # Strategy 2: Look for common pagination patterns
    for pattern in [".next a", "a.next", ".pagination .next", "[aria-label='Next']",
                    "a[aria-label='Next page']", ".page-next a"]:
        el = soup.select_one(pattern)
        if el and el.get("href"):
            return urljoin(current_url, el["href"])

    # Strategy 3: URL pattern (page/N, ?page=N, &p=N)
    parsed = urlparse(current_url)
    next_page = current_page + 1

    # /page/1 -> /page/2
    new_path = re.sub(r"/page/\d+", f"/page/{next_page}", parsed.path)
    if new_path != parsed.path:
        return urljoin(current_url, new_path)

    # ?page=1 -> ?page=2
    if f"page={current_page}" in (parsed.query or ""):
        new_url = current_url.replace(f"page={current_page}", f"page={next_page}")
        return new_url

    return None


# ─── Output helpers ──────────────────────────────────────────

def _output(results: list, fmt: str, output: str = None):
    """Format and output results."""
    if fmt == "json":
        text = json.dumps(results, indent=2, ensure_ascii=False)
    elif fmt == "csv":
        buf = io.StringIO()
        if results:
            keys = list(results[0].keys())
            writer = csv.DictWriter(buf, fieldnames=keys, extrasaction="ignore")
            writer.writeheader()
            for r in results:
                writer.writerow(r)
        text = buf.getvalue()
    elif fmt == "md":
        lines = []
        for r in results:
            lines.append(f"### {r.get('tag', 'item')}")
            lines.append(r.get("text", ""))
            if r.get("href"):
                lines.append(f"[Link]({r['href']})")
            lines.append("")
        text = "\n".join(lines)
    else:
        lines = []
        for r in results:
            lines.append(r.get("text", str(r)))
        text = "\n\n".join(lines)

    _write_output(text, output)


def _write_output(text: str, output: str = None):
    """Write to file or stdout."""
    if output:
        Path(output).write_text(text, encoding="utf-8")
        print(f"Saved to: {output}", file=sys.stderr)
    else:
        print(text)


# ─── CLI ─────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Smart Web Scraper — Extract structured data from web pages.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # extract
    p_ext = sub.add_parser("extract", help="Extract content from a URL")
    p_ext.add_argument("url", help="URL to scrape")
    p_ext.add_argument("-s", "--selector", help="CSS selector to filter elements")
    p_ext.add_argument("-f", "--format", default="text", choices=["text", "json", "csv", "md"])
    p_ext.add_argument("-o", "--output", help="Save output to file")

    # tables
    p_tab = sub.add_parser("tables", help="Auto-detect and extract HTML tables")
    p_tab.add_argument("url", help="URL to scrape")
    p_tab.add_argument("-f", "--format", default="text", choices=["text", "json", "csv", "md"])
    p_tab.add_argument("-o", "--output", help="Save output to file")

    # links
    p_lnk = sub.add_parser("links", help="Extract all links from a page")
    p_lnk.add_argument("url", help="URL to scrape")
    p_lnk.add_argument("--external", action="store_true", help="Only external links")
    p_lnk.add_argument("--internal", action="store_true", help="Only internal links")

    # structure
    p_str = sub.add_parser("structure", help="Extract page structure")
    p_str.add_argument("url", help="URL to analyze")

    # crawl
    p_crawl = sub.add_parser("crawl", help="Multi-page scrape with pagination")
    p_crawl.add_argument("url", help="Starting URL")
    p_crawl.add_argument("--pages", type=int, default=5, help="Max pages to crawl (default: 5)")
    p_crawl.add_argument("-s", "--selector", help="CSS selector to filter elements")
    p_crawl.add_argument("-f", "--format", default="text", choices=["text", "json", "csv", "md"])
    p_crawl.add_argument("-o", "--output", help="Save output to file")
    p_crawl.add_argument("--delay", type=float, default=DEFAULT_DELAY, help="Delay between requests (seconds)")
    p_crawl.add_argument("--ignore-robots", action="store_true", help="Ignore robots.txt")

    args = parser.parse_args()

    if args.command == "extract":
        cmd_extract(args.url, args.selector, args.format, args.output)
    elif args.command == "tables":
        cmd_tables(args.url, args.format, args.output)
    elif args.command == "links":
        cmd_links(args.url, args.external, args.internal)
    elif args.command == "structure":
        cmd_structure(args.url)
    elif args.command == "crawl":
        cmd_crawl(args.url, args.pages, args.selector, args.format, args.output,
                  args.delay, args.ignore_robots)


if __name__ == "__main__":
    main()
