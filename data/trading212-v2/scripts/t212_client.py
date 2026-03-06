"""
Trading212 API client.

Handles authentication, rate-limit awareness, caching, retry logic,
and all required REST endpoints for positions, orders, cash, dividends,
and historical orders.
"""

from __future__ import annotations

import base64
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from cache import TTLCache

DEMO_BASE = "https://demo.trading212.com/api/v0"
LIVE_BASE = "https://live.trading212.com/api/v0"

# Human-readable error messages for common HTTP status codes.
_ERROR_MESSAGES: Dict[int, str] = {
    401: "Ongeldige API-credentials. Controleer TRADING212_API_KEY en TRADING212_API_SECRET.",
    403: "Toegang geweigerd. Je API-key heeft onvoldoende rechten voor deze actie.",
    404: "Resource niet gevonden. Controleer of de ticker of order-ID klopt.",
    429: "Rate limit bereikt. Probeer het later opnieuw.",
}

# Maximum number of retries for transient errors (429, 5xx, connection errors).
_MAX_RETRIES = 3


class Trading212Error(Exception):
    """Raised when the Trading212 API returns an error."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(f"HTTP {status_code}: {message}")


class Trading212Client:
    """Thin wrapper around the Trading212 REST API (v0)."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        demo: Optional[bool] = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("TRADING212_API_KEY", "")
        self.api_secret = api_secret or os.environ.get("TRADING212_API_SECRET", "")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "TRADING212_API_KEY and TRADING212_API_SECRET must be set "
                "(pass them directly or via environment variables)."
            )

        if demo is None:
            demo = os.environ.get("TRADING212_DEMO", "true").lower() == "true"
        self.demo = demo
        self.base_url = DEMO_BASE if demo else LIVE_BASE

        credentials = f"{self.api_key}:{self.api_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        self._headers = {
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/json",
        }

        # Simple per-endpoint rate-limit tracker (path -> next_allowed_ts).
        self._rate_limits: Dict[str, float] = {}

        # In-memory TTL cache (default 60 seconds).
        self._cache = TTLCache(default_ttl=60.0)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _wait_for_rate_limit(self, path: str, min_interval: float) -> None:
        """Block until the rate-limit window for *path* has passed."""
        now = time.time()
        earliest = self._rate_limits.get(path, 0.0)
        if now < earliest:
            time.sleep(earliest - now)
        self._rate_limits[path] = time.time() + min_interval

    @staticmethod
    def _friendly_error(status_code: int, raw_text: str) -> str:
        """Return a human-readable error message for the given status code."""
        friendly = _ERROR_MESSAGES.get(status_code)
        if friendly:
            return f"{friendly} (HTTP {status_code}: {raw_text})"
        if 500 <= status_code < 600:
            return (
                f"Trading212 serverfout (HTTP {status_code}). "
                f"Probeer het later opnieuw. Details: {raw_text}"
            )
        return f"HTTP {status_code}: {raw_text}"

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        min_interval: float = 1.0,
    ) -> Any:
        """Execute an HTTP request with retry logic for transient errors.

        Retries up to ``_MAX_RETRIES`` times for 429 (rate-limited) and
        5xx (server errors), with exponential backoff.  Connection errors
        and timeouts are also retried.
        """
        self._wait_for_rate_limit(path, min_interval)
        url = f"{self.base_url}{path}"

        last_error: Optional[Exception] = None

        for attempt in range(_MAX_RETRIES):
            try:
                response = requests.request(
                    method,
                    url,
                    headers=self._headers,
                    params=params,
                    json=json_body,
                    timeout=30,
                )
            except requests.ConnectionError as exc:
                last_error = exc
                backoff = 2 ** attempt
                time.sleep(backoff)
                continue
            except requests.Timeout as exc:
                last_error = exc
                backoff = 2 ** attempt
                time.sleep(backoff)
                continue

            if response.status_code == 429:
                retry_after = float(response.headers.get("Retry-After", str(2 ** attempt)))
                time.sleep(retry_after)
                last_error = Trading212Error(429, self._friendly_error(429, response.text))
                continue

            if 500 <= response.status_code < 600:
                backoff = 2 ** attempt
                time.sleep(backoff)
                last_error = Trading212Error(
                    response.status_code,
                    self._friendly_error(response.status_code, response.text),
                )
                continue

            # Non-retryable error.
            if not response.ok:
                raise Trading212Error(
                    response.status_code,
                    self._friendly_error(response.status_code, response.text),
                )

            # Success.
            if response.content:
                return response.json()
            return None

        # All retries exhausted.
        if last_error is not None:
            if isinstance(last_error, Trading212Error):
                raise last_error
            raise Trading212Error(
                0,
                f"Verbinding met Trading212 mislukt na {_MAX_RETRIES} pogingen: {last_error}",
            )
        return None

    # ------------------------------------------------------------------
    # Account
    # ------------------------------------------------------------------

    def get_cash(self) -> Dict[str, Any]:
        """Return account cash balance information (cached 60s)."""
        return self._cache.cached_call(
            "cash",
            self._request,
            "GET",
            "/equity/account/cash",
            min_interval=1.0,
        )

    # ------------------------------------------------------------------
    # Positions
    # ------------------------------------------------------------------

    def get_positions(self, ticker: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all open positions (cached 60s, optionally filtered by ticker)."""
        cache_key = f"positions:{ticker or 'all'}"

        def _fetch() -> List[Dict[str, Any]]:
            params = {}
            if ticker:
                params["ticker"] = ticker
            result = self._request(
                "GET", "/equity/positions", params=params or None, min_interval=1.0
            )
            if result is None:
                return []
            return result if isinstance(result, list) else [result]

        return self._cache.cached_call(cache_key, _fetch)

    # ------------------------------------------------------------------
    # Pending orders
    # ------------------------------------------------------------------

    def get_pending_orders(self) -> List[Dict[str, Any]]:
        """Return all currently pending (unfilled) orders."""
        result = self._request("GET", "/equity/orders", min_interval=5.0)
        if result is None:
            return []
        return result if isinstance(result, list) else [result]

    def get_pending_order_by_id(self, order_id: int) -> Dict[str, Any]:
        """Return a single pending order by its ID."""
        return self._request("GET", f"/equity/orders/{order_id}", min_interval=1.0)

    # ------------------------------------------------------------------
    # Place orders
    # ------------------------------------------------------------------

    def place_market_order(
        self,
        ticker: str,
        quantity: float,
        extended_hours: bool = False,
    ) -> Dict[str, Any]:
        """Place a market order. Use negative quantity for sell."""
        body: Dict[str, Any] = {
            "ticker": ticker,
            "quantity": quantity,
            "extendedHours": extended_hours,
        }
        # Invalidate position/cash cache after placing an order.
        self._cache.clear()
        return self._request(
            "POST",
            "/equity/orders/market",
            json_body=body,
            min_interval=1.2,
        )

    def place_limit_order(
        self,
        ticker: str,
        quantity: float,
        limit_price: float,
        time_in_force: str = "GOOD_TILL_CANCEL",
    ) -> Dict[str, Any]:
        """Place a limit order. Use negative quantity for sell."""
        body: Dict[str, Any] = {
            "ticker": ticker,
            "quantity": quantity,
            "limitPrice": limit_price,
            "timeInForce": time_in_force,
        }
        self._cache.clear()
        return self._request(
            "POST",
            "/equity/orders/limit",
            json_body=body,
            min_interval=2.0,
        )

    def cancel_order(self, order_id: int) -> None:
        """Cancel a pending order by its ID."""
        self._cache.clear()
        self._request(
            "DELETE",
            f"/equity/orders/{order_id}",
            min_interval=1.2,
        )

    # ------------------------------------------------------------------
    # Historical data
    # ------------------------------------------------------------------

    def get_historical_orders(
        self,
        ticker: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return historical (filled/cancelled) orders.

        Returns ``{"items": [...], "nextPagePath": "..."}``
        """
        params: Dict[str, Any] = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(
            "GET",
            "/equity/history/orders",
            params=params,
            min_interval=10.0,  # 6 req / 60 s
        )

    def get_all_historical_orders(
        self,
        ticker: Optional[str] = None,
        max_pages: int = 20,
    ) -> List[Dict[str, Any]]:
        """Paginate through all historical orders and return a flat list."""
        all_items: List[Dict[str, Any]] = []
        cursor: Optional[int] = None

        for _ in range(max_pages):
            data = self.get_historical_orders(ticker=ticker, limit=50, cursor=cursor)
            items = data.get("items", [])
            all_items.extend(items)

            next_path = data.get("nextPagePath")
            if not next_path or not items:
                break

            # Extract cursor from nextPagePath query string.
            try:
                from urllib.parse import parse_qs, urlparse
                parsed = urlparse(next_path)
                qs = parse_qs(parsed.query)
                cursor_vals = qs.get("cursor", [])
                cursor = int(cursor_vals[0]) if cursor_vals else None
            except (ValueError, IndexError):
                break

            if cursor is None:
                break

        return all_items

    def get_dividends(
        self,
        ticker: Optional[str] = None,
        limit: int = 50,
        cursor: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Return paid-out dividends.

        Returns ``{"items": [...], "nextPagePath": "..."}``
        """
        params: Dict[str, Any] = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if cursor is not None:
            params["cursor"] = cursor
        return self._request(
            "GET",
            "/equity/history/dividends",
            params=params,
            min_interval=10.0,
        )

    def get_all_dividends(
        self,
        ticker: Optional[str] = None,
        max_pages: int = 20,
    ) -> List[Dict[str, Any]]:
        """Paginate through all dividends and return a flat list."""
        all_items: List[Dict[str, Any]] = []
        cursor: Optional[int] = None

        for _ in range(max_pages):
            data = self.get_dividends(ticker=ticker, limit=50, cursor=cursor)
            items = data.get("items", [])
            all_items.extend(items)

            next_path = data.get("nextPagePath")
            if not next_path or not items:
                break

            try:
                from urllib.parse import parse_qs, urlparse
                parsed = urlparse(next_path)
                qs = parse_qs(parsed.query)
                cursor_vals = qs.get("cursor", [])
                cursor = int(cursor_vals[0]) if cursor_vals else None
            except (ValueError, IndexError):
                break

            if cursor is None:
                break

        return all_items

    def get_transactions(
        self,
        limit: int = 50,
        cursor: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return account transactions (deposits, withdrawals, fees).

        Returns ``{"items": [...], "nextPagePath": "..."}``
        """
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._request(
            "GET",
            "/equity/history/transactions",
            params=params,
            min_interval=10.0,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def get_todays_orders(self) -> List[Dict[str, Any]]:
        """Convenience: return only orders filled today (UTC)."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = self.get_historical_orders(limit=50)
        items = data.get("items", [])
        todays: List[Dict[str, Any]] = []
        for item in items:
            fill = item.get("fill", {})
            filled_at = fill.get("filledAt", "")
            if filled_at.startswith(today_str):
                todays.append(item)
        return todays

    def get_todays_dividends(self) -> List[Dict[str, Any]]:
        """Convenience: return only dividends paid today (UTC)."""
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        data = self.get_dividends(limit=50)
        items = data.get("items", [])
        return [
            d for d in items if d.get("paidOn", "").startswith(today_str)
        ]
