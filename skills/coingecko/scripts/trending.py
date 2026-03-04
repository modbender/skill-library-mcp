#!/usr/bin/env python3
"""Fetch trending coins from CoinGecko."""
import json, urllib.request, urllib.error

def main():
    url = "https://api.coingecko.com/api/v3/search/trending"
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "openclaw-coingecko/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}"}))
        import sys; sys.exit(1)

    results = []
    for item in data.get("coins", []):
        coin = item.get("item", {})
        results.append({
            "id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "name": coin.get("name"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "price_btc": coin.get("price_btc"),
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
