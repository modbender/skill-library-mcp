#!/usr/bin/env python3
"""
x402Compute — Provision a new compute instance.

Handles the full x402 payment flow:
1. POST /compute/provision → get 402 challenge
2. Sign USDC TransferWithAuthorization locally
3. Resend with X-Payment header → instance provisioned

Usage:
  python provision.py <plan_id> <region> [--months N | --days N] [--os-id ID] [--label NAME] [--network base|solana] [--ssh-public-key KEY | --ssh-key-file PATH]

Example:
  python provision.py vcg-a100-1c-2g-6gb lax --months 1 --label "my-gpu"
  python provision.py vc2-1c-1gb ewr --days 1 --label "test-daily"
"""

import argparse
import json
import os
import sys
from typing import Dict, Optional

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


def provision_instance(
    plan: str,
    region: str,
    months: int = 0,
    days: int = 0,
    os_id: int = 2284,
    label: str = "x402-instance",
    network: str = "base",
    ssh_public_key: Optional[str] = None,
) -> dict:
    """Provision a compute instance with x402 payment."""
    if days > 0:
        prepaid_hours = days * 24
        duration_label = f"{days} day(s)"
    else:
        prepaid_hours = max(1, months) * 720
        duration_label = f"{max(1, months)} month(s)"
    body = {
        "plan": plan,
        "region": region,
        "os_id": os_id,
        "label": label,
        "prepaid_hours": prepaid_hours,
        "network": network,
    }
    if ssh_public_key:
        body["ssh_public_key"] = ssh_public_key.strip()
    body_json = json.dumps(body, separators=(",", ":"))
    auth_chain = load_compute_chain()

    print(f"Provisioning {plan} in {region} for {duration_label}...")

    # Step 1: Get 402 challenge
    path = "/compute/provision"
    auth_headers: Dict[str, str] = {}
    try:
        auth_headers = create_compute_auth_headers("POST", path, body_json, chain=auth_chain)
    except Exception as exc:
        return {"error": f"Failed to build auth headers: {exc}"}
    response = requests.post(
        f"{BASE_URL}/compute/provision",
        data=body_json,
        headers={
            "Content-Type": "application/json",
            **auth_headers,
        },
        timeout=30,
    )

    if response.status_code == 200:
        print("Instance provisioned (no payment required)")
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

    # Step 2: Pay and provision
    # NOTE: Do NOT send compute auth headers here.
    # The x402 X-Payment header authenticates the payer via on-chain payment.
    # Sending auth headers causes 401 (nonce already consumed from step 1).
    response = requests.post(
        f"{BASE_URL}/compute/provision",
        data=body_json,
        headers={
            "Content-Type": "application/json",
            "X-Payment": x_payment,
        },
        timeout=120,
    )

    print(f"Response: {response.status_code}")

    if response.status_code in (200, 201):
        data = response.json()
        order = data.get("order", {})
        print(f"✅ Instance provisioned!")
        print(f"   ID:      {order.get('id', 'N/A')}")
        print(f"   IP:      {order.get('ip_address', 'pending')}")
        print(f"   Plan:    {order.get('plan', plan)}")
        print(f"   Expires: {order.get('expires_at', 'N/A')}")
        if data.get("tx_hash"):
            print(f"   TX:      {data['tx_hash']}")
        return data

    return {"error": f"Provisioning failed: {response.status_code}", "response": response.text[:2000]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Provision a compute instance")
    parser.add_argument("plan", help="Plan ID (e.g. vcg-a100-1c-2g-6gb)")
    parser.add_argument("region", help="Region ID (e.g. lax)")
    duration = parser.add_mutually_exclusive_group()
    duration.add_argument("--months", type=int, default=0, help="Duration in months (default: 1 if --days not set)")
    duration.add_argument("--days", type=int, default=0, help="Duration in days (minimum: 1)")
    parser.add_argument("--os-id", type=int, default=2284, help="OS image ID (default: 2284 = Ubuntu 24.04)")
    parser.add_argument("--label", default="x402-instance", help="Instance label")
    parser.add_argument("--network", default="base", choices=["base", "solana"], help="Payment network")
    parser.add_argument("--ssh-public-key", help="SSH public key contents (recommended)")
    parser.add_argument("--ssh-key-file", help="Path to SSH public key file (e.g. ~/.ssh/id_ed25519.pub)")
    args = parser.parse_args()
    if args.ssh_public_key and args.ssh_key_file:
        print("Error: provide either --ssh-public-key or --ssh-key-file, not both.")
        sys.exit(1)

    ssh_public_key = args.ssh_public_key
    if args.ssh_key_file:
        try:
            with open(args.ssh_key_file, "r", encoding="utf-8") as handle:
                ssh_public_key = handle.read().strip()
        except OSError as exc:
            print(f"Failed to read SSH key file: {exc}")
            sys.exit(1)

    # Default to 1 month if neither --days nor --months specified
    months = args.months if args.months > 0 else (0 if args.days > 0 else 1)
    days = args.days

    result = provision_instance(
        plan=args.plan,
        region=args.region,
        months=months,
        days=days,
        os_id=args.os_id,
        label=args.label,
        network=args.network,
        ssh_public_key=ssh_public_key,
    )
    if "error" in result:
        print(json.dumps(result, indent=2))
        sys.exit(1)
