#!/usr/bin/env python3
"""
x402Compute — Extend an instance's lifetime.

Handles the full x402 payment flow:
1. POST /compute/instances/:id/extend → get 402 challenge
2. Sign USDC TransferWithAuthorization locally
3. Resend with X-Payment header → instance extended

Usage:
  python extend_instance.py <instance_id> [--hours N] [--network base|solana]

Example:
  python extend_instance.py abc-123 --hours 720  # extend by 1 month
"""

import argparse
import json
import sys
from typing import Dict

import requests

from solana_signing import create_solana_xpayment_from_accept, ensure_solana_destination_ready
from wallet_signing import create_compute_auth_headers, load_compute_chain, load_payment_signer

BASE_URL = "https://compute.x402layer.cc"


def _find_accept_option(challenge: dict, requested_network: str) -> dict:
    for option in challenge.get("accepts", []):
        network = str(option.get("network", "")).lower()
        if requested_network == "base" and (network == "base" or "8453" in network):
            return option
        if requested_network == "solana" and (network == "solana" or network.startswith("solana:")):
            return option
    raise ValueError(f"No {requested_network} payment option found in 402 challenge")


def extend_instance(instance_id: str, hours: int = 720, network: str = "base") -> dict:
    """Extend a compute instance with x402 payment."""
    body = {
        "extend_hours": hours,
        "network": network,
    }
    body_json = json.dumps(body, separators=(",", ":"))
    auth_chain = load_compute_chain()

    print(f"Extending instance {instance_id} by {hours} hours...")

    # Step 1: Get 402 challenge
    path = f"/compute/instances/{instance_id}/extend"
    auth_headers: Dict[str, str] = {}
    try:
        auth_headers = create_compute_auth_headers("POST", path, body_json, chain=auth_chain)
    except Exception as exc:
        return {"error": f"Failed to build auth headers: {exc}"}
    response = requests.post(
        f"{BASE_URL}/compute/instances/{instance_id}/extend",
        data=body_json,
        headers={
            "Content-Type": "application/json",
            **auth_headers,
        },
        timeout=30,
    )

    if response.status_code == 200:
        print("Instance extended (no payment required)")
        return response.json()

    if response.status_code != 402:
        return {"error": f"Unexpected status {response.status_code}", "response": response.text[:500]}

    challenge = response.json()

    option = _find_accept_option(challenge, network)

    pay_to = option["payTo"]
    amount = int(option["maxAmountRequired"])
    print(f"Payment required: {amount} atomic USDC units (${amount / 1_000_000:.2f})")

    if network == "base":
        signer = load_payment_signer()
        x_payment = signer.create_x402_payment_header(pay_to=pay_to, amount=amount)
    else:
        ensure_solana_destination_ready(option)
        x_payment = create_solana_xpayment_from_accept(option)

    # Step 2: Pay and extend
    # NOTE: Do NOT send compute auth headers here.
    # The x402 X-Payment header authenticates the payer via on-chain payment.
    # Sending auth headers causes 401 (nonce already consumed from step 1).
    response = requests.post(
        f"{BASE_URL}/compute/instances/{instance_id}/extend",
        data=body_json,
        headers={
            "Content-Type": "application/json",
            "X-Payment": x_payment,
        },
        timeout=60,
    )

    print(f"Response: {response.status_code}")

    if response.status_code in (200, 201):
        data = response.json()
        order = data.get("order", {})
        print(f"✅ Instance extended!")
        print(f"   New Expiry: {order.get('expires_at', 'N/A')}")
        if data.get("tx_hash"):
            print(f"   TX: {data['tx_hash']}")
        return data

    return {"error": f"Extension failed: {response.status_code}", "response": response.text[:500]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extend a compute instance")
    parser.add_argument("instance_id", help="Instance ID to extend")
    parser.add_argument("--hours", type=int, default=720, help="Hours to extend (default: 720 = ~1 month)")
    parser.add_argument("--network", default="base", choices=["base", "solana"], help="Payment network")
    args = parser.parse_args()

    result = extend_instance(
        instance_id=args.instance_id,
        hours=args.hours,
        network=args.network,
    )
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
