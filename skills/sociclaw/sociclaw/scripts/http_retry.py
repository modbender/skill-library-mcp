"""
HTTP retry helpers for external integrations.

Goals:
- Keep retry behavior consistent across providers.
- Retry only transient failures (network/timeouts/429/5xx).
- Preserve existing request/response handling in callers.
"""

from __future__ import annotations

import random
import time
from typing import Iterable, Optional

import requests


DEFAULT_RETRY_STATUSES = (429, 500, 502, 503, 504)


def request_with_retry(
    *,
    session: requests.Session,
    method: str,
    url: str,
    headers: Optional[dict] = None,
    json: Optional[dict] = None,
    timeout: int = 30,
    max_retries: int = 3,
    backoff_base_seconds: float = 0.5,
    retry_statuses: Optional[Iterable[int]] = None,
) -> requests.Response:
    """
    Execute an HTTP request with retry/backoff for transient failures.

    `max_retries` means additional attempts after the first request.
    So total attempts = 1 + max_retries.
    """
    retryable_statuses = set(retry_statuses or DEFAULT_RETRY_STATUSES)
    last_exception: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            resp = session.request(
                method=method.upper().strip(),
                url=url,
                headers=headers,
                json=json,
                timeout=timeout,
            )

            if resp.status_code in retryable_statuses and attempt < max_retries:
                _sleep_with_jitter(backoff_base_seconds, attempt)
                continue

            return resp
        except requests.RequestException as exc:
            last_exception = exc
            if attempt >= max_retries:
                raise
            _sleep_with_jitter(backoff_base_seconds, attempt)

    # Defensive fallback; loop always returns or raises.
    if last_exception:
        raise last_exception
    raise RuntimeError("request_with_retry failed unexpectedly")


def _sleep_with_jitter(base_seconds: float, attempt: int) -> None:
    delay = max(0.05, float(base_seconds)) * (2 ** int(attempt))
    jitter = random.uniform(0.0, min(0.25, delay * 0.2))
    time.sleep(delay + jitter)
