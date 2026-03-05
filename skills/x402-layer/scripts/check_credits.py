#!/usr/bin/env python3
"""
x402 Credit Balance Check

Check your credit balance for a credits-mode endpoint.

Usage:
    python check_credits.py <endpoint_slug>

Example:
    python check_credits.py weather-data

Environment Variables:
    WALLET_ADDRESS - Your wallet address
"""

import json
import os
import sys
import requests

API_BASE = "https://api.x402layer.cc"


def load_wallet() -> str:
    wallet = os.getenv("WALLET_ADDRESS")
    if not wallet:
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
            wallet = os.getenv("WALLET_ADDRESS")
        except Exception:
            pass

    if not wallet:
        raise ValueError("Set WALLET_ADDRESS environment variable")
    return wallet


def check_credits(endpoint_slug: str) -> dict:
    wallet = load_wallet()
    url = f"{API_BASE}/e/{endpoint_slug}"

    print(f"Checking credits for: {endpoint_slug}")
    print(f"Wallet: {wallet}")

    response = requests.get(
        url,
        params={"action": "balance", "wallet": wallet},
        headers={"Accept": "application/json"},
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        print(f"Balance: {data.get('balance', 0)} credits")
        return data

    return {"error": f"Status {response.status_code}", "response": response.text}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python check_credits.py <endpoint_slug>")
        sys.exit(1)

    try:
        result = check_credits(sys.argv[1])
    except requests.RequestException as exc:
        result = {"error": str(exc)}
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
