#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="Submit delivery proof for a PayLock contract")
    parser.add_argument("--id", required=True, help="Contract ID")
    parser.add_argument("--delivery-payload", required=True, help="Delivery data/details")
    parser.add_argument("--delivery-hash", required=True, help="Hash of delivery payload")
    parser.add_argument("--payee-token", default=None, help="Payee secret token (or set PAYLOCK_PAYEE_TOKEN)")
    parser.add_argument("--api", default=None, help="Override API base URL")
    args = parser.parse_args()

    token = args.payee_token or os.getenv("PAYLOCK_PAYEE_TOKEN")
    if not token:
        parser.error("Payee token required: use --payee-token or set PAYLOCK_PAYEE_TOKEN env var")

    client = PayLockClient(base_url=args.api)
    payload = {
        "delivery_payload": args.delivery_payload,
        "delivery_hash": args.delivery_hash,
        "payee_token": token,
    }
    print_json(client.request("POST", f"/{args.id}/deliver", payload=payload))


if __name__ == "__main__":
    run_with_error_handling(main)
