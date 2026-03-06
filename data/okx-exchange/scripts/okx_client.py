"""OKX V5 API Client"""
import hmac
import base64
import hashlib
import json
import os
import time
from datetime import datetime, timezone
from typing import Any
import requests

from config import load_prefs
from errors import NetworkError, APIError
from okx_ws_client import get_feed, get_private_feed

def _load_env() -> None:
    env_file = os.path.expanduser("~/.openclaw/workspace/.env")
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

BASE_URL = os.getenv("OKX_API_URL", "https://www.okx.com")

_time_offset: float = 0.0
_last_sync: float = 0.0


def _sync_time() -> None:
    """Fetch OKX server time and calculate offset. Cached for 5 minutes."""
    global _time_offset, _last_sync
    if time.time() - _last_sync < 300:
        return
    try:
        r = requests.get(f"{BASE_URL}/api/v5/public/time", timeout=5)
        server_ms = int(r.json()["data"][0]["ts"])
        _time_offset = server_ms / 1000 - time.time()
        _last_sync = time.time()
    except Exception:
        _time_offset = 0.0


def _timestamp() -> str:
    t = datetime.fromtimestamp(time.time() + _time_offset, tz=timezone.utc)
    return t.strftime("%Y-%m-%dT%H:%M:%S.") + str(t.microsecond // 1000).zfill(3) + "Z"


def _sign(ts: str, method: str, path: str, body: str, secret: str) -> str:
    msg = ts + method.upper() + path + body
    return base64.b64encode(
        hmac.new(secret.encode(), msg.encode(), hashlib.sha256).digest()
    ).decode()


class OKXClient:
    def __init__(self):
        mode = load_prefs().get("mode", "demo")
        if mode == "live":
            self.api_key = os.getenv("OKX_API_KEY_LIVE", "")
            self.secret = os.getenv("OKX_SECRET_KEY_LIVE", "")
            self.passphrase = os.getenv("OKX_PASSPHRASE_LIVE", "")
            self.simulated = False
        else:
            self.api_key = os.getenv("OKX_API_KEY", "")
            self.secret = os.getenv("OKX_SECRET_KEY", "")
            self.passphrase = os.getenv("OKX_PASSPHRASE", "")
            self.simulated = os.getenv("OKX_SIMULATED", "0") == "1"
        _sync_time()

    def _headers(self, method: str, path: str, body: str = "") -> dict:
        ts = _timestamp()
        return {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": _sign(ts, method, path, body, self.secret),
            "OK-ACCESS-TIMESTAMP": ts,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
            "OK-ACCESS-SBE": "0",
            "x-simulated-trading": "1" if self.simulated else "0",
            "Content-Type": "application/json",
        }

    def _request(self, method: str, full_path: str, data: str = None) -> dict:
        url = BASE_URL + full_path
        _retryable = (
            requests.exceptions.SSLError,
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
        )
        for attempt in range(3):
            try:
                headers = self._headers(method, full_path, data or "")
                if method == "GET":
                    r = requests.get(url, headers=headers, timeout=10)
                else:
                    r = requests.post(url, headers=headers, data=data, timeout=10)
                if not r.ok:
                    try:
                        err = r.json()
                        raise APIError(
                            f"OKX {r.status_code}: code={err.get('code')} msg={err.get('msg')}",
                            code=str(err.get("code", "")),
                            status=r.status_code,
                        )
                    except (ValueError, KeyError):
                        raise APIError(f"HTTP {r.status_code}", status=r.status_code)
                return r.json()
            except _retryable as e:
                if attempt == 2:
                    raise NetworkError(str(e)) from e
                time.sleep(0.5 * (attempt + 1))

    def get(self, path: str, params: dict = None) -> dict:
        qs = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
        return self._request("GET", path + qs)

    def post(self, path: str, body: dict) -> dict:
        return self._request("POST", path, json.dumps(body))

    # ── Market Data (no auth needed) ──────────────────────────────────────────

    def ticker(self, inst_id: str) -> dict:
        feed = get_feed()
        if feed:
            feed.subscribe_tickers([inst_id])
            cached = feed.get_ticker(inst_id)
            if cached:
                return {"code": "0", "data": [cached]}
        return self.get("/api/v5/market/ticker", {"instId": inst_id})

    def tickers(self, inst_type: str) -> dict:
        """Fetch all tickers for a given instrument type (SPOT/SWAP/FUTURES)."""
        return self.get("/api/v5/market/tickers", {"instType": inst_type.upper()})

    def candles(self, inst_id: str, bar: str = "1H", limit: int = 100) -> dict:
        feed = get_feed()
        if feed:
            feed.subscribe_candles([inst_id], bar)
            cached = feed.get_candles(inst_id, bar)
            if cached and len(cached) >= limit:
                return {"code": "0", "data": cached[:limit]}
        # REST fallback — also seeds the WS cache so future calls hit the cache
        result = self.get("/api/v5/market/candles", {"instId": inst_id, "bar": bar, "limit": limit})
        if feed and result.get("code") == "0":
            for row in reversed(result["data"]):  # oldest→newest so deque order is correct
                feed._update_candle(inst_id, bar, row)
        return result

    def orderbook(self, inst_id: str, sz: int = 20) -> dict:
        return self.get("/api/v5/market/books", {"instId": inst_id, "sz": sz})

    def instruments(self, inst_type: str) -> dict:
        return self.get("/api/v5/public/instruments", {"instType": inst_type})

    def funding_rate(self, inst_id: str) -> dict:
        return self.get("/api/v5/public/funding-rate", {"instId": inst_id})

    # ── Account ──────────────────────────────────────────────────────────────

    def balance(self, ccy: str = "") -> dict:
        pfeed = get_private_feed()
        if pfeed:
            cached = pfeed.get_account()
            if cached:
                details = [v for v in cached.values() if not ccy or v.get("ccy") == ccy]
                if details:
                    return {"code": "0", "data": [{"details": details}]}
        p = {"ccy": ccy} if ccy else {}
        return self.get("/api/v5/account/balance", p)

    def positions(self, inst_type: str = "", inst_id: str = "") -> dict:
        pfeed = get_private_feed()
        if pfeed:
            cached = pfeed.get_positions()
            if cached:
                positions = list(cached.values())
                if inst_id:
                    positions = [p for p in positions if p.get("instId") == inst_id]
                if inst_type:
                    positions = [p for p in positions if p.get("instType") == inst_type]
                return {"code": "0", "data": positions}
        p = {}
        if inst_type:
            p["instType"] = inst_type
        if inst_id:
            p["instId"] = inst_id
        return self.get("/api/v5/account/positions", p)

    def account_config(self) -> dict:
        return self.get("/api/v5/account/config")

    # ── Trading ──────────────────────────────────────────────────────────────

    def place_order(self, inst_id: str, td_mode: str, side: str, ord_type: str,
                    sz: str, px: str = "", reduce_only: bool = False,
                    pos_side: str = "", tp_trigger_px: str = "",
                    tp_ord_px: str = "", sl_trigger_px: str = "",
                    sl_ord_px: str = "") -> dict:
        body: dict[str, Any] = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
        }
        if px:
            body["px"] = px
        if reduce_only:
            body["reduceOnly"] = "true"
        if pos_side:
            body["posSide"] = pos_side
        if tp_trigger_px or sl_trigger_px:
            algo: dict[str, Any] = {}
            if tp_trigger_px:
                algo["tpTriggerPx"] = tp_trigger_px
                algo["tpOrdPx"] = tp_ord_px or "-1"
                algo["tpTriggerPxType"] = "last"
            if sl_trigger_px:
                algo["slTriggerPx"] = sl_trigger_px
                algo["slOrdPx"] = sl_ord_px or "-1"
                algo["slTriggerPxType"] = "last"
            body["attachAlgoOrds"] = [algo]
        return self.post("/api/v5/trade/order", body)

    def cancel_order(self, inst_id: str, ord_id: str) -> dict:
        return self.post("/api/v5/trade/cancel-order", {"instId": inst_id, "ordId": ord_id})

    def cancel_all_orders(self, inst_id: str) -> dict:
        pending = self.pending_orders(inst_id)
        results = []
        for o in pending.get("data", []):
            results.append(self.cancel_order(inst_id, o["ordId"]))
        succeeded = sum(1 for r in results if r.get("code") == "0")
        failed = len(results) - succeeded
        return {"cancelled": succeeded, "failed": failed, "results": results}

    def amend_order(self, inst_id: str, ord_id: str, new_sz: str = "", new_px: str = "") -> dict:
        body: dict[str, Any] = {"instId": inst_id, "ordId": ord_id}
        if new_sz:
            body["newSz"] = new_sz
        if new_px:
            body["newPx"] = new_px
        return self.post("/api/v5/trade/amend-order", body)

    def pending_orders(self, inst_id: str = "", inst_type: str = "") -> dict:
        p = {}
        if inst_id:
            p["instId"] = inst_id
        if inst_type:
            p["instType"] = inst_type
        return self.get("/api/v5/trade/orders-pending", p)

    def order_history(self, inst_type: str, inst_id: str = "", limit: int = 20) -> dict:
        p: dict[str, Any] = {"instType": inst_type, "limit": limit}
        if inst_id:
            p["instId"] = inst_id
        return self.get("/api/v5/trade/orders-history", p)

    def set_leverage(self, inst_id: str, lever: int, mg_mode: str = "cross", pos_side: str = "") -> dict:
        body: dict[str, Any] = {"instId": inst_id, "lever": str(lever), "mgnMode": mg_mode}
        if pos_side:
            body["posSide"] = pos_side
        return self.post("/api/v5/account/set-leverage", body)

    def position_risk(self, inst_type: str = "") -> dict:
        """Fetch position risk data including liquidation price per position."""
        p = {"instType": inst_type} if inst_type else {}
        return self.get("/api/v5/account/position-risk", p)

    # ── Algo Orders ───────────────────────────────────────────────────────────

    def place_algo_order(self, inst_id: str, td_mode: str, side: str,
                         ord_type: str, sz: str,
                         tp_trigger_px: str = "", tp_ord_px: str = "",
                         sl_trigger_px: str = "", sl_ord_px: str = "",
                         pos_side: str = "", reduce_only: bool = False) -> dict:
        """Place a standalone algo order (conditional / oco).

        ord_type:
          'conditional' — single TP or SL trigger
          'oco'         — TP + SL together; whichever triggers first cancels the other
        """
        body: dict[str, Any] = {
            "instId": inst_id,
            "tdMode": td_mode,
            "side": side,
            "ordType": ord_type,
            "sz": sz,
        }
        if pos_side:
            body["posSide"] = pos_side
        if reduce_only:
            body["reduceOnly"] = "true"
        if tp_trigger_px:
            body["tpTriggerPx"] = tp_trigger_px
            body["tpOrdPx"] = tp_ord_px or "-1"
            body["tpTriggerPxType"] = "last"
        if sl_trigger_px:
            body["slTriggerPx"] = sl_trigger_px
            body["slOrdPx"] = sl_ord_px or "-1"
            body["slTriggerPxType"] = "last"
        return self.post("/api/v5/trade/order-algo", body)

    def cancel_algo_order(self, inst_id: str, algo_id: str) -> dict:
        """Cancel a pending algo order by algoId."""
        return self.post("/api/v5/trade/cancel-algos",
                         [{"instId": inst_id, "algoId": algo_id}])

    def pending_algo_orders(self, inst_id: str = "", ord_type: str = "") -> dict:
        """Fetch pending algo orders (conditional / oco / trigger / iceberg / twap)."""
        p: dict[str, Any] = {"ordType": ord_type} if ord_type else {}
        if inst_id:
            p["instId"] = inst_id
        return self.get("/api/v5/trade/orders-algo-pending", p)

    # ── Batch Orders ──────────────────────────────────────────────────────────

    def batch_orders(self, orders: list[dict]) -> dict:
        """Place up to 20 orders in a single request.

        Each element of `orders` is a dict with the same fields as place_order().
        Returns a list of results, one per order.
        """
        return self.post("/api/v5/trade/batch-orders", orders)

    def transfer(self, ccy: str, amt: str, from_: str, to: str) -> dict:
        """from/to: 6=funding, 18=trading"""
        return self.post("/api/v5/asset/transfer", {
            "ccy": ccy, "amt": amt, "from": from_, "to": to, "type": "0"
        })
