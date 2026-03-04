#!/usr/bin/env python3
from __future__ import annotations

import argparse

from milaex_client import print_json, request_json


def main() -> None:
    ap = argparse.ArgumentParser(description="List markets (pairs) for an exchange via Milaex")
    ap.add_argument("--exchange", required=False, help="Exchange id/name (optional; if omitted returns combined/available)")
    ap.add_argument("--no-rate-headers", action="store_true")
    args = ap.parse_args()

    params = {}
    if args.exchange:
        params["exchange"] = args.exchange

    data = request_json("/api/v1/exchange/markets", params=params, print_rate_headers=not args.no_rate_headers)
    print_json(data)


if __name__ == "__main__":
    main()
