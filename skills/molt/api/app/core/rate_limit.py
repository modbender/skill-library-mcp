"""In-memory rate limiter for agent registration."""
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException

from app.core.config import settings


# In-memory store: ip -> (window_start_timestamp, request_count)
_store: Dict[str, Tuple[float, int]] = defaultdict(lambda: (0.0, 0))


def clear_rate_limit_store() -> None:
    """Clear the rate limit store (for tests)."""
    _store.clear()


def _get_client_ip(request: Request) -> str:
    """Get client IP, respecting X-Forwarded-For when present."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host or "unknown"
    return "unknown"


def check_agent_registration_rate_limit(request: Request) -> None:
    """
    Check rate limit for agent registration. Raises HTTPException 429 if exceeded.
    Uses fixed window: max N requests per IP per window_seconds.
    """
    limit = settings.agent_registration_rate_limit
    window_seconds = settings.agent_registration_rate_window_seconds
    ip = _get_client_ip(request)
    now = time.time()

    window_start, count = _store[ip]
    if now - window_start >= window_seconds:
        # Window expired, reset
        _store[ip] = (now, 1)
        return

    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Too many agent registrations. Try again later.",
        )
    _store[ip] = (window_start, count + 1)
