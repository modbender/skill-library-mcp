"""OKX WebSocket feed — runs in background thread, maintains a local data cache.

Activated via OKX_WS=1 environment variable.
OKXClient.ticker() and OKXClient.candles() read from this cache transparently.

Private feed (OKXPrivateWebSocketFeed) streams real-time account/positions/orders
and is activated when API credentials are available.
"""
import base64
import hashlib
import hmac
import json
import os
import threading
import time
from collections import deque
from typing import Optional

import websocket

from logger import get_logger

log = get_logger("okx.ws")

_WS_PUBLIC = "wss://ws.okx.com:8443/ws/v5/public"
_WS_PUBLIC_SIM = "wss://wspap.okx.com:8443/ws/v5/public?brokerId=9999"
_WS_PRIVATE = "wss://ws.okx.com:8443/ws/v5/private"
_WS_PRIVATE_SIM = "wss://wspap.okx.com:8443/ws/v5/private?brokerId=9999"

_PING_INTERVAL = 25  # OKX requires ping every 30s; send at 25s to be safe


class OKXWebSocketFeed:
    """Singleton background WebSocket feed.

    Subscribes to ticker and candle channels for a given instrument list.
    Data is stored in thread-safe caches and read by OKXClient methods.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._ticker_cache: dict = {}       # inst_id → latest ticker dict
        self._candle_cache: dict = {}       # (inst_id, bar) → deque of candle rows
        self._subscriptions: list = []      # list of {"channel":…, "instId":…}
        self._ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = threading.Event()
        self._running = False
        self._simulated = os.getenv("OKX_SIMULATED", "0") == "1"

    # ── Public API ────────────────────────────────────────────────────────────

    def subscribe_tickers(self, inst_ids: list[str]) -> None:
        for inst_id in inst_ids:
            arg = {"channel": "tickers", "instId": inst_id}
            if arg not in self._subscriptions:
                self._subscriptions.append(arg)
                if self._connected.is_set():
                    self._send({"op": "subscribe", "args": [arg]})

    def subscribe_candles(self, inst_ids: list[str], bar: str = "1H") -> None:
        # Simulated trading WS does not support candle channels
        if self._simulated:
            return
        channel = f"candle{bar}"
        for inst_id in inst_ids:
            arg = {"channel": channel, "instId": inst_id}
            if arg not in self._subscriptions:
                self._subscriptions.append(arg)
                if self._connected.is_set():
                    self._send({"op": "subscribe", "args": [arg]})

    def get_ticker(self, inst_id: str) -> Optional[dict]:
        with self._lock:
            return self._ticker_cache.get(inst_id)

    def get_candles(self, inst_id: str, bar: str = "1H") -> Optional[list]:
        """Return candle rows in OKX REST format (newest first), or None if not cached."""
        with self._lock:
            key = (inst_id, bar)
            dq = self._candle_cache.get(key)
            if dq:
                return list(dq)  # newest first (same order as REST API)
        return None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        # Give it a moment to connect before callers proceed
        self._connected.wait(timeout=5)

    def stop(self) -> None:
        self._running = False
        if self._ws:
            self._ws.close()

    def wait_ready(self, timeout: float = 5.0) -> bool:
        return self._connected.wait(timeout=timeout)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _url(self) -> str:
        return _WS_PUBLIC_SIM if self._simulated else _WS_PUBLIC

    def _run_loop(self) -> None:
        while self._running:
            try:
                self._connect()
            except Exception as e:
                log.warning(f"WS error: {e}. Reconnecting in 5s…")
            if self._running:
                time.sleep(5)

    def _connect(self) -> None:
        self._connected.clear()
        self._ws = websocket.WebSocketApp(
            self._url(),
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws.run_forever(ping_interval=_PING_INTERVAL, ping_timeout=10)

    def _on_open(self, ws) -> None:
        log.info(f"WS connected ({'simulated' if self._simulated else 'live'})")
        self._connected.set()
        if self._subscriptions:
            self._send({"op": "subscribe", "args": self._subscriptions})

    def _on_message(self, ws, raw: str) -> None:
        if raw == "pong":
            return
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return

        event = msg.get("event")
        if event == "subscribe":
            log.debug(f"WS subscribed: {msg.get('arg')}")
            return
        if event == "error":
            log.warning(f"WS error event: {msg.get('msg')}")
            return

        arg = msg.get("arg", {})
        data = msg.get("data", [])
        channel = arg.get("channel", "")
        inst_id = arg.get("instId", "")

        if channel == "tickers" and data:
            self._update_ticker(inst_id, data[0])
        elif channel.startswith("candle") and data:
            bar = channel[len("candle"):]
            self._update_candle(inst_id, bar, data[0])

    def _on_error(self, ws, error) -> None:
        log.warning(f"WS error: {error}")
        self._connected.clear()

    def _on_close(self, ws, code, msg) -> None:
        log.info(f"WS closed (code={code})")
        self._connected.clear()

    def _send(self, payload: dict) -> None:
        try:
            if self._ws:
                self._ws.send(json.dumps(payload))
        except Exception as e:
            log.warning(f"WS send failed: {e}")

    def _update_ticker(self, inst_id: str, data: dict) -> None:
        with self._lock:
            self._ticker_cache[inst_id] = data

    def _update_candle(self, inst_id: str, bar: str, row: list) -> None:
        """OKX candle row: [ts, open, high, low, close, vol, volCcy, …]
        Stored in a deque (newest first, max 300 rows per symbol/bar).
        """
        key = (inst_id, bar)
        with self._lock:
            if key not in self._candle_cache:
                self._candle_cache[key] = deque(maxlen=300)
            dq = self._candle_cache[key]
            ts = row[0]
            # Replace the most-recent (in-progress) candle if same timestamp
            if dq and dq[0][0] == ts:
                dq[0] = row
            else:
                dq.appendleft(row)


# ── Public feed singleton ─────────────────────────────────────────────────────

_feed: Optional[OKXWebSocketFeed] = None
_feed_lock = threading.Lock()


def get_feed() -> Optional[OKXWebSocketFeed]:
    """Return the running WS feed, or None if OKX_WS is not enabled."""
    if os.getenv("OKX_WS", "0") != "1":
        return None
    global _feed
    with _feed_lock:
        if _feed is None:
            _feed = OKXWebSocketFeed()
            _feed.start()
    return _feed


# ── Private WebSocket Feed ────────────────────────────────────────────────────

class OKXPrivateWebSocketFeed:
    """Authenticated private WebSocket feed for real-time account/positions/orders.

    Requires OKX_WS=1 plus valid API credentials.
    Channels: account, positions, orders.
    """

    def __init__(self, api_key: str, secret: str, passphrase: str, simulated: bool = False):
        self._api_key = api_key
        self._secret = secret
        self._passphrase = passphrase
        self._simulated = simulated
        self._lock = threading.Lock()
        self._account_cache: dict = {}          # ccy → balance dict
        self._positions_cache: dict = {}        # inst_id → position dict
        self._orders_cache: dict = {}           # ord_id → order dict (last 50)
        self._ws: Optional[websocket.WebSocketApp] = None
        self._thread: Optional[threading.Thread] = None
        self._connected = threading.Event()
        self._logged_in = threading.Event()
        self._running = False

    # ── Public API ────────────────────────────────────────────────────────────

    def get_positions(self) -> dict:
        """Return cached positions dict {inst_id: position_data}."""
        with self._lock:
            return dict(self._positions_cache)

    def get_account(self) -> dict:
        """Return cached account balances {ccy: balance_data}."""
        with self._lock:
            return dict(self._account_cache)

    def get_orders(self) -> dict:
        """Return cached recent orders {ord_id: order_data}."""
        with self._lock:
            return dict(self._orders_cache)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._logged_in.wait(timeout=8)

    def stop(self) -> None:
        self._running = False
        if self._ws:
            self._ws.close()

    def wait_ready(self, timeout: float = 8.0) -> bool:
        return self._logged_in.wait(timeout=timeout)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _url(self) -> str:
        return _WS_PRIVATE_SIM if self._simulated else _WS_PRIVATE

    def _login_payload(self) -> dict:
        ts = str(int(time.time()))
        msg = ts + "GET" + "/users/self/verify"
        sign = base64.b64encode(
            hmac.new(self._secret.encode(), msg.encode(), hashlib.sha256).digest()
        ).decode()
        return {
            "op": "login",
            "args": [{"apiKey": self._api_key, "passphrase": self._passphrase,
                       "timestamp": ts, "sign": sign}],
        }

    def _run_loop(self) -> None:
        while self._running:
            try:
                self._connect()
            except Exception as e:
                log.warning(f"Private WS error: {e}. Reconnecting in 5s…")
            if self._running:
                time.sleep(5)

    def _connect(self) -> None:
        self._connected.clear()
        self._logged_in.clear()
        self._ws = websocket.WebSocketApp(
            self._url(),
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self._ws.run_forever(ping_interval=_PING_INTERVAL, ping_timeout=10)

    def _on_open(self, ws) -> None:
        log.info(f"Private WS connected ({'simulated' if self._simulated else 'live'})")
        self._connected.set()
        self._send(self._login_payload())

    def _on_message(self, ws, raw: str) -> None:
        if raw == "pong":
            return
        try:
            msg = json.loads(raw)
        except json.JSONDecodeError:
            return

        event = msg.get("event")
        if event == "login":
            if msg.get("code") == "0":
                log.info("Private WS login successful")
                self._logged_in.set()
                self._send({"op": "subscribe", "args": [
                    {"channel": "account"},
                    {"channel": "positions", "instType": "ANY"},
                    {"channel": "orders", "instType": "ANY"},
                ]})
            else:
                log.warning(f"Private WS login failed: {msg.get('msg')}")
            return
        if event == "subscribe":
            log.debug(f"Private WS subscribed: {msg.get('arg')}")
            return
        if event == "error":
            log.warning(f"Private WS error event: {msg.get('msg')}")
            return

        arg = msg.get("arg", {})
        data = msg.get("data", [])
        channel = arg.get("channel", "")

        if channel == "account" and data:
            self._update_account(data[0])
        elif channel == "positions" and data:
            for pos in data:
                self._update_position(pos)
        elif channel == "orders" and data:
            for order in data:
                self._update_order(order)

    def _on_error(self, ws, error) -> None:
        log.warning(f"Private WS error: {error}")
        self._connected.clear()

    def _on_close(self, ws, code, msg) -> None:
        log.info(f"Private WS closed (code={code})")
        self._connected.clear()
        self._logged_in.clear()

    def _send(self, payload: dict) -> None:
        try:
            if self._ws:
                self._ws.send(json.dumps(payload))
        except Exception as e:
            log.warning(f"Private WS send failed: {e}")

    def _update_account(self, data: dict) -> None:
        with self._lock:
            for detail in data.get("details", []):
                ccy = detail.get("ccy", "")
                if ccy:
                    self._account_cache[ccy] = detail

    def _update_position(self, pos: dict) -> None:
        with self._lock:
            inst_id = pos.get("instId", "")
            pos_side = pos.get("posSide", "net")
            key = f"{inst_id}:{pos_side}"
            if pos.get("pos", "0") == "0":
                self._positions_cache.pop(key, None)  # closed position
            else:
                self._positions_cache[key] = pos

    def _update_order(self, order: dict) -> None:
        with self._lock:
            ord_id = order.get("ordId", "")
            if ord_id:
                self._orders_cache[ord_id] = order
                # Keep only last 50 orders
                if len(self._orders_cache) > 50:
                    oldest = next(iter(self._orders_cache))
                    del self._orders_cache[oldest]


# ── Private feed singleton ────────────────────────────────────────────────────

_private_feed: Optional[OKXPrivateWebSocketFeed] = None
_private_feed_lock = threading.Lock()


def get_private_feed() -> Optional[OKXPrivateWebSocketFeed]:
    """Return the running private WS feed, or None if OKX_WS is not enabled or no credentials."""
    if os.getenv("OKX_WS", "0") != "1":
        return None
    from config import load_prefs
    prefs = load_prefs()
    mode = prefs.get("mode", "demo")
    if mode == "live":
        api_key = os.getenv("OKX_API_KEY_LIVE", "")
        secret = os.getenv("OKX_SECRET_KEY_LIVE", "")
        passphrase = os.getenv("OKX_PASSPHRASE_LIVE", "")
        simulated = False
    else:
        api_key = os.getenv("OKX_API_KEY", "")
        secret = os.getenv("OKX_SECRET_KEY", "")
        passphrase = os.getenv("OKX_PASSPHRASE", "")
        simulated = os.getenv("OKX_SIMULATED", "0") == "1"
    if not api_key:
        return None
    global _private_feed
    with _private_feed_lock:
        if _private_feed is None:
            _private_feed = OKXPrivateWebSocketFeed(api_key, secret, passphrase, simulated)
            _private_feed.start()
    return _private_feed
