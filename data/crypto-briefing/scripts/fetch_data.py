#!/usr/bin/env python3
"""
Fetch crypto prices from CoinGecko and Fear & Greed Index.
Usage: python fetch_data.py
"""

import json
import urllib.request
import sys

def fetch_json(url):
    """Fetch JSON data from URL."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def main():
    # Fetch prices
    coin_ids = "bitcoin,ethereum,solana,sui,worldcoin-wld,dogwifcoin"
    price_url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd&include_24hr_change=true"
    
    prices = fetch_json(price_url)
    
    # Fetch Fear & Greed Index
    fng_url = "https://api.alternative.me/fng/?limit=1"
    fng_data = fetch_json(fng_url)
    
    if not prices or not fng_data:
        print("Failed to fetch data", file=sys.stderr)
        sys.exit(1)
    
    # Combine results
    result = {
        "prices": prices,
        "fear_greed": fng_data["data"][0] if fng_data.get("data") else None
    }
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
