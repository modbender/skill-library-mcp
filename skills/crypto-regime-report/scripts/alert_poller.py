#!/usr/bin/env python3
"""
Lightweight alert poller for crypto regime changes.
No model in the loop - just fetch, check, alert.
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
config_env = os.environ.get("REGIME_CONFIG", "")
if config_env:
    config_path = Path(config_env)
    if config_path.is_absolute():
        raise ValueError("REGIME_CONFIG must be a relative path within the skill directory")
    CONFIG_PATH = (BASE_DIR / config_path).resolve()
    try:
        CONFIG_PATH.relative_to(BASE_DIR)
    except ValueError:
        raise ValueError("REGIME_CONFIG path escapes skill directory")
else:
    CONFIG_PATH = BASE_DIR / "references" / "config.json"

with open(CONFIG_PATH) as f:
    CONFIG = json.load(f)

CACHE_PATH = BASE_DIR / "references" / "cache.json"
ALERT_STATE_PATH = BASE_DIR / "references" / "alert_state.json"


def load_cache() -> dict:
    if CACHE_PATH.exists():
        with open(CACHE_PATH) as f:
            return json.load(f)
    return {}


def save_cache(cache: dict):
    with open(CACHE_PATH, 'w') as f:
        json.dump(cache, f, indent=2)


def load_alert_state() -> dict:
    if ALERT_STATE_PATH.exists():
        with open(ALERT_STATE_PATH) as f:
            return json.load(f)
    return {"triggered": {}, "last_run": None}


def save_alert_state(state: dict):
    with open(ALERT_STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def okx_request(endpoint: str) -> dict:
    url = f"https://www.okx.com{endpoint}"
    result = subprocess.run(
        ["curl", "-s", "--connect-timeout", "10", "--max-time", "30", url],
        capture_output=True, text=True, timeout=35
    )
    if result.returncode != 0:
        raise Exception(f"curl failed: {result.stderr}")
    return json.loads(result.stdout)


def fetch_candles(symbol: str, bar: str = "1D", limit: int = 100) -> list:
    resp = okx_request(f"/api/v5/market/candles?instId={symbol}&bar={bar}&limit={limit}")
    if resp.get("code") != "0":
        raise Exception(f"OKX error: {resp.get('msg')}")
    candles = resp["data"][::-1]
    return [{
        "ts": int(c[0]), "open": float(c[1]), "high": float(c[2]),
        "low": float(c[3]), "close": float(c[4]), "vol": float(c[5])
    } for c in candles]


def fetch_funding_rate(symbol: str) -> dict:
    resp = okx_request(f"/api/v5/public/funding-rate?instId={symbol}")
    if resp.get("code") != "0" or not resp.get("data"):
        return {"rate": None}
    return {"rate": float(resp["data"][0].get("fundingRate", 0))}


def fetch_open_interest(symbol: str) -> float:
    resp = okx_request(f"/api/v5/public/open-interest?instId={symbol}")
    if resp.get("code") != "0" or not resp.get("data"):
        return 0
    return float(resp["data"][0].get("oiUsd", 0))


def fetch_asset_data(asset: dict) -> tuple:
    okx_symbol = asset["okx"]
    try:
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


def check_alerts(results: list, cache: dict, alert_state: dict) -> list:
    """Check for alert conditions and return list of alerts.
    
    States are cleared when conditions normalize, allowing re-alerting.
    """
    alerts = []
    now = datetime.now().isoformat()
    current_keys = set()  # Track which keys are still active this run
    
    for r in results:
        if "error" in r:
            continue
        
        symbol = r["symbol"]
        regime = r["regime"]
        adx = r["adx"]
        funding = r.get("funding_rate")
        vol_ratio = r.get("vol_ratio", 0)
        change_24h = r.get("change_24h", 0)
        
        # Regime flip
        prev_regime = cache.get(f"{symbol}_regime")
        if prev_regime and prev_regime != regime:
            alert_key = f"{symbol}_regime_flip"
            current_keys.add(alert_key)
            if alert_state["triggered"].get(alert_key) != f"{prev_regime}->{regime}":
                alerts.append(f"🔄 *{symbol}*: {prev_regime} → {regime}")
                alert_state["triggered"][alert_key] = f"{prev_regime}->{regime}"
        
        # ADX near threshold (potential flip)
        if adx is not None and regime in ["Weak Bull", "Weak Bear"] and adx < 22:
            alert_key = f"{symbol}_adx_weak"
            current_keys.add(alert_key)
            threshold_key = f"{symbol}_{regime}_adx_{adx:.0f}"
            if alert_state["triggered"].get(alert_key) != threshold_key:
                alerts.append(f"⚠️ *{symbol}*: ADX {adx:.1f} (near Ranging)")
                alert_state["triggered"][alert_key] = threshold_key
        
        # Contrarian funding signals (price/funding divergence)
        # Only flag when funding is at least 0.03% in the opposite direction
        if funding is not None and abs(funding) > 0.03:
            if change_24h < 0 and funding > 0:
                # Price down, longs paying → trapped longs
                alert_key = f"{symbol}_contrarian_trapped_longs"
                current_keys.add(alert_key)
                contrarian_key = f"{funding:.4f}_{change_24h:.1f}"
                if alert_state["triggered"].get(alert_key) != contrarian_key:
                    alerts.append(f"⚡ *{symbol}*: CONTRARIAN - Price down, longs paying (trapped longs)")
                    alert_state["triggered"][alert_key] = contrarian_key
            elif change_24h > 0 and funding < 0:
                # Price up, shorts paying → trapped shorts
                alert_key = f"{symbol}_contrarian_squeeze"
                current_keys.add(alert_key)
                contrarian_key = f"{funding:.4f}_{change_24h:.1f}"
                if alert_state["triggered"].get(alert_key) != contrarian_key:
                    alerts.append(f"⚡ *{symbol}*: CONTRARIAN - Price up, shorts paying (squeeze setup)")
                    alert_state["triggered"][alert_key] = contrarian_key
        
        # Funding extreme (threshold: 0.03%)
        if funding is not None and abs(funding) > 0.03:
            alert_key = f"{symbol}_funding_extreme"
            current_keys.add(alert_key)
            funding_key = f"{funding:.4f}"
            if alert_state["triggered"].get(alert_key) != funding_key:
                direction = "longs paying" if funding > 0 else "shorts paying"
                alerts.append(f"🔥 *{symbol}*: Funding {funding:+.2f}% ({direction})")
                alert_state["triggered"][alert_key] = funding_key
        
        # Volume spike (threshold: 3x average)
        if vol_ratio > 3.0:
            alert_key = f"{symbol}_volume_spike"
            current_keys.add(alert_key)
            vol_key = f"{vol_ratio:.1f}"
            if alert_state["triggered"].get(alert_key) != vol_key:
                alerts.append(f"🔊 *{symbol}*: Volume {vol_ratio:.1f}x avg")
                alert_state["triggered"][alert_key] = vol_key
    
    # Clear states for conditions that no longer exist
    # This allows re-alerting when conditions return
    keys_to_clear = []
    for key in alert_state["triggered"]:
        if key not in current_keys:
            keys_to_clear.append(key)
    
    for key in keys_to_clear:
        del alert_state["triggered"][key]
    
    alert_state["last_run"] = now
    return alerts


def main():
    cache = load_cache()
    alert_state = load_alert_state()
    
    # Fetch all assets in parallel
    all_data = []
    with ThreadPoolExecutor(max_workers=17) as executor:
        futures = {executor.submit(fetch_asset_data, asset): asset for asset in CONFIG["watchlist"]}
        for future in as_completed(futures, timeout=60):
            asset, candles, funding, oi, error = future.result()
            all_data.append((asset, candles, funding, oi, error))
    
    # Calculate regime for each asset
    results = []
    cache_updates = {}
    
    for asset, candles, funding, oi, error in all_data:
        if error:
            results.append({"error": error, "symbol": asset["symbol"]})
            continue
        
        if candles is None or len(candles) < 30:
            results.append({"error": "Not enough data", "symbol": asset["symbol"]})
            continue
        
        st, direction = calculate_supertrend(candles,
            CONFIG["indicators"]["supertrend"]["period"],
            CONFIG["indicators"]["supertrend"]["multiplier"])
        adx = calculate_adx(candles, CONFIG["indicators"]["adx"]["period"])
        
        current_price = candles[-1]["close"]
        current_st, current_dir, current_adx = st[-1], direction[-1], adx[-1]
        
        if current_st is None or current_adx is None:
            results.append({"error": "Indicator failed", "symbol": asset["symbol"]})
            continue
        
        regime = get_regime(current_dir, current_adx, CONFIG["indicators"]["adx"])
        
        vol_20 = sum(c["vol"] for c in candles[-20:]) / 20
        vol_current = candles[-1]["vol"]
        vol_ratio = vol_current / vol_20 if vol_20 > 0 else 1
        
        # Calculate 24h price change
        prev_close = candles[-2]["close"] if len(candles) > 1 else current_price
        change_24h = ((current_price - prev_close) / prev_close) * 100 if prev_close > 0 else 0
        
        funding_rate = funding.get("rate")
        
        results.append({
            "symbol": asset["symbol"],
            "regime": regime,
            "adx": current_adx,
            "funding_rate": funding_rate * 100 if funding_rate else None,
            "vol_ratio": vol_ratio,
            "price": current_price,
            "change_24h": change_24h
        })
        
        cache_updates[f"{asset['symbol']}_funding"] = funding_rate
        cache_updates[f"{asset['symbol']}_oi"] = oi
        cache_updates[f"{asset['symbol']}_regime"] = regime
    
    # Check alerts
    alerts = check_alerts(results, cache, alert_state)
    
    # Update cache and state
    cache.update(cache_updates)
    save_cache(cache)
    save_alert_state(alert_state)
    
    # Output alerts (or "no alerts" status)
    if alerts:
        print("🚨 *ALERTS*")
        for alert in alerts:
            print(alert)
        return alerts
    else:
        print("✅ No alerts", file=sys.stderr)
        return []


if __name__ == "__main__":
    main()
