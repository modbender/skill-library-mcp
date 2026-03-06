#!/usr/bin/env python3
"""
x402 Endpoint Credit Topup (PROVIDER)

Add credits to YOUR OWN agentic endpoint.

Modes:
- private-key (default): Base + Solana supported
- awal: Base payments via AWAL CLI
"""

import json
import os
import sys

import requests

from awal_bridge import awal_pay_url
from network_selection import pick_payment_option
from solana_signing import create_solana_xpayment_from_accept
from wallet_signing import is_awal_mode, load_wallet_address

API_BASE = "https://api.x402layer.cc"


def _load_api_key() -> str:
    api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        try:
            from dotenv import load_dotenv  # type: ignore

            load_dotenv()
            api_key = os.getenv("X_API_KEY") or os.getenv("API_KEY")
        except Exception:
            pass
    if not api_key:
        raise ValueError("Set X_API_KEY (or API_KEY) environment variable")
    return api_key


def topup_endpoint(endpoint_slug: str, amount_usd: float) -> dict:
    if amount_usd <= 0:
        return {"error": "Amount must be positive"}

    api_key = _load_api_key()

    url = f"{API_BASE}/agent/endpoints"
    params = {"slug": endpoint_slug}
    data = {"topup_amount": amount_usd}

    print(f"[PROVIDER] Topping up endpoint: {endpoint_slug}")
    print(f"Amount: ${amount_usd} USD")

    if is_awal_mode():
        wallet = load_wallet_address(required=False)
        headers = {"X-API-Key": api_key}
        if wallet:
            headers["x-wallet-address"] = wallet
        print("Payment mode: AWAL (Base)")
        return awal_pay_url(
            f"{url}?slug={endpoint_slug}",
            method="PUT",
            data=data,
            headers=headers,
        )

    response = requests.put(
        url,
        params=params,
        json=data,
        headers={"X-API-Key": api_key},
        timeout=30,
    )

    if response.status_code != 402:
        if response.status_code == 401:
            return {"error": "Invalid API key. Use the endpoint API key returned at creation time."}
        return {"error": f"Unexpected status: {response.status_code}", "response": response.text}

    challenge = response.json()
    try:
        selected_network, selected_option, signer = pick_payment_option(challenge, context="endpoint topup")
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
        else:
            x_payment = create_solana_xpayment_from_accept(selected_option)
    except Exception as exc:
        return {"error": f"Failed to build {selected_network} payment: {exc}"}

    response = requests.put(
        url,
        params=params,
        json=data,
        headers={
            "X-API-Key": api_key,
            "X-Payment": x_payment,
        },
        timeout=45,
    )

    print(f"Payment network used: {selected_network}")
    print(f"Response: {response.status_code}")

    if response.status_code == 200:
        print("\nCredits added to endpoint")
        return response.json()

    return {"error": response.text}


def main() -> None:
    if len(sys.argv) < 3:
        print("=" * 60)
        print("PROVIDER MODE: Top up YOUR OWN endpoint credits")
        print("=" * 60)
        print("\nUsage: python topup_endpoint.py <your_endpoint_slug> <amount_usd>")
        print("Example: python topup_endpoint.py my-weather-api 10")
        print("\nRequired env: X_API_KEY (or API_KEY)")
        sys.exit(1)

    result = topup_endpoint(sys.argv[1], float(sys.argv[2]))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, indent=2))
        sys.exit(1)
