#!/usr/bin/env python3
"""
Web Multi-Search Skill for OpenClaw.

Searches across multiple search engines (Bing, Yahoo, Startpage, Aol, Ask)
using async-search-scraper, iterating through result pages.
"""

import argparse
import asyncio
import json
import csv
import io
import sys
from typing import Optional

from search_engines import Bing, Yahoo, Startpage, Aol, Ask, Torch
from search_engines.engines import search_engines_dict

# Engines known to work without special setup
WORKING_ENGINES = {
    "bing": Bing,
    "yahoo": Yahoo,
    "startpage": Startpage,
    "aol": Aol,
    "ask": Ask,
}

# Requires a running TOR proxy
TOR_ENGINES = {
    "torch": Torch,
}

ALL_ENGINES = {**WORKING_ENGINES, **TOR_ENGINES}


async def search_engine(
    engine_cls,
    query: str,
    pages: int,
    proxy: Optional[str] = None,
    timeout: int = 10,
    unique_urls: bool = False,
    unique_domains: bool = False,
) -> list[dict]:
    """Run a search on a single engine and return results."""
    engine = engine_cls(
        proxy=proxy,
        timeout=timeout,
        suppress_console_output=True,
    )
    engine.ignore_duplicate_urls = unique_urls
    engine.ignore_duplicate_domains = unique_domains

    try:
        results = await engine.search(query, pages=pages)
        engine_name = engine_cls.__name__

        items = []
        for r in results.results():
            items.append(
                {
                    "engine": engine_name,
                    "host": r.get("host", ""),
                    "link": r.get("link", ""),
                    "title": r.get("title", ""),
                    "text": r.get("text", ""),
                }
            )
        return items
    except Exception as e:
        print(
            f"Warning: {engine_cls.__name__} failed: {e}",
            file=sys.stderr,
        )
        return []
    finally:
        await engine.close()


async def multi_search(
    query: str,
    engines: list[str],
    pages: int = 3,
    proxy: Optional[str] = None,
    timeout: int = 10,
    unique_urls: bool = False,
    unique_domains: bool = False,
) -> list[dict]:
    """Search across multiple engines concurrently."""
    tasks = []
    for name in engines:
        name_lower = name.lower().strip()
        if name_lower not in ALL_ENGINES:
            print(
                f"Warning: Unknown engine '{name}', skipping. "
                f"Available: {', '.join(ALL_ENGINES.keys())}",
                file=sys.stderr,
            )
            continue
        engine_cls = ALL_ENGINES[name_lower]
        tasks.append(
            search_engine(
                engine_cls,
                query,
                pages,
                proxy=proxy,
                timeout=timeout,
                unique_urls=unique_urls,
                unique_domains=unique_domains,
            )
        )

    if not tasks:
        print("Error: No valid engines selected.", file=sys.stderr)
        return []

    results_lists = await asyncio.gather(*tasks)

    all_results = []
    seen_urls = set()
    for result_list in results_lists:
        for item in result_list:
            if unique_urls and item["link"] in seen_urls:
                continue
            seen_urls.add(item["link"])
            all_results.append(item)

    return all_results


def format_json(results: list[dict]) -> str:
    """Format results as JSON."""
    return json.dumps(results, indent=2, ensure_ascii=False)


def format_csv(results: list[dict]) -> str:
    """Format results as CSV."""
    if not results:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["engine", "host", "link", "title", "text"],
    )
    writer.writeheader()
    writer.writerows(results)
    return output.getvalue()


def format_text(results: list[dict]) -> str:
    """Format results as human-readable text."""
    if not results:
        return "No results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] ({r['engine']}) {r['title']}")
        lines.append(f"    {r['link']}")
        if r["text"]:
            lines.append(f"    {r['text'][:200]}")
        lines.append("")
    return "\n".join(lines)


FORMATTERS = {
    "json": format_json,
    "csv": format_csv,
    "text": format_text,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search the web using multiple search engines simultaneously.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            '  %(prog)s "python async tutorial"\n'
            '  %(prog)s "machine learning" --engines bing,yahoo --pages 5\n'
            '  %(prog)s "OpenClaw skills" --unique-urls --output csv\n'
        ),
    )
    parser.add_argument(
        "query",
        help="The search query string",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Number of result pages to fetch per engine (default: 3)",
    )
    parser.add_argument(
        "--engines",
        type=str,
        default=",".join(WORKING_ENGINES.keys()),
        help=(
            f"Comma-separated list of engines to use "
            f"(default: {','.join(WORKING_ENGINES.keys())}). "
            f"Available: {', '.join(ALL_ENGINES.keys())}"
        ),
    )
    parser.add_argument(
        "--proxy",
        type=str,
        default=None,
        help="HTTP or SOCKS proxy URL (e.g. socks5://127.0.0.1:9050)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="HTTP request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=FORMATTERS.keys(),
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--unique-urls",
        action="store_true",
        help="Deduplicate results by URL across all engines",
    )
    parser.add_argument(
        "--unique-domains",
        action="store_true",
        help="Deduplicate results by domain across all engines",
    )
    return parser.parse_args()


async def main():
    args = parse_args()
    engines = [e.strip() for e in args.engines.split(",") if e.strip()]

    print(
        f"Searching {len(engines)} engine(s) for: {args.query} "
        f"({args.pages} page(s) each)...",
        file=sys.stderr,
    )

    results = await multi_search(
        query=args.query,
        engines=engines,
        pages=args.pages,
        proxy=args.proxy,
        timeout=args.timeout,
        unique_urls=args.unique_urls,
        unique_domains=args.unique_domains,
    )

    print(
        f"Found {len(results)} result(s) total.",
        file=sys.stderr,
    )

    formatter = FORMATTERS[args.output]
    print(formatter(results))


if __name__ == "__main__":
    asyncio.run(main())
