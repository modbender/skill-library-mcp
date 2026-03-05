#!/usr/bin/env python3
"""
swarm_search.py
-----------------

This script powers the `ok-computer-swarm` skill.  It accepts one or more search
queries and performs concurrent DuckDuckGo searches for each query.  Results are
returned as a JSON array, where each entry contains the original query and the
top search results (title and URL).  Concurrency is implemented using
ThreadPoolExecutor to parallelise network requests, which speeds up research on
multiple topics.

Usage:

    python swarm_search.py --query "Agent Swarm" --query "OpenClaw skills"

Dependencies:

    - requests (install via pip or see requirements.txt)

The script prints the JSON report to stdout.  If an error occurs for a given
query, the corresponding entry will include an "error" field with details.
"""

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any
from urllib.parse import quote_plus

import requests


DUCKDUCKGO_API = "https://api.duckduckgo.com/"


def search_duckduckgo(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Perform a DuckDuckGo search and return a dictionary with results.

    DuckDuckGo's free API returns a JSON object containing a `RelatedTopics`
    field, which may include nested topics.  This function extracts up to
    `max_results` items with both a title and a URL.  If the API call fails or
    returns no usable data, the returned dict includes an `error` field.

    Args:
        query: The search phrase.
        max_results: Maximum number of results to include.

    Returns:
        A dict with the keys:
            - query: the original query string.
            - results: list of {title, url} objects, if successful.
            - error: error message, if any occurred.
    """
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1,
    }
    try:
        response = requests.get(DUCKDUCKGO_API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:
        return {"query": query, "results": [], "error": f"Request failed: {exc}"}

    results: List[Dict[str, str]] = []
    # The API may return a list of topics or nested lists.  Flatten and extract.
    topics = data.get("RelatedTopics", [])
    # Flatten nested topics
    flat_topics = []
    for item in topics:
        if isinstance(item.get("Topics"), list):
            flat_topics.extend(item["Topics"])
        else:
            flat_topics.append(item)

    for item in flat_topics:
        text = item.get("Text")
        url = item.get("FirstURL")
        if text and url:
            results.append({"title": text, "url": url})
        if len(results) >= max_results:
            break

    return {"query": query, "results": results}


def perform_concurrent_searches(queries: List[str], max_results: int = 5) -> List[Dict[str, Any]]:
    """Execute searches concurrently using a thread pool.

    Args:
        queries: List of search terms.
        max_results: Maximum results per query.

    Returns:
        A list of result dictionaries in the same order as the input queries.
    """
    results: List[Dict[str, Any]] = [None] * len(queries)
    with ThreadPoolExecutor(max_workers=min(len(queries), 8)) as executor:
        future_to_index = {
            executor.submit(search_duckduckgo, q, max_results): idx
            for idx, q in enumerate(queries)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                results[idx] = future.result()
            except Exception as exc:
                results[idx] = {"query": queries[idx], "results": [], "error": str(exc)}
    return results


def parse_args(argv: List[str]) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run concurrent DuckDuckGo searches.")
    parser.add_argument(
        "--query",
        action="append",
        dest="queries",
        required=True,
        help="Search query.  Repeat this option to search multiple topics.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Maximum number of results to return per query (default: 5).",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    queries = [q.strip() for q in args.queries if q.strip()]
    if not queries:
        print(json.dumps({"error": "No queries provided"}, indent=2))
        return 1

    results = perform_concurrent_searches(queries, max_results=args.max_results)
    # Print JSON to stdout
    json.dump(results, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
