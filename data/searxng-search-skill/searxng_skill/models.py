"""
Data models for SearXNG search results
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime


@dataclass
class SearchResult:
    """Structured search result"""
    title: str
    url: str
    content: str
    engine: str
    category: str
    score: float = 0.0
    thumbnail: Optional[str] = None
    publishedDate: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "engine": self.engine,
            "category": self.category,
            "score": self.score,
            "thumbnail": self.thumbnail,
            "publishedDate": self.publishedDate,
            "metadata": self.metadata,
        }


@dataclass
class ImageResult(SearchResult):
    """Image-specific search result"""
    img_src: Optional[str] = None
    thumbnail_src: Optional[str] = None
    resolution: Optional[str] = None
    img_format: Optional[str] = None


@dataclass
class VideoResult(SearchResult):
    """Video-specific search result"""
    duration: Optional[str] = None
    iframe_src: Optional[str] = None


@dataclass
class NewsResult(SearchResult):
    """News-specific search result"""
    source: Optional[str] = None
    author: Optional[str] = None


@dataclass
class SearchResponse:
    """Complete search response"""
    query: str
    number_of_results: int
    results: List[SearchResult] = field(default_factory=list)
    answers: List[str] = field(default_factory=list)
    corrections: List[str] = field(default_factory=list)
    infoboxes: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    unresponsive_engines: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "query": self.query,
            "number_of_results": self.number_of_results,
            "results": [r.to_dict() for r in self.results],
            "answers": self.answers,
            "corrections": self.corrections,
            "infoboxes": self.infoboxes,
            "suggestions": self.suggestions,
            "unresponsive_engines": self.unresponsive_engines,
        }


@dataclass
class EngineInfo:
    """Information about a search engine"""
    name: str
    categories: List[str]
    enabled: bool
    language_support: Optional[bool] = None
    time_range_support: Optional[bool] = None
    safesearch_support: Optional[bool] = None
    timeout: Optional[float] = None