#!/usr/bin/env python3
"""Fetch real-time quotes for US stocks, BIST, crypto, and forex."""

import sys
import os
import json
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.formatters import fmt_price, fmt_change, fmt_volume, detect_asset_type, symbol_normalize
from lib.rate_limiter import wait_if_needed
from lib.db import get_connection


def get_cached_price(symbol, asset_type, max_age_seconds=60):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM price_cache WHERE symbol=? AND asset_type=? "
            "AND fetched_at > datetime('now', ?)",
            (symbol, asset_type, f"-{max_age_seconds} seconds")
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_cache(symbol, asset_type, price, change=None, change_pct=None, volume=None):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO price_cache "
            "(symbol, asset_type, price, change, change_pct, volume, fetched_at) "
            "VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (symbol, asset_type, price, change, change_pct, volume)
        )
        conn.commit()
    finally:
        conn.close()


def quote_us_stock(symbol):
    import requests
    api_key = get_api_key("finnhubApiKey")
    if not api_key:
        return quote_stock_yf(symbol)
    wait_if_needed("finnhub")
    resp = requests.get("https://finnhub.io/api/v1/quote",
                        params={"symbol": symbol, "token": api_key}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("c", 0) == 0:
        return quote_stock_yf(symbol)
    return {"symbol": symbol, "price": data["c"], "change": data["d"],
            "change_pct": data["dp"], "high": data["h"], "low": data["l"],
            "open": data["o"], "prev_close": data["pc"], "currency": "USD", "source": "Finnhub"}


def quote_stock_yf(symbol):
    import yfinance as yf
    wait_if_needed("yfinance")
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info
    price = info.last_price
    prev = info.previous_close
    change = price - prev if prev else 0
    change_pct = (change / prev * 100) if prev else 0
    return {"symbol": symbol, "price": price, "change": round(change, 2),
            "change_pct": round(change_pct, 2), "high": getattr(info, 'day_high', None),
            "low": getattr(info, 'day_low', None), "open": getattr(info, 'open', None),
            "prev_close": prev, "currency": "USD", "source": "yfinance"}


def quote_bist(symbol):
    import yfinance as yf
    if not symbol.endswith(".IS"):
        symbol = symbol + ".IS"
    wait_if_needed("yfinance")
    ticker = yf.Ticker(symbol)
    info = ticker.fast_info
    price = info.last_price
    prev = info.previous_close
    change = price - prev if prev else 0
    change_pct = (change / prev * 100) if prev else 0
    return {"symbol": symbol, "price": price, "change": round(change, 2),
            "change_pct": round(change_pct, 2), "high": getattr(info, 'day_high', None),
            "low": getattr(info, 'day_low', None), "open": getattr(info, 'open', None),
            "prev_close": prev, "currency": "TRY", "source": "yfinance"}


def quote_crypto(symbol):
    import requests
    pair = symbol.upper()
    if not pair.endswith("USDT") and not pair.endswith("BUSD"):
        pair = pair + "USDT"
    wait_if_needed("binance")
    resp = requests.get("https://api.binance.com/api/v3/ticker/24hr",
                        params={"symbol": pair}, timeout=10)
    resp.raise_for_status()
    d = resp.json()
    return {"symbol": symbol.upper(), "pair": pair, "price": float(d["lastPrice"]),
            "change": float(d["priceChange"]), "change_pct": float(d["priceChangePercent"]),
            "high": float(d["highPrice"]), "low": float(d["lowPrice"]),
            "volume": float(d["volume"]), "currency": "USDT", "source": "Binance"}


def quote_forex(symbol):
    import requests
    api_key = get_api_key("exchangeRateApiKey")
    parts = symbol.replace("/", "").upper()
    base, target = parts[:3], parts[3:]
    if api_key:
        wait_if_needed("exchangerate")
        resp = requests.get(f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{base}/{target}", timeout=10)
        resp.raise_for_status()
        rate = resp.json()["conversion_rate"]
    else:
        wait_if_needed("exchangerate")
        resp = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=10)
        resp.raise_for_status()
        rate = resp.json()["rates"].get(target, 0)
    return {"symbol": f"{base}/{target}", "price": rate, "change": None,
            "change_pct": None, "currency": target, "source": "ExchangeRate-API"}


def get_quote(symbol, force=False):
    symbol = symbol_normalize(symbol)
    asset_type = detect_asset_type(symbol)
    if not force:
        cached = get_cached_price(symbol, asset_type)
        if cached:
            return {"symbol": symbol, "price": cached["price"], "change": cached["change"],
                    "change_pct": cached["change_pct"], "volume": cached["volume"],
                    "asset_type": asset_type, "cached": True, "source": "cache"}

    fetchers = {"stock_us": quote_us_stock, "stock_bist": quote_bist,
                "crypto": quote_crypto, "forex": quote_forex}
    result = fetchers[asset_type](symbol)
    result["asset_type"] = asset_type
    update_cache(symbol, asset_type, result["price"],
                 result.get("change"), result.get("change_pct"), result.get("volume"))
    return result


def format_quote(q):
    if "error" in q:
        return f"Error: {q['error']}"
    currency = q.get("currency", "USD")
    lines = [f"**{q['symbol']}** — {fmt_price(q['price'], currency)}"]
    if q.get("change") is not None and q.get("change_pct") is not None:
        lines.append(fmt_change(q["change"], q["change_pct"]))
    details = []
    if q.get("open"): details.append(f"Open: {fmt_price(q['open'], currency)}")
    if q.get("high"): details.append(f"High: {fmt_price(q['high'], currency)}")
    if q.get("low"): details.append(f"Low: {fmt_price(q['low'], currency)}")
    if q.get("volume"): details.append(fmt_volume(q["volume"]))
    if details: lines.append(" | ".join(details))
    src = "cached" if q.get("cached") else q.get("source", "")
    lines.append(f"_Source: {src}_")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Get financial quotes")
    parser.add_argument("symbols", nargs="+", help="Ticker symbol(s)")
    parser.add_argument("--force", action="store_true", help="Skip cache")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()
    results = [get_quote(sym, force=args.force) for sym in args.symbols]
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        for q in results:
            print(format_quote(q))
            print()


if __name__ == "__main__":
    main()
