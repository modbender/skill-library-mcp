#!/usr/bin/env python3
"""Local search & fetch tool for LLM agents without built-in web tools.

Usage:
    python search_fetch.py search "query string" [--num 10]
    python search_fetch.py fetch "https://example.com" [--timeout 15] [--max-chars 12000] [--strategy direct]

Fetch strategies:
    direct   — (default) browser-like headers + session, all traffic stays local
    jina     — r.jina.ai reader proxy; target URL is sent to r.jina.ai (third-party)
    archive  — Wayback Machine snapshot; target URL is sent to archive.org (third-party)
    auto     — tries direct → jina → archive; may contact third-party services on fallback

Data flow notice:
    - 'direct' strategy: requests go directly from your machine to the target site.
    - 'jina' / 'archive' / 'auto-fallback': the target URL (and response content) passes
      through r.jina.ai or archive.org. Do NOT use these strategies for sensitive or
      internal URLs.

Output: JSON to stdout. Errors are returned as JSON {"error": "..."}.

Setup: npm run setup  (see package.json)
"""

import argparse
import json
import re
import time


# Realistic Chrome browser headers for direct fetching
_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Cache-Control": "max-age=0",
}


def _extract_text(html: str, url: str) -> str:
    """Extract main text from HTML. Tries trafilatura first, falls back to BS4."""
    # trafilatura gives much cleaner extraction (handles boilerplate, ads, nav)
    try:
        import trafilatura
        text = trafilatura.extract(html, url=url, include_comments=False, include_tables=True)
        if text and len(text) > 200:
            return text
    except ImportError:
        pass

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()
    body = soup.find("main") or soup.find("article") or soup.find(id="content") or soup.body
    raw = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    return "\n".join(lines)


def _build_result(url: str, status: int, title: str, text: str, strategy: str, max_chars: int) -> dict:
    return {
        "url": url,
        "status": status,
        "title": title,
        "strategy": strategy,
        "content": text[:max_chars],
        "truncated": len(text) > max_chars,
        "total_chars": len(text),
    }


def _fetch_direct(url: str, timeout: int, max_chars: int) -> dict:
    import requests
    from bs4 import BeautifulSoup

    session = requests.Session()
    session.headers.update(_BROWSER_HEADERS)

    # Visit root domain first to pick up cookies (helps with some anti-bot)
    try:
        from urllib.parse import urlparse
        root = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"
        if root != url:
            session.get(root, timeout=timeout, allow_redirects=True)
            time.sleep(0.5)
    except Exception:
        pass

    resp = session.get(url, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.string.strip() if soup.title else ""
    text = _extract_text(resp.text, url)
    return _build_result(url, resp.status_code, title, text, "direct", max_chars)


def _fetch_jina(url: str, timeout: int, max_chars: int) -> dict:
    """Use r.jina.ai as a reader proxy — free, no API key, returns clean markdown."""
    import requests

    jina_url = f"https://r.jina.ai/{url}"
    headers = {
        "User-Agent": _BROWSER_HEADERS["User-Agent"],
        "Accept": "text/plain, text/markdown, */*",
        "X-Return-Format": "markdown",
    }
    resp = requests.get(jina_url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    text = resp.text.strip()
    # Extract title from first markdown heading if present
    title = ""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            title = line.lstrip("# ").strip()
            break

    return _build_result(url, resp.status_code, title, text, "jina", max_chars)


def _fetch_archive(url: str, timeout: int, max_chars: int) -> dict:
    """Fall back to the latest Wayback Machine snapshot."""
    import requests
    from bs4 import BeautifulSoup

    # Query availability API
    avail = requests.get(
        "https://archive.org/wayback/available",
        params={"url": url},
        timeout=timeout,
    ).json()

    snapshots = avail.get("archived_snapshots", {})
    closest = snapshots.get("closest", {})
    if not closest.get("available"):
        raise ValueError("No Wayback Machine snapshot found")

    archive_url = closest["url"]
    resp = requests.get(archive_url, headers=_BROWSER_HEADERS, timeout=timeout, allow_redirects=True)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"

    soup = BeautifulSoup(resp.text, "lxml")
    title = soup.title.string.strip() if soup.title else ""
    text = _extract_text(resp.text, archive_url)
    result = _build_result(url, resp.status_code, title, text, "archive", max_chars)
    result["archive_url"] = archive_url
    result["archive_timestamp"] = closest.get("timestamp", "")
    return result


_STRATEGIES = {
    "direct": _fetch_direct,
    "jina": _fetch_jina,
    "archive": _fetch_archive,
}


def do_fetch(url: str, timeout: int = 15, max_chars: int = 12000, strategy: str = "auto") -> dict:
    try:
        import requests  # noqa: F401
        from bs4 import BeautifulSoup  # noqa: F401
    except ImportError:
        return {"error": "missing deps: pip install requests beautifulsoup4 lxml"}

    order = list(_STRATEGIES.keys()) if strategy == "auto" else [strategy]
    errors = {}

    for name in order:
        try:
            return _STRATEGIES[name](url, timeout, max_chars)
        except Exception as e:
            errors[name] = str(e)
            if strategy != "auto":
                break  # Don't cascade if a specific strategy was requested

    return {"url": url, "error": "all strategies failed", "details": errors}


# ── Search ────────────────────────────────────────────────────────────────────

def do_search(query: str, num: int = 10) -> list:
    # Package was renamed from duckduckgo-search to ddgs; try both
    try:
        from ddgs import DDGS
    except ImportError:
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return [{"error": "missing dep: pip install ddgs"}]

    try:
        with DDGS() as ddgs:
            return [
                {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
                for r in ddgs.text(query, max_results=num)
            ]
    except Exception as e:
        return [{"error": str(e)}]


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Local search & fetch tool for LLM agents")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("search", help="DuckDuckGo web search")
    sp.add_argument("query")
    sp.add_argument("--num", type=int, default=10, help="max results (default: 10)")

    fp = sub.add_parser("fetch", help="Fetch and extract text from URL")
    fp.add_argument("url")
    fp.add_argument("--timeout", type=int, default=15, help="request timeout seconds (default: 15)")
    fp.add_argument("--max-chars", type=int, default=12000, help="max content chars (default: 12000)")
    fp.add_argument(
        "--strategy",
        choices=["auto", "direct", "jina", "archive"],
        default="direct",
        help="fetch strategy (default: direct). 'auto' falls back to jina/archive which send URLs to third-party services.",
    )
    fp.add_argument(
        "--no-third-party",
        action="store_true",
        help="force direct-only fetch; overrides --strategy to 'direct' and never contacts third-party proxies",
    )

    args = parser.parse_args()

    if args.cmd == "search":
        result = do_search(args.query, args.num)
    else:
        strategy = "direct" if args.no_third_party else args.strategy
        result = do_fetch(args.url, args.timeout, args.max_chars, strategy)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
