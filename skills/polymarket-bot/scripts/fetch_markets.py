# fetch_markets.py

import requests
import json

def fetch_active_markets(limit=20):
    url = "https://gamma-api.polymarket.com/markets"
    params = {"active": "true", "closed": "false", "limit": str(limit)}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        markets = response.json()
        return markets  # Returns list of markets with ID, question, outcomes, and prices
    except requests.exceptions.RequestException as e:
        print(f"Error fetching markets: {e}")
        return None

# Example usage
if __name__ == "__main__":
    markets = fetch_active_markets()
    if markets:
        for market in markets:
            print(f"Market ID: {market.get('id')}, Question: {market.get('question')}")
