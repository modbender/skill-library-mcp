#!/usr/bin/env python3
"""
ZEDEDA API HTTP Client

Shared HTTP transport used by every service module.  Handles Bearer-token
authentication, structured logging, token sanitisation, retry logic, and
consistent error mapping.

Environment variables
---------------------
ZEDEDA_API_TOKEN  – Required. Bearer token for the ZEDEDA API.
ZEDEDA_BASE_URL   – Optional. Override the default base URL.
ZEDEDA_LOG_LEVEL  – Optional. DEBUG | INFO (default) | WARNING | ERROR.
"""

# SECURITY MANIFEST:
# Environment variables accessed: ZEDEDA_API_TOKEN, ZEDEDA_BASE_URL, ZEDEDA_LOG_LEVEL
# External endpoints called: https://zedcontrol.zededa.net/api (default, configurable)
# Local files read: none
# Local files written: none

from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .errors import ZededaAuthError, ZededaError, error_for_status

# ---------------------------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------------------------

_LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
}

_log_level_name = os.environ.get("ZEDEDA_LOG_LEVEL", "INFO").upper()
_log_level = _LOG_LEVELS.get(_log_level_name, logging.INFO)

# Scope logging to the "zededa" namespace only — avoids polluting global config.
logger = logging.getLogger("zededa.client")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    logger.addHandler(_handler)
logger.setLevel(_log_level)
logger.propagate = False

DEFAULT_BASE_URL = "https://zedcontrol.zededa.net/api"
MAX_RETRIES = 2
RETRY_BACKOFF = 1.0  # seconds


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class ZededaClient:
    """Low-level HTTP client for the ZEDEDA REST API."""

    def __init__(self, token: str | None = None, base_url: str | None = None):
        self.token = token or os.environ.get("ZEDEDA_API_TOKEN", "")
        self.base_url = (base_url or os.environ.get("ZEDEDA_BASE_URL", DEFAULT_BASE_URL)).rstrip("/")
        if not self.token:
            raise ZededaAuthError(
                "ZEDEDA_API_TOKEN environment variable is not set.",
                endpoint="<init>", method="INIT", status_code=0,
            )

    # -- internal helpers ---------------------------------------------------

    @staticmethod
    def _sanitise(text: str, token: str) -> str:
        """Replace the bearer token in *text* with a redacted placeholder."""
        if token:
            text = text.replace(token, "***REDACTED***")
        return text

    def _build_url(self, path: str, query: dict[str, Any] | None = None) -> str:
        url = f"{self.base_url}/{path.lstrip('/')}"
        if query:
            # Drop keys whose value is None
            filtered = {k: v for k, v in query.items() if v is not None}
            if filtered:
                url += ("&" if "?" in url else "?") + urllib.parse.urlencode(filtered, doseq=True)
        return url

    # -- public request methods ---------------------------------------------

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, Any] | None = None,
        body: Any | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        """Execute an HTTP request against the ZEDEDA API.

        Parameters
        ----------
        method : str
            HTTP verb (GET, POST, PUT, DELETE, PATCH).
        path : str
            API path *after* the base URL, e.g. ``/v1/devices``.
        query : dict, optional
            Query-string parameters.
        body : Any, optional
            JSON-serialisable request body.
        extra_headers : dict, optional
            Additional headers merged into the default set.

        Returns
        -------
        dict | list | str
            Parsed JSON response or raw text.
        """
        url = self._build_url(path, query)
        headers: dict[str, str] = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)

        encoded_body: bytes | None = None
        if body is not None:
            encoded_body = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"

        safe_url = self._sanitise(url, self.token)
        logger.debug(">>> %s %s", method, safe_url)
        if encoded_body:
            logger.debug("    body: %s", self._sanitise(encoded_body.decode()[:500], self.token))

        last_exc: Exception | None = None
        for attempt in range(1, MAX_RETRIES + 2):  # attempt 1 .. MAX_RETRIES+1
            t0 = time.monotonic()
            try:
                req = urllib.request.Request(url, data=encoded_body, headers=headers, method=method.upper())
                with urllib.request.urlopen(req) as resp:
                    elapsed = time.monotonic() - t0
                    raw = resp.read().decode("utf-8")
                    logger.info("<<< %s %s → %s (%.3fs)", method, safe_url, resp.status, elapsed)
                    if not raw.strip():
                        return {}
                    try:
                        return json.loads(raw)
                    except json.JSONDecodeError:
                        return {"raw": raw}

            except urllib.error.HTTPError as exc:
                elapsed = time.monotonic() - t0
                err_body = exc.read().decode("utf-8", errors="replace")
                safe_body = self._sanitise(err_body, self.token)
                logger.warning(
                    "<<< %s %s → HTTP %s (%.3fs) — %s",
                    method, safe_url, exc.code, elapsed, safe_body[:300],
                )
                # Retry on 429 / 5xx
                if exc.code in (429, 500, 502, 503, 504) and attempt <= MAX_RETRIES:
                    wait = RETRY_BACKOFF * attempt
                    logger.info("    retrying in %.1fs (attempt %d/%d)", wait, attempt, MAX_RETRIES)
                    time.sleep(wait)
                    last_exc = exc
                    continue

                raise error_for_status(
                    exc.code,
                    message=f"HTTP {exc.code} on {method} {path}: {safe_body[:200]}",
                    endpoint=path,
                    method=method,
                    response_body=safe_body,
                )
            except Exception as exc:
                elapsed = time.monotonic() - t0
                msg = self._sanitise(str(exc), self.token)
                logger.error("<<< %s %s → ERROR (%.3fs) — %s", method, safe_url, elapsed, msg)
                raise ZededaError(
                    message=msg,
                    endpoint=path,
                    method=method,
                )

        # Should not be reached, but just in case:
        if last_exc:
            raise last_exc  # pragma: no cover

    # -- convenience wrappers -----------------------------------------------

    def get(self, path: str, *, query: dict[str, Any] | None = None, **kw: Any) -> Any:
        return self.request("GET", path, query=query, **kw)

    def post(self, path: str, *, body: Any | None = None, query: dict[str, Any] | None = None, **kw: Any) -> Any:
        return self.request("POST", path, body=body, query=query, **kw)

    def put(self, path: str, *, body: Any | None = None, query: dict[str, Any] | None = None, **kw: Any) -> Any:
        return self.request("PUT", path, body=body, query=query, **kw)

    def delete(self, path: str, *, query: dict[str, Any] | None = None, **kw: Any) -> Any:
        return self.request("DELETE", path, query=query, **kw)

    def patch(self, path: str, *, body: Any | None = None, query: dict[str, Any] | None = None, **kw: Any) -> Any:
        return self.request("PATCH", path, body=body, query=query, **kw)
