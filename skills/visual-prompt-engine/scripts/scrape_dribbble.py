#!/usr/bin/env python3
"""
Scrape trending designs from Dribbble for visual reference.
Supports RSS feed (no dependencies) and HTML scraping (requires requests + bs4).
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

# Dribbble RSS feeds
FEEDS = {
    "popular": "https://dribbble.com/shots/popular.rss",
    "recent": "https://dribbble.com/shots/recent.rss",
    "animated": "https://dribbble.com/shots/animated.rss",
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_rss(feed_url: str, count: int = 20) -> list[dict]:
    """Fetch designs from Dribbble RSS feed (no external dependencies)."""
    req = Request(feed_url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(req, timeout=30) as resp:
            status = resp.getcode()
            xml_data = resp.read()
            if status != 200 or len(xml_data) < 100:
                print(f"RSS returned status {status} or empty body (WAF block likely)", file=sys.stderr)
                print("Tip: Use --method html with Camofox, or import references manually.", file=sys.stderr)
                return []
    except Exception as e:
        print(f"RSS fetch failed: {e}", file=sys.stderr)
        return []

    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"RSS parse failed: {e}", file=sys.stderr)
        return []

    items = root.findall(".//item")

    results = []
    for item in items[:count]:
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = item.findtext("description", "")
        pub_date = item.findtext("pubDate", "")

        # Extract image URL from description HTML
        img_match = re.search(r'src="([^"]+)"', desc)
        img_url = img_match.group(1) if img_match else ""

        # Clean description text
        clean_desc = re.sub(r"<[^>]+>", "", desc).strip()

        results.append({
            "title": title,
            "url": link,
            "image_url": img_url,
            "description": clean_desc[:500],
            "published": pub_date,
            "source": "dribbble_rss",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })

    return results


def fetch_html(url: str = "https://dribbble.com/shots/popular", count: int = 20) -> list[dict]:
    """Fetch designs via HTML scraping (requires requests + beautifulsoup4)."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        print("HTML scraping requires: pip install requests beautifulsoup4", file=sys.stderr)
        print("Falling back to RSS feed...", file=sys.stderr)
        return fetch_rss(FEEDS["popular"], count)

    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    shots = soup.select("li.shot-thumbnail-container, div.shot-thumbnail-container")

    if not shots:
        # Fallback: try finding shot links
        shots = soup.select("a[href*='/shots/']")

    results = []
    seen_urls = set()

    for shot in shots:
        if len(results) >= count:
            break

        # Extract link
        link_el = shot if shot.name == "a" else shot.select_one("a[href*='/shots/']")
        if not link_el or not link_el.get("href"):
            continue

        href = link_el["href"]
        if not href.startswith("http"):
            href = f"https://dribbble.com{href}"

        if href in seen_urls:
            continue
        seen_urls.add(href)

        # Extract title
        title = ""
        title_el = shot.select_one(".shot-title, [class*='title']")
        if title_el:
            title = title_el.get_text(strip=True)
        elif link_el.get("title"):
            title = link_el["title"]

        # Extract image
        img_url = ""
        img_el = shot.select_one("img")
        if img_el:
            img_url = img_el.get("src", "") or img_el.get("data-src", "")

        results.append({
            "title": title or "Untitled",
            "url": href,
            "image_url": img_url,
            "description": "",
            "published": "",
            "source": "dribbble_html",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })

    return results


def import_manual(input_path: str) -> list[dict]:
    """Import manually collected references from a JSON file.
    
    Use this when automated scraping is blocked. The agent can browse Dribbble
    with a browser tool and save results in this format:
    [{"title": "...", "url": "https://dribbble.com/shots/...", "image_url": "..."}]
    """
    with open(input_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    
    results = []
    for item in raw:
        results.append({
            "title": item.get("title", "Untitled"),
            "url": item.get("url", ""),
            "image_url": item.get("image_url", ""),
            "description": item.get("description", ""),
            "published": item.get("published", ""),
            "source": "manual_import",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        })
    return results


def main():
    parser = argparse.ArgumentParser(description="Scrape Dribbble for visual references")
    parser.add_argument("--output", "-o", default="data/references.json", help="Output JSON path")
    parser.add_argument("--count", "-c", type=int, default=20, help="Number of designs to fetch")
    parser.add_argument("--feed", choices=list(FEEDS.keys()), default="popular", help="RSS feed type")
    parser.add_argument("--method", choices=["rss", "html", "import"], default="rss", help="Scraping method (import reads from --import-file)")
    parser.add_argument("--import-file", help="JSON file to import (for --method import)")
    parser.add_argument("--append", action="store_true", help="Append to existing file instead of overwriting")
    args = parser.parse_args()

    # Ensure output directory exists
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Fetch designs
    print(f"Fetching {args.count} designs from Dribbble ({args.method})...")

    if args.method == "import":
        if not args.import_file:
            print("Error: --import-file required with --method import", file=sys.stderr)
            sys.exit(1)
        designs = import_manual(args.import_file)
    elif args.method == "html":
        designs = fetch_html(count=args.count)
    else:
        designs = fetch_rss(FEEDS[args.feed], count=args.count)
        if not designs:
            print("RSS blocked. Trying HTML fallback...", file=sys.stderr)
            designs = fetch_html(count=args.count)

    print(f"Found {len(designs)} designs")

    # Handle append mode
    if args.append and out_path.exists():
        with open(out_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_urls = {d["url"] for d in existing}
        new_designs = [d for d in designs if d["url"] not in existing_urls]
        designs = existing + new_designs
        print(f"Appended {len(new_designs)} new designs (total: {len(designs)})")

    # Save
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(designs, f, indent=2, ensure_ascii=False)

    print(f"Saved to {out_path}")


if __name__ == "__main__":
    main()
