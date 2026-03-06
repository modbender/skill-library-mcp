"""
SearXNG HTTP client. Handles search requests, error handling, rate limiting,
and response parsing. Zero external API keys — all searches route through
your SearXNG instance.
"""

from __future__ import annotations
import time
import logging
import httpx
from typing import Any
from .models import SearchResult

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Synchronous SearXNG API client with retry and rate limiting."""

    def __init__(
        self,
        base_url: str = "http://localhost:8888",
        timeout: float = 30.0,
        max_retries: int = 2,
        rate_limit_delay: float = 0.5,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self._last_request_time = 0.0
        self._client = httpx.Client(
            timeout=timeout,
            verify=verify_ssl,
            headers={"Accept": "application/json"},
            follow_redirects=True,
        )

    def search(
        self,
        query: str,
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        language: str = "auto",
        pageno: int = 1,
        time_range: str = "",
        safesearch: int = 0,
    ) -> dict[str, Any]:
        """Execute a single search query against SearXNG.

        Returns the full JSON response dict including results, suggestions,
        corrections, infoboxes, and unresponsive_engines.
        """
        self._rate_limit()

        params: dict[str, Any] = {
            "q": query,
            "format": "json",
            "pageno": pageno,
            "safesearch": safesearch,
        }
        if engines:
            params["engines"] = ",".join(engines)
        if categories:
            params["categories"] = ",".join(categories)
        if language and language != "auto":
            params["language"] = language
        if time_range:
            params["time_range"] = time_range

        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.get(f"{self.base_url}/search", params=params)
                resp.raise_for_status()
                data = resp.json()
                logger.debug(
                    f"Search '{query}' returned {len(data.get('results', []))} results"
                )
                return data
            except httpx.TimeoutException:
                logger.warning(f"Timeout on attempt {attempt+1} for query: {query}")
                if attempt == self.max_retries:
                    return self._empty_response(query, "Timeout")
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP {e.response.status_code} for query: {query}")
                if e.response.status_code == 429:
                    time.sleep(self.rate_limit_delay * (attempt + 2))
                    continue
                if attempt == self.max_retries:
                    return self._empty_response(query, f"HTTP {e.response.status_code}")
            except Exception as e:
                logger.error(f"Error searching '{query}': {e}")
                if attempt == self.max_retries:
                    return self._empty_response(query, str(e))

        return self._empty_response(query, "Max retries exceeded")

    def search_batch(
        self,
        queries: list[str],
        engines: list[str] | None = None,
        categories: list[str] | None = None,
        time_range: str = "",
    ) -> list[dict[str, Any]]:
        """Execute multiple search queries sequentially."""
        results = []
        for q in queries:
            results.append(
                self.search(
                    q,
                    engines=engines,
                    categories=categories,
                    time_range=time_range,
                )
            )
        return results

    def parse_results(self, raw_response: dict[str, Any]) -> list[SearchResult]:
        """Convert raw SearXNG JSON response to SearchResult objects."""
        results = []
        for item in raw_response.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                engines=item.get("engines", []),
                score=float(item.get("score", 0.0)),
                category=item.get("category", "general"),
                positions=item.get("positions", []),
                metadata={
                    "template": item.get("template", ""),
                    "parsed_url": item.get("parsed_url", []),
                    "publishedDate": item.get("publishedDate", ""),
                    "thumbnail": item.get("thumbnail", ""),
                    "img_src": item.get("img_src", ""),
                },
            ))
        return results

    def get_suggestions(self, raw_response: dict[str, Any]) -> list[str]:
        return raw_response.get("suggestions", [])

    def get_corrections(self, raw_response: dict[str, Any]) -> list[str]:
        return raw_response.get("corrections", [])

    def get_unresponsive(self, raw_response: dict[str, Any]) -> list[str]:
        return raw_response.get("unresponsive_engines", [])

    def health_check(self) -> bool:
        """Check if the SearXNG instance is reachable."""
        try:
            resp = self._client.get(f"{self.base_url}/healthz", timeout=5.0)
            return resp.status_code == 200
        except Exception:
            try:
                resp = self._client.get(
                    f"{self.base_url}/search",
                    params={"q": "test", "format": "json"},
                    timeout=5.0,
                )
                return resp.status_code == 200
            except Exception:
                return False

    def _rate_limit(self):
        elapsed = time.time() - self._last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self._last_request_time = time.time()

    @staticmethod
    def _empty_response(query: str, error: str) -> dict[str, Any]:
        return {
            "query": query,
            "number_of_results": 0,
            "results": [],
            "answers": [],
            "corrections": [],
            "infoboxes": [],
            "suggestions": [],
            "unresponsive_engines": [],
            "_error": error,
        }

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()