#!/usr/bin/env python3
"""
example_agent.py — TWZRD Agent Template
========================================

Minimal working skeleton for an autonomous TWZRD prediction market agent.

Auth: Ed25519 wallet-signed JWT (24h TTL, auto-refreshed)
  GET  /v1/agent/challenge  → nonce
  POST /v1/agent/verify     → JWT

Usage:
  pip install -r requirements.txt
  cp .env.example .env && $EDITOR .env
  python example_agent.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import aiohttp
import base58
import nacl.signing
from dotenv import load_dotenv

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("wzrd_agent")

# ── Config ────────────────────────────────────────────────────────────────────

load_dotenv()


def _require(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        log.error(f"Required env var {name!r} is not set. See .env.example.")
        sys.exit(1)
    return v


def _opt(name: str, default: str) -> str:
    return (os.getenv(name) or default).strip()


def _parse_signing_key(raw: str) -> nacl.signing.SigningKey:
    """Parse Ed25519 signing key from base58, JSON array, or hex."""
    raw = raw.strip()
    # JSON array format (Solana keypair file — 64 bytes: seed + pubkey)
    if raw.startswith("["):
        arr = json.loads(raw)
        return nacl.signing.SigningKey(bytes(arr[:32]))
    # Hex format (64 or 128 chars)
    if all(c in "0123456789abcdefABCDEF" for c in raw) and len(raw) in (64, 128):
        return nacl.signing.SigningKey(bytes.fromhex(raw)[:32])
    # Base58 format (Phantom export or raw 32-byte seed)
    decoded = base58.b58decode(raw)
    return nacl.signing.SigningKey(decoded[:32])


API_BASE       = _opt("WZRD_API_BASE", "https://api.twzrd.xyz").rstrip("/")
POLL_INTERVAL  = int(_opt("WZRD_POLL_INTERVAL", "60"))
STAKE_PER_BET  = int(_opt("WZRD_STAKE_PER_BET", "50"))

SIGNING_KEY    = _parse_signing_key(_require("WZRD_PRIVATE_KEY"))
WALLET         = base58.b58encode(bytes(SIGNING_KEY.verify_key)).decode()
DOMAIN         = "twzrd.xyz"

# ── Auth ──────────────────────────────────────────────────────────────────────

@dataclass
class _Token:
    jwt: str
    expires_at: float  # Unix timestamp


class AgentAuth:
    """Obtains and auto-refreshes the 24h agent JWT.

    Canonical message (must match backend exactly):
      "ccm-agent-auth v1 | wallet:{wallet} | nonce:{nonce} | domain:twzrd.xyz"
    Signature: raw Ed25519 bytes, base58-encoded.
    """

    REFRESH_MARGIN = 300  # refresh 5 min before expiry

    def __init__(self, http: aiohttp.ClientSession) -> None:
        self._http = http
        self._token: Optional[_Token] = None
        self._lock = asyncio.Lock()

    async def bearer(self) -> str:
        async with self._lock:
            now = time.time()
            if self._token and self._token.expires_at > now + self.REFRESH_MARGIN:
                return f"Bearer {self._token.jwt}"
            self._token = await self._authenticate()
            return f"Bearer {self._token.jwt}"

    async def _authenticate(self) -> _Token:
        log.info("auth: requesting challenge")
        async with self._http.get(f"{API_BASE}/v1/agent/challenge") as r:
            if r.status != 200:
                raise RuntimeError(f"challenge {r.status}: {await r.text()}")
            nonce: str = (await r.json())["nonce"]

        msg = f"ccm-agent-auth v1 | wallet:{WALLET} | nonce:{nonce} | domain:{DOMAIN}"
        sig_b58 = base58.b58encode(SIGNING_KEY.sign(msg.encode()).signature).decode()

        log.info("auth: verifying signature")
        async with self._http.post(
            f"{API_BASE}/v1/agent/verify",
            json={"wallet": WALLET, "message": msg, "signature": sig_b58},
        ) as r:
            if r.status != 200:
                raise RuntimeError(f"verify {r.status}: {await r.text()}")
            body = await r.json()

        dt = datetime.fromisoformat(body["expires_at"].replace("Z", "+00:00"))
        log.info(f"auth: JWT issued  wallet={WALLET[:8]}...  expires={body['expires_at']}")
        return _Token(jwt=body["token"], expires_at=dt.timestamp())


# ── API Client ────────────────────────────────────────────────────────────────

class WzrdClient:
    def __init__(self, http: aiohttp.ClientSession, auth: AgentAuth) -> None:
        self._http = http
        self._auth = auth

    async def markets(self, status: str = "open", limit: int = 100) -> list[dict]:
        async with self._http.get(
            f"{API_BASE}/v2/markets", params={"status": status, "limit": str(limit)}
        ) as r:
            if r.status != 200:
                raise RuntimeError(f"markets {r.status}: {await r.text()}")
            return (await r.json()).get("markets", [])

    async def predict(self, market_id: str, outcome: bool, amount: int) -> dict:
        auth = await self._auth.bearer()
        async with self._http.post(
            f"{API_BASE}/v1/predictions",
            headers={"Authorization": auth},
            json={"market_id": market_id, "predicted_outcome": outcome, "amount": amount},
        ) as r:
            body = await r.json()
            if r.status not in (200, 201):
                raise RuntimeError(f"predict {r.status}: {json.dumps(body)}")
            return body

    async def my_predictions(self) -> list[dict]:
        auth = await self._auth.bearer()
        async with self._http.get(
            f"{API_BASE}/v1/predictions/me",
            headers={"Authorization": auth},
        ) as r:
            if r.status != 200:
                raise RuntimeError(f"my_predictions {r.status}: {await r.text()}")
            return (await r.json()).get("predictions", [])

    async def me(self) -> dict:
        """GET /v1/agent/me — returns user_id, wallet, balance, open_predictions."""
        auth = await self._auth.bearer()
        async with self._http.get(
            f"{API_BASE}/v1/agent/me",
            headers={"Authorization": auth},
        ) as r:
            if r.status != 200:
                raise RuntimeError(f"me {r.status}: {await r.text()}")
            return await r.json()

    async def points(self, user_id: str) -> dict:
        async with self._http.get(f"{API_BASE}/v1/points/{user_id}") as r:
            if r.status != 200:
                raise RuntimeError(f"points {r.status}: {await r.text()}")
            return await r.json()

    async def propose_market(
        self, market_type: str, subject_id: str, threshold: float,
        period_start: str | None = None, period_end: str | None = None,
        question: str | None = None,
    ) -> dict:
        """POST /v1/agent/markets/propose — create a market (3/hr rate limit)."""
        auth = await self._auth.bearer()
        body: dict = {"market_type": market_type, "subject_id": subject_id, "threshold": threshold}
        if period_start:
            body["period_start"] = period_start
        if period_end:
            body["period_end"] = period_end
        if question:
            body["question"] = question
        async with self._http.post(
            f"{API_BASE}/v1/agent/markets/propose",
            headers={"Authorization": auth},
            json=body,
        ) as r:
            resp = await r.json()
            if r.status not in (200, 201):
                raise RuntimeError(f"propose_market {r.status}: {json.dumps(resp)}")
            return resp

    async def trades(self, limit: int = 50, cursor: int | None = None,
                     market_type: str | None = None) -> dict:
        """GET /v2/markets/trades — public trade feed with cursor pagination."""
        params: dict = {"limit": str(limit)}
        if cursor:
            params["cursor"] = str(cursor)
        if market_type:
            params["market_type"] = market_type
        async with self._http.get(f"{API_BASE}/v2/markets/trades", params=params) as r:
            if r.status != 200:
                raise RuntimeError(f"trades {r.status}: {await r.text()}")
            return await r.json()

    async def leaderboard(self, window: str = "all") -> dict:
        """GET /v1/leaderboard — ranked performance by profit."""
        async with self._http.get(
            f"{API_BASE}/v1/leaderboard", params={"window": window}
        ) as r:
            if r.status != 200:
                raise RuntimeError(f"leaderboard {r.status}: {await r.text()}")
            return await r.json()


# ── Strategy ──────────────────────────────────────────────────────────────────

def pick_outcome(market: dict) -> bool:
    """
    TODO: implement your prediction logic here.

    Inputs available on each market dict:
      market["market_type"]       — e.g. "stream_still_live", "stream_viewer_count_gt"
      market["implied_probability"] — fraction of stakes currently on YES (0.0–1.0)
      market["odds_yes"]          — payout multiplier if YES wins
      market["odds_no"]           — payout multiplier if NO wins
      market["yes_count"]         — number of YES predictions
      market["no_count"]          — number of NO predictions
      market["parameters"]        — market-specific data (thresholds, session age, etc.)
      market["closes_at"]         — ISO8601 close time

    Parimutuel payout:
      Lower implied_probability on your side = higher multiplier = better expected value
      if your edge on that side exceeds the market's implied probability.

    Return True for YES, False for NO.
    """
    # Default: always YES — replace with your actual strategy
    return True


def should_enter(market: dict) -> bool:
    """
    TODO: implement your market filter here.

    Filter out markets you don't want to trade. Common filters:
      - market closes too soon (check market["closes_at"])
      - market type not supported
      - already have a position (tracked in predicted set)
      - odds not favorable given your edge estimate

    Return True to enter, False to skip.
    """
    # Default: accept all open markets — replace with your actual filter
    return market.get("status") == "open"


# ── Main loop ─────────────────────────────────────────────────────────────────

async def tick(
    client: WzrdClient,
    predicted: set[str],
    user_id: str,
) -> None:
    # Log current balance via /v1/agent/me (single call: balance + open positions)
    try:
        me = await client.me()
        log.info(
            f"balance={me.get('balance', 0)}  open_predictions={me.get('open_predictions', 0)}"
        )
    except Exception as e:
        log.warning(f"me: {e}")

    # Refresh prediction history to track open positions
    try:
        history = await client.my_predictions()
        for p in history:
            predicted.add(str(p["market_id"]))
    except Exception as e:
        log.warning(f"my_predictions: {e}")

    # Fetch and filter markets
    try:
        markets = await client.markets()
    except Exception as e:
        log.error(f"markets: {e}")
        return

    log.info(f"fetched {len(markets)} open markets")

    for m in markets:
        mid = str(m["id"])
        if mid in predicted:
            continue
        if not should_enter(m):
            continue

        outcome = pick_outcome(m)
        side = "YES" if outcome else "NO"

        try:
            result = await client.predict(mid, outcome, STAKE_PER_BET)
            predicted.add(mid)
            log.info(
                f"predicted  market={mid}  side={side}  amount={STAKE_PER_BET}  "
                f"pred_id={result.get('prediction_id', '?')}"
            )
        except RuntimeError as e:
            if "409" in str(e):
                predicted.add(mid)  # already have a position
            else:
                log.warning(f"predict market={mid}: {e}")


async def main() -> None:
    log.info("=" * 60)
    log.info("TWZRD Agent")
    log.info(f"  wallet   : {WALLET}")
    log.info(f"  api_base : {API_BASE}")
    log.info(f"  interval : {POLL_INTERVAL}s")
    log.info(f"  stake    : {STAKE_PER_BET} points/bet")
    log.info("=" * 60)

    timeout = aiohttp.ClientTimeout(total=30)
    connector = aiohttp.TCPConnector(limit=10, ssl=True)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as http:
        auth = AgentAuth(http)
        client = WzrdClient(http, auth)

        # Warm up auth — fail fast if key is invalid, fetch identity on startup
        try:
            await auth.bearer()
            me = await client.me()
            user_id = me["user_id"]
            log.info(
                f"auth OK  user_id={user_id}  balance={me.get('balance', 0)}pts"
                f"  display={me.get('display_name', '?')}"
            )
        except Exception as e:
            log.error(f"startup failed: {e}")
            sys.exit(1)

        predicted: set[str] = set()
        iteration = 0

        while True:
            iteration += 1
            log.info(f"── tick #{iteration} ──────────────────")
            try:
                await tick(client, predicted, user_id)
            except Exception as e:
                log.error(f"tick error: {e}", exc_info=True)
            log.info(f"sleeping {POLL_INTERVAL}s")
            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("shutdown")
