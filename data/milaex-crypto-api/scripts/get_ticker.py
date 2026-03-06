#!/usr/bin/env python3
from __future__ import annotations

import argparse

from milaex_client import print_json, request_json


def _split_symbol(symbol: str) -> tuple[str, str]:
    # Accept formats like BTC/USDT or BTC-USDT or BTC_USDT
    for sep in ("/", "-", "_"):
        if sep in symbol:
            base, quote = symbol.split(sep, 1)
            return base.strip(), quote.strip()
    raise SystemExit("Invalid --symbol format. Use BTC/USDT (or BTC-USDT).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Get a single ticker for a market pair")
    ap.add_argument("--exchange", required=False, help="Exchange id/name (optional)")
    ap.add_argument("--symbol", required=True, help="Market pair like BTC/USDT")
    ap.add_argument("--no-rate-headers", action="store_true")
    args = ap.parse_args()

    base, quote = _split_symbol(args.symbol)

    params = {
        "base_name": base,
        "quote_name": quote,
    }
    if args.exchange:
        params["exchange"] = args.exchange

    data = request_json("/api/v1/exchange/ticker", params=params, print_rate_headers=not args.no_rate_headers)
    print_json(data)


if __name__ == "__main__":
    main()
