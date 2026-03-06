#!/usr/bin/env python3
"""Web search via multiple engines. No API key required.

Usage:
    python3 google_search.py "search term" [--pages N] [--engine ENGINE]

Flags:
    --pages N        Number of result pages (default: 1, ~10 results each)
    --engine ENGINE  Search engine: duckduckgo (default), brave, google
                     Note: google often blocks with CAPTCHA

Outputs JSON array of {title, url, snippet} per result.
"""

import argparse
import json
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup


def json_error(message: str) -> str:
    """Return standardized JSON error format."""
    return json.dumps({"error": message}, indent=2, ensure_ascii=False)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def search_duckduckgo(query: str, pages: int = 1) -> list[dict]:
    """DuckDuckGo HTML endpoint — most reliable, no CAPTCHA."""
    results = []
    form_data = {"q": query}

    for page in range(pages):
        resp = requests.post("https://html.duckduckgo.com/html/", data=form_data, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for res in soup.select(".result"):
            title_el = res.select_one(".result__title a, a.result__a")
            snippet_el = res.select_one(".result__snippet")
            if not title_el:
                continue
            href = title_el.get("href", "")
            if "uddg=" in href:
                href = urllib.parse.unquote(
                    urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get("uddg", [href])[0]
                )
            if href.startswith("http"):
                results.append({
                    "title": title_el.get_text(strip=True),
                    "url": href,
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })

        if page < pages - 1:
            next_form = None
            for btn in soup.find_all("input", {"value": "Next"}):
                if btn.parent and btn.parent.name == "form":
                    next_form = btn.parent
                    break
            if not next_form:
                break
            form_data = {}
            for inp in next_form.find_all("input"):
                name = inp.get("name")
                if name:
                    form_data[name] = inp.get("value", "")
            time.sleep(1)

    return results


def search_brave(query: str, pages: int = 1) -> list[dict]:
    """Brave Search HTML — good alternative, sometimes more results."""
    results = []

    for page in range(pages):
        offset = page * 10
        params = {"q": query, "offset": str(offset)}
        resp = requests.get("https://search.brave.com/search", params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select('div[data-type="web"]'):
            # Title: dedicated title span, or first link text
            title_el = item.select_one(".title.search-snippet-title, .search-snippet-title")
            link_el = item.select_one("a[href^='http']")
            # Description/snippet
            snippet_el = item.select_one(".generic-snippet .content, .generic-snippet, .snippet-description")

            if not link_el:
                continue
            href = link_el.get("href", "")
            title = title_el.get_text(strip=True) if title_el else link_el.get_text(strip=True)
            if href.startswith("http") and title:
                results.append({
                    "title": title,
                    "url": href,
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })

        if page < pages - 1:
            time.sleep(1)

    return results


def search_google(query: str, pages: int = 1) -> list[dict]:
    """Google HTML — often blocked by CAPTCHA. Use as fallback."""
    results = []

    for page in range(pages):
        start = page * 10
        params = {"q": query, "start": str(start), "hl": "en"}
        resp = requests.get("https://www.google.com/search", params=params, headers=HEADERS, timeout=15)
        resp.raise_for_status()

        if "sorry" in resp.url or "unusual traffic" in resp.text.lower():
            if not results:
                raise RuntimeError("Google blocked the request (CAPTCHA). Try --engine duckduckgo or brave.")
            break

        soup = BeautifulSoup(resp.text, "html.parser")
        for h3 in soup.find_all("h3"):
            parent_a = h3.find_parent("a")
            if parent_a and parent_a.get("href", "").startswith("http"):
                # Find snippet near the h3
                container = h3.find_parent("div", class_="g") or h3.parent
                snippet_el = container.select_one("div[data-sncf], div.VwiC3b, span.st") if container else None
                results.append({
                    "title": h3.get_text(strip=True),
                    "url": parent_a["href"],
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                })

        if page < pages - 1:
            time.sleep(1.5)

    return results


ENGINES = {
    "duckduckgo": search_duckduckgo,
    "ddg": search_duckduckgo,
    "brave": search_brave,
    "google": search_google,
}


def main():
    parser = argparse.ArgumentParser(description="Web search (multi-engine, no API key)")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--pages", type=int, default=1, help="Number of result pages (default: 1)")
    parser.add_argument("--engine", choices=["duckduckgo", "ddg", "brave", "google"],
                        default="duckduckgo", help="Search engine (default: duckduckgo)")
    args = parser.parse_args()

    try:
        search_fn = ENGINES[args.engine]
        results = search_fn(args.query, args.pages)

        # Deduplicate
        seen = set()
        deduped = []
        for r in results:
            if r["url"] not in seen:
                seen.add(r["url"])
                deduped.append(r)

        print(json.dumps(deduped, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json_error(f"Search failed: {str(e)}"))


if __name__ == "__main__":
    main()
