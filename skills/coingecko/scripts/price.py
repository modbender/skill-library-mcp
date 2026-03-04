#!/usr/bin/env python3
"""Fetch current prices for one or more CoinGecko coin IDs."""
import sys, json, urllib.request, urllib.error

def main():
    if len(sys.argv) < 2:
        print("Usage: price.py <coin_id> [coin_id2 ...]", file=sys.stderr)
        sys.exit(1)

    ids = ",".join(sys.argv[1:])
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&ids={ids}&order=market_cap_desc&sparkline=false&price_change_percentage=24h,7d"

    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "openclaw-coingecko/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}", "message": e.read().decode()[:500]}))
        sys.exit(1)

    results = []
    for coin in data:
        results.append({
            "id": coin["id"],
            "symbol": coin["symbol"].upper(),
            "name": coin["name"],
            "price": coin["current_price"],
            "market_cap": coin["market_cap"],
            "volume_24h": coin["total_volume"],
            "change_24h_pct": coin.get("price_change_percentage_24h"),
            "change_7d_pct": coin.get("price_change_percentage_7d_in_currency"),
            "high_24h": coin["high_24h"],
            "low_24h": coin["low_24h"],
            "ath": coin["ath"],
            "ath_change_pct": coin["ath_change_percentage"],
            "rank": coin["market_cap_rank"],
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
