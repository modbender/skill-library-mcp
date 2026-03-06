#!/usr/bin/env python3
"""
Tavily Search v1.0 - AI-powered web search platform with 5 modes.
Author: Leo 🦁
Created: 2026-02-07

Commands:
- search: General web search with optional LLM answer
- news: News-optimized search (topic=news)
- finance: Finance-optimized search (topic=finance)
- extract: Extract content from URLs
- crawl: Crawl a website
- map: Discover sitemap URLs
- research: Deep AI research with citations

Environment Variables:
- TAVILY_API_KEY: Required. Tavily API key.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from typing import Any, Optional

# ─── Configuration ───────────────────────────────────────────────────────────

API_KEY: str = os.environ.get("TAVILY_API_KEY", "")
BASE_URL: str = "https://api.tavily.com"
REQUEST_TIMEOUT: int = 30
RESEARCH_TIMEOUT: int = 120  # Research can take longer


# ─── HTTP Helper ─────────────────────────────────────────────────────────────

def _api_request(
    endpoint: str,
    payload: dict[str, Any],
    timeout: int = REQUEST_TIMEOUT,
) -> dict[str, Any]:
    """
    Make a POST request to the Tavily API.

    Args:
        endpoint: API endpoint path (e.g., '/search').
        payload: JSON request body.
        timeout: Request timeout in seconds.

    Returns:
        Parsed JSON response.

    Raises:
        SystemExit: On API errors with descriptive messages.
    """
    url = f"{BASE_URL}{endpoint}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        if e.code == 401:
            print("Error: Invalid TAVILY_API_KEY. Check your key at https://app.tavily.com", file=sys.stderr)
        elif e.code == 429:
            print("Error: Rate limit exceeded. Try again later.", file=sys.stderr)
        elif e.code == 400:
            # Try to extract error message from JSON response
            try:
                err_data = json.loads(body)
                msg = err_data.get("detail", err_data.get("message", body))
                print(f"Error: Bad request - {msg}", file=sys.stderr)
            except (json.JSONDecodeError, KeyError):
                print(f"Error: Bad request - {body}", file=sys.stderr)
        else:
            print(f"Error: Tavily API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Network error - {e.reason}", file=sys.stderr)
        sys.exit(1)
    except TimeoutError:
        print(f"Error: Request timed out after {timeout}s", file=sys.stderr)
        sys.exit(1)


# ─── Output Formatting ──────────────────────────────────────────────────────

def _format_search_results(data: dict[str, Any], as_json: bool = False) -> str:
    """Format search/news/finance results for display."""
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines: list[str] = []

    # LLM answer
    answer = data.get("answer")
    if answer:
        lines.append(f"Answer: {answer}")
        lines.append("")

    # Images
    images = data.get("images")
    if images:
        lines.append("Images:")
        for img in images:
            if isinstance(img, dict):
                lines.append(f"  - {img.get('url', img)}")
            else:
                lines.append(f"  - {img}")
        lines.append("")

    # Results
    results = data.get("results", [])
    if results:
        lines.append("Results:")
        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            content = r.get("content", "")
            score = r.get("score")
            published = r.get("published_date", "")

            lines.append(f"  {i}. {title}")
            lines.append(f"     {url}")
            if published:
                lines.append(f"     Published: {published}")
            if score is not None:
                lines.append(f"     Score: {score:.4f}")
            if content:
                # Truncate long content to keep output readable
                snippet = content[:500].strip()
                if len(content) > 500:
                    snippet += "..."
                lines.append(f"     {snippet}")

            # Raw content (if requested)
            raw = r.get("raw_content")
            if raw:
                lines.append(f"     --- Raw Content ---")
                raw_snippet = raw[:1000].strip()
                if len(raw) > 1000:
                    raw_snippet += f"... [{len(raw)} chars total]"
                lines.append(f"     {raw_snippet}")

            lines.append("")
    elif not answer:
        lines.append("No results found.")

    return "\n".join(lines).rstrip()


def _format_extract_results(data: dict[str, Any], as_json: bool = False) -> str:
    """Format extract results for display."""
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines: list[str] = []
    results = data.get("results", [])

    if not results:
        return "No content extracted."

    for r in results:
        url = r.get("url", "Unknown URL")
        content = r.get("raw_content", "")
        lines.append(f"URL: {url}")
        lines.append("─" * 50)
        if content:
            lines.append(content.strip())
        else:
            lines.append("(No content extracted)")
        lines.append("")

    # Failed URLs
    failed = data.get("failed_results", [])
    if failed:
        lines.append("Failed URLs:")
        for f in failed:
            url = f.get("url", "Unknown")
            error = f.get("error", "Unknown error")
            lines.append(f"  ✗ {url}: {error}")

    return "\n".join(lines).rstrip()


def _format_crawl_results(data: dict[str, Any], as_json: bool = False) -> str:
    """Format crawl results for display."""
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines: list[str] = []
    results = data.get("results", [])
    base_url = data.get("base_url", "")

    lines.append(f"Crawled {len(results)} pages from {base_url}")
    lines.append("")

    for i, r in enumerate(results, 1):
        url = r.get("url", "Unknown URL")
        content = r.get("raw_content", "")
        lines.append(f"Page {i}: {url}")
        lines.append("─" * 50)
        if content:
            # Truncate very long pages
            snippet = content[:2000].strip()
            if len(content) > 2000:
                snippet += f"\n... [{len(content)} chars total]"
            lines.append(snippet)
        else:
            lines.append("(No content)")
        lines.append("")

    # Failed
    failed = data.get("failed_results", [])
    if failed:
        lines.append("Failed URLs:")
        for f in failed:
            url = f.get("url", "Unknown")
            error = f.get("error", "Unknown error")
            lines.append(f"  ✗ {url}: {error}")

    return "\n".join(lines).rstrip()


def _format_map_results(data: dict[str, Any], url: str, as_json: bool = False) -> str:
    """Format map/sitemap results for display."""
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2)

    urls = data.get("results", [])
    lines: list[str] = []
    lines.append(f"Sitemap for {url} ({len(urls)} URLs found):")
    lines.append("")

    for i, u in enumerate(urls, 1):
        if isinstance(u, dict):
            lines.append(f"  {i}. {u.get('url', u)}")
        else:
            lines.append(f"  {i}. {u}")

    if not urls:
        lines.append("  No URLs discovered.")

    return "\n".join(lines).rstrip()


def _format_research_results(data: dict[str, Any], as_json: bool = False) -> str:
    """Format research results for display."""
    if as_json:
        return json.dumps(data, ensure_ascii=False, indent=2)

    lines: list[str] = []

    # Topic
    topic = data.get("topic") or data.get("query", "")
    if topic:
        lines.append(f"Research: {topic}")
        lines.append("")

    # Main content
    content = data.get("content") or data.get("output") or data.get("report", "")
    if content:
        lines.append(content.strip())
    else:
        lines.append("No research output returned.")

    # Sources
    sources = data.get("sources", [])
    if sources:
        lines.append("")
        lines.append("Sources:")
        for i, src in enumerate(sources, 1):
            if isinstance(src, dict):
                url = src.get("url", src.get("link", str(src)))
                title = src.get("title", "")
                if title:
                    lines.append(f"  [{i}] {title}")
                    lines.append(f"      {url}")
                else:
                    lines.append(f"  [{i}] {url}")
            else:
                lines.append(f"  [{i}] {src}")

    return "\n".join(lines).rstrip()


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_search(args: argparse.Namespace) -> str:
    """Execute search/news/finance command."""
    topic_map = {
        "search": "general",
        "news": "news",
        "finance": "finance",
    }

    payload: dict[str, Any] = {
        "query": args.query,
        "topic": topic_map.get(args.command, "general"),
        "search_depth": args.depth,
        "max_results": args.n,
    }

    if args.answer:
        payload["include_answer"] = True
    if args.raw:
        payload["include_raw_content"] = "markdown"
    if args.images:
        payload["include_images"] = True
    if args.time:
        payload["time_range"] = args.time
    if args.include_domains:
        payload["include_domains"] = [d.strip() for d in args.include_domains.split(",")]
    if args.exclude_domains:
        payload["exclude_domains"] = [d.strip() for d in args.exclude_domains.split(",")]
    if args.country:
        payload["country"] = args.country

    data = _api_request("/search", payload)
    return _format_search_results(data, as_json=args.as_json)


def cmd_extract(args: argparse.Namespace) -> str:
    """Execute extract command."""
    urls = args.urls
    if not urls:
        print("Error: At least one URL is required for extract.", file=sys.stderr)
        sys.exit(1)

    payload: dict[str, Any] = {
        "urls": urls if len(urls) > 1 else urls[0],
    }

    if args.depth and args.depth != "basic":
        payload["extract_depth"] = args.depth
    if hasattr(args, "format_type") and args.format_type:
        payload["format"] = args.format_type
    if hasattr(args, "query") and args.query:
        payload["query"] = args.query

    data = _api_request("/extract", payload)
    return _format_extract_results(data, as_json=args.as_json)


def cmd_crawl(args: argparse.Namespace) -> str:
    """Execute crawl command."""
    payload: dict[str, Any] = {
        "url": args.url,
    }

    if args.max_depth is not None:
        payload["max_depth"] = args.max_depth
    if args.max_breadth is not None:
        payload["max_breadth"] = args.max_breadth
    if args.limit is not None:
        payload["limit"] = args.limit
    if hasattr(args, "instructions") and args.instructions:
        payload["instructions"] = args.instructions
    if hasattr(args, "select_paths") and args.select_paths:
        payload["select_paths"] = [p.strip() for p in args.select_paths.split(",")]
    if hasattr(args, "exclude_paths") and args.exclude_paths:
        payload["exclude_paths"] = [p.strip() for p in args.exclude_paths.split(",")]
    if hasattr(args, "format_type") and args.format_type:
        payload["format"] = args.format_type

    data = _api_request("/crawl", payload, timeout=60)
    return _format_crawl_results(data, as_json=args.as_json)


def cmd_map(args: argparse.Namespace) -> str:
    """Execute map/sitemap command."""
    payload: dict[str, Any] = {
        "url": args.url,
    }

    if args.max_depth is not None:
        payload["max_depth"] = args.max_depth
    if args.max_breadth is not None:
        payload["max_breadth"] = args.max_breadth
    if args.limit is not None:
        payload["limit"] = args.limit

    data = _api_request("/map", payload)
    return _format_map_results(data, args.url, as_json=args.as_json)


def cmd_research(args: argparse.Namespace) -> str:
    """Execute research command."""
    payload: dict[str, Any] = {
        "input": args.query,
    }

    if args.model:
        payload["model"] = args.model

    data = _api_request("/research", payload, timeout=RESEARCH_TIMEOUT)
    return _format_research_results(data, as_json=args.as_json)


# ─── CLI ─────────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser with all subcommands."""
    parser = argparse.ArgumentParser(
        description="Tavily Search v1.0 - AI-powered web search platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "latest AI news" --answer
  %(prog)s news "tech industry" --time week
  %(prog)s finance "NVIDIA stock" --depth advanced
  %(prog)s extract "https://example.com/article"
  %(prog)s crawl "https://docs.example.com" --limit 20
  %(prog)s map "https://example.com"
  %(prog)s research "Impact of AI on healthcare"
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # ── Common search options ──
    def add_search_options(sub: argparse.ArgumentParser) -> None:
        sub.add_argument("query", help="Search query")
        sub.add_argument("--depth", choices=["basic", "advanced"], default="basic",
                         help="Search depth (default: basic; advanced = 2 credits)")
        sub.add_argument("--time", choices=["day", "week", "month", "year", "d", "w", "m", "y"],
                         default=None, help="Time range filter")
        sub.add_argument("-n", type=int, default=5, help="Max results 0-20 (default: 5)")
        sub.add_argument("--answer", action="store_true", help="Include LLM-synthesized answer")
        sub.add_argument("--raw", action="store_true", help="Include raw page content")
        sub.add_argument("--images", action="store_true", help="Include image URLs")
        sub.add_argument("--include-domains", default=None,
                         help="Comma-separated domains to include")
        sub.add_argument("--exclude-domains", default=None,
                         help="Comma-separated domains to exclude")
        sub.add_argument("--country", default=None, help="Country code to boost (e.g., US, IL)")
        sub.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # search
    p_search = subparsers.add_parser("search", help="Web search (general)")
    add_search_options(p_search)

    # news
    p_news = subparsers.add_parser("news", help="News search")
    add_search_options(p_news)

    # finance
    p_finance = subparsers.add_parser("finance", help="Finance search")
    add_search_options(p_finance)

    # extract
    p_extract = subparsers.add_parser("extract", help="Extract content from URLs")
    p_extract.add_argument("urls", nargs="+", help="URLs to extract content from")
    p_extract.add_argument("--depth", choices=["basic", "advanced"], default="basic",
                           help="Extraction depth")
    p_extract.add_argument("--format", dest="format_type", choices=["markdown", "text"],
                           default=None, help="Output format (default: markdown)")
    p_extract.add_argument("--query", default=None,
                           help="Query for relevance reranking of chunks")
    p_extract.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # crawl
    p_crawl = subparsers.add_parser("crawl", help="Crawl a website")
    p_crawl.add_argument("url", help="Root URL to crawl")
    p_crawl.add_argument("--depth", choices=["basic", "advanced"], default=None,
                         help="Crawl depth")
    p_crawl.add_argument("--max-depth", type=int, default=None, help="Max link depth (default: 2)")
    p_crawl.add_argument("--max-breadth", type=int, default=None,
                         help="Max pages per level (default: 10)")
    p_crawl.add_argument("--limit", type=int, default=None, help="Max total pages (default: 10)")
    p_crawl.add_argument("--instructions", default=None,
                         help="Natural language crawl instructions")
    p_crawl.add_argument("--select-paths", default=None,
                         help="Comma-separated path patterns to include")
    p_crawl.add_argument("--exclude-paths", default=None,
                         help="Comma-separated path patterns to exclude")
    p_crawl.add_argument("--format", dest="format_type", choices=["markdown", "text"],
                         default=None, help="Output format")
    p_crawl.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # map
    p_map = subparsers.add_parser("map", help="Discover sitemap URLs")
    p_map.add_argument("url", help="Root URL to map")
    p_map.add_argument("--max-depth", type=int, default=None, help="Max depth (default: 2)")
    p_map.add_argument("--max-breadth", type=int, default=None,
                       help="Max breadth per level (default: 20)")
    p_map.add_argument("--limit", type=int, default=None, help="Max URLs (default: 50)")
    p_map.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    # research
    p_research = subparsers.add_parser("research", help="Deep AI research")
    p_research.add_argument("query", help="Research question")
    p_research.add_argument("--model", choices=["mini", "pro", "auto"], default=None,
                            help="Research model (default: auto)")
    p_research.add_argument("--json", action="store_true", dest="as_json", help="JSON output")

    return parser


def main() -> None:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if not API_KEY:
        print("Error: TAVILY_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it in OpenClaw config or export TAVILY_API_KEY=your_key", file=sys.stderr)
        sys.exit(1)

    try:
        if args.command in ("search", "news", "finance"):
            result = cmd_search(args)
        elif args.command == "extract":
            result = cmd_extract(args)
        elif args.command == "crawl":
            result = cmd_crawl(args)
        elif args.command == "map":
            result = cmd_map(args)
        elif args.command == "research":
            result = cmd_research(args)
        else:
            parser.print_help()
            sys.exit(1)

        print(result)
    except SystemExit:
        raise
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
