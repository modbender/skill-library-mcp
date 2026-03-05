#!/usr/bin/env python3
"""
Enhanced Crypto Regime Report Generator - Parallelized

Fetches data from OKX in parallel for faster execution.
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Base directory (skill root)
BASE_DIR = Path(__file__).parent.parent

# Config path - restricted to skill directory for security
# Only allow relative paths within the skill's references folder
config_env = os.environ.get("REGIME_CONFIG", "")
if config_env:
    # If provided, must be a relative path within the skill directory
    config_path = Path(config_env)
    if config_path.is_absolute():
        raise ValueError("REGIME_CONFIG must be a relative path within the skill directory")
    CONFIG_PATH = (BASE_DIR / config_path).resolve()
    # Ensure the resolved path is still within BASE_DIR (prevent traversal)
    try:
        CONFIG_PATH.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError("REGIME_CONFIG path escapes skill directory")
else:
    CONFIG_PATH = BASE_DIR / "references" / "config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

# Cache file
CACHE_PATH = BASE_DIR / "references" / "cache.json"

# Yahoo Finance symbol mapping
YAHOO_SYMBOLS = {
    "BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD",
    "AVAX": "AVAX-USD", "ADA": "ADA-USD", "DOT": "DOT-USD",
    "NEAR": "NEAR-USD", "ARB": "ARB-USD", "OP": "OP-USD",
    "POL": "POL-USD", "MATIC": "POL-USD", "UNI": "UNI-USD",
    "AAVE": "AAVE-USD", "LINK": "LINK-USD", "HYPE": "HYPE-USD",
    "RNDR": "RENDER-USD", "RENDER": "RENDER-USD",
    "SUI": "SUI-USD", "APT": "APT-USD",
}


def load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)


def okx_request(endpoint: str) -> dict:
    """Make a request to OKX API."""
    url = f"https://www.okx.com{endpoint}"
    result = subprocess.run(
        ["curl", "-s", "--connect-timeout", "10", "--max-time", "30", url],
        capture_output=True,
        text=True,
        timeout=35
    )
    if result.returncode != 0:
        raise Exception(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def fetch_candles(symbol: str, bar: str = "1D", limit: int = 100) -> list:
    """Fetch OHLCV candles from OKX."""
    resp = okx_request(f"/api/v5/market/candles?instId={symbol}&bar={bar}&limit={limit}")
    if resp.get("code") != "0":
        raise Exception(f"OKX error: {resp.get('msg')}")
    candles = resp["data"][::-1]
    return [{
        "ts": int(c[0]),
        "open": float(c[1]),
        "high": float(c[2]),
        "low": float(c[3]),
        "close": float(c[4]),
        "vol": float(c[5])
    } for c in candles]


def fetch_funding_rate(symbol: str) -> dict:
    """Fetch funding rate from OKX."""
    resp = okx_request(f"/api/v5/public/funding-rate?instId={symbol}")
    if resp.get("code") != "0" or not resp.get("data"):
        return {"rate": None}
    return {"rate": float(resp["data"][0].get("fundingRate", 0))}


def fetch_open_interest(symbol: str) -> float:
    """Fetch open interest from OKX."""
    resp = okx_request(f"/api/v5/public/open-interest?instId={symbol}")
    if resp.get("code") != "0" or not resp.get("data"):
        return 0
    return float(resp["data"][0].get("oiUsd", 0))


def fetch_all_asset_data(asset: dict) -> tuple:
    """Fetch all data for an asset in parallel."""
    okx_symbol = asset["okx"]
    try:
        # Fetch candles, funding, and OI in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            candles_future = executor.submit(fetch_candles, okx_symbol, "1D", 100)
            funding_future = executor.submit(fetch_funding_rate, okx_symbol)
            oi_future = executor.submit(fetch_open_interest, okx_symbol)
            
            candles = candles_future.result(timeout=40)
            funding = funding_future.result(timeout=40)
            oi = oi_future.result(timeout=40)
        
        return (asset, candles, funding, oi, None)
    except Exception as e:
        return (asset, None, None, None, str(e))


def calculate_atr(candles: list, period: int = 10) -> list:
    if len(candles) < period + 1:
        return [None] * len(candles)
    trs = []
    for i in range(len(candles)):
        if i == 0:
            trs.append(candles[i]["high"] - candles[i]["low"])
        else:
            h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
            trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    atr = [None] * period
    atr.append(sum(trs[:period]) / period)
    for i in range(period + 1, len(candles)):
        atr.append((atr[-1] * (period - 1) + trs[i]) / period)
    return atr


def calculate_supertrend(candles: list, period: int = 10, multiplier: float = 3.0) -> tuple:
    atr = calculate_atr(candles, period)
    supertrend, direction = [], []
    for i in range(len(candles)):
        if atr[i] is None:
            supertrend.append(None)
            direction.append(0)
            continue
        hl2 = (candles[i]["high"] + candles[i]["low"]) / 2
        upper, lower = hl2 + multiplier * atr[i], hl2 - multiplier * atr[i]
        if i == 0 or supertrend[-1] is None:
            supertrend.append(lower)
            direction.append(1)
            continue
        prev_st, prev_dir, prev_close = supertrend[-1], direction[-1], candles[i-1]["close"]
        final_lower = lower if lower > prev_st or prev_close < prev_st else prev_st
        final_upper = upper if upper < prev_st or prev_close > prev_st else prev_st
        if prev_dir >= 0:
            new_dir, new_st = (-1, final_upper) if candles[i]["close"] < final_lower else (1, final_lower)
        else:
            new_dir, new_st = (1, final_lower) if candles[i]["close"] > final_upper else (-1, final_upper)
        supertrend.append(new_st)
        direction.append(new_dir)
    return supertrend, direction


def calculate_adx(candles: list, period: int = 14) -> list:
    if len(candles) < period * 2:
        return [None] * len(candles)
    plus_dm, minus_dm = [0], [0]
    for i in range(1, len(candles)):
        up = candles[i]["high"] - candles[i-1]["high"]
        down = candles[i-1]["low"] - candles[i]["low"]
        plus_dm.append(up if up > down and up > 0 else 0)
        minus_dm.append(down if down > up and down > 0 else 0)
    trs = [candles[0]["high"] - candles[0]["low"]]
    for i in range(1, len(candles)):
        h, l, pc = candles[i]["high"], candles[i]["low"], candles[i-1]["close"]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    def wilder_smooth(values, period):
        smoothed = []
        for i in range(len(values)):
            if i < period - 1: smoothed.append(None)
            elif i == period - 1: smoothed.append(sum(values[:period]))
            else: smoothed.append(smoothed[-1] - smoothed[-1]/period + values[i])
        return smoothed
    smoothed_tr = wilder_smooth(trs, period)
    smoothed_plus = wilder_smooth(plus_dm, period)
    smoothed_minus = wilder_smooth(minus_dm, period)
    plus_di, minus_di, dx = [], [], []
    for i in range(len(candles)):
        if smoothed_tr[i] is None or smoothed_tr[i] == 0:
            plus_di.append(None); minus_di.append(None); dx.append(None)
        else:
            pdi = 100 * smoothed_plus[i] / smoothed_tr[i]
            mdi = 100 * smoothed_minus[i] / smoothed_tr[i]
            plus_di.append(pdi); minus_di.append(mdi)
            di_sum = pdi + mdi
            dx.append(0 if di_sum == 0 else 100 * abs(pdi - mdi) / di_sum)
    adx = [None] * len(candles)
    first_valid = next((i for i, d in enumerate(dx) if d is not None), None)
    if first_valid is None: return adx
    valid_dx = [d for d in dx if d is not None]
    if len(valid_dx) < period: return adx
    adx[first_valid + period - 1] = sum(valid_dx[:period]) / period
    for i in range(first_valid + period, len(candles)):
        if dx[i] is not None:
            adx[i] = (adx[i-1] * (period - 1) + dx[i]) / period
    return adx


def calculate_correlation(returns1: list, returns2: list) -> float:
    if len(returns1) != len(returns2) or len(returns1) < 10:
        return None
    n = len(returns1)
    mean1, mean2 = sum(returns1)/n, sum(returns2)/n
    cov = sum((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(returns1, returns2))
    var1 = sum((r - mean1)**2 for r in returns1)
    var2 = sum((r - mean2)**2 for r in returns2)
    if var1 == 0 or var2 == 0: return None
    return cov / (var1 * var2) ** 0.5


def get_regime(direction: int, adx_value: float, thresholds: dict) -> str:
    if adx_value is None: return "Unknown"
    strong, weak = thresholds["strong_threshold"], thresholds["weak_threshold"]
    if direction > 0:
        if adx_value >= strong: return "Strong Bull"
        elif adx_value >= weak: return "Weak Bull"
        else: return "Ranging"
    else:
        if adx_value >= strong: return "Strong Bear"
        elif adx_value >= weak: return "Weak Bear"
        else: return "Ranging"


def process_asset_data(asset: dict, candles: list, funding: dict, oi: float, 
                       btc_candles: list, cache: dict) -> dict:
    """Process fetched data into analysis result."""
    symbol = asset["symbol"]
    
    if candles is None or len(candles) < 30:
        return {"error": "Not enough data", "symbol": symbol}
    
    st, direction = calculate_supertrend(candles,
        CONFIG["indicators"]["supertrend"]["period"],
        CONFIG["indicators"]["supertrend"]["multiplier"])
    adx = calculate_adx(candles, CONFIG["indicators"]["adx"]["period"])
    
    current_price = candles[-1]["close"]
    current_st, current_dir, current_adx = st[-1], direction[-1], adx[-1]
    
    if current_st is None or current_adx is None:
        return {"error": "Indicator calculation failed", "symbol": symbol}
    
    prev_close = candles[-2]["close"]
    price_change = ((current_price - prev_close) / prev_close) * 100
    st_distance = ((current_price - current_st) / current_st) * 100
    
    vol_20 = sum(c["vol"] for c in candles[-20:]) / 20
    vol_current = candles[-1]["vol"]
    vol_ratio = vol_current / vol_20 if vol_20 > 0 else 1
    
    funding_rate = funding.get("rate")
    
    cache_key = f"{symbol}_funding"
    prev_funding = cache.get(cache_key)
    funding_change = None
    if prev_funding is not None and funding_rate is not None:
        funding_change = (funding_rate - prev_funding) * 100
    
    oi_cache_key = f"{symbol}_oi"
    prev_oi = cache.get(oi_cache_key)
    oi_change = None
    if prev_oi is not None and oi > 0:
        oi_change = ((oi - prev_oi) / prev_oi) * 100
    
    correlation = None
    if btc_candles and len(btc_candles) >= 30:
        asset_returns = [(candles[i]["close"] / candles[i-1]["close"] - 1) for i in range(-30, 0)]
        btc_returns = [(btc_candles[i]["close"] / btc_candles[i-1]["close"] - 1) for i in range(-30, 0)]
        correlation = calculate_correlation(asset_returns, btc_returns)
    
    regime = get_regime(current_dir, current_adx, CONFIG["indicators"]["adx"])
    
    return {
        "symbol": symbol,
        "name": asset["name"],
        "price": current_price,
        "change_24h": price_change,
        "supertrend": current_st,
        "st_distance": st_distance,
        "direction": "bullish" if current_dir > 0 else "bearish",
        "adx": current_adx,
        "regime": regime,
        "vol_ratio": vol_ratio,
        "funding_rate": funding_rate * 100 if funding_rate else None,
        "funding_change": funding_change,
        "open_interest": oi / 1e9 if oi else None,
        "oi_change": oi_change,
        "btc_correlation": correlation,
        "_cache_updates": {
            cache_key: funding_rate,
            oi_cache_key: oi,
            f"{symbol}_regime": regime
        }
    }


def format_report(results: list, cache: dict) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M PST")
    lines = [f"📊 *Crypto Regime Report*", f"_{now}_", ""]
    
    # Build watching section
    watching = []
    for r in results:
        if "error" in r:
            continue
        
        symbol = r["symbol"]
        regime = r["regime"]
        adx = r["adx"]
        change_24h = r.get("change_24h", 0)
        funding = r.get("funding_rate")
        
        # Check regime change
        prev_regime = cache.get(f"{symbol}_regime")
        if prev_regime and prev_regime != regime:
            watching.append(f"🔄 *{symbol}*: {prev_regime} → {regime}")
        
        # Check ADX near threshold
        if adx is not None:
            if regime in ["Weak Bull", "Weak Bear"] and adx < 22:
                watching.append(f"⚠️ *{symbol}*: ADX {adx:.1f} (near Ranging)")
            elif regime == "Ranging" and adx > 18:
                watching.append(f"⚠️ *{symbol}*: ADX {adx:.1f} (trending)")
        
        # Check contrarian funding signals (price/funding divergence)
        # Only flag when funding is at least 0.03% in the opposite direction
        if funding is not None and abs(funding) > 0.03:
            if change_24h < 0 and funding > 0:
                # Price down, longs paying → trapped longs
                watching.append(f"⚡ *{symbol}*: CONTRARIAN - Price down, longs paying (trapped longs)")
            elif change_24h > 0 and funding < 0:
                # Price up, shorts paying → trapped shorts
                watching.append(f"⚡ *{symbol}*: CONTRARIAN - Price up, shorts paying (squeeze setup)")
        
        # Check funding extremes (threshold: 0.03%)
        if funding is not None and abs(funding) > 0.03:
            direction = "longs paying" if funding > 0 else "shorts paying"
            watching.append(f"🔥 *{symbol}*: Funding {funding:+.2f}% ({direction})")
        
        # Check volume spike (threshold: 3x average)
        if r.get("vol_ratio", 0) > 3.0:
            watching.append(f"🔊 *{symbol}*: Volume {r['vol_ratio']:.1f}x avg")
        
        # Check large OI change
        if r.get("oi_change") is not None and abs(r["oi_change"]) > 10:
            direction = "building" if r["oi_change"] > 0 else "unwinding"
            watching.append(f"📊 *{symbol}*: OI {r['oi_change']:+.1f}% ({direction})")
    
    if watching:
        lines.append("👁️ *WATCHING:*")
        lines.extend(watching)
        lines.append("")
    
    regime_order = {"Strong Bull": 0, "Weak Bull": 1, "Ranging": 2, "Weak Bear": 3, "Strong Bear": 4, "Unknown": 5}
    sorted_results = sorted(results, key=lambda x: regime_order.get(x.get("regime", "Unknown"), 5))
    
    for r in sorted_results:
        if "error" in r:
            lines.append(f"❌ *{r['symbol']}*: {r['error']}")
            continue
        
        regime_emoji = {"Strong Bull": "🟢", "Weak Bull": "🟡", "Ranging": "⚪", "Weak Bear": "🟠", "Strong Bear": "🔴"}.get(r["regime"], "❓")
        
        if r["price"] >= 1000: price_str = f"${r['price']:,.0f}"
        elif r["price"] >= 1: price_str = f"${r['price']:,.2f}"
        else: price_str = f"${r['price']:,.4f}"
        
        change_emoji = "📈" if r["change_24h"] > 0 else "📉" if r["change_24h"] < 0 else "➡️"
        
        lines.append(f"{regime_emoji} *{r['symbol']}* {price_str} {change_emoji} {r['change_24h']:+.1f}%")
        lines.append(f"   _{r['regime']}_ | ADX: {r['adx']:.1f} | {r['direction'].capitalize()}")
        
        st_dir = "above" if r["st_distance"] > 0 else "below"
        lines.append(f"   ST dist: {abs(r['st_distance']):.1f}% {st_dir}")
        
        vol_emoji = "🔊" if r["vol_ratio"] > 1.5 else "🔇" if r["vol_ratio"] < 0.5 else ""
        lines.append(f"   Vol: {r['vol_ratio']:.1f}x 20d avg {vol_emoji}")
        
        if r["funding_rate"] is not None:
            funding_emoji = "🔥" if abs(r["funding_rate"]) > 0.01 else ""
            change_str = f" ({r['funding_change']:+.2f}bps)" if r["funding_change"] is not None else ""
            lines.append(f"   Funding: {r['funding_rate']:+.4f}%{change_str} {funding_emoji}")
        
        if r["open_interest"] is not None:
            oi_change_str = f" ({r['oi_change']:+.1f}%)" if r["oi_change"] is not None else ""
            lines.append(f"   OI: ${r['open_interest']:.1f}B{oi_change_str}")
        
        if r["btc_correlation"] is not None:
            corr_emoji = "🔗" if r["btc_correlation"] > 0.7 else "〰️" if r["btc_correlation"] < 0.3 else ""
            lines.append(f"   BTC corr: {r['btc_correlation']:.2f} {corr_emoji}")
        
        lines.append("")
    
    bull_count = sum(1 for r in sorted_results if "Bull" in r.get("regime", ""))
    bear_count = sum(1 for r in sorted_results if "Bear" in r.get("regime", ""))
    range_count = sum(1 for r in sorted_results if r.get("regime") == "Ranging")
    
    lines.append(f"📈 Bulls: {bull_count} | 📉 Bears: {bear_count} | ⚪ Range: {range_count}")
    
    return "\n".join(lines)


def main():
    """Main entry point with parallelized data fetching."""
    cache = load_cache()
    cache_updates = {}
    
    print("Fetching market data (parallel)...", file=sys.stderr)
    
    # Fetch all assets in parallel
    all_data = []
    with ThreadPoolExecutor(max_workers=17) as executor:
        futures = {executor.submit(fetch_all_asset_data, asset): asset for asset in CONFIG["watchlist"]}
        for future in as_completed(futures, timeout=60):
            asset, candles, funding, oi, error = future.result()
            all_data.append((asset, candles, funding, oi, error))
            print(f"  Got {asset['symbol']}...", file=sys.stderr)
    
    # Extract BTC candles for correlation
    btc_candles = None
    for asset, candles, funding, oi, error in all_data:
        if asset["symbol"] == "BTC" and candles:
            btc_candles = candles
            break
    
    # Process all assets
    results = []
    for asset, candles, funding, oi, error in all_data:
        if error:
            results.append({"error": error, "symbol": asset["symbol"]})
        else:
            result = process_asset_data(asset, candles, funding, oi, btc_candles, cache)
            results.append(result)
            if "_cache_updates" in result:
                cache_updates.update(result["_cache_updates"])
    
    # Update cache
    if cache_updates:
        cache.update(cache_updates)
        save_cache(cache)
    
    print("\n" + "="*50 + "\n", file=sys.stderr)
    report = format_report(results, cache)
    print(report)
    return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--weekly", action="store_true")
    args = parser.parse_args()
    
    main()
