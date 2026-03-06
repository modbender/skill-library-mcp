"""
search-intelligence-skill: Advanced AI-powered search skill using SearXNG.
"""

from .skill import SearchSkill
from .models import (
    SearchReport, SearchResult, SearchIntent, SearchStrategy,
    DorkQuery, Depth, IntentCategory,
)
from .dorks import DorkGenerator
from .intent import IntentParser
from .analyzer import ResultAnalyzer
from .client import SearXNGClient

__version__ = "1.0.0"
__all__ = [
    "SearchSkill",
    "SearchReport",
    "SearchResult",
    "SearchIntent",
    "SearchStrategy",
    "DorkQuery",
    "Depth",
    "IntentCategory",
    "DorkGenerator",
    "IntentParser",
    "ResultAnalyzer",
    "SearXNGClient",
]