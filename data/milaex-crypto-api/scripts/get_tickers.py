#!/usr/bin/env python3
from __future__ import annotations

import argparse

from milaex_client import print_json, request_json


def main() -> None:
    ap = argparse.ArgumentParser(description="Get tickers for multiple symbols")
    ap.add_argument("--exchange", required=False, help="Exchange id/name (optional)")
    ap.add_argument(
        "--symbols",
        required=False,
        help="Comma-separated symbols. Format typically BASE/QUOTE (e.g. BTC/USDT,ETH/USDT).",
    )
    ap.add_argument("--no-rate-headers", action="store_true")
    args = ap.parse_args()

    params = {}
    if args.exchange:
        params["exchange"] = args.exchange
    if args.symbols:
        params["symbols"] = args.symbols

    data = request_json("/api/v1/exchange/tickers", params=params, print_rate_headers=not args.no_rate_headers)
    print_json(data)


if __name__ == "__main__":
    main()
