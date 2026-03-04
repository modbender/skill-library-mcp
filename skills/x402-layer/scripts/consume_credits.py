#!/usr/bin/env python3
"""
x402 Credit-Based Consumption

Consume API endpoints using pre-purchased credits instead of per-request payments.
Credits provide instant access without blockchain latency.

Usage:
    python consume_credits.py <endpoint_url>
    
Example:
    python consume_credits.py https://api.x402layer.cc/e/weather-data
    
Environment Variables:
    WALLET_ADDRESS - Your wallet address (0x... for EVM, base58 for Solana)
"""

import os
import sys
import json
import requests
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def load_wallet():
    """Load wallet address from environment."""
    wallet = os.getenv("WALLET_ADDRESS")
    if not wallet:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            wallet = os.getenv("WALLET_ADDRESS")
        except ImportError:
            pass
    
    if not wallet:
        print("Error: Set WALLET_ADDRESS environment variable")
        sys.exit(1)
    return wallet

def consume_with_credits(endpoint_url: str) -> dict:
    """Consume an endpoint using credits."""
    wallet = load_wallet()
    parsed = urlparse(endpoint_url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query["useCredits"] = "1"
    credits_url = urlunparse(parsed._replace(query=urlencode(query)))
    
    print(f"Wallet: {wallet}")
    print(f"Consuming: {credits_url}")
    
    try:
        response = requests.get(
            credits_url,
            headers={
                "x-wallet-address": wallet,
                "Accept": "application/json"
            },
            timeout=30
        )
    except requests.RequestException as exc:
        return {"error": str(exc)}
    
    print(f"Response: {response.status_code}")
    
    if response.status_code == 200:
        return response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text[:500]}
    elif response.status_code == 402:
        return {"error": "Insufficient credits", "challenge": response.json()}
    else:
        return {"error": response.text}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python consume_credits.py <endpoint_url>")
        sys.exit(1)
    
    result = consume_with_credits(sys.argv[1])
    print(json.dumps(result, indent=2)[:500])
