#!/usr/bin/env python3
from __future__ import annotations

import argparse

from paylock_api import PayLockClient, print_json, run_with_error_handling


def main() -> None:
    parser = argparse.ArgumentParser(description="Mark a PayLock contract as funded")
    parser.add_argument("--contract-id", required=True, help="Contract ID")
    parser.add_argument("--tx-hash", required=True, help="Funding transaction hash")
    parser.add_argument("--api", default=None, help="Override API base URL")
    args = parser.parse_args()

    client = PayLockClient(base_url=args.api)
    payload = {"contract_id": args.contract_id, "tx_hash": args.tx_hash}
    print_json(client.request("POST", "/fund", payload=payload))


if __name__ == "__main__":
    run_with_error_handling(main)
