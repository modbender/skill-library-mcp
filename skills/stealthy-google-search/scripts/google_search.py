#!/usr/bin/env python3

import argparse
import json
from urllib.parse import quote_plus


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Stealthy Google search via Scrapling")
    ap.add_argument("--query", required=True)
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--hl", default="en")
    ap.add_argument("--gl", default="us")
    ap.add_argument("--json", action="store_true", dest="as_json")
    return ap.parse_args()


def main() -> int:
    args = parse_args()

    try:
        from scrapling.fetchers import StealthyFetcher
    except Exception as e:
        raise SystemExit(
            "scrapling is not installed for this Python environment. "
            "Run the skill installer first: bash scripts/install.sh\n\n" + str(e)
        )

    url = (
        f"https://www.google.com/search?q={quote_plus(args.query)}"
        f"&hl={quote_plus(args.hl)}&gl={quote_plus(args.gl)}"
    )

    page = StealthyFetcher.fetch(
        url,
        headless=True,
        network_idle=True,
        google_search=True,
    )

    results = []
    for h3 in page.css("h3"):
        title = (h3.css("::text").get() or "").strip()
        if not title:
            continue
        a = h3.xpath("ancestor::a[1]")
        href = (a.css("::attr(href)").get() if a else "") or ""
        href = href.strip()
        if not href.startswith("http"):
            continue
        results.append({"title": title, "url": href})

    results = results[: max(args.top, 0)]

    if args.as_json:
        print(json.dumps({"query": args.query, "url": url, "results": results}, ensure_ascii=False))
    else:
        print(f"Query: {args.query}")
        print(f"URL: {url}")
        print(f"Results: {len(results)}")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}\n   {r['url']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
