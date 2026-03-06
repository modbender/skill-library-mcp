#!/usr/bin/env python3
"""
Crypto Sniper Oracle - Quantitative Market Data Engine
Version: 3.2.0-Enterprise
Author: Georges Andronescu (Wesley Armando) & Quant Engine
License: MIT

Fetches market data from Binance public API with:
- Order Book Imbalance (OBI) & VWAP Mathematics
- Rate limiting protection (Local Caching)
- Exponential Backoff Retry Logic
- Stale Cache Fallback
- Strict JSON Schema stdout for Agent parsing
"""

import sys
import json
import argparse
import urllib.request
import urllib.error
import logging
import time
import re
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================
CACHE_FILE = Path("/workspace/.oracle_cache.json")
CACHE_TTL_SECONDS = 45
MAX_RETRIES = 3
REQUEST_TIMEOUT_SECONDS = 5

# ==========================================
# LOGGER SETUP (STDERR ONLY)
# ==========================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger(__name__)


class CacheManager:
    """Manages local file cache to prevent rate limit bans."""
    def __init__(self, cache_file: Path, ttl: int):
        self.cache_file = cache_file
        self.ttl = ttl
    
    def get(self, symbol: str) -> dict:
        try:
            if not self.cache_file.exists():
                return None
            with open(self.cache_file, 'r') as f:
                cache = json.load(f)
            
            if symbol not in cache:
                return None
            
            entry = cache[symbol]
            age = time.time() - entry['timestamp']
            
            if age <= self.ttl:
                logger.info(f"Cache hit for {symbol} (age: {age:.1f}s)")
                return entry['data']
            return None
        except Exception as e:
            logger.warning(f"Cache read error: {e}")
            return None
    
    def set(self, symbol: str, data: dict):
        try:
            cache = {}
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
            
            cache[symbol] = {
                'data': data,
                'timestamp': time.time()
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


class BinanceQuantOracle:
    BASE_URL = "https://api.binance.com/api/v3"
    
    def __init__(self, symbol: str, depth: int = 10):
        self.symbol = symbol.upper()
        self.depth = min(depth, 5000)
        self.headers = {
            'User-Agent': 'OpenClaw-Quant-Engine/3.2',
            'Accept': 'application/json'
        }
        self.cache = CacheManager(CACHE_FILE, CACHE_TTL_SECONDS)
    
    def _make_request(self, endpoint: str) -> dict:
        """HTTP request with Exponential Backoff Retry logic."""
        url = f"{self.BASE_URL}{endpoint}"
        
        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    return json.loads(response.read().decode('utf-8'))
                    
            except urllib.error.HTTPError as e:
                if e.code in [429, 418]:  # Rate Limit Exceeded
                    backoff = 2 ** attempt  # Exponential: 1s, 2s, 4s
                    logger.warning(f"Rate limit (HTTP {e.code}). Backing off for {backoff}s...")
                    time.sleep(backoff)
                    continue
                elif e.code == 400:
                    raise Exception("INVALID_SYMBOL")
                else:
                    raise Exception(f"HTTP_ERROR_{e.code}")
                    
            except urllib.error.URLError as e:
                logger.warning(f"Network error: {e.reason}. Retrying...")
                time.sleep(1)
            except Exception as e:
                raise Exception(f"SYSTEM_ERROR: {str(e)}")
                
        raise Exception("MAX_RETRIES_EXCEEDED")

    def fetch_market_state(self) -> str:
        # 1. Vérification du Cache Actif
        cached_data = self.cache.get(self.symbol)
        if cached_data:
            return json.dumps(cached_data, indent=2)
        
        try:
            logger.info(f"Fetching live quantitative data for {self.symbol}...")
            
            # 2. Appels API
            ticker_data = self._make_request(f"/ticker/24hr?symbol={self.symbol}")
            depth_data = self._make_request(f"/depth?symbol={self.symbol}&limit={self.depth}")
            
            # 3. Mathématiques Financières
            bids = [
                {"price": float(b[0]), "qty": float(b[1])} 
                for b in depth_data.get("bids", [])
            ]
            asks = [
                {"price": float(a[0]), "qty": float(a[1])} 
                for a in depth_data.get("asks", [])
            ]
            
            spread, spread_pct, spread_bps = 0.0, 0.0, 0.0
            bid_vol, ask_vol, imbalance = 0.0, 0.0, 0.0
            last_price = float(ticker_data.get("lastPrice", 0))

            if bids and asks and last_price > 0:
                best_bid, best_ask = bids[0]["price"], asks[0]["price"]
                spread = best_ask - best_bid
                spread_pct = (spread / last_price) * 100
                spread_bps = spread_pct * 100
                
                # Order Book Imbalance (OBI)
                # Positive = Buying pressure
                # Negative = Selling pressure
                bid_vol = sum(b["qty"] for b in bids)
                ask_vol = sum(a["qty"] for a in asks)
                total_vol = bid_vol + ask_vol
                imbalance = (bid_vol - ask_vol) / total_vol if total_vol > 0 else 0.0
            
            # 4. Construction du Payload
            payload = {
                "status": "success",
                "asset": self.symbol,
                "timestamp_ms": int(time.time() * 1000),
                "ticker": {
                    "last_price": round(last_price, 8),
                    "vwap_24h": round(float(ticker_data.get("weightedAvgPrice", 0)), 8),
                    "volume_24h_asset": round(float(ticker_data.get("volume", 0)), 4),
                    "volume_24h_quote": round(float(ticker_data.get("quoteVolume", 0)), 2),
                    "price_change_pct": round(float(ticker_data.get("priceChangePercent", 0)), 2),
                    "high_24h": round(float(ticker_data.get("highPrice", 0)), 8),
                    "low_24h": round(float(ticker_data.get("lowPrice", 0)), 8),
                    "trades_count_24h": int(ticker_data.get("count", 0))
                },
                "order_book": {
                    "spread_absolute": round(spread, 8),
                    "spread_bps": round(spread_bps, 2),
                    "imbalance_ratio": round(imbalance, 4),
                    "bid_volume": round(bid_vol, 4),
                    "ask_volume": round(ask_vol, 4),
                    "top_bids": bids[:5],
                    "top_asks": asks[:5]
                },
                "quant_signals": {
                    "obi_direction": "BUY_PRESSURE" if imbalance > 0.1 else ("SELL_PRESSURE" if imbalance < -0.1 else "NEUTRAL"),
                    "liquidity_quality": "EXCELLENT" if spread_bps < 5 else ("GOOD" if spread_bps < 10 else "POOR"),
                    "price_vs_vwap_pct": round(((last_price / float(ticker_data.get("weightedAvgPrice", last_price)) - 1) * 100), 2)
                }
            }
            
            # 5. Sauvegarde en Cache
            self.cache.set(self.symbol, payload)
            logger.info("Data aggregation successful.")
            return json.dumps(payload, indent=2)
            
        except Exception as e:
            error_code = str(e)
            logger.error(f"Fetch failed: {error_code}")
            
            # 6. Fallback sur le Cache Périmé (Stale Cache)
            try:
                if CACHE_FILE.exists():
                    with open(CACHE_FILE, 'r') as f:
                        cache = json.load(f)
                    if self.symbol in cache:
                        age = time.time() - cache[self.symbol]['timestamp']
                        stale_data = cache[self.symbol]['data']
                        stale_data['status'] = 'success_cached_stale'
                        stale_data['cache_age_seconds'] = int(age)
                        stale_data['warning'] = f"API unreachable. Data is {int(age)}s old."
                        logger.warning(f"Yielding stale cache (age: {int(age)}s)")
                        return json.dumps(stale_data, indent=2)
            except Exception:
                pass
            
            # 7. Erreur Fatale
            error_payload = {
                "status": "error",
                "asset": self.symbol,
                "timestamp_ms": int(time.time() * 1000),
                "error_code": error_code,
                "message": f"Failed to fetch market data: {error_code}"
            }
            return json.dumps(error_payload, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Institutional Quant Oracle for OpenClaw",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 crypto_oracle.py --symbol BTCUSDT
  python3 crypto_oracle.py --symbol ETHBTC --depth 20
  python3 crypto_oracle.py --symbol SOLUSDC
        """
    )
    parser.add_argument(
        "--symbol",
        type=str,
        required=True,
        help="Trading pair (e.g., BTCUSDT, ETHBTC, BNBUSDC)"
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=10,
        help="Order book depth level (default: 10, max: 5000)"
    )
    
    args = parser.parse_args()
    
    # Regex corrigée pour autoriser toutes les paires (pas juste USDT)
    # Accepte 4-12 caractères alphanumériques majuscules
    if not re.match(r'^[A-Z0-9]{4,12}$', args.symbol.upper()):
        error_output = {
            "status": "error",
            "error_code": "INVALID_FORMAT",
            "asset": args.symbol,
            "message": f"Invalid symbol format: {args.symbol}. Use 4-12 uppercase alphanumeric chars (e.g., BTCUSDT, ETHBTC)"
        }
        print(json.dumps(error_output, indent=2))
        sys.exit(1)
    
    oracle = BinanceQuantOracle(symbol=args.symbol, depth=args.depth)
    output = oracle.fetch_market_state()
    
    print(output)
    sys.exit(1 if '"status": "error"' in output else 0)


if __name__ == "__main__":
    main()
