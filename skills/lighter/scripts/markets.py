"""
Lighter Protocol - List markets (read-only)
"""
import requests

API_BASE = "https://mainnet.zklighter.elliot.ai/api/v1"

def list_markets():
    response = requests.get(f"{API_BASE}/orderBooks")
    data = response.json()
    
    markets = data.get("order_books", [])
    print(f"Total markets: {len(markets)}\n")
    
    for m in markets[:20]:
        print(f"{m.get('symbol')}: ID={m.get('market_id')}, Type={m.get('market_type')}")
    
    if len(markets) > 20:
        print(f"\n... and {len(markets) - 20} more")

if __name__ == "__main__":
    list_markets()
