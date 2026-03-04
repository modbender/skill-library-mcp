#!/usr/bin/env python3
"""Crypto prices from Binance and CoinGecko."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.formatters import fmt_price, fmt_change, fmt_number
from lib.rate_limiter import wait_if_needed
import requests


def binance_price(symbol):
    pair = symbol.upper()
    if not pair.endswith("USDT") and not pair.endswith("BUSD"):
        pair = pair + "USDT"
    wait_if_needed("binance")
    d = requests.get("https://api.binance.com/api/v3/ticker/24hr",
                     params={"symbol": pair}, timeout=10).json()
    return {"symbol": symbol.upper(), "pair": pair, "price": float(d["lastPrice"]),
            "change": float(d["priceChange"]), "change_pct": float(d["priceChangePercent"]),
            "high_24h": float(d["highPrice"]), "low_24h": float(d["lowPrice"]),
            "volume_24h": float(d["volume"]), "quote_volume_24h": float(d["quoteVolume"]),
            "source": "Binance"}


def binance_top_gainers(limit=10):
    wait_if_needed("binance")
    data = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=15).json()
    usdt = [d for d in data if d["symbol"].endswith("USDT") and float(d["quoteVolume"]) > 1_000_000]
    usdt.sort(key=lambda x: float(x["priceChangePercent"]), reverse=True)
    return [{"symbol": d["symbol"].replace("USDT", ""), "price": float(d["lastPrice"]),
             "change_pct": float(d["priceChangePercent"]),
             "volume_usdt": float(d["quoteVolume"])} for d in usdt[:limit]]


COIN_MAP = {"BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin", "SOL": "solana",
            "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin", "DOT": "polkadot",
            "AVAX": "avalanche-2", "MATIC": "matic-network", "LINK": "chainlink",
            "UNI": "uniswap", "LTC": "litecoin", "ATOM": "cosmos", "SHIB": "shiba-inu"}


def coingecko_price_try(symbol):
    coin_id = COIN_MAP.get(symbol.upper())
    if not coin_id:
        return {"error": f"Unknown coin: {symbol}. Supported: {', '.join(COIN_MAP.keys())}"}
    wait_if_needed("coingecko")
    data = requests.get("https://api.coingecko.com/api/v3/simple/price",
                        params={"ids": coin_id, "vs_currencies": "try,usd",
                                "include_24hr_change": "true"}, timeout=10).json().get(coin_id, {})
    return {"symbol": symbol.upper(), "price_try": data.get("try", 0),
            "price_usd": data.get("usd", 0), "change_pct_24h": data.get("usd_24h_change", 0),
            "source": "CoinGecko"}


def main():
    parser = argparse.ArgumentParser(description="Crypto prices")
    parser.add_argument("action", choices=["price", "top", "try"])
    parser.add_argument("symbol", nargs="?", default="BTC")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.action == "price":
        r = binance_price(args.symbol)
        if args.json: print(json.dumps(r, indent=2))
        else:
            print(f"**{r['symbol']}** — {fmt_price(r['price'], 'USD')}")
            print(fmt_change(r["change"], r["change_pct"]))
            print(f"24h Range: {fmt_price(r['low_24h'], 'USD')} — {fmt_price(r['high_24h'], 'USD')}")
            print(f"24h Volume: {fmt_number(r['volume_24h'])} coins ({fmt_number(r['quote_volume_24h'])} USDT)")
    elif args.action == "top":
        results = binance_top_gainers(args.limit)
        if args.json: print(json.dumps(results, indent=2))
        else:
            print(f"**Top {args.limit} Crypto Gainers (24h)**\n")
            for i, r in enumerate(results, 1):
                s = "+" if r["change_pct"] >= 0 else ""
                print(f"{i}. **{r['symbol']}** — {fmt_price(r['price'], 'USD')} ({s}{r['change_pct']:.2f}%)")
    elif args.action == "try":
        r = coingecko_price_try(args.symbol)
        if args.json: print(json.dumps(r, indent=2))
        elif "error" in r: print(r["error"])
        else:
            print(f"**{r['symbol']}** — {fmt_price(r['price_try'], 'TRY')} / {fmt_price(r['price_usd'], 'USD')}")
            if r.get("change_pct_24h"):
                s = "+" if r["change_pct_24h"] >= 0 else ""
                print(f"24h: {s}{r['change_pct_24h']:.2f}%")


if __name__ == "__main__":
    main()
