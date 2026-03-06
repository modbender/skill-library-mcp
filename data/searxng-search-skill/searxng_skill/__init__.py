"""
SearXNG Advanced Search Skill
A comprehensive Python library for interacting with SearXNG instances.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .core import SearXNGSkill
from .models import SearchResult
from .enums import SearchCategory, TimeRange, SafeSearch
from .exceptions import (
    SearXNGException,
    TimeoutException,
    ConnectionException,
    InvalidParameterException
)

__all__ = [
    "SearXNGSkill",
    "SearchResult",
    "SearchCategory",
    "TimeRange",
    "SafeSearch",
    "SearXNGException",
    "TimeoutException",
    "ConnectionException",
    "InvalidParameterException",
]