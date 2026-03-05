#!/usr/bin/env python3
"""
DuckDuckGo Web Search
Privacy-focused search using DuckDuckGo API and HTML scraping.
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Dict, Optional
import urllib.parse


class DuckDuckGoSearcher:
    """DuckDuckGo search client with privacy focus."""

    def __init__(self, user_agent: Optional[str] = None):
        """Initialize searcher with optional custom user agent."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.base_url = "https://duckduckgo.com/html/"
        self.json_api_url = "https://api.duckduckgo.com/"

    def search(self, query: str, max_results: int = 10, delay: float = 1.0) -> List[Dict]:
        """
        Perform web search and return parsed results.

        Args:
            query: Search query string
            max_results: Maximum number of results to return
            delay: Delay before search (rate limiting)

        Returns:
            List of result dictionaries with 'title', 'url', 'snippet'
        """
        if delay > 0:
            time.sleep(delay)

        params = {"q": query}
        response = self.session.post(self.base_url, data=params)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        for link in soup.find_all("a", class_="result__a")[:max_results]:
            parent = link.find_parent("div", class_="result__body")

            # Extract title
            title = link.get_text(strip=True)

            # Extract URL (may be DuckDuckGo redirect)
            url = link.get("href", "")
            url = self._clean_ddg_url(url)

            # Extract snippet
            snippet = ""
            if parent:
                snippet_elem = parent.find("a", class_="result__snippet")
                if snippet_elem:
                    snippet = snippet_elem.get_text(strip=True)

            results.append({
                "title": title,
                "url": url,
                "snippet": snippet
            })

        return results

    def search_json(self, query: str, max_results: int = 10, delay: float = 1.0) -> Dict:
        """
        Search using DuckDuckGo JSON API (instant answers).

        Args:
            query: Search query
            max_results: Max related topics to return
            delay: Delay before search

        Returns:
            Dictionary with instant answer and related topics
        """
        if delay > 0:
            time.sleep(delay)

        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 0
        }

        response = self.session.get(self.json_api_url, params=params)
        response.raise_for_status()

        data = response.json()

        return {
            "abstract": data.get("Abstract", ""),
            "abstract_source": data.get("AbstractSource", ""),
            "abstract_url": data.get("AbstractURL", ""),
            "definition": data.get("Definition", ""),
            "answer": data.get("Answer", ""),
            "answer_type": data.get("AnswerType", ""),
            "related_topics": [
                {
                    "text": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                }
                for topic in (data.get("RelatedTopics", []) or [])
                if isinstance(topic, dict) and topic.get("Text")
            ][:max_results]
        }

    def search_images(self, query: str, max_results: int = 10, delay: float = 1.0) -> List[Dict]:
        """
        Search for images.

        Args:
            query: Search query
            max_results: Max images to return
            delay: Delay before search

        Returns:
            List of image results with title, url, thumbnail, source
        """
        if delay > 0:
            time.sleep(delay)

        # First get VQD token
        vqd_url = "https://duckduckgo.com/html/"
        params = {"q": query}
        response = self.session.get(vqd_url, params=params)

        vqd_match = re.search(r'vqd="([^"]+)"', response.text)
        vqd = vqd_match.group(1) if vqd_match else ""

        # Now search images
        image_url = "https://duckduckgo.com/i.js"
        params = {
            "q": query,
            "o": "json",
            "vqd": vqd,
            "f": ",,,",
            "p": "1"
        }

        response = self.session.get(image_url, params=params)
        response.raise_for_status()

        data = response.json()
        results = []

        for result in (data.get("results", []) or [])[:max_results]:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("image", ""),
                "thumbnail": result.get("thumbnail", ""),
                "source": result.get("source", ""),
                "width": result.get("width", 0),
                "height": result.get("height", 0)
            })

        return results

    def _clean_ddg_url(self, url: str) -> str:
        """
        Remove DuckDuckGo redirect wrapper from URLs.

        Args:
            url: DuckDuckGo wrapped URL

        Returns:
            Clean URL
        """
        # Pattern for DDG redirect URLs
        ddg_pattern = r"https://l\.duckduckgo\.com/l/\?uddg=[^&]*&(?:ru|u)=([^&]+)"
        match = re.search(ddg_pattern, url)

        if match:
            # URL decode the actual URL
            actual_url = urllib.parse.unquote(match.group(1))
            return actual_url

        # If no redirect, return as-is
        return url


def search(query: str, max_results: int = 10, mode: str = "web") -> List[Dict]:
    """
    Simple search function.

    Args:
        query: Search query
        max_results: Maximum results
        mode: 'web', 'images', or 'json'

    Returns:
        Search results as list or dict
    """
    searcher = DuckDuckGoSearcher()

    if mode == "images":
        return searcher.search_images(query, max_results)
    elif mode == "json":
        return searcher.search_json(query, max_results)
    else:
        return searcher.search(query, max_results)


def format_markdown(results: List[Dict], query: str) -> str:
    """
    Format search results as Markdown.

    Args:
        results: List of search result dicts
        query: Original search query

    Returns:
        Markdown formatted string
    """
    output = f"# Search Results: {query}\n\n"
    output += f"Found {len(results)} results\n\n"
    output += "---\n\n"

    for i, result in enumerate(results, 1):
        title = result.get("title", "Untitled")
        url = result.get("url", "N/A")
        snippet = result.get("snippet", result.get("text", ""))

        output += f"## {i}. {title}\n\n"
        output += f"**URL:** {url}\n\n"

        if snippet:
            output += f"{snippet}\n\n"

        output += "---\n\n"

    return output


def main():
    """CLI interface for testing."""
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="DuckDuckGo web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--num", type=int, default=10, help="Number of results")
    parser.add_argument("-m", "--mode", choices=["web", "images", "json"], default="web", help="Search mode")
    parser.add_argument("-f", "--format", choices=["text", "json", "md"], default="md", help="Output format")

    args = parser.parse_args()

    try:
        results = search(args.query, max_results=args.num, mode=args.mode)

        if args.format == "md":
            print(format_markdown(results if isinstance(results, list) else results.get("related_topics", []), args.query))
        elif args.format == "json":
            import json
            output = {"query": args.query, "results": results}
            print(json.dumps(output, indent=2))
        else:
            # Text format
            for i, result in enumerate(results if isinstance(results, list) else results.get("related_topics", []), 1):
                print(f"{i}. {result.get('title', result.get('text', ''))}")
                print(f"   {result.get('url', '')}")
                if result.get("snippet"):
                    print(f"   {result.get('snippet')}")
                print()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
