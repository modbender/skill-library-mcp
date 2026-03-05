#!/usr/bin/env python3
"""
x402 Credit Recharge (CONSUMER)

Buy credits for a credits-mode endpoint.

Flow:
1) GET /e/{slug}?action=purchase -> 402 challenge
2) GET /e/{slug}?action=purchase with X-Payment -> settles + adds credits

Modes:
- private-key (default): Base + Solana supported
- awal: Base payments via AWAL CLI
"""

import json
import sys
from typing import Optional

import requests

from awal_bridge import awal_pay_url
from network_selection import pick_payment_option
from solana_signing import create_solana_xpayment_from_accept, load_solana_wallet_address
from wallet_signing import is_awal_mode, load_wallet_address

API_BASE = "https://api.x402layer.cc"


def get_available_packs(endpoint_slug: str) -> list:
    """Return synthetic pack info from worker challenge (single-package model)."""
    url = f"{API_BASE}/e/{endpoint_slug}"
    response = requests.get(url, params={"action": "purchase"}, headers={"Accept": "application/json"}, timeout=30)

    if response.status_code != 402:
        return []

    challenge = response.json()
    package = challenge.get("credit_package", {})
    accepts = challenge.get("accepts", [])

    if not package and not accepts:
        return []

    first = accepts[0] if accepts else {}
    max_amount = None
    raw = first.get("maxAmountRequired")
    if raw is not None:
        try:
            max_amount = float(raw) / 1_000_000
        except Exception:
            max_amount = None

    return [
        {
            "id": "default",
            "credits": package.get("size"),
            "price_usdc": max_amount,
            "network": first.get("network"),
            "purchase_url": f"{API_BASE}/e/{endpoint_slug}?action=purchase",
        }
    ]


def recharge_credits(endpoint_slug: str, pack_id: Optional[str] = None) -> dict:
    if pack_id:
        print(f"Note: pack_id '{pack_id}' is ignored on current API (single package endpoint model).")

    url = f"{API_BASE}/e/{endpoint_slug}"
    params = {"action": "purchase"}

    print(f"Purchasing credits for endpoint: {endpoint_slug}")

    if is_awal_mode():
        wallet = load_wallet_address(required=False)
        headers = {"Accept": "application/json"}
        if wallet:
            headers["x-wallet-address"] = wallet
        print("Payment mode: AWAL (Base)")
        return awal_pay_url(f"{url}?action=purchase", method="GET", headers=headers)

    response = requests.get(url, params=params, headers={"Accept": "application/json"}, timeout=30)

    if response.status_code != 402:
        return {"error": f"Unexpected status: {response.status_code}", "response": response.text}

    challenge = response.json()
    try:
        selected_network, selected_option, signer = pick_payment_option(challenge, context="credit purchase")
    except ValueError as exc:
        return {"error": str(exc)}

    try:
        if selected_network == "base":
            if signer is None:
                return {"error": "Internal error: missing Base signer"}
            x_payment = signer.create_x402_payment_header(
                pay_to=selected_option["payTo"],
                amount=int(selected_option["maxAmountRequired"]),
            )
            wallet = signer.wallet
        else:
            x_payment = create_solana_xpayment_from_accept(selected_option)
            wallet = load_solana_wallet_address()
            if not wallet:
                return {"error": "Failed to derive Solana wallet address"}
    except Exception as exc:
        return {"error": f"Failed to build {selected_network} payment: {exc}"}

    response = requests.get(
        url,
        params=params,
        headers={
            "X-Payment": x_payment,
            "x-wallet-address": wallet,
            "Accept": "application/json",
        },
        timeout=45,
    )

    print(f"Payment network used: {selected_network}")
    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        return response.json()

    return {"error": response.text}


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python recharge_credits.py <endpoint_slug> [pack_id]")
        print("       python recharge_credits.py --list <endpoint_slug>")
        sys.exit(1)

    if sys.argv[1] == "--list":
        if len(sys.argv) < 3:
            print("Usage: python recharge_credits.py --list <endpoint_slug>")
            sys.exit(1)
        packs = get_available_packs(sys.argv[2])
        print(json.dumps(packs, indent=2))
        return

    endpoint_slug = sys.argv[1]
    pack_id = sys.argv[2] if len(sys.argv) >= 3 else None
    result = recharge_credits(endpoint_slug, pack_id)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(1)
