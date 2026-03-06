#!/usr/bin/env python3
"""Search CoinGecko for a coin by name or ticker."""
import sys, json, urllib.request, urllib.error, urllib.parse

def main():
    if len(sys.argv) < 2:
        print("Usage: search.py <query>", file=sys.stderr)
        sys.exit(1)

    query = urllib.parse.quote(" ".join(sys.argv[1:]))
    url = f"https://api.coingecko.com/api/v3/search?query={query}"

    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "openclaw-coingecko/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": f"HTTP {e.code}"}))
        sys.exit(1)

    results = []
    for coin in data.get("coins", [])[:10]:
        results.append({
            "id": coin["id"],
            "symbol": coin["symbol"],
            "name": coin["name"],
            "market_cap_rank": coin.get("market_cap_rank"),
        })

    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
