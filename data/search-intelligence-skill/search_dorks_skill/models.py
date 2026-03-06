"""
Data models for the search-intelligence-skill.
All structured data flows through these dataclasses.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from enum import Enum


class Depth(str, Enum):
    QUICK = "quick"          # 1 query, top engines
    STANDARD = "standard"    # 2-4 queries, multi-engine
    DEEP = "deep"            # 5-10 queries, multi-step strategy
    EXHAUSTIVE = "exhaustive" # 10+ queries, full OSINT chain


class IntentCategory(str, Enum):
    GENERAL = "general"
    SECURITY = "security"
    SEO = "seo"
    OSINT = "osint"
    ACADEMIC = "academic"
    CODE = "code"
    FILES = "files"
    NEWS = "news"
    IMAGES = "images"
    VIDEOS = "videos"
    SOCIAL = "social"
    SHOPPING = "shopping"
    LEGAL = "legal"
    MEDICAL = "medical"


@dataclass
class SearchIntent:
    category: IntentCategory
    subcategory: str = ""
    entities: dict[str, Any] = field(default_factory=dict)
    keywords: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    time_range: str = ""          # day, week, month, year, ""
    depth: Depth = Depth.STANDARD
    confidence: float = 0.0


@dataclass
class DorkQuery:
    query: str
    engine_hint: str = ""         # preferred engine
    category_hint: str = "general"
    operators_used: list[str] = field(default_factory=list)
    purpose: str = ""             # human-readable description


@dataclass
class SearchStep:
    queries: list[DorkQuery]
    engines: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    time_range: str = ""
    max_results: int = 20
    description: str = ""


@dataclass
class SearchStrategy:
    name: str
    steps: list[SearchStep]
    description: str = ""


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    engines: list[str] = field(default_factory=list)
    score: float = 0.0
    category: str = "general"
    positions: list[int] = field(default_factory=list)
    relevance: float = 0.0       # computed by analyzer
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchReport:
    """Final output returned to the AI agent."""
    query: str
    intent: SearchIntent
    strategy: SearchStrategy
    results: list[SearchResult]
    total_found: int = 0
    suggestions: list[str] = field(default_factory=list)
    refined_queries: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timing_seconds: float = 0.0
    engines_used: list[str] = field(default_factory=list)

    def to_context(self, max_results: int = 20) -> str:
        """Format results for LLM context window."""
        lines = [
            f"=== Search Report ===",
            f"Query: {self.query}",
            f"Intent: {self.intent.category.value}/{self.intent.subcategory}",
            f"Strategy: {self.strategy.name}",
            f"Results: {len(self.results)} (of {self.total_found} total)",
            f"Engines: {', '.join(self.engines_used)}",
            f"Time: {self.timing_seconds:.2f}s",
            "",
        ]
        for i, r in enumerate(self.results[:max_results], 1):
            lines.append(f"[{i}] {r.title}")
            lines.append(f"    URL: {r.url}")
            lines.append(f"    {r.snippet[:300]}")
            lines.append(f"    Score: {r.relevance:.2f} | Engines: {', '.join(r.engines)}")
            lines.append("")

        if self.suggestions:
            lines.append("Suggested refinements:")
            for s in self.suggestions[:5]:
                lines.append(f"  • {s}")

        return "\n".join(lines)

    def top(self, n: int = 5) -> list[SearchResult]:
        return sorted(self.results, key=lambda r: r.relevance, reverse=True)[:n]