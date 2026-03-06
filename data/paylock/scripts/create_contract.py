#!/usr/bin/env python3
from __future__ import annotations

import argparse

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a PayLock escrow contract")
    parser.add_argument("--payer", required=True, help="Payer agent name/id")
    parser.add_argument("--payee", required=True, help="Payee agent name/id")
    parser.add_argument("--amount", type=float, required=True, help="Amount in SOL")
    parser.add_argument("--description", required=True, help="Contract description")
    parser.add_argument("--payer-address", required=True, help="Payer SOL wallet")
    parser.add_argument("--payee-address", required=True, help="Payee SOL wallet")
    parser.add_argument("--currency", default="SOL", help="Currency (default: SOL)")
    parser.add_argument("--api", default=None, help="Override API base URL")
    args = parser.parse_args()

    client = PayLockClient(base_url=args.api)
    payload = {
        "payer": args.payer,
        "payee": args.payee,
        "amount": args.amount,
        "currency": args.currency,
        "description": args.description,
        "payer_address": args.payer_address,
        "payee_address": args.payee_address,
    }
    print_json(client.request("POST", "/contract", payload=payload))


if __name__ == "__main__":
    run_with_error_handling(main)
