#!/usr/bin/env python3
"""SearXNG search client - query a local SearXNG instance and return results."""

import argparse
import json
import sys
import urllib.request
import urllib.parse
import urllib.error

DEFAULT_BASE_URL = "http://127.0.0.1:8888"
DEFAULT_NUM_RESULTS = 10


def search(
    query: str,
    base_url: str = DEFAULT_BASE_URL,
    categories: str = "general",
    language: str = "auto",
    time_range: str = "",
    num_results: int = DEFAULT_NUM_RESULTS,
    engines: str = "",
    output_json: bool = False,
) -> str:
    """Perform a search via SearXNG JSON API."""
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
        "language": language,
    }
    if time_range:
        params["time_range"] = time_range
    if engines:
        params["engines"] = engines

    url = f"{base_url.rstrip('/')}/search?{urllib.parse.urlencode(params)}"

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Error: HTTP {e.code} from SearXNG: {body[:500]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: cannot reach SearXNG at {base_url}: {e.reason}", file=sys.stderr)
        sys.exit(1)

    results = data.get("results", [])[:num_results]

    if output_json:
        compact = []
        for r in results:
            compact.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", ""),
                "engines": r.get("engines", []),
                "score": r.get("score", 0),
                "publishedDate": r.get("publishedDate"),
            })
        return json.dumps(compact, ensure_ascii=False, indent=2)

    # Human-readable output
    lines = []
    lines.append(f"搜索: {query}")
    lines.append(f"结果数: {data.get('number_of_results', len(results))}")
    lines.append("")

    for i, r in enumerate(results, 1):
        title = r.get("title", "(no title)")
        url = r.get("url", "")
        content = r.get("content", "")
        engines_list = ", ".join(r.get("engines", []))
        score = r.get("score", 0)

        lines.append(f"{i}. {title}")
        lines.append(f"   {url}")
        if content:
            # Truncate long snippets
            snippet = content[:300] + ("..." if len(content) > 300 else "")
            lines.append(f"   {snippet}")
        lines.append(f"   [来源: {engines_list} | 评分: {score}]")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Search via local SearXNG instance")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("-q", "--query-flag", dest="query_flag", help="Search query (alternative)")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help=f"SearXNG base URL (default: {DEFAULT_BASE_URL})")
    parser.add_argument("-n", "--num", type=int, default=DEFAULT_NUM_RESULTS, help=f"Number of results (default: {DEFAULT_NUM_RESULTS})")
    parser.add_argument("-c", "--categories", default="general", help="Search categories: general, images, news, videos, it, science, files, social media (default: general)")
    parser.add_argument("-l", "--language", default="auto", help="Language code: auto, zh, en, ja, etc. (default: auto)")
    parser.add_argument("-t", "--time-range", default="", help="Time range: day, week, month, year (default: none)")
    parser.add_argument("-e", "--engines", default="", help="Comma-separated engine names: google, bing, duckduckgo, wikipedia, etc.")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    query = args.query or args.query_flag
    if not query:
        parser.error("Search query is required")

    result = search(
        query=query,
        base_url=args.base_url,
        categories=args.categories,
        language=args.language,
        time_range=args.time_range,
        num_results=args.num,
        engines=args.engines,
        output_json=args.json,
    )
    print(result)


if __name__ == "__main__":
    main()
