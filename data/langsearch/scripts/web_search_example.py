#!/usr/bin/env python3
"""
LangSearch Web Search API Example with Error Handling

This script demonstrates how to use the LangSearch web search API
with proper error handling and result processing.

Usage:
    export LANGSEARCH_API_KEY="your-api-key"
    python3 web_search_example.py "your search query"
"""

import requests
import json
import os
import sys
import time
from typing import Optional, Dict, List


def search_web(
    query: str,
    count: int = 10,
    include_summary: bool = True,
    freshness: Optional[str] = None,
    max_retries: int = 3
) -> Optional[List[Dict]]:
    """
    Perform a web search using LangSearch API.

    Args:
        query: The search query
        count: Number of results to return (1-100)
        include_summary: Include markdown summaries in results
        freshness: Filter by freshness (day, week, month, year)
        max_retries: Maximum number of retry attempts

    Returns:
        List of search results or None if failed
    """
    api_key = os.getenv("LANGSEARCH_API_KEY")
    if not api_key:
        print("Error: LANGSEARCH_API_KEY environment variable not set")
        print("Get a free API key at https://langsearch.com/api-keys")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "count": min(count, 100),  # Cap at API limit
        "summary": include_summary
    }

    if freshness:
        payload["freshness"] = freshness

    url = "https://api.langsearch.com/v1/web-search"

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print("Error: Unauthorized. Check your API key.")
                return None
            elif response.status_code == 429:
                # Rate limited - exponential backoff
                wait_time = 2 ** attempt
                print(f"Rate limited. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                continue
            elif response.status_code >= 500:
                # Server error - retry
                wait_time = 2 ** attempt
                print(f"Server error (HTTP {response.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
                continue
            else:
                print(f"Error: HTTP {response.status_code}")
                print(response.text)
                return None

        except requests.exceptions.Timeout:
            print("Error: Request timeout")
            if attempt < max_retries - 1:
                print(f"Retrying... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2 ** attempt)
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    print("Error: Max retries exceeded")
    return None


def format_results(results: List[Dict]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found"

    output = []
    for i, result in enumerate(results, 1):
        output.append(f"\n{i}. {result.get('title', 'No title')}")
        output.append(f"   URL: {result.get('url', 'No URL')}")
        if result.get('snippet'):
            output.append(f"   Snippet: {result['snippet'][:200]}...")
        if result.get('summary'):
            output.append(f"   Summary: {result['summary'][:300]}...")

    return "\n".join(output)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 web_search_example.py 'your search query'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}\n")

    results = search_web(query, count=5, include_summary=True)

    if results:
        print(format_results(results))
        print(f"\n\nRaw JSON output:")
        print(json.dumps(results, indent=2))
    else:
        print("Search failed")
