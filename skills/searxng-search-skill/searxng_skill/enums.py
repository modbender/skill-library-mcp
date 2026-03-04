"""
Enumerations for SearXNG search parameters
"""

from enum import Enum


class SearchCategory(Enum):
    """Available SearXNG search categories"""
    GENERAL = "general"
    IMAGES = "images"
    VIDEOS = "videos"
    NEWS = "news"
    MAP = "map"
    MUSIC = "music"
    IT = "it"
    SCIENCE = "science"
    FILES = "files"
    SOCIAL_MEDIA = "social media"


class TimeRange(Enum):
    """Time range filters for search results"""
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    ALL = ""


class SafeSearch(Enum):
    """Safe search levels"""
    NONE = 0
    MODERATE = 1
    STRICT = 2


class OutputFormat(Enum):
    """Output formats supported by SearXNG"""
    JSON = "json"
    CSV = "csv"
    RSS = "rss"
    HTML = "html"


class ImageSize(Enum):
    """Image size filters"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ANY = ""