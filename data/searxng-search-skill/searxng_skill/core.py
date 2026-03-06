"""
Core SearXNG skill implementation
"""

import requests
from typing import Dict, List, Optional, Any, Union
from urllib.parse import urljoin

from .models import SearchResult, SearchResponse, EngineInfo
from .enums import SearchCategory, TimeRange, SafeSearch, OutputFormat
from .exceptions import (
    TimeoutException,
    ConnectionException,
    InvalidParameterException,
    InstanceUnavailableException
)
from .retry import RetryStrategy
from .utils import build_search_url, sanitize_query, validate_url
from .config import SearXNGConfig


class SearXNGSkill:
    """Advanced SearXNG Search Skill with comprehensive features"""
    
    def __init__(
        self,
        instance_url: Optional[str] = None,
        config: Optional[SearXNGConfig] = None,
        **kwargs
    ):
        """
        Initialize SearXNG skill
        
        Args:
            instance_url: SearXNG instance URL (overrides config)
            config: SearXNGConfig object
            **kwargs: Additional config parameters
        """
        if config:
            self.config = config
        else:
            self.config = SearXNGConfig(**kwargs)
        
        if instance_url:
            self.config.instance_url = instance_url
        
        if not validate_url(self.config.instance_url):
            raise InvalidParameterException(
                f"Invalid instance URL: {self.config.instance_url}"
            )
        
        self.retry_strategy = RetryStrategy(
            max_retries=self.config.max_retries,
            initial_delay=self.config.retry_delay,
            backoff_factor=self.config.backoff_factor
        )
        
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """Create requests session with default headers"""
        session = requests.Session()
        session.headers.update({
            'User-Agent': self.config.user_agent,
            'Accept': 'application/json',
            'Accept-Language': f'{self.config.default_language};q=0.9',
        })
        session.headers.update(self.config.custom_headers)
        return session
    
    def _make_request(
        self,
        endpoint: str,
        params: Dict[str, Any],
        timeout: Optional[int] = None
    ) -> requests.Response:
        """Make HTTP request with retry logic"""
        url = build_search_url(self.config.instance_url, endpoint)
        timeout = timeout or self.config.default_timeout
        
        def _request():
            return self.session.get(
                url,
                params=params,
                timeout=timeout,
                verify=self.config.verify_ssl
            )
        
        try:
            response = self.retry_strategy.execute(_request)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout as e:
            raise TimeoutException(f"Request timed out: {e}")
        except requests.exceptions.ConnectionError as e:
            raise ConnectionException(f"Connection failed: {e}")
    
    def search(
        self,
        query: str,
        categories: Optional[List[Union[SearchCategory, str]]] = None,
        engines: Optional[List[str]] = None,
        language: Optional[str] = None,
        page: int = 1,
        time_range: Optional[Union[TimeRange, str]] = None,
        safe_search: Optional[Union[SafeSearch, int]] = None,
        timeout: Optional[int] = None,
        format: OutputFormat = OutputFormat.JSON
    ) -> Dict[str, Any]:
        """
        Perform search with all parameters
        
        See main documentation for parameter details
        """
        query = sanitize_query(query)
        if not query:
            raise InvalidParameterException("Query cannot be empty")
        
        params = {
            "q": query,
            "language": language or self.config.default_language,
            "pageno": page,
            "format": format.value if isinstance(format, OutputFormat) else format
        }
        
        # Add categories
        if categories:
            cat_list = []
            for cat in categories:
                if isinstance(cat, SearchCategory):
                    cat_list.append(cat.value)
                else:
                    cat_list.append(cat)
            params["categories"] = ",".join(cat_list)
        
        # Add engines
        if engines:
            params["engines"] = ",".join(engines)
        
        # Add time range
        if time_range:
            if isinstance(time_range, TimeRange):
                params["time_range"] = time_range.value
            else:
                params["time_range"] = time_range
        
        # Add safe search
        if safe_search is not None:
            if isinstance(safe_search, SafeSearch):
                params["safesearch"] = safe_search.value
            else:
                params["safesearch"] = safe_search
        else:
            params["safesearch"] = self.config.default_safe_search
        
        response = self._make_request("/search", params, timeout)
        
        if format in (OutputFormat.JSON, "json"):
            return response.json()
        else:
            return {"content": response.text}
    
    def search_structured(
        self,
        query: str,
        **kwargs
    ) -> SearchResponse:
        """
        Perform search and return structured response object
        """
        kwargs["format"] = OutputFormat.JSON
        raw_results = self.search(query, **kwargs)
        
        results = []
        for result in raw_results.get("results", []):
            results.append(SearchResult(
                title=result.get("title", ""),
                url=result.get("url", ""),
                content=result.get("content", ""),
                engine=result.get("engine", ""),
                category=result.get("category", ""),
                score=result.get("score", 0.0),
                thumbnail=result.get("thumbnail"),
                publishedDate=result.get("publishedDate"),
                metadata=result.get("metadata")
            ))
        
        return SearchResponse(
            query=query,
            number_of_results=raw_results.get("number_of_results", len(results)),
            results=results,
            answers=raw_results.get("answers", []),
            corrections=raw_results.get("corrections", []),
            infoboxes=raw_results.get("infoboxes", []),
            suggestions=raw_results.get("suggestions", []),
            unresponsive_engines=raw_results.get("unresponsive_engines", [])
        )
    
    def autocomplete(
        self,
        query: str,
        timeout: Optional[int] = None
    ) -> List[str]:
        """Get autocomplete suggestions"""
        params = {"q": sanitize_query(query)}
        response = self._make_request("/autocompleter", params, timeout)
        return response.json()
    
    def image_search(
        self,
        query: str,
        page: int = 1,
        safesearch: Optional[Union[SafeSearch, int]] = None,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Specialized image search"""
        results = self.search(
            query=query,
            categories=[SearchCategory.IMAGES],
            page=page,
            safe_search=safesearch,
            timeout=timeout
        )
        return results.get("results", [])
    
    def news_search(
        self,
        query: str,
        time_range: Union[TimeRange, str] = TimeRange.WEEK,
        page: int = 1,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Specialized news search"""
        results = self.search(
            query=query,
            categories=[SearchCategory.NEWS],
            time_range=time_range,
            page=page,
            timeout=timeout
        )
        return results.get("results", [])
    
    def video_search(
        self,
        query: str,
        page: int = 1,
        timeout: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Specialized video search"""
        results = self.search(
            query=query,
            categories=[SearchCategory.VIDEOS],
            page=page,
            timeout=timeout
        )
        return results.get("results", [])
    
    def advanced_search(
        self,
        query: str,
        exact_phrase: Optional[str] = None,
        exclude_words: Optional[List[str]] = None,
        site: Optional[str] = None,
        filetype: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Advanced search with operators"""
        advanced_query_parts = [query]
        
        if exact_phrase:
            advanced_query_parts.append(f'"{exact_phrase}"')
        
        if exclude_words:
            for word in exclude_words:
                advanced_query_parts.append(f"-{word}")
        
        if site:
            advanced_query_parts.append(f"site:{site}")
        
        if filetype:
            advanced_query_parts.append(f"filetype:{filetype}")
        
        final_query = " ".join(advanced_query_parts)
        return self.search(final_query, **kwargs)
    
    def health_check(self, timeout: Optional[int] = 5) -> bool:
        """Check if SearXNG instance is healthy"""
        try:
            url = urljoin(self.config.instance_url, "/healthz")
            response = self.session.get(
                url,
                timeout=timeout or 5,
                verify=self.config.verify_ssl
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_engines_info(
        self,
        timeout: Optional[int] = None
    ) -> List[EngineInfo]:
        """Get information about available engines"""
        try:
            response = self._make_request("/config", {}, timeout)
            config = response.json()
            
            engines = []
            for engine_data in config.get("engines", []):
                engines.append(EngineInfo(
                    name=engine_data.get("name", ""),
                    categories=engine_data.get("categories", []),
                    enabled=engine_data.get("enabled", False),
                    language_support=engine_data.get("language_support"),
                    time_range_support=engine_data.get("time_range_support"),
                    safesearch_support=engine_data.get("safesearch_support"),
                    timeout=engine_data.get("timeout")
                ))
            
            return engines
        except Exception as e:
            print(f"Error fetching engines info: {e}")
            return []