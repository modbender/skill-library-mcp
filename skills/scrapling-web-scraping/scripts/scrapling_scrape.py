#!/usr/bin/env python3
"""Quick one-off scraping helper using Scrapling.

Examples:
  python3 scrapling_scrape.py --url "https://quotes.toscrape.com" --css ".quote .text::text"
  python3 scrapling_scrape.py --url "https://example.com" --xpath "//h1/text()" --mode dynamic --headless
  python3 scrapling_scrape.py --url "https://example.com" --css "title::text" --mode stealthy --headless --solve-cloudflare

Notes:
- For anything beyond small, explicit extraction, prefer Scrapling Spiders.
- Some flags (adaptive/auto-save) depend on the installed Scrapling version.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any


def _die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _select(page: Any, *, css: str | None, xpath: str | None, adaptive: bool, auto_save: bool) -> Any:
    if css:
        # Try to pass adaptive/auto_save if supported; fall back if not.
        try:
            return page.css(css, adaptive=adaptive or None, auto_save=auto_save or None)
        except TypeError:
            return page.css(css)
    else:
        try:
            return page.xpath(xpath, adaptive=adaptive or None, auto_save=auto_save or None)  # type: ignore[arg-type]
        except TypeError:
            return page.xpath(xpath)  # type: ignore[arg-type]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--url", required=True)
    p.add_argument("--mode", choices=["fetcher", "dynamic", "stealthy"], default="fetcher")
    p.add_argument("--css", help="CSS selector (supports ::text and ::attr())")
    p.add_argument("--xpath", help="XPath selector")
    p.add_argument("--first", action="store_true", help="Return only the first match")
    p.add_argument("--headless", action="store_true", help="Headless browser (dynamic/stealthy)")
    p.add_argument("--solve-cloudflare", action="store_true", help="Attempt to solve Cloudflare (stealthy session)")
    p.add_argument("--network-idle", action="store_true", help="Wait for network idle (dynamic session)")
    p.add_argument("--adaptive", action="store_true", help="Use adaptive selectors (if supported)")
    p.add_argument("--auto-save", action="store_true", help="Auto-save selector fingerprints (if supported)")
    p.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = p.parse_args()

    if not args.css and not args.xpath:
        _die("Provide --css or --xpath")

    url = args.url

    try:
        # Sessions are more reliable than one-shot fetchers for anything non-trivial.
        from scrapling.fetchers import FetcherSession, DynamicSession, StealthySession
    except Exception:
        _die(
            "Scrapling is not installed in this Python environment. Try:\n"
            "  python3 -m pip install scrapling\n"
            "If you need browser-based fetching, you may also need:\n"
            "  python3 -m playwright install chromium"
        )

    if args.mode == "fetcher":
        with FetcherSession(impersonate="chrome") as session:
            page = session.get(url, stealthy_headers=True)

    elif args.mode == "dynamic":
        with DynamicSession(headless=args.headless, network_idle=args.network_idle) as session:
            page = session.fetch(url)

    else:
        # Use only when authorized.
        with StealthySession(headless=args.headless, solve_cloudflare=args.solve_cloudflare) as session:
            page = session.fetch(url, google_search=False)

    out = _select(page, css=args.css, xpath=args.xpath, adaptive=args.adaptive, auto_save=args.auto_save)

    result: Any
    if args.first:
        result = out.get()
    else:
        result = out.getall()

    payload = {
        "url": url,
        "mode": args.mode,
        "options": {
            "headless": bool(args.headless),
            "solve_cloudflare": bool(args.solve_cloudflare),
            "network_idle": bool(args.network_idle),
            "adaptive": bool(args.adaptive),
            "auto_save": bool(args.auto_save),
        },
        "selector": {"css": args.css, "xpath": args.xpath},
        "result": result,
    }

    if args.pretty:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
