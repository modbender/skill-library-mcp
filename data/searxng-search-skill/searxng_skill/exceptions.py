"""
Custom exceptions for SearXNG skill
"""


class SearXNGException(Exception):
    """Base exception for SearXNG skill"""
    pass


class TimeoutException(SearXNGException):
    """Raised when a request times out"""
    pass


class ConnectionException(SearXNGException):
    """Raised when connection to SearXNG instance fails"""
    pass


class InvalidParameterException(SearXNGException):
    """Raised when invalid parameters are provided"""
    pass


class RateLimitException(SearXNGException):
    """Raised when rate limit is exceeded"""
    pass


class InstanceUnavailableException(SearXNGException):
    """Raised when SearXNG instance is unavailable"""
    pass


class ParseException(SearXNGException):
    """Raised when response parsing fails"""
    pass