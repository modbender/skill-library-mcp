#!/usr/bin/env python3
"""
x402 Payment - Solana Network

Pay for API access using USDC on Solana.

Signer support:
- private-key mode: SOLANA_SECRET_KEY
- coinbase-wallet mode: CDP_SOLANA_ACCOUNT_ADDRESS + CDP credentials
"""

import json
import sys

import requests

from solana_signing import create_solana_xpayment_from_accept, has_solana_credentials, load_solana_wallet_address


def _find_solana_accept(challenge: dict) -> dict:
    for option in challenge.get("accepts", []):
        if str(option.get("network", "")).lower() == "solana":
            return option
    raise ValueError("No Solana payment option available in challenge")


def pay_for_access(endpoint_url: str) -> dict:
    """Execute paid request to an x402 endpoint using Solana payment option."""
    if not has_solana_credentials():
        return {
            "error": (
                "No Solana signer available. Set SOLANA_SECRET_KEY, or set CDP_API_KEY_ID, "
                "CDP_API_KEY_SECRET, CDP_WALLET_SECRET, CDP_SOLANA_ACCOUNT_ADDRESS."
            )
        }

    print(f"Requesting: {endpoint_url}")

    response = requests.get(endpoint_url, headers={"Accept": "application/json"}, timeout=30)

    if response.status_code == 200:
        print("Access granted (free endpoint)")
        return response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text}

    if response.status_code != 402:
        return {"error": f"Unexpected status: {response.status_code}", "response": response.text}

    challenge = response.json()
    try:
        solana_option = _find_solana_accept(challenge)
    except ValueError as exc:
        return {"error": str(exc)}

    print(f"Solana payment required: {solana_option.get('maxAmountRequired')} atomic units")

    try:
        x_payment = create_solana_xpayment_from_accept(solana_option)
    except Exception as exc:
        return {"error": f"Failed to create Solana payment: {exc}"}

    wallet_address = load_solana_wallet_address()
    if not wallet_address:
        return {"error": "Failed to resolve Solana wallet address"}

    response = requests.get(
        endpoint_url,
        headers={
            "X-Payment": x_payment,
            "x-wallet-address": wallet_address,
            "Accept": "application/json",
        },
        timeout=45,
    )

    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        return response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text[:500]}

    return {"error": response.text}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pay_solana.py <endpoint_url>")
        sys.exit(1)

    result = pay_for_access(sys.argv[1])
    print(json.dumps(result, indent=2)[:2000])
