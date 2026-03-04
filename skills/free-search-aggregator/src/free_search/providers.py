"""Search provider implementations with a unified output contract."""

from __future__ import annotations

import logging
import time
import warnings
from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 12
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/122.0 Safari/537.36"
)
MAX_RESPONSE_BYTES = 5 * 1024 * 1024  # 5 MB guard against runaway responses


class ProviderError(Exception):
    """Base class for provider failures."""


class AuthError(ProviderError):
    """Raised when provider credentials are missing or rejected."""


class NetworkError(ProviderError):
    """Raised when upstream networking fails."""


class RateLimitError(ProviderError):
    """Raised when provider reports rate limiting."""


class QuotaExceededError(ProviderError):
    """Raised when provider quota has been exhausted."""


class ParseError(ProviderError):
    """Raised when an upstream response cannot be parsed safely."""


class UpstreamError(ProviderError):
    """Raised for non-recoverable upstream API errors."""


@dataclass(slots=True)
class SearchItem:
    """Unified search result item."""

    title: str
    url: str
    snippet: str
    source: str
    rank: int


class BaseProvider:
    """Base provider contract for search services."""

    name = "base"

    def __init__(
        self,
        *,
        config: dict[str, Any],
        session: requests.Session | None = None,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()
        self.enabled = bool(config.get("enabled", True))
        self.timeout = int(config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
        self.min_interval_seconds = float(config.get("min_interval_seconds", 0.0))
        self._last_request_ts = 0.0

    def is_enabled(self) -> bool:
        return self.enabled

    def maybe_sleep_for_rate_limit(self) -> float:
        if self.min_interval_seconds <= 0:
            return 0.0
        now = time.time()
        elapsed = now - self._last_request_ts
        remaining = self.min_interval_seconds - elapsed
        if remaining > 0:
            logger.debug("Provider %s sleeping %.2fs for pacing", self.name, remaining)
            time.sleep(remaining)
            return remaining
        return 0.0

    def _mark_request(self) -> None:
        self._last_request_ts = time.time()

    @staticmethod
    def _http_error_detail(response: requests.Response) -> str:
        try:
            payload = response.json()
            if isinstance(payload, dict):
                for key in ("error", "message", "detail"):
                    value = payload.get(key)
                    if value:
                        return str(value)
        except ValueError:
            pass
        text = (response.text or "").strip()
        if text:
            return text[:180]
        return ""

    @staticmethod
    def _guard_response_size(response: requests.Response) -> None:
        """Raise ParseError if the response body exceeds MAX_RESPONSE_BYTES."""
        cl = response.headers.get("content-length")
        if cl:
            try:
                if int(cl) > MAX_RESPONSE_BYTES:
                    raise ParseError(
                        f"Response content-length {cl} bytes exceeds {MAX_RESPONSE_BYTES} limit"
                    )
            except ValueError:
                pass
        if len(response.content) > MAX_RESPONSE_BYTES:
            raise ParseError(
                f"Response body {len(response.content)} bytes exceeds {MAX_RESPONSE_BYTES} limit"
            )

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        raise NotImplementedError


class BraveProvider(BaseProvider):
    name = "brave"
    endpoint = "https://api.search.brave.com/res/v1/web/search"

    @staticmethod
    def _api_key_candidates(api_key: str) -> list[str]:
        key = api_key.strip()
        if not key:
            return []
        candidates = [key]
        if key.startswith("BSA"):
            candidates.append(f"BSa{key[3:]}")
        elif key.startswith("BSa"):
            candidates.append(f"BSA{key[3:]}")
        deduped: list[str] = []
        for candidate in candidates:
            if candidate not in deduped:
                deduped.append(candidate)
        return deduped

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("Brave API key missing")

        self.maybe_sleep_for_rate_limit()
        params = {"q": query, "count": max_results}
        key_candidates = self._api_key_candidates(api_key)
        if not key_candidates:
            raise AuthError("Brave API key missing")

        response: requests.Response | None = None
        for index, candidate in enumerate(key_candidates):
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": candidate,
            }
            logger.debug(
                "Brave request: query=%r max_results=%s attempt=%s",
                query,
                max_results,
                index + 1,
            )
            try:
                response = self.session.get(
                    self.endpoint,
                    params=params,
                    headers=headers,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise NetworkError(f"Brave request failed: {exc}") from exc
            finally:
                self._mark_request()

            if response.status_code not in (401, 403):
                break
            if index + 1 < len(key_candidates):
                logger.warning(
                    "Brave auth failed with current key format; retrying with alternate prefix"
                )

        if response is None:
            raise UpstreamError("Brave request did not receive a response")

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Brave auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Brave rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Brave server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Brave request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Brave returned non-JSON response") from exc

        web = payload.get("web", {})
        raw_results = web.get("results", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("url") or "").strip()
            snippet = (row.get("description") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Brave returned %s results for query=%r", len(items), query)
        return items


class TavilyProvider(BaseProvider):
    name = "tavily"
    endpoint = "https://api.tavily.com/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("Tavily API key missing")

        self.maybe_sleep_for_rate_limit()
        body = {
            "api_key": api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": False,
            "search_depth": self.config.get("search_depth", "basic"),
        }

        try:
            logger.debug("Tavily request: query=%r max_results=%s", query, max_results)
            response = self.session.post(self.endpoint, json=body, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Tavily request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Tavily auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Tavily rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Tavily server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Tavily request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Tavily returned non-JSON response") from exc

        raw_results = payload.get("results", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("url") or "").strip()
            snippet = (row.get("content") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Tavily returned %s results for query=%r", len(items), query)
        return items


class DuckDuckGoProvider(BaseProvider):
    name = "duckduckgo"
    endpoint = "https://duckduckgo.com/html/"

    @staticmethod
    def _extract_target_url(href: str) -> str:
        raw_href = href.strip()
        if not raw_href:
            return ""
        if raw_href.startswith("//"):
            raw_href = f"https:{raw_href}"

        parsed = urlparse(raw_href)
        if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
            target = parse_qs(parsed.query).get("uddg", [""])[0]
            if target:
                return unquote(target).strip()
        return raw_href

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        self.maybe_sleep_for_rate_limit()
        params = {"q": query}
        headers = {"User-Agent": DEFAULT_USER_AGENT}

        try:
            logger.debug("DuckDuckGo HTML request: query=%r max_results=%s", query, max_results)
            response = self.session.get(
                self.endpoint, params=params, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise NetworkError(f"DuckDuckGo request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("DuckDuckGo rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"DuckDuckGo server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"DuckDuckGo request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        soup = BeautifulSoup(response.text, "html.parser")
        node_selectors = (
            "div.result",
            "article[data-testid='result']",
            "li[data-layout='organic']",
            "div.results_links",
        )
        nodes: list[Any] = []
        for selector in node_selectors:
            nodes.extend(soup.select(selector))

        items: list[SearchItem] = []
        seen_urls: set[str] = set()
        rank = 0
        for node in nodes:
            link = (
                node.select_one("a.result__a")
                or node.select_one("a[data-testid='result-title-a']")
                or node.select_one("h2 a[href]")
            )
            if not link:
                continue
            href = self._extract_target_url(link.get("href") or "")
            title = link.get_text(" ", strip=True)
            snippet_node = (
                node.select_one("a.result__snippet")
                or node.select_one(".result__snippet")
                or node.select_one("[data-result='snippet']")
                or node.select_one("[data-testid='result-snippet']")
            )
            snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""
            if not (title and href) or href in seen_urls:
                continue
            seen_urls.add(href)
            rank += 1
            items.append(
                SearchItem(title=title, url=href, snippet=snippet, source=self.name, rank=rank)
            )
            if rank >= max_results:
                break

        # Return empty list (not an error) — router will continue to next provider
        if not items:
            logger.info("DuckDuckGo HTML returned no results for query=%r", query)
        else:
            logger.info("DuckDuckGo HTML returned %s results for query=%r", len(items), query)
        return items


class SerperProvider(BaseProvider):
    name = "serper"
    endpoint = "https://google.serper.dev/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("Serper API key missing")

        self.maybe_sleep_for_rate_limit()
        headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
        body = {"q": query, "num": max_results}

        try:
            logger.debug("Serper request: query=%r max_results=%s", query, max_results)
            response = self.session.post(
                self.endpoint, headers=headers, json=body, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise NetworkError(f"Serper request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Serper auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Serper rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Serper server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Serper request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Serper returned non-JSON response") from exc

        raw_results = payload.get("organic", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("link") or "").strip()
            snippet = (row.get("snippet") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Serper returned %s results for query=%r", len(items), query)
        return items


class SearchApiProvider(BaseProvider):
    name = "searchapi"
    endpoint = "https://www.searchapi.io/api/v1/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("SearchApi API key missing")

        self.maybe_sleep_for_rate_limit()
        params = {
            "engine": self.config.get("engine", "google"),
            "q": query,
            "num": max_results,
        }
        # Use Bearer token header only — avoids leaking key in query string / server logs
        headers = {"Authorization": f"Bearer {api_key}"}

        try:
            logger.debug("SearchApi request: query=%r max_results=%s", query, max_results)
            response = self.session.get(
                self.endpoint, params=params, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise NetworkError(f"SearchApi request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"SearchApi auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("SearchApi rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"SearchApi server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"SearchApi request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("SearchApi returned non-JSON response") from exc

        raw_results = payload.get("organic_results", []) or payload.get("results", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("link") or row.get("url") or "").strip()
            snippet = (row.get("snippet") or row.get("description") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("SearchApi returned %s results for query=%r", len(items), query)
        return items


class DuckDuckGoInstantProvider(BaseProvider):
    name = "duckduckgo_instant"
    endpoint = "https://api.duckduckgo.com/"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        self.maybe_sleep_for_rate_limit()
        params = {"q": query, "format": "json", "no_redirect": 1, "no_html": 1}
        headers = {"User-Agent": DEFAULT_USER_AGENT}

        try:
            logger.debug(
                "DuckDuckGo Instant request: query=%r max_results=%s", query, max_results
            )
            response = self.session.get(
                self.endpoint, params=params, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise NetworkError(f"DuckDuckGo Instant request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("DuckDuckGo Instant rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"DuckDuckGo Instant server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"DuckDuckGo Instant request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("DuckDuckGo Instant returned non-JSON response") from exc

        flattened: list[tuple[str, str]] = []
        abstract_text = (payload.get("AbstractText") or "").strip()
        abstract_url = (payload.get("AbstractURL") or "").strip()
        if abstract_text and abstract_url:
            flattened.append((abstract_text, abstract_url))

        def _collect(rows: list[dict[str, Any]]) -> None:
            for row in rows:
                if "Topics" in row and isinstance(row.get("Topics"), list):
                    _collect(row["Topics"])
                    continue
                text = (row.get("Text") or "").strip()
                url = (row.get("FirstURL") or "").strip()
                if text and url:
                    flattened.append((text, url))

        _collect(payload.get("Results", []))
        _collect(payload.get("RelatedTopics", []))

        items: list[SearchItem] = []
        seen_urls: set[str] = set()
        for text, url in flattened:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            title = text.split(" - ", 1)[0].strip() or text[:80]
            items.append(
                SearchItem(
                    title=title, url=url, snippet=text, source=self.name, rank=len(items) + 1
                )
            )
            if len(items) >= max_results:
                break

        logger.info("DuckDuckGo Instant returned %s results for query=%r", len(items), query)
        return items


class BingRSSProvider(BaseProvider):
    """Bing web search via RSS feed — no API key required, uses Bing's XML endpoint.

    This avoids JavaScript/bot-detection issues of HTML scraping by consuming
    Bing's built-in RSS output (format=rss), which returns clean XML with direct URLs.
    """

    name = "bing_html"   # Kept as "bing_html" for backwards-compatibility in configs
    endpoint = "https://www.bing.com/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        self.maybe_sleep_for_rate_limit()
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "application/rss+xml,application/xml,text/xml,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        params = {"q": query, "format": "rss", "count": max_results}

        try:
            logger.debug("Bing RSS request: query=%r max_results=%s", query, max_results)
            response = self.session.get(
                self.endpoint, params=params, headers=headers, timeout=self.timeout
            )
        except requests.RequestException as exc:
            raise NetworkError(f"Bing RSS request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("Bing rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Bing server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"Bing request rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as exc:
            raise ParseError(f"Bing RSS returned unparseable XML: {exc}") from exc

        channel = root.find("channel")
        raw_items = channel.findall("item") if channel is not None else root.findall(".//item")

        items: list[SearchItem] = []
        seen_urls: set[str] = set()
        for idx, item in enumerate(raw_items[:max_results], start=1):
            title = (item.findtext("title") or "").strip()
            url = (item.findtext("link") or "").strip()
            snippet = (item.findtext("description") or "").strip()
            # Strip any HTML tags from snippet
            if "<" in snippet:
                snippet = BeautifulSoup(snippet, "html.parser").get_text(" ", strip=True)
            if not (title and url) or url in seen_urls:
                continue
            seen_urls.add(url)
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )

        if not items:
            logger.info("Bing RSS returned no results for query=%r", query)
        else:
            logger.info("Bing RSS returned %s results for query=%r", len(items), query)
        return items


class MojeekProvider(BaseProvider):
    """Mojeek web search — no API key required, independent index (not Google/Bing).

    Mojeek is a privacy-focused search engine with its own web crawler and index.
    Provides a different result set from Google/Bing-based providers.
    HTML scraping of public search results (no API key needed for basic use).
    Optional: use Mojeek's JSON API with MOJEEK_API_KEY for higher limits.
    """

    name = "mojeek"
    endpoint = "https://www.mojeek.com/search"
    api_endpoint = "https://www.mojeek.com/api/v1/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()

        self.maybe_sleep_for_rate_limit()

        if api_key:
            return self._search_api(query, max_results=max_results, api_key=api_key)
        return self._search_html(query, max_results=max_results)

    def _search_api(self, query: str, *, max_results: int, api_key: str) -> list[SearchItem]:
        """Use official Mojeek JSON API (requires MOJEEK_API_KEY)."""
        params = {"q": query, "api_key": api_key, "fmt": "json", "nb": max_results}
        try:
            logger.debug("Mojeek API request: query=%r max_results=%s", query, max_results)
            response = self.session.get(self.api_endpoint, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Mojeek API request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            raise AuthError(f"Mojeek API auth failed: HTTP {response.status_code}")
        if response.status_code == 429:
            raise RateLimitError("Mojeek rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Mojeek server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"Mojeek API rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Mojeek API returned non-JSON") from exc

        raw_results = payload.get("results", payload if isinstance(payload, list) else [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("link") or row.get("url") or "").strip()
            snippet = (row.get("desc") or row.get("snippet") or "").strip()
            if not (title and url):
                continue
            items.append(SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx))
        logger.info("Mojeek API returned %s results for query=%r", len(items), query)
        return items

    def _search_html(self, query: str, *, max_results: int) -> list[SearchItem]:
        """Fallback: scrape Mojeek HTML search results."""
        headers = {
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        params = {"q": query, "nb": max_results}
        try:
            logger.debug("Mojeek HTML request: query=%r max_results=%s", query, max_results)
            response = self.session.get(self.endpoint, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Mojeek HTML request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("Mojeek rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Mojeek server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"Mojeek request rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        soup = BeautifulSoup(response.text, "html.parser")

        items: list[SearchItem] = []
        seen_urls: set[str] = set()
        rank = 0
        for li in soup.select("ul.results-standard li"):
            # Title and URL from h2 > a.title
            h2 = li.select_one("h2 a.title") or li.select_one("h2 a[href]")
            if not h2:
                continue
            title = h2.get_text(" ", strip=True)
            url = (h2.get("href") or "").strip()
            # Snippet from p.s (Mojeek's description class)
            snippet_node = li.select_one("p.s")
            snippet = snippet_node.get_text(" ", strip=True) if snippet_node else ""
            if not (title and url) or not url.startswith("http") or url in seen_urls:
                continue
            seen_urls.add(url)
            rank += 1
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=rank)
            )
            if rank >= max_results:
                break

        if not items:
            logger.info("Mojeek HTML returned no results for query=%r", query)
        else:
            logger.info("Mojeek HTML returned %s results for query=%r", len(items), query)
        return items


class SearXNGProvider(BaseProvider):
    """SearXNG meta-search (self-hosted or private instance only) — no API key required.

    Public instances are typically rate-limited for server-to-server requests.
    Configure your own self-hosted instance via the `endpoint` config key.
    See: https://searxng.github.io/searxng/
    """

    name = "searxng"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        base = (self.config.get("endpoint") or "").rstrip("/")
        if not base:
            raise AuthError("SearXNG endpoint not configured (set searxng.endpoint in providers.yaml)")

        url = f"{base}/search"
        categories = self.config.get("categories", "general")

        self.maybe_sleep_for_rate_limit()
        params = {"q": query, "format": "json", "categories": categories}
        headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": "application/json"}

        try:
            logger.debug("SearXNG request: endpoint=%s query=%r", base, query)
            response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"SearXNG request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("SearXNG rate limited")
        if response.status_code in (403, 401):
            raise UpstreamError(f"SearXNG returned {response.status_code} — JSON API may be disabled on this instance")
        if response.status_code >= 500:
            raise UpstreamError(f"SearXNG server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"SearXNG request rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("SearXNG returned non-JSON (enable format=json on your instance)") from exc

        raw_results = payload.get("results", [])
        items: list[SearchItem] = []
        seen_urls: set[str] = set()
        rank = 0
        for row in raw_results:
            title = (row.get("title") or "").strip()
            url_ = (row.get("url") or "").strip()
            snippet = (row.get("content") or "").strip()
            if not (title and url_) or url_ in seen_urls:
                continue
            seen_urls.add(url_)
            rank += 1
            items.append(
                SearchItem(title=title, url=url_, snippet=snippet, source=self.name, rank=rank)
            )
            if rank >= max_results:
                break

        if not items:
            logger.info("SearXNG returned no results for query=%r (endpoint=%s)", query, base)
        else:
            logger.info("SearXNG returned %s results for query=%r", len(items), query)
        return items


class WikipediaProvider(BaseProvider):
    """Wikipedia Search API — completely free, no API key, great for factual queries."""

    name = "wikipedia"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        lang = self.config.get("lang", "en")
        endpoint = f"https://{lang}.wikipedia.org/w/api.php"

        self.maybe_sleep_for_rate_limit()
        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results,
            "format": "json",
            "srprop": "snippet|titlesnippet",
            "utf8": 1,
        }
        headers = {"User-Agent": DEFAULT_USER_AGENT}

        try:
            logger.debug("Wikipedia request: query=%r max_results=%s lang=%s", query, max_results, lang)
            response = self.session.get(endpoint, params=params, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Wikipedia request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code == 429:
            raise RateLimitError("Wikipedia rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Wikipedia server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"Wikipedia request rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Wikipedia returned non-JSON response") from exc

        search_results = payload.get("query", {}).get("search", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(search_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            if not title:
                continue
            # Strip HTML tags from snippet
            raw_snippet = row.get("snippet") or ""
            snippet = BeautifulSoup(raw_snippet, "html.parser").get_text(" ", strip=True)
            page_url = f"https://{lang}.wikipedia.org/wiki/{title.replace(' ', '_')}"
            items.append(
                SearchItem(title=title, url=page_url, snippet=snippet, source=self.name, rank=idx)
            )

        if not items:
            logger.info("Wikipedia returned no results for query=%r", query)
        else:
            logger.info("Wikipedia returned %s results for query=%r", len(items), query)
        return items


class GoogleCSEProvider(BaseProvider):
    """Google Custom Search JSON API — 100 queries/day free tier. Requires GOOGLE_API_KEY + GOOGLE_CX."""

    name = "google_cse"
    endpoint = "https://www.googleapis.com/customsearch/v1"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        cx = (self.config.get("cx") or "").strip()
        if not api_key:
            raise AuthError("Google CSE API key (GOOGLE_API_KEY) missing")
        if not cx:
            raise AuthError("Google CSE search engine ID (GOOGLE_CX) missing")

        # Google CSE returns at most 10 results per request
        num = min(max_results, 10)

        self.maybe_sleep_for_rate_limit()
        params = {"key": api_key, "cx": cx, "q": query, "num": num}

        try:
            logger.debug("Google CSE request: query=%r num=%s", query, num)
            response = self.session.get(self.endpoint, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Google CSE request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Google CSE auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Google CSE rate limited (daily quota likely exhausted)")
        if response.status_code >= 500:
            raise UpstreamError(f"Google CSE server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Google CSE request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Google CSE returned non-JSON response") from exc

        raw_results = payload.get("items", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("link") or "").strip()
            snippet = (row.get("snippet") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Google CSE returned %s results for query=%r", len(items), query)
        return items


class ExaProvider(BaseProvider):
    """Exa.ai neural/keyword search — 1000 searches/month free tier. Requires EXA_API_KEY."""

    name = "exa"
    endpoint = "https://api.exa.ai/search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("Exa API key missing")

        self.maybe_sleep_for_rate_limit()
        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        body: dict[str, Any] = {
            "query": query,
            "numResults": max_results,
            "type": self.config.get("search_type", "auto"),
        }
        # Optionally include text snippets
        if self.config.get("include_text", True):
            body["contents"] = {"text": {"maxCharacters": 500}}

        try:
            logger.debug("Exa request: query=%r max_results=%s type=%s", query, max_results, body["type"])
            response = self.session.post(self.endpoint, json=body, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Exa request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Exa auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Exa rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Exa server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Exa request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Exa returned non-JSON response") from exc

        raw_results = payload.get("results", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("url") or "").strip()
            # Exa returns content in a nested structure or at top level
            contents = row.get("contents") or {}
            snippet = (
                contents.get("text")
                or row.get("text")
                or row.get("excerpt")
                or row.get("summary")
                or ""
            ).strip()
            if len(snippet) > 500:
                snippet = snippet[:500].rsplit(" ", 1)[0] + "…"
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Exa returned %s results for query=%r", len(items), query)
        return items


class BaiduProvider(BaseProvider):
    """Baidu Qianfan AI Search — good for Chinese-language content. Requires BAIDU_API_KEY."""

    name = "baidu"
    endpoint = "https://qianfan.baidubce.com/v2/ai_search/web_search"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        api_key = (self.config.get("api_key") or "").strip()
        if not api_key:
            raise AuthError("Baidu API key missing")

        self.maybe_sleep_for_rate_limit()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Appbuilder-From": "openclaw",
            "Content-Type": "application/json",
        }
        top_k = max(max_results, 5)
        body = {
            "messages": [{"content": query, "role": "user"}],
            "edition": self.config.get("edition", "standard"),
            "search_source": "baidu_search_v2",
            "resource_type_filter": [{"type": "web", "top_k": top_k}],
            "search_recency_filter": self.config.get("search_recency_filter", "year"),
            "safe_search": False,
        }

        try:
            logger.debug("Baidu request: query=%r max_results=%s", query, max_results)
            response = self.session.post(self.endpoint, json=body, headers=headers, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"Baidu request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            detail = self._http_error_detail(response)
            raise AuthError(
                f"Baidu auth failed: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )
        if response.status_code == 429:
            raise RateLimitError("Baidu rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"Baidu server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            detail = self._http_error_detail(response)
            raise UpstreamError(
                f"Baidu request rejected: HTTP {response.status_code}"
                + (f" ({detail})" if detail else "")
            )

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("Baidu returned non-JSON response") from exc

        if isinstance(payload, dict) and "code" in payload:
            raise UpstreamError(f"Baidu API error: {payload.get('message', 'unknown error')}")

        raw_results = payload.get("references", [])
        items: list[SearchItem] = []
        for idx, row in enumerate(raw_results[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("url") or "").strip()
            snippet = (
                row.get("content") or row.get("abstract") or row.get("site_name") or ""
            ).strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        logger.info("Baidu returned %s results for query=%r", len(items), query)
        return items


class YaCyProvider(BaseProvider):
    name = "yacy"
    endpoint = "http://localhost:8090/yacysearch.json"

    def search(self, query: str, *, max_results: int) -> list[SearchItem]:
        endpoint = self.config.get("endpoint") or self.endpoint

        self.maybe_sleep_for_rate_limit()
        params = {
            "query": query,
            "maximumRecords": max_results,
            "startRecord": 0,
            "resource": self.config.get("resource", "global"),
        }

        try:
            response = self.session.get(endpoint, params=params, timeout=self.timeout)
        except requests.RequestException as exc:
            raise NetworkError(f"YaCy request failed: {exc}") from exc
        finally:
            self._mark_request()

        if response.status_code in (401, 403):
            raise AuthError(f"YaCy auth failed: HTTP {response.status_code}")
        if response.status_code == 429:
            raise RateLimitError("YaCy rate limited")
        if response.status_code >= 500:
            raise UpstreamError(f"YaCy server error: HTTP {response.status_code}")
        if response.status_code >= 400:
            raise UpstreamError(f"YaCy request rejected: HTTP {response.status_code}")

        self._guard_response_size(response)
        try:
            payload = response.json()
        except ValueError as exc:
            raise ParseError("YaCy returned non-JSON response") from exc

        raw_items: list[dict[str, Any]] = []
        channels = payload.get("channels")
        if isinstance(channels, list):
            for channel in channels:
                if isinstance(channel, dict) and isinstance(channel.get("items"), list):
                    raw_items.extend(channel["items"])
        if not raw_items and isinstance(payload.get("items"), list):
            raw_items = payload["items"]

        items: list[SearchItem] = []
        for idx, row in enumerate(raw_items[:max_results], start=1):
            title = (row.get("title") or "").strip()
            url = (row.get("link") or row.get("url") or "").strip()
            snippet = (row.get("description") or row.get("snippet") or "").strip()
            if not (title and url):
                continue
            items.append(
                SearchItem(title=title, url=url, snippet=snippet, source=self.name, rank=idx)
            )
        return items


PROVIDER_REGISTRY = {
    BraveProvider.name: BraveProvider,
    TavilyProvider.name: TavilyProvider,
    DuckDuckGoProvider.name: DuckDuckGoProvider,
    DuckDuckGoInstantProvider.name: DuckDuckGoInstantProvider,
    SearchApiProvider.name: SearchApiProvider,
    YaCyProvider.name: YaCyProvider,
    SerperProvider.name: SerperProvider,
    BingRSSProvider.name: BingRSSProvider,
    MojeekProvider.name: MojeekProvider,
    SearXNGProvider.name: SearXNGProvider,
    WikipediaProvider.name: WikipediaProvider,
    GoogleCSEProvider.name: GoogleCSEProvider,
    ExaProvider.name: ExaProvider,
    BaiduProvider.name: BaiduProvider,
}
