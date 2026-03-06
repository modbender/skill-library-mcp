"""Smart rate limiting with random jitter to mimic human browsing patterns."""

import random
import time
from typing import Dict

MIN_DELAY = 3.0
MAX_DELAY = 8.0
BURST_EXTRA = 4.0
_DOMAIN_OVERRIDES = {"tor.reddit.com": (6.0, 12.0)}

_last_request: Dict[str, float] = {}
_request_count: Dict[str, int] = {}


def _jittered_delay(domain: str) -> float:
    count = _request_count.get(domain, 0)
    lo, hi = _DOMAIN_OVERRIDES.get(domain, (MIN_DELAY, MAX_DELAY))
    base = random.uniform(lo, hi)
    if count > 5:
        base += random.uniform(0, BURST_EXTRA)
    return base


def wait(domain: str = "reddit") -> None:
    now = time.monotonic()
    last = _last_request.get(domain, 0.0)
    elapsed = now - last
    delay = _jittered_delay(domain)
    if elapsed < delay:
        time.sleep(delay - elapsed)


def mark(domain: str = "reddit") -> None:
    _last_request[domain] = time.monotonic()
    _request_count[domain] = _request_count.get(domain, 0) + 1


def get_count(domain: str = "reddit") -> int:
    return _request_count.get(domain, 0)


def reset(domain: str = "reddit") -> None:
    _last_request.pop(domain, None)
    _request_count.pop(domain, None)
