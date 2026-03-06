#!/usr/bin/env python3
"""
Standalone Kalshi API Client for Autopilot Trading

Uses persistent connection pooling, proper retry logic, and correct
RSA-PSS path signing (full /trade-api/v2 prefix required by Kalshi).

Usage:
    python kalshi_client.py balance
    python kalshi_client.py markets --series KXNBASPREAD
    python kalshi_client.py markets --query "Duke"
    python kalshi_client.py market KXNBASPREAD-26MAR02LACGSW-LAC1
    python kalshi_client.py positions
    python kalshi_client.py orders
"""

import os
import sys
import time
import base64
import json
import argparse
from typing import Dict, List, Optional, Any

try:
    import httpx
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.backends import default_backend
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Install with: pip install httpx cryptography python-dotenv")
    sys.exit(1)

# Load .env from skill root (one level up from scripts/)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_script_dir, "..", ".env")
load_dotenv(_env_path)
load_dotenv()  # Also check cwd


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class KalshiClient:
    """
    Kalshi API client with persistent HTTP connection, RSA-PSS auth,
    automatic retries, and pagination support.
    """

    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    SIGN_PREFIX = "/trade-api/v2"  # Kalshi requires full path in signature
    MAX_RETRIES = 2
    RETRY_DELAY = 1.0  # seconds between retries

    def __init__(self):
        self.api_key_id = os.getenv("KALSHI_API_KEY_ID", "").strip()
        self.private_key_pem = os.getenv("KALSHI_PRIVATE_KEY", "").strip()
        self._private_key = None
        self.debug = os.getenv("DEBUG", "").lower() in ("1", "true", "yes")

        # Persistent connection pool — reused across all API calls
        self._http: Optional[httpx.Client] = None

        if self.api_key_id and self.private_key_pem:
            self._load_private_key()

    # -- lifecycle ----------------------------------------------------------

    @property
    def http(self) -> httpx.Client:
        """Lazy-init persistent HTTP client with connection pooling."""
        if self._http is None or self._http.is_closed:
            self._http = httpx.Client(
                base_url=self.BASE_URL,
                timeout=httpx.Timeout(15.0, connect=10.0),
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            )
        return self._http

    def close(self):
        """Close the HTTP connection pool."""
        if self._http and not self._http.is_closed:
            self._http.close()

    def __del__(self):
        self.close()

    # -- auth ---------------------------------------------------------------

    def _load_private_key(self):
        pem = self.private_key_pem.replace("\\n", "\n").strip()
        if not pem.startswith("-----BEGIN"):
            raise ValueError("Invalid private key: missing BEGIN marker")
        self._private_key = serialization.load_pem_private_key(
            pem.encode(), password=None, backend=default_backend()
        )
        self._log("RSA private key loaded")

    def _sign(self, timestamp: str, method: str, path: str) -> str:
        msg = f"{timestamp}{method}{path}".encode()
        sig = self._private_key.sign(
            msg,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256(),
        )
        return base64.b64encode(sig).decode()

    # Portfolio endpoints do NOT include query strings in the signature.
    # Market/event endpoints DO include query strings.
    _SIGN_PATH_ONLY = frozenset([
        "/portfolio/balance",
        "/portfolio/positions",
        "/portfolio/orders",
    ])

    def _auth_headers(self, method: str, endpoint_path: str) -> Dict[str, str]:
        """
        Build auth headers.  `endpoint_path` is the path *after* BASE_URL,
        possibly including a query string (e.g. "/markets?limit=20").

        Kalshi quirk: portfolio endpoints sign path-only (no query string),
        while market/event endpoints sign path+query string.
        """
        ts = str(int(time.time() * 1000))

        # Strip query string for portfolio endpoints
        base_path = endpoint_path.split("?")[0]
        if base_path in self._SIGN_PATH_ONLY or base_path.startswith("/portfolio/orders/"):
            sign_target = f"{self.SIGN_PREFIX}{base_path}"
        else:
            sign_target = f"{self.SIGN_PREFIX}{endpoint_path}"

        return {
            "KALSHI-ACCESS-KEY": self.api_key_id,
            "KALSHI-ACCESS-SIGNATURE": self._sign(ts, method, sign_target),
            "KALSHI-ACCESS-TIMESTAMP": ts,
            "Content-Type": "application/json",
        }

    def is_configured(self) -> bool:
        return bool(self.api_key_id and self._private_key)

    # -- helpers ------------------------------------------------------------

    def _log(self, msg: str):
        if self.debug:
            print(f"[KALSHI] {msg}", file=sys.stderr)

    @staticmethod
    def _qs(params: Dict[str, str]) -> str:
        """Deterministic query-string (sorted keys for consistent signing)."""
        return "&".join(f"{k}={v}" for k, v in sorted(params.items()))

    def _get(self, path: str, params: Optional[Dict[str, str]] = None) -> Dict:
        """
        Authenticated GET with retry.  Returns parsed JSON dict.
        `path` is the endpoint path (e.g. "/markets").

        We build the query string ourselves and append it to the path so that
        the exact bytes we sign are the exact bytes sent on the wire.  This
        avoids any mismatch between our signing and httpx's own URL encoding.
        """
        if not self.is_configured():
            return {"_error": "Kalshi client not configured"}

        qs = self._qs(params) if params else ""
        sign_path = f"{path}?{qs}" if qs else path
        # Use the full path+qs for the actual request too (no separate params)
        request_path = sign_path

        for attempt in range(1, self.MAX_RETRIES + 2):
            headers = self._auth_headers("GET", sign_path)
            self._log(f"GET {sign_path} (attempt {attempt})")
            try:
                r = self.http.get(request_path, headers=headers)
                if r.status_code == 200:
                    return r.json()
                elif r.status_code in (429,):
                    wait = self.RETRY_DELAY * attempt
                    self._log(f"Rate limited, waiting {wait}s")
                    time.sleep(wait)
                    continue
                elif r.status_code == 401 and attempt <= self.MAX_RETRIES:
                    # Timestamp might be stale — regenerate and retry
                    self._log(f"401 auth error, retrying with fresh timestamp")
                    time.sleep(0.2)
                    continue
                else:
                    return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                if attempt <= self.MAX_RETRIES:
                    self._log(f"Retry after {exc.__class__.__name__}")
                    time.sleep(self.RETRY_DELAY)
                    continue
                return {"_error": str(exc)}
        return {"_error": "Max retries exceeded"}

    def _post(self, path: str, body: Dict) -> Dict:
        """Authenticated POST with retry."""
        if not self.is_configured():
            return {"_error": "Kalshi client not configured"}

        for attempt in range(1, self.MAX_RETRIES + 2):
            headers = self._auth_headers("POST", path)
            self._log(f"POST {path} (attempt {attempt})")
            try:
                r = self.http.post(path, json=body, headers=headers)
                if r.status_code in (200, 201):
                    return r.json()
                elif r.status_code == 429:
                    time.sleep(self.RETRY_DELAY * attempt)
                    continue
                elif r.status_code == 401 and attempt <= self.MAX_RETRIES:
                    time.sleep(0.2)
                    continue
                else:
                    return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
            except (httpx.TimeoutException, httpx.ConnectError) as exc:
                if attempt <= self.MAX_RETRIES:
                    time.sleep(self.RETRY_DELAY)
                    continue
                return {"_error": str(exc)}
        return {"_error": "Max retries exceeded"}

    def _delete(self, path: str) -> Dict:
        """Authenticated DELETE."""
        if not self.is_configured():
            return {"_error": "Kalshi client not configured"}
        headers = self._auth_headers("DELETE", path)
        try:
            r = self.http.delete(path, headers=headers)
            if r.status_code in (200, 204):
                return {"success": True}
            return {"_error": f"HTTP {r.status_code}: {r.text[:200]}"}
        except Exception as exc:
            return {"_error": str(exc)}

    # -- public API ---------------------------------------------------------

    def get_balance(self) -> Dict[str, Any]:
        """Account balance."""
        data = self._get("/portfolio/balance")
        if "_error" in data:
            return {"success": False, "error": data["_error"]}
        bal = data.get("balance", 0)
        return {
            "success": True,
            "balance_cents": bal,
            "balance_dollars": bal / 100,
            "portfolio_value": data.get("portfolio_value", 0) / 100,
        }

    def get_markets(self, limit: int = 100, status: str = "open",
                    series_ticker: Optional[str] = None,
                    event_ticker: Optional[str] = None,
                    cursor: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch markets (single page). Use get_all_markets() for pagination."""
        params = {"limit": str(limit), "status": status}
        if series_ticker:
            params["series_ticker"] = series_ticker
        if event_ticker:
            params["event_ticker"] = event_ticker
        if cursor:
            params["cursor"] = cursor
        data = self._get("/markets", params)
        if "_error" in data:
            print(f"❌ {data['_error']}", file=sys.stderr)
            return []
        return data.get("markets", [])

    def get_all_markets(self, series_ticker: Optional[str] = None,
                        event_ticker: Optional[str] = None,
                        status: str = "open",
                        max_pages: int = 5) -> List[Dict[str, Any]]:
        """Paginated market fetch — follows cursor up to max_pages."""
        all_mkts: List[Dict] = []
        cursor = None
        for page in range(max_pages):
            params: Dict[str, str] = {"limit": "200", "status": status}
            if series_ticker:
                params["series_ticker"] = series_ticker
            if event_ticker:
                params["event_ticker"] = event_ticker
            if cursor:
                params["cursor"] = cursor

            data = self._get("/markets", params)
            if "_error" in data:
                self._log(f"Page {page+1} error: {data['_error']}")
                break
            mkts = data.get("markets", [])
            all_mkts.extend(mkts)
            cursor = data.get("cursor")
            self._log(f"Page {page+1}: {len(mkts)} markets, cursor={'yes' if cursor else 'no'}")
            if not cursor:
                break
            time.sleep(0.3)  # Be nice to the API between pages
        return all_mkts

    def search_markets(self, query: str, series_ticker: Optional[str] = None,
                       limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search markets by text.  If `series_ticker` is given, search within
        that series; otherwise search across all open markets.
        """
        markets = self.get_all_markets(series_ticker=series_ticker)
        if not query:
            return markets[:limit]
        q = query.lower()
        return [m for m in markets
                if q in m.get("title", "").lower()
                or q in m.get("subtitle", "").lower()
                or q in m.get("ticker", "").lower()][:limit]

    def get_market(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch a single market by ticker."""
        data = self._get(f"/markets/{ticker}")
        if "_error" in data:
            return None
        return data.get("market", data)

    def get_events(self, limit: int = 50, status: str = "open",
                   series_ticker: Optional[str] = None) -> List[Dict]:
        params: Dict[str, str] = {"limit": str(limit), "status": status}
        if series_ticker:
            params["series_ticker"] = series_ticker
        data = self._get("/events", params)
        return data.get("events", []) if "_error" not in data else []

    # -- portfolio ----------------------------------------------------------

    def get_positions(self, limit: int = 200) -> List[Dict[str, Any]]:
        params = {"limit": str(limit)}
        data = self._get("/portfolio/positions", params)
        if "_error" in data:
            print(f"❌ {data['_error']}", file=sys.stderr)
            return []
        return data.get("market_positions", [])

    def get_orders(self, status: str = "resting", limit: int = 100) -> List[Dict]:
        params = {"limit": str(limit), "status": status}
        data = self._get("/portfolio/orders", params)
        if "_error" in data:
            print(f"❌ {data['_error']}", file=sys.stderr)
            return []
        return data.get("orders", [])

    def place_order(self, ticker: str, side: str, action: str, count: int,
                    order_type: str = "limit",
                    yes_price: Optional[int] = None) -> Dict[str, Any]:
        """
        Place an order.

        Args:
            ticker:     Market ticker
            side:       "yes" or "no"
            action:     "buy" or "sell"
            count:      Number of contracts (≥1)
            order_type: "limit" or "market"
            yes_price:  Price in cents 1-99 (required for limit)
        """
        if side not in ("yes", "no"):
            return {"success": False, "error": "side must be 'yes' or 'no'"}
        if action not in ("buy", "sell"):
            return {"success": False, "error": "action must be 'buy' or 'sell'"}
        if count < 1:
            return {"success": False, "error": "count must be ≥ 1"}
        if order_type == "limit" and yes_price is None:
            return {"success": False, "error": "yes_price required for limit orders"}
        if yes_price is not None and not (1 <= yes_price <= 99):
            return {"success": False, "error": "yes_price must be 1-99"}

        body: Dict[str, Any] = {
            "ticker": ticker, "side": side, "action": action,
            "count": count, "type": order_type,
        }
        if yes_price is not None:
            body["yes_price"] = yes_price

        data = self._post("/portfolio/orders", body)
        if "_error" in data:
            return {"success": False, "error": data["_error"]}
        order = data.get("order", {})
        return {
            "success": True,
            "order_id": order.get("order_id"),
            "ticker": order.get("ticker"),
            "status": order.get("status"),
            "side": order.get("side"),
            "action": order.get("action"),
            "count": order.get("remaining_count", order.get("count")),
            "yes_price": order.get("yes_price"),
        }

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        result = self._delete(f"/portfolio/orders/{order_id}")
        if "_error" in result:
            return {"success": False, "error": result["_error"]}
        return {"success": True, "order_id": order_id}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Kalshi API Client")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("balance", help="Account balance")

    mp = sub.add_parser("markets", help="List/search markets")
    mp.add_argument("--series", help="Series ticker (e.g. KXNBASPREAD)")
    mp.add_argument("--event", help="Event ticker")
    mp.add_argument("--query", "-q", help="Text search within results")
    mp.add_argument("--limit", type=int, default=50)

    dp = sub.add_parser("market", help="Single market details")
    dp.add_argument("ticker", help="Market ticker")

    sub.add_parser("positions", help="Current positions")

    op = sub.add_parser("orders", help="Open orders")
    op.add_argument("--status", default="resting")

    ep = sub.add_parser("events", help="List events")
    ep.add_argument("--series", help="Series ticker filter")
    ep.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return

    client = KalshiClient()
    if not client.is_configured():
        print("❌ Kalshi not configured. Set KALSHI_API_KEY_ID and KALSHI_PRIVATE_KEY in .env")
        sys.exit(1)

    try:
        if args.cmd == "balance":
            r = client.get_balance()
            if r["success"]:
                print(f"💰 Balance:         ${r['balance_dollars']:.2f}")
                print(f"📊 Portfolio Value:  ${r['portfolio_value']:.2f}")
            else:
                print(f"❌ {r['error']}")

        elif args.cmd == "markets":
            if args.query and not args.series:
                markets = client.search_markets(args.query, limit=args.limit)
            elif args.query and args.series:
                markets = client.search_markets(args.query, series_ticker=args.series, limit=args.limit)
            else:
                markets = client.get_all_markets(series_ticker=args.series, event_ticker=args.event)[:args.limit]

            print(f"📊 {len(markets)} markets:")
            for m in markets:
                yes = m.get("yes_ask", m.get("yes_price", m.get("last_price", "?")))
                vol = m.get("volume", 0)
                t = m.get("ticker", "")[:45]
                title = m.get("title", "")[:60]
                print(f"  {t:<45} YES:{yes:>3}¢  vol:{vol:>6,}  {title}")

        elif args.cmd == "market":
            m = client.get_market(args.ticker)
            if m:
                yes = m.get("yes_ask", m.get("yes_price", m.get("last_price", "?")))
                print(f"Ticker:    {m.get('ticker')}")
                print(f"Title:     {m.get('title')}")
                print(f"Subtitle:  {m.get('subtitle', '')}")
                print(f"YES:       {yes}¢   NO: {100-int(yes) if str(yes).isdigit() else '?'}¢")
                print(f"Volume:    {m.get('volume', 0):,}")
                print(f"OI:        {m.get('open_interest', 0):,}")
                print(f"Status:    {m.get('status')}")
                print(f"URL:       https://kalshi.com/markets/{m.get('ticker')}")
            else:
                print(f"❌ Not found: {args.ticker}")

        elif args.cmd == "positions":
            pos = client.get_positions()
            if pos:
                print(f"📈 {len(pos)} positions:")
                for p in pos:
                    ct = p.get("total_traded", p.get("position", 0))
                    print(f"  {p.get('ticker',''):<40} {ct:>4} contracts")
            else:
                print("📈 No positions")

        elif args.cmd == "orders":
            orders = client.get_orders(args.status)
            if orders:
                print(f"📋 {len(orders)} orders:")
                for o in orders:
                    print(f"  {o.get('ticker',''):<40} {o.get('action','').upper()} "
                          f"{o.get('side','').upper()} {o.get('remaining_count', o.get('count',0))} "
                          f"@ {o.get('yes_price','?')}¢  [{o.get('status','')}]")
            else:
                print("📋 No orders")

        elif args.cmd == "events":
            events = client.get_events(limit=args.limit, series_ticker=args.series)
            print(f"📅 {len(events)} events:")
            for e in events:
                print(f"  {e.get('event_ticker',''):<30} [{e.get('category','')}] {e.get('title','')[:60]}")

    finally:
        client.close()


if __name__ == "__main__":
    main()
