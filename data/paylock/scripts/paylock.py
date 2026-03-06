#!/usr/bin/env python3
from __future__ import annotations

import argparse

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="Unified CLI for PayLock escrow API")
    parser.add_argument("--api", default=None, help="Override API base URL")
    sub = parser.add_subparsers(dest="command", required=True)

    c = sub.add_parser("create", help="Create escrow contract")
    c.add_argument("--payer", required=True)
    c.add_argument("--payee", required=True)
    c.add_argument("--amount", type=float, required=True)
    c.add_argument("--currency", default="SOL")
    c.add_argument("--description", required=True)
    c.add_argument("--payer-address", required=True)
    c.add_argument("--payee-address", required=True)

    f = sub.add_parser("fund", help="Fund contract")
    f.add_argument("--contract-id", required=True)
    f.add_argument("--tx-hash", required=True)

    d = sub.add_parser("deliver", help="Deliver work for contract")
    d.add_argument("--id", required=True)
    d.add_argument("--delivery-payload", required=True)
    d.add_argument("--delivery-hash", required=True)
    d.add_argument("--payee-token", required=True)

    v = sub.add_parser("verify", help="Verify delivery")
    v.add_argument("--id", required=True)
    v.add_argument("--payer-token", required=True)

    s = sub.add_parser("status", help="Get contract status")
    s.add_argument("--id", required=True)

    sub.add_parser("list", help="List contracts")

    args = parser.parse_args()
    client = PayLockClient(base_url=args.api)

    if args.command == "create":
        result = client.request(
            "POST",
            "/contract",
            payload={
                "payer": args.payer,
                "payee": args.payee,
                "amount": args.amount,
                "currency": args.currency,
                "description": args.description,
                "payer_address": args.payer_address,
                "payee_address": args.payee_address,
            },
        )
    elif args.command == "fund":
        result = client.request(
            "POST", "/fund", payload={"contract_id": args.contract_id, "tx_hash": args.tx_hash}
        )
    elif args.command == "deliver":
        result = client.request(
            "POST",
            f"/{args.id}/deliver",
            payload={
                "delivery_payload": args.delivery_payload,
                "delivery_hash": args.delivery_hash,
                "payee_token": args.payee_token,
            },
        )
    elif args.command == "verify":
        result = client.request("POST", f"/{args.id}/verify", payload={"payer_token": args.payer_token})
    elif args.command == "status":
        result = client.request("GET", f"/contract/{args.id}")
    elif args.command == "list":
        result = client.request("GET", "/contracts")
    else:
        raise ValueError(f"Unsupported command: {args.command}")

    print_json(result)


if __name__ == "__main__":
    run_with_error_handling(main)
