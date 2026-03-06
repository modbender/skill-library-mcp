"""
Security utilities for finance-data-intelligence skill.

This module provides:
- Input validation (tickers, dates, symbols)
- Rate limiting decorators
- Secure logging configuration
- Safe error handling
"""

import re
import time
import logging
from functools import wraps
from typing import Optional, Callable, Any


# ============================================================================
# INPUT VALIDATION
# ============================================================================

def validate_ticker(ticker: str) -> bool:
    """
    Validate ticker symbol format.
    
    Supported formats:
    - US: AAPL, BRK.B, BF.A
    - HK: 0700.HK, 3690.HK
    - Tokyo: 7203.T, 6758.T
    - Taiwan: 2330.TW, 2317.TW
    - Korea: 005930.KS, 035420.KS
    - China: 600519.SS, 000001.SZ
    - Indices: ^GSPC, ^N225, ^HSI
    - Futures: ES=F, CL=F, GC=F
    """
    if not ticker or not isinstance(ticker, str):
        return False
    
    ticker = ticker.strip().upper()
    
    # Length check (1-20 chars)
    if len(ticker) < 1 or len(ticker) > 20:
        return False
    
    # Valid characters: letters, numbers, ^, ., =, -
    if not re.match(r'^[A-Z0-9\^\.\=\-]+$', ticker):
        return False
    
    # Prevent path traversal attempts
    if '..' in ticker or '/' in ticker or '\\' in ticker:
        return False
    
    # Prevent SQL injection patterns
    dangerous = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', '--', ';']
    if any(d in ticker for d in dangerous):
        return False
    
    return True


def sanitize_ticker(ticker: str) -> Optional[str]:
    """
    Sanitize and validate ticker. Returns cleaned ticker or None if invalid.
    """
    if not ticker:
        return None
    
    # Remove whitespace and convert to uppercase
    cleaned = ticker.strip().upper()
    
    if validate_ticker(cleaned):
        return cleaned
    
    return None


def validate_date_string(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        from datetime import datetime
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_numeric(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """
    Validate numeric value with optional range checks.
    """
    try:
        num = float(value)
        if min_val is not None and num < min_val:
            return False
        if max_val is not None and num > max_val:
            return False
        return True
    except (ValueError, TypeError):
        return False


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """
    Rate limiter for API calls.
    
    Usage:
        @RateLimiter(max_calls=25, period=86400)  # 25 calls per day
        def fetch_data(ticker):
            ...
    """
    
    def __init__(self, max_calls: int, period: int):
        """
        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            
            # Remove old calls outside the time window
            cutoff = now - self.period
            self.calls = [c for c in self.calls if c > cutoff]
            
            # Check if limit exceeded
            if len(self.calls) >= self.max_calls:
                oldest_call = min(self.calls)
                wait_time = int(self.period - (now - oldest_call))
                raise RateLimitExceeded(
                    f"Rate limit exceeded ({self.max_calls} calls per {self.period}s). "
                    f"Wait {wait_time}s or upgrade your API tier."
                )
            
            # Record this call
            self.calls.append(now)
            
            return func(*args, **kwargs)
        
        return wrapper


class RateLimitExceeded(Exception):
    """Raised when rate limit is exceeded."""
    pass


# Pre-configured rate limiters for common APIs
alpha_vantage_limiter = RateLimiter(max_calls=25, period=86400)  # 25/day
sec_edgar_limiter = RateLimiter(max_calls=10, period=60)  # 10/minute
news_api_limiter = RateLimiter(max_calls=100, period=86400)  # 100/day
fred_limiter = RateLimiter(max_calls=120, period=60)  # 120/minute


def rate_limited(max_calls: int, period: int):
    """
    Decorator factory for rate limiting.
    
    Usage:
        @rate_limited(max_calls=25, period=86400)
        def my_api_call():
            ...
    """
    limiter = RateLimiter(max_calls, period)
    return limiter


# ============================================================================
# SECURE LOGGING
# ============================================================================

def setup_secure_logging(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Setup secure logging that doesn't leak sensitive data.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove any existing handlers
    logger.handlers = []
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


class SecureLogger:
    """
    Logger that automatically sanitizes sensitive information.
    """
    
    SENSITIVE_PATTERNS = [
        (r'[A-Za-z0-9]{32,}', '[API_KEY_REDACTED]'),  # API keys
        (r'ghp_[A-Za-z0-9]{36}', '[GITHUB_TOKEN_REDACTED]'),
        (r'sk-[A-Za-z0-9]{48}', '[SECRET_KEY_REDACTED]'),
        (r'password[=:]\s*\S+', 'password=[REDACTED]'),
        (r'token[=:]\s*\S+', 'token=[REDACTED]'),
    ]
    
    def __init__(self, name: str):
        self.logger = setup_secure_logging(name)
    
    def _sanitize(self, message: str) -> str:
        """Remove sensitive patterns from log messages."""
        import re
        sanitized = message
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
        return sanitized
    
    def debug(self, message: str, *args, **kwargs):
        self.logger.debug(self._sanitize(message), *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        self.logger.info(self._sanitize(message), *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        self.logger.warning(self._sanitize(message), *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        self.logger.error(self._sanitize(message), *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        self.logger.exception(self._sanitize(message), *args, **kwargs)


# ============================================================================
# SAFE ERROR HANDLING
# ============================================================================

class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class APIError(Exception):
    """Raised when external API call fails."""
    pass


def safe_api_call(func: Callable) -> Callable:
    """
    Decorator for safe API calls with proper error handling.
    
    - Catches exceptions
    - Logs safely (no sensitive data)
    - Returns user-friendly error messages
    """
    logger = SecureLogger(f"safe_api.{func.__name__}")
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RateLimitExceeded as e:
            logger.warning(f"Rate limit: {e}")
            return {"error": str(e), "type": "rate_limit"}
        except ValidationError as e:
            logger.warning(f"Validation error: {e}")
            return {"error": str(e), "type": "validation"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error in {func.__name__}: {type(e).__name__}")
            return {"error": "Network error. Please try again later.", "type": "network"}
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {type(e).__name__}")
            return {"error": "An unexpected error occurred.", "type": "unknown"}
    
    return wrapper


# ============================================================================
# SECURITY HELPERS
# ============================================================================

def is_safe_filename(filename: str) -> bool:
    """
    Check if filename is safe (no path traversal).
    """
    if not filename:
        return False
    
    dangerous_patterns = [
        '..', '/', '\\', '~', '$', '%', '&', '*', '|', '<', '>', '`', '"', "'"
    ]
    
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    
    # Only allow alphanumeric, underscore, hyphen, dot
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', filename):
        return False
    
    return True


def truncate_string(value: str, max_length: int = 100) -> str:
    """
    Truncate string to prevent memory issues.
    """
    if not value:
        return value
    
    if len(value) > max_length:
        return value[:max_length] + "... [truncated]"
    
    return value


# ============================================================================
# MODULE INITIALIZATION
# ============================================================================

# Import requests for safe_api_call decorator
import requests

# Create default logger
logger = SecureLogger("security")

__all__ = [
    'validate_ticker',
    'sanitize_ticker',
    'validate_date_string',
    'validate_numeric',
    'RateLimiter',
    'RateLimitExceeded',
    'rate_limited',
    'alpha_vantage_limiter',
    'sec_edgar_limiter',
    'news_api_limiter',
    'fred_limiter',
    'setup_secure_logging',
    'SecureLogger',
    'ValidationError',
    'APIError',
    'safe_api_call',
    'is_safe_filename',
    'truncate_string',
]
