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
    ap = argparse.ArgumentParser(description="Get orderbook for a market pair")
    ap.add_argument("--exchange", required=False, help="Exchange id/name (optional)")
    ap.add_argument("--symbol", required=True, help="Market pair like BTC/USDT")
    ap.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit bids/asks client-side if present (best-effort)",
    )
    ap.add_argument("--complete", action="store_true", help="Use /orderbook/complete endpoint when available")
    ap.add_argument("--no-rate-headers", action="store_true")
    args = ap.parse_args()

    base, quote = _split_symbol(args.symbol)

    params = {
        "base_name": base,
        "quote_name": quote,
    }
    if args.exchange:
        params["exchange"] = args.exchange

    path = "/api/v1/exchange/orderbook/complete" if args.complete else "/api/v1/exchange/orderbook"
    data = request_json(path, params=params, print_rate_headers=not args.no_rate_headers)

    if args.limit is not None and isinstance(data, dict):
        # Common shapes: Data: { bids: [...], asks: [...] } OR direct bids/asks
        ob = data.get("Data") if isinstance(data.get("Data"), dict) else data
        if isinstance(ob, dict):
            for side in ("bids", "asks", "Bids", "Asks"):
                if side in ob and isinstance(ob[side], list):
                    ob[side] = ob[side][: args.limit]

    print_json(data)


if __name__ == "__main__":
    main()
