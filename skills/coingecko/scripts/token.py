#!/usr/bin/env python3
"""Look up a token by contract address on a given platform."""
import sys, json, urllib.request, urllib.error

PLATFORMS = {"solana": "solana", "ethereum": "ethereum", "base": "base", "arbitrum": "arbitrum-one", "polygon": "polygon-pos"}

def main():
    if len(sys.argv) < 3:
        print("Usage: token.py <platform> <contract_address>", file=sys.stderr)
        print(f"Platforms: {', '.join(PLATFORMS.keys())}", file=sys.stderr)
        sys.exit(1)

    platform = PLATFORMS.get(sys.argv[1].lower(), sys.argv[1].lower())
    address = sys.argv[2]
    url = f"https://api.coingecko.com/api/v3/coins/{platform}/contract/{address}"

    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "openclaw-coingecko/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(json.dumps({"error": "Token not found", "platform": platform, "address": address}))
        else:
            print(json.dumps({"error": f"HTTP {e.code}", "message": e.read().decode()[:500]}))
        sys.exit(1)

    market = data.get("market_data", {})
    result = {
        "id": data.get("id"),
        "symbol": data.get("symbol", "").upper(),
        "name": data.get("name"),
        "price_usd": market.get("current_price", {}).get("usd"),
        "market_cap_usd": market.get("market_cap", {}).get("usd"),
        "volume_24h_usd": market.get("total_volume", {}).get("usd"),
        "change_24h_pct": market.get("price_change_percentage_24h"),
        "change_7d_pct": market.get("price_change_percentage_7d"),
        "total_supply": market.get("total_supply"),
        "circulating_supply": market.get("circulating_supply"),
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
