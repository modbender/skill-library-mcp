#!/usr/bin/env python3
"""
Hyperliquid Caching Proxy Server

Transparent proxy that caches /info responses to reduce API weight usage.
The SDK just needs base_url pointed to localhost:18731.

Usage:
    python server.py                          # Start with defaults
    HL_PROXY_PORT=9999 python server.py       # Custom port
    HL_CACHE_WARMUP=false python server.py    # Skip cache warmup

Env vars:
    HL_UPSTREAM_URL  - Upstream API (default: https://api.hyperliquid.xyz)
    HL_PROXY_PORT    - Proxy port (default: 8888)
    HL_CACHE_WARMUP  - Pre-warm cache on startup (default: true)
"""

import asyncio
import json
import logging
import os
import time
from contextlib import asynccontextmanager
from threading import Lock

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

UPSTREAM_URL = os.getenv("HL_UPSTREAM_URL", "https://api.hyperliquid.xyz")
PROXY_PORT = int(os.getenv("HL_PROXY_PORT", "18731"))
CACHE_WARMUP = os.getenv("HL_CACHE_WARMUP", "true").lower() == "true"

# TTL per info type (seconds)
TTL_CONFIG: dict[str, int] = {
    # Heavy metadata — rarely changes
    "meta": 300,
    "spotMeta": 300,
    "perpDexs": 300,
    "userAbstraction": 300,
    "userDexAbstraction": 300,
    # Prices — need freshness
    "allMids": 5,
    "l2Book": 3,
    # User state — changes after trades
    "clearinghouseState": 2,
    "spotClearinghouseState": 2,
    "openOrders": 2,
    "frontendOpenOrders": 2,
    # Aggregated data
    "metaAndAssetCtxs": 10,
    "spotMetaAndAssetCtxs": 10,
    # User history
    "userFills": 5,
    "userFillsByTime": 5,
    # Reference data
    "fundingHistory": 30,
    "candleSnapshot": 10,
    "recentTrades": 5,
}
DEFAULT_TTL = 10  # For unknown info types

# User-scoped types (invalidated after /exchange)
USER_SCOPED_TYPES = {
    "clearinghouseState",
    "spotClearinghouseState",
    "openOrders",
    "frontendOpenOrders",
    "userFills",
    "userFillsByTime",
}

CLEANUP_INTERVAL = 60  # seconds

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("hl-proxy")

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------


class CacheEntry:
    __slots__ = ("body", "expires_at")

    def __init__(self, body: bytes, ttl: int):
        self.body = body
        self.expires_at = time.monotonic() + ttl


class ProxyCache:
    def __init__(self):
        self._store: dict[str, CacheEntry] = {}
        self._lock = Lock()
        # Reverse index: address -> set of cache keys
        self._user_keys: dict[str, set[str]] = {}
        # Stats
        self.hits: dict[str, int] = {}
        self.misses: dict[str, int] = {}

    def get(self, key: str, info_type: str) -> bytes | None:
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                self.misses[info_type] = self.misses.get(info_type, 0) + 1
                return None
            if time.monotonic() > entry.expires_at:
                del self._store[key]
                self.misses[info_type] = self.misses.get(info_type, 0) + 1
                return None
            self.hits[info_type] = self.hits.get(info_type, 0) + 1
            return entry.body

    def put(self, key: str, body: bytes, ttl: int, user: str | None = None):
        with self._lock:
            self._store[key] = CacheEntry(body, ttl)
            if user:
                self._user_keys.setdefault(user.lower(), set()).add(key)

    def invalidate_user(self, address: str):
        addr = address.lower()
        with self._lock:
            keys = self._user_keys.pop(addr, set())
            for k in keys:
                self._store.pop(k, None)
            count = len(keys)
        if count:
            log.info("Invalidated %d cache entries for %s", count, addr)

    def invalidate_user_scoped(self):
        """Fallback: clear all entries whose type is user-scoped."""
        with self._lock:
            to_delete = []
            for key in self._store:
                try:
                    payload = json.loads(key)
                    if payload.get("type") in USER_SCOPED_TYPES:
                        to_delete.append(key)
                except (json.JSONDecodeError, TypeError):
                    pass
            for k in to_delete:
                del self._store[k]
            if to_delete:
                log.info("Invalidated %d user-scoped cache entries", len(to_delete))

    def clear_by_type(self, info_type: str) -> int:
        with self._lock:
            to_delete = []
            for key in self._store:
                try:
                    payload = json.loads(key)
                    if payload.get("type") == info_type:
                        to_delete.append(key)
                except (json.JSONDecodeError, TypeError):
                    pass
            for k in to_delete:
                del self._store[k]
            return len(to_delete)

    def clear_all(self) -> int:
        with self._lock:
            count = len(self._store)
            self._store.clear()
            self._user_keys.clear()
            return count

    def sweep_expired(self) -> int:
        now = time.monotonic()
        with self._lock:
            expired = [k for k, v in self._store.items() if now > v.expires_at]
            for k in expired:
                del self._store[k]
            # Clean user reverse index
            for addr in list(self._user_keys):
                self._user_keys[addr] -= set(expired)
                if not self._user_keys[addr]:
                    del self._user_keys[addr]
            return len(expired)

    @property
    def size(self) -> int:
        return len(self._store)

    def stats(self) -> dict:
        total_hits = sum(self.hits.values())
        total_misses = sum(self.misses.values())
        total = total_hits + total_misses
        return {
            "entries": self.size,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate": f"{(total_hits / total * 100):.1f}%" if total > 0 else "0.0%",
            "by_type": {
                t: {
                    "hits": self.hits.get(t, 0),
                    "misses": self.misses.get(t, 0),
                }
                for t in sorted(set(list(self.hits.keys()) + list(self.misses.keys())))
            },
        }


# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------

cache = ProxyCache()
http_client: httpx.AsyncClient | None = None
start_time: float = 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def canonical_key(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def get_ttl(info_type: str) -> int:
    return TTL_CONFIG.get(info_type, DEFAULT_TTL)


def extract_user(payload: dict, headers: dict) -> str | None:
    """Extract user address from payload or headers."""
    # Check payload fields
    for field in ("user", "address"):
        if field in payload:
            return payload[field]
    # Check header (CLI can send this)
    return headers.get("x-hl-address")


# ---------------------------------------------------------------------------
# App lifecycle
# ---------------------------------------------------------------------------


async def warmup_cache():
    """Pre-fetch heavy metadata endpoints."""
    warmup_payloads = [
        {"type": "meta"},
        {"type": "spotMeta"},
        {"type": "perpDexs"},
        {"type": "allMids"},
    ]
    for payload in warmup_payloads:
        info_type = payload["type"]
        try:
            resp = await http_client.post(
                f"{UPSTREAM_URL}/info",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            if resp.status_code == 200:
                key = canonical_key(payload)
                ttl = get_ttl(info_type)
                cache.put(key, resp.content, ttl)
                log.info("Warmed cache: %s (TTL %ds)", info_type, ttl)
        except Exception as e:
            log.warning("Warmup failed for %s: %s", info_type, e)


async def cleanup_loop():
    """Periodically sweep expired entries."""
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        swept = cache.sweep_expired()
        if swept:
            log.debug("Swept %d expired entries", swept)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client, start_time
    start_time = time.time()

    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
    )
    log.info("Proxy started — upstream: %s, port: %d", UPSTREAM_URL, PROXY_PORT)

    if CACHE_WARMUP:
        await warmup_cache()

    cleanup_task = asyncio.create_task(cleanup_loop())

    yield

    cleanup_task.cancel()
    await http_client.aclose()
    log.info("Proxy stopped")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Hyperliquid Caching Proxy", lifespan=lifespan)


@app.post("/info")
async def proxy_info(request: Request):
    """Cached proxy for /info endpoint."""
    body = await request.body()
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    info_type = payload.get("type", "unknown")
    ttl = get_ttl(info_type)
    key = canonical_key(payload)

    # Check cache
    cached = cache.get(key, info_type)
    if cached is not None:
        return Response(
            content=cached,
            media_type="application/json",
            headers={"X-Cache": "HIT", "X-Cache-Type": info_type},
        )

    # Forward upstream
    try:
        resp = await http_client.post(
            f"{UPSTREAM_URL}/info",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    except httpx.TimeoutException:
        return JSONResponse(
            {"error": "Upstream timeout"}, status_code=502,
            headers={"X-Cache": "ERROR"},
        )
    except httpx.ConnectError:
        return JSONResponse(
            {"error": "Upstream connection failed"}, status_code=502,
            headers={"X-Cache": "ERROR"},
        )

    # Only cache 200 responses
    if resp.status_code == 200:
        user = extract_user(payload, dict(request.headers))
        cache.put(key, resp.content, ttl, user=user)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
        headers={"X-Cache": "MISS", "X-Cache-Type": info_type},
    )


@app.post("/exchange")
async def proxy_exchange(request: Request):
    """Pass-through for /exchange — never cached, invalidates user cache on success."""
    body = await request.body()

    try:
        resp = await http_client.post(
            f"{UPSTREAM_URL}/exchange",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    except httpx.TimeoutException:
        return JSONResponse({"error": "Upstream timeout"}, status_code=502)
    except httpx.ConnectError:
        return JSONResponse({"error": "Upstream connection failed"}, status_code=502)

    # Invalidate user cache on successful exchange
    if resp.status_code == 200:
        try:
            resp_data = resp.json()
            if resp_data.get("status") == "ok":
                # Try to find user address
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    payload = {}

                user = extract_user(payload, dict(request.headers))
                if user:
                    cache.invalidate_user(user)
                else:
                    cache.invalidate_user_scoped()
        except (json.JSONDecodeError, AttributeError):
            pass

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        media_type="application/json",
    )


@app.get("/health")
async def health():
    """Health check with proxy status."""
    uptime = time.time() - start_time
    return {
        "status": "ok",
        "upstream": UPSTREAM_URL,
        "cache_entries": cache.size,
        "uptime_seconds": int(uptime),
        "uptime_human": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m {int(uptime % 60)}s",
    }


@app.get("/cache/stats")
async def cache_stats():
    """Cache hit/miss statistics."""
    return cache.stats()


@app.post("/cache/clear")
async def cache_clear(request: Request):
    """Clear cache. Optional body: {"type": "..."} or {"user": "0x..."}."""
    try:
        body = await request.body()
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {}

    if "type" in payload:
        count = cache.clear_by_type(payload["type"])
        return {"cleared": count, "filter": {"type": payload["type"]}}
    elif "user" in payload:
        cache.invalidate_user(payload["user"])
        return {"cleared": "user_entries", "filter": {"user": payload["user"]}}
    else:
        count = cache.clear_all()
        return {"cleared": count, "filter": "all"}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=PROXY_PORT,
        log_level="info",
    )
