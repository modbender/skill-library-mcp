#!/usr/bin/env python3
"""
x402 Payment - Base (EVM) Network

Pay for API access on Base.

Modes:
- private-key (default): PRIVATE_KEY + WALLET_ADDRESS
- awal: Coinbase Agentic Wallet CLI (AWAL)
"""

import json
import sys

import requests

from awal_bridge import awal_pay_url
from wallet_signing import is_awal_mode, load_payment_signer, load_wallet_address


def _find_base_accept_option(challenge: dict) -> dict:
    for option in challenge.get("accepts", []):
        network = str(option.get("network", "")).lower()
        if network == "base" or "8453" in network:
            return option
    raise ValueError("No Base payment option found in challenge")


def pay_for_access(endpoint_url: str) -> dict:
    """Execute paid request to an x402 endpoint."""
    if is_awal_mode():
        wallet = load_wallet_address(required=False)
        headers = {"x-wallet-address": wallet} if wallet else None
        print(f"Requesting with AWAL: {endpoint_url}")
        return awal_pay_url(endpoint_url, method="GET", headers=headers)

    signer = load_payment_signer()

    print(f"Requesting: {endpoint_url}")

    response = requests.get(endpoint_url, headers={"Accept": "application/json"}, timeout=30)

    if response.status_code == 200:
        print("Access granted (free endpoint or already authorized)")
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"data": response.text[:500]}

    if response.status_code != 402:
        return {"error": f"Unexpected status {response.status_code}", "response": response.text}

    challenge = response.json()
    base_option = _find_base_accept_option(challenge)

    pay_to = base_option["payTo"]
    amount = int(base_option["maxAmountRequired"])
    print(f"Payment required: {amount} atomic USDC units")

    x_payment = signer.create_x402_payment_header(pay_to=pay_to, amount=amount)

    response = requests.get(
        endpoint_url,
        headers={
            "X-Payment": x_payment,
            "x-wallet-address": signer.wallet,
            "Accept": "application/json",
        },
        timeout=45,
    )

    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        if response.headers.get("content-type", "").startswith("application/json"):
            return response.json()
        return {"data": response.text[:500]}

    return {"error": response.text}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pay_base.py <endpoint_url>")
        sys.exit(1)

    result = pay_for_access(sys.argv[1])
    print(json.dumps(result, indent=2)[:2000])
