#!/usr/bin/env python3
from __future__ import annotations

import argparse

from milaex_client import print_json, request_json


def _split_symbol(symbol: str) -> tuple[str, str]:
    for sep in ("/", "-", "_"):
        if sep in symbol:
            base, quote = symbol.split(sep, 1)
            return base.strip(), quote.strip()
    raise SystemExit("Invalid --symbol format. Use BTC/USDT (or BTC-USDT).")


def main() -> None:
    ap = argparse.ArgumentParser(description="Get OHLCV (candles) for a market pair")
    ap.add_argument("--exchange", required=False, help="Exchange id/name (optional)")
    ap.add_argument("--symbol", required=True, help="Market pair like BTC/USDT")
    ap.add_argument(
        "--timeframe",
        required=False,
        help="Not currently exposed in Milaex v1 OpenAPI; accepted for forwards-compat. (ignored client-side)",
    )
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit returned candles client-side (if response is a list/array)",
    )
    ap.add_argument("--no-rate-headers", action="store_true")
    args = ap.parse_args()

    base, quote = _split_symbol(args.symbol)

    params = {
        "base_name": base,
        "quote_name": quote,
    }
    if args.exchange:
        params["exchange"] = args.exchange

    data = request_json("/api/v1/exchange/ohlcv", params=params, print_rate_headers=not args.no_rate_headers)

    # Best-effort limit if it's an array-like structure.
    if args.limit is not None:
        if isinstance(data, list):
            data = data[: args.limit]
        elif isinstance(data, dict) and "Data" in data and isinstance(data["Data"], list):
            data["Data"] = data["Data"][: args.limit]

    print_json(data)


if __name__ == "__main__":
    main()
