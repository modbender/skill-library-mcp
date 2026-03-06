"""
_retry.py - Exponential backoff for transient network errors.
Shared retry logic for OpenClaw skills. Stdlib only.

Usage:
    from _retry import with_retry
    data = with_retry(lambda: urllib.request.urlopen(req))
"""

import time
import urllib.error

# HTTP status codes considered transient (worth retrying)
_TRANSIENT_STATUS = {429, 502, 503, 504}

# Default settings
MAX_RETRIES = 3
BASE_DELAY  = 1.0      # seconds
BACKOFF     = 2.0      # multiplier


def with_retry(fn, max_retries: int = MAX_RETRIES, base_delay: float = BASE_DELAY,
               backoff: float = BACKOFF):
    """
    Call fn() up to max_retries+1 times with exponential backoff.
    Retries on:
      - urllib.error.URLError (network-level: DNS, timeout, refused)
      - urllib.error.HTTPError with transient status (429, 502, 503, 504)
      - OSError / ConnectionError (socket-level)
    All other exceptions propagate immediately.
    """
    delay = base_delay
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except urllib.error.HTTPError as exc:
            if exc.code not in _TRANSIENT_STATUS:
                raise                           # 4xx client error → don't retry
            last_exc = exc
        except (urllib.error.URLError, OSError, ConnectionError) as exc:
            last_exc = exc
        # Don't sleep after last attempt
        if attempt < max_retries:
            time.sleep(delay)
            delay *= backoff
    raise last_exc
