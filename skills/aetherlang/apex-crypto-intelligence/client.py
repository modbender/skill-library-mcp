"""
APEX Crypto Intelligence — Client Library
Auditable code showing exactly what data is sent to the API.

SECURITY GUARANTEE:
- Exchange API keys are loaded from environment variables LOCALLY
- Keys are used ONLY to authenticate with exchange APIs directly
- Keys are NEVER included in any payload sent to api.neurodoc.app
- Run `python client.py` to inspect the exact outbound payload

ENVIRONMENT VARIABLES (all optional):
  BINANCE_API_KEY, BINANCE_API_SECRET
  BYBIT_API_KEY, BYBIT_API_SECRET
  KUCOIN_API_KEY, KUCOIN_API_SECRET
  MEXC_API_KEY, MEXC_API_SECRET
  GATEIO_API_KEY, GATEIO_API_SECRET
"""

import os
import json
import hmac
import hashlib
import time
import httpx
from typing import Optional
from urllib.parse import urlencode

NEURODOC_API = "https://api.neurodoc.app/aetherlang/execute"


# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION — Keys loaded from env vars, used LOCALLY only
# ═══════════════════════════════════════════════════════════════

def get_exchange_keys(exchange: str) -> tuple[str, str]:
    """
    Load API keys from environment variables.
    Keys are used ONLY for direct exchange API calls.
    Keys are NEVER sent to api.neurodoc.app.
    """
    key = os.getenv(f"{exchange.upper()}_API_KEY", "")
    secret = os.getenv(f"{exchange.upper()}_API_SECRET", "")
    return key, secret


# ═══════════════════════════════════════════════════════════════
#  LOCAL EXCHANGE DATA FETCHERS
#  These run on the USER'S machine. Keys are used here for
#  authenticated endpoints (higher rate limits, more data).
#  Public endpoints work without keys.
# ═══════════════════════════════════════════════════════════════

async def fetch_coingecko(coin_ids: list[str]) -> list[dict]:
    """Free tier — no API key needed"""
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(coin_ids),
        "order": "market_cap_desc",
        "sparkline": "false",
        "price_change_percentage": "24h,7d",
    }
    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=15)
        return r.json() if r.status_code == 200 else []


async def fetch_binance(symbol: str) -> dict:
    """
    Fetch from Binance. Uses API key for higher rate limits if available.
    Key is sent ONLY to api.binance.com, never to neurodoc.
    """
    api_key, _ = get_exchange_keys("BINANCE")
    headers = {}
    if api_key:
        headers["X-MBX-APIKEY"] = api_key  # Sent to Binance ONLY
    
    url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={symbol}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return {
                "exchange": "Binance",
                "bid": float(d.get("bidPrice") or 0),
                "ask": float(d.get("askPrice") or 0),
                "volume": float(d.get("quoteVolume") or 0),
            }
    return {}


async def fetch_bybit(symbol: str) -> dict:
    """
    Fetch from Bybit. Uses API key for authenticated data if available.
    Key is sent ONLY to api.bybit.com, never to neurodoc.
    """
    api_key, api_secret = get_exchange_keys("BYBIT")
    headers = {}
    if api_key and api_secret:
        ts = str(int(time.time() * 1000))
        sign_str = f"{ts}{api_key}5000"
        signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
        headers = {
            "X-BAPI-API-KEY": api_key,       # Sent to Bybit ONLY
            "X-BAPI-TIMESTAMP": ts,
            "X-BAPI-SIGN": signature,
        }
    
    url = f"https://api.bybit.com/v5/market/tickers?category=spot&symbol={symbol}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            items = r.json().get("result", {}).get("list", [])
            if items:
                t = items[0]
                return {
                    "exchange": "Bybit",
                    "bid": float(t.get("bid1Price") or 0),
                    "ask": float(t.get("ask1Price") or 0),
                    "volume": float(t.get("turnover24h") or 0),
                }
    return {}


async def fetch_kucoin(symbol: str) -> dict:
    """
    Fetch from KuCoin. Uses API key for authenticated data if available.
    Key is sent ONLY to api.kucoin.com, never to neurodoc.
    """
    api_key, api_secret = get_exchange_keys("KUCOIN")
    headers = {}
    if api_key and api_secret:
        ts = str(int(time.time() * 1000))
        path = f"/api/v1/market/orderbook/level1?symbol={symbol}"
        sign_str = f"{ts}GET{path}"
        signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha256).hexdigest()
        headers = {
            "KC-API-KEY": api_key,            # Sent to KuCoin ONLY
            "KC-API-TIMESTAMP": ts,
            "KC-API-SIGN": signature,
        }
    
    url = f"https://api.kucoin.com/api/v1/market/orderbook/level1?symbol={symbol}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            d = r.json().get("data", {})
            return {
                "exchange": "KuCoin",
                "bid": float(d.get("bestBid") or 0),
                "ask": float(d.get("bestAsk") or 0),
            }
    return {}


async def fetch_mexc(symbol: str) -> dict:
    """
    Fetch from MEXC. Uses API key for higher rate limits if available.
    Key is sent ONLY to api.mexc.com, never to neurodoc.
    """
    api_key, _ = get_exchange_keys("MEXC")
    headers = {}
    if api_key:
        headers["X-MEXC-APIKEY"] = api_key   # Sent to MEXC ONLY
    
    url = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            d = r.json()
            return {
                "exchange": "MEXC",
                "bid": float(d.get("bidPrice") or 0),
                "ask": float(d.get("askPrice") or 0),
                "volume": float(d.get("quoteVolume") or 0),
            }
    return {}


async def fetch_gateio(symbol: str) -> dict:
    """
    Fetch from Gate.io. Uses API key for authenticated data if available.
    Key is sent ONLY to api.gateio.ws, never to neurodoc.
    """
    api_key, api_secret = get_exchange_keys("GATEIO")
    headers = {}
    if api_key and api_secret:
        ts = str(int(time.time()))
        sign_str = f"GET\n/api/v4/spot/tickers\ncurrency_pair={symbol}\n\n{ts}"
        signature = hmac.new(api_secret.encode(), sign_str.encode(), hashlib.sha512).hexdigest()
        headers = {
            "KEY": api_key,                   # Sent to Gate.io ONLY
            "Timestamp": ts,
            "SIGN": signature,
        }
    
    url = f"https://api.gateio.ws/api/v4/spot/tickers?currency_pair={symbol}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data:
                d = data[0]
                return {
                    "exchange": "Gate.io",
                    "bid": float(d.get("highest_bid") or 0),
                    "ask": float(d.get("lowest_ask") or 0),
                    "volume": float(d.get("quote_volume") or 0),
                }
    return {}


# ═══════════════════════════════════════════════════════════════
#  API REQUEST BUILDER
#  This is the ONLY function that sends data to api.neurodoc.app
#  *** INSPECT THIS TO VERIFY NO KEYS ARE INCLUDED ***
# ═══════════════════════════════════════════════════════════════

def build_api_request(query: str, market_data: list[dict], exchange_data: list[dict], mode: str = "analysis") -> dict:
    """
    Build the exact payload sent to api.neurodoc.app.
    
    WHAT IS SENT:     prices, volumes, query text
    WHAT IS NOT SENT: API keys, secrets, credentials, wallet addresses
    
    Run `python client.py` to print this payload and verify yourself.
    """
    
    # Build context from LOCALLY-fetched data (only numbers, no keys)
    context_lines = [f"Market query: {query}", "", "LIVE MARKET DATA:"]
    for coin in market_data:
        if isinstance(coin, dict):
            context_lines.append(
                f"  {coin.get('symbol','?').upper()}: "
                f"${coin.get('current_price',0):,.2f} "
                f"24h:{coin.get('price_change_percentage_24h',0):+.1f}% "
                f"MCap:${coin.get('market_cap',0)/1e9:.1f}B"
            )
    
    context_lines.append("\nEXCHANGE DATA:")
    for ex in exchange_data:
        if ex:
            context_lines.append(
                f"  {ex.get('exchange','?')}: "
                f"bid={ex.get('bid',0)} ask={ex.get('ask',0)} "
                f"vol={ex.get('volume',0)}"
            )
    
    flow_code = f'''flow CryptoAnalysis {{
  using target "neuroaether" version ">=0.3";
  input text query;
  node Apex: crypto mode="{mode}", language="en";
  output text result from Apex;
}}'''
    
    # ╔══════════════════════════════════════════════════════════╗
    # ║  THIS IS THE COMPLETE PAYLOAD — NOTHING ELSE IS SENT   ║
    # ║  No API keys. No secrets. No credentials. Verify below.║
    # ╚══════════════════════════════════════════════════════════╝
    payload = {
        "code": flow_code,
        "query": "\n".join(context_lines),
    }
    
    return payload


async def analyze(query: str, coin_ids: list[str], mode: str = "analysis") -> dict:
    """
    Full pipeline:
    1. Load keys from env vars (LOCAL)
    2. Fetch data from exchanges using keys (LOCAL → exchange)
    3. Build payload with ONLY market data (no keys)
    4. Send payload to api.neurodoc.app (no keys in payload)
    """
    
    # Step 1 & 2: Fetch data LOCALLY (keys used here, sent to exchanges only)
    market_data = await fetch_coingecko(coin_ids)
    
    symbol_map = {
        "bitcoin":  ("BTCUSDT",  "BTCUSDT",  "BTC-USDT",  "BTCUSDT",  "BTC_USDT"),
        "ethereum": ("ETHUSDT",  "ETHUSDT",  "ETH-USDT",  "ETHUSDT",  "ETH_USDT"),
        "solana":   ("SOLUSDT",  "SOLUSDT",  "SOL-USDT",  "SOLUSDT",  "SOL_USDT"),
    }
    
    exchange_data = []
    for coin_id in coin_ids[:3]:
        if coin_id in symbol_map:
            bn, bb, kc, mx, gt = symbol_map[coin_id]
            exchange_data.append(await fetch_binance(bn))
            exchange_data.append(await fetch_bybit(bb))
            exchange_data.append(await fetch_kucoin(kc))
            exchange_data.append(await fetch_mexc(mx))
            exchange_data.append(await fetch_gateio(gt))
    
    # Step 3: Build payload — VERIFY: no keys in this dict
    payload = build_api_request(query, market_data, exchange_data, mode)
    
    # Step 4: Send ONLY the payload (no keys)
    async with httpx.AsyncClient() as client:
        r = await client.post(NEURODOC_API, json=payload, timeout=120)
        return r.json()


# ═══════════════════════════════════════════════════════════════
#  VERIFICATION MODE
#  Run: python client.py
#  This prints the EXACT payload without sending anything.
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import asyncio
    
    async def verify():
        """Inspect the exact payload before sending — nothing is transmitted."""
        
        print("=" * 60)
        print("APEX Crypto Intelligence — Payload Verification")
        print("=" * 60)
        
        # Show which keys are configured (not the values!)
        exchanges = ["BINANCE", "BYBIT", "KUCOIN", "MEXC", "GATEIO"]
        print("\n1. CONFIGURED EXCHANGE KEYS (values hidden):")
        for ex in exchanges:
            key, secret = get_exchange_keys(ex)
            status = "✅ configured" if key else "⬜ not set (public endpoints used)"
            print(f"   {ex}: {status}")
        
        # Fetch data locally
        print("\n2. FETCHING DATA LOCALLY (keys sent to exchanges only)...")
        market_data = await fetch_coingecko(["bitcoin"])
        exchange_data = [
            await fetch_binance("BTCUSDT"),
            await fetch_bybit("BTCUSDT"),
            await fetch_kucoin("BTC-USDT"),
            await fetch_mexc("BTCUSDT"),
            await fetch_gateio("BTC_USDT"),
        ]
        
        for ex in exchange_data:
            if ex:
                print(f"   ✅ {ex['exchange']}: bid={ex.get('bid')} ask={ex.get('ask')}")
            else:
                print(f"   ⬜ (no data)")
        
        # Build and display payload
        payload = build_api_request("Analyze BTC", market_data, exchange_data)
        
        print("\n3. EXACT PAYLOAD THAT WOULD BE SENT TO api.neurodoc.app:")
        print("-" * 60)
        print(json.dumps(payload, indent=2))
        print("-" * 60)
        
        # Verify no keys in payload
        payload_str = json.dumps(payload)
        print("\n4. SECURITY VERIFICATION:")
        has_keys = False
        for ex in exchanges:
            key, secret = get_exchange_keys(ex)
            if key and key in payload_str:
                print(f"   ❌ WARNING: {ex} API key found in payload!")
                has_keys = True
            if secret and secret in payload_str:
                print(f"   ❌ WARNING: {ex} secret found in payload!")
                has_keys = True
        
        if not has_keys:
            print("   ✅ VERIFIED: No API keys or secrets in outbound payload.")
            print("   ✅ VERIFIED: Only market prices and query text are sent.")
        
        print("\n" + "=" * 60)
        print("Verification complete. No data was sent to any server.")
        print("=" * 60)
    
    asyncio.run(verify())
