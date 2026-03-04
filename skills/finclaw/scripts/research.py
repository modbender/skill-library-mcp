#!/usr/bin/env python3
"""Deep-dive ticker research."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.config import get_api_key
from lib.formatters import fmt_price, fmt_number, detect_asset_type
from lib.rate_limiter import wait_if_needed
from scripts.quote import get_quote
import requests


def research(symbol):
    symbol = symbol.upper()
    asset_type = detect_asset_type(symbol)
    result = {"symbol": symbol, "asset_type": asset_type}
    try: result["quote"] = get_quote(symbol, force=True)
    except: result["quote"] = {"error": "unavailable"}

    if asset_type in ("stock_us", "stock_bist"):
        import yfinance as yf
        ticker_sym = symbol if asset_type == "stock_us" else (symbol if symbol.endswith(".IS") else symbol + ".IS")
        wait_if_needed("yfinance")
        try:
            info = yf.Ticker(ticker_sym).info
            result["info"] = {k: info.get(k) for k in ["longName", "sector", "industry", "marketCap",
                "trailingPE", "forwardPE", "trailingEps", "dividendYield", "beta",
                "fiftyTwoWeekHigh", "fiftyTwoWeekLow", "averageVolume", "longBusinessSummary"]}
            if result["info"].get("longBusinessSummary"):
                result["info"]["longBusinessSummary"] = result["info"]["longBusinessSummary"][:500]
        except: result["info"] = {}
    return result


def format_research(d):
    lines = [f"**Research: {d['symbol']}** ({d['asset_type']})\n"]
    q = d.get("quote", {})
    if "error" not in q:
        c = q.get("currency", "USD")
        lines.append(f"**Price**: {fmt_price(q.get('price', 0), c)}")
        if q.get("change_pct") is not None:
            lines.append(f"Change: {'+' if q['change_pct'] >= 0 else ''}{q['change_pct']:.2f}%")
    info = d.get("info", {})
    if info:
        if info.get("longName"): lines.append(f"\n**{info['longName']}**")
        if info.get("sector"): lines.append(f"Sector: {info['sector']} | Industry: {info.get('industry', 'N/A')}")
        if info.get("marketCap"): lines.append(f"Market Cap: {fmt_number(info['marketCap'])}")
        if info.get("trailingPE"): lines.append(f"P/E: {info['trailingPE']:.2f}")
        if info.get("trailingEps"): lines.append(f"EPS: {info['trailingEps']:.2f}")
        if info.get("dividendYield"): lines.append(f"Div Yield: {info['dividendYield']*100:.2f}%")
        if info.get("beta"): lines.append(f"Beta: {info['beta']:.2f}")
        if info.get("fiftyTwoWeekHigh") and info.get("fiftyTwoWeekLow"):
            lines.append(f"52W Range: {info['fiftyTwoWeekLow']:.2f} — {info['fiftyTwoWeekHigh']:.2f}")
        if info.get("longBusinessSummary"): lines.append(f"\n**About**: {info['longBusinessSummary']}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Ticker research")
    parser.add_argument("symbol"); parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    d = research(args.symbol)
    print(json.dumps(d, indent=2, default=str) if args.json else format_research(d))


if __name__ == "__main__":
    main()
