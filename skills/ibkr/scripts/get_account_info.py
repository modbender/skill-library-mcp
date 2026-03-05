#!/usr/bin/env python3
"""Backward-compatible account summary + positions wrapper.

Usage: python get_account_info.py [--host ... --port ... --client-id ... --account ... --json]
"""

from __future__ import annotations

import argparse
from ibkr_cli import main as ibkr_main


def build_args() -> list[str]:
    parser = argparse.ArgumentParser(description="Get account summary and positions")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--client-id", type=int)
    parser.add_argument("--account")
    parser.add_argument("--readonly", action="store_true")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    shared = []
    if args.host:
        shared += ["--host", args.host]
    if args.port is not None:
        shared += ["--port", str(args.port)]
    if args.client_id is not None:
        shared += ["--client-id", str(args.client_id)]
    if args.account:
        shared += ["--account", args.account]
    if args.readonly:
        shared += ["--readonly"]
    if args.timeout is not None:
        shared += ["--timeout", str(args.timeout)]
    if args.json:
        shared += ["--json"]

    return shared


def main() -> int:
    shared = build_args()
    rc = ibkr_main(["account-summary", *shared])
    if rc != 0:
        return rc
    return ibkr_main(["positions", *shared])


if __name__ == "__main__":
    raise SystemExit(main())
