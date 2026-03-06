#!/usr/bin/env python3
"""Volatility scanner for Finam top-100 stocks."""

import json
import math
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

import urllib.request
import urllib.error

BASE_URL = "https://api.finam.ru/v1"
ASSETS_DIR = Path(__file__).parent.parent / "assets"


DEBUG = False


def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def parse_args():
    global DEBUG
    market = "ru"
    n = 10
    for arg in sys.argv[1:]:
        if arg in ("ru", "us"):
            market = arg
        elif arg.isdigit():
            n = int(arg)
        elif arg == "--debug":
            DEBUG = True
    # Validate market to prevent path traversal
    if market not in ("ru", "us"):
        print(f"Error: Invalid market '{market}'. Must be 'ru' or 'us'.", file=sys.stderr)
        sys.exit(1)
    return market, n


def get_token(api_key):
    url = f"{BASE_URL}/sessions"
    payload = json.dumps({"secret": api_key}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read())
    return data["token"]


def load_equities(market):
    path = ASSETS_DIR / f"top_{market}_equities.json"
    with open(path) as f:
        return json.load(f)


def fetch_bars(symbol, token):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=60)
    start_str = start.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_str = end.strftime("%Y-%m-%dT%H:%M:%SZ")
    url = (
        f"{BASE_URL}/instruments/{symbol}/bars"
        f"?timeframe=TIME_FRAME_D"
        f"&interval.startTime={start_str}"
        f"&interval.endTime={end_str}"
    )
    req = urllib.request.Request(url, headers={"Authorization": token})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        return data.get("bars") or []
    except urllib.error.HTTPError as e:
        print(f"  Warning: HTTP {e.code} for {symbol}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  Warning: error fetching {symbol}: {e}", file=sys.stderr)
        return []


def compute_volatility(bars):
    closes = [float(b["close"]["value"]) for b in bars]
    if len(closes) < 5:
        return None
    log_returns = [math.log(closes[i] / closes[i - 1]) for i in range(1, len(closes))]
    n = len(log_returns)
    mean = sum(log_returns) / n
    variance = sum((r - mean) ** 2 for r in log_returns) / (n - 1)
    return math.sqrt(variance) * math.sqrt(252)


def main():
    market, n = parse_args()

    api_key = os.environ.get("FINAM_API_KEY")
    if not api_key:
        print("Error: FINAM_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    _account_id = os.environ.get("FINAM_ACCOUNT_ID")

    dprint("Obtaining JWT token...")
    try:
        token = get_token(api_key)
    except Exception as e:
        print(f"Error: failed to authenticate: {e}", file=sys.stderr)
        sys.exit(1)
    dprint("Token obtained.")

    equities = load_equities(market)
    total = len(equities)
    dprint(f"Fetching bars for {total} {market.upper()} tickers (last 60 days)...")

    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_bars, eq["ticker"], token): eq
            for eq in equities
        }
        done = 0
        for future in as_completed(futures):
            eq = futures[future]
            bars = future.result()
            done += 1
            if not bars:
                dprint(f"  [{done}/{total}] {eq['ticker']} — skipped (no data)")
                continue
            vol = compute_volatility(bars)
            if vol is None:
                dprint(f"  [{done}/{total}] {eq['ticker']} — skipped (only {len(bars)} bars)")
                continue
            results[eq["ticker"]] = {"name": eq["name"], "vol": vol}
            dprint(f"  [{done}/{total}] {eq['ticker']} — {vol * 100:.1f}%")

    if not results:
        print("No results to display.")
        return

    sorted_results = sorted(results.items(), key=lambda x: x[1]["vol"], reverse=True)
    top = sorted_results[:n]

    market_label = "RU" if market == "ru" else "US"
    print(f"\nTop {n} most volatile {market_label} stocks (annualized volatility, last 60 days):\n")
    header = f"{'#':<5}{'Symbol':<18}{'Name':<35}{'Volatility':>10}"
    print(header)
    print("\u2500" * len(header))
    for i, (symbol, info) in enumerate(top, 1):
        print(f"{i:<5}{symbol:<18}{info['name']:<35}{info['vol'] * 100:>9.1f}%")


if __name__ == "__main__":
    main()
