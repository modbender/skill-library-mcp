#!/usr/bin/env python3
"""Backward-compatible order placement wrapper.

Modern usage:
  python place_order.py --symbol AAPL --action BUY --quantity 100 --order-type MKT

Legacy usage:
  python place_order.py <symbol> <action> <quantity> [type] [price]
"""

from __future__ import annotations

import argparse
import sys
from ibkr_cli import main as ibkr_main


def parse_legacy(argv: list[str]) -> list[str]:
    symbol = argv[0]
    action = argv[1].upper()
    quantity = argv[2]
    order_type = argv[3].upper() if len(argv) > 3 else "MKT"
    price = argv[4] if len(argv) > 4 else None

    cli_args = [
        "place-order",
        "--symbol",
        symbol,
        "--sec-type",
        "STK",
        "--exchange",
        "SMART",
        "--currency",
        "USD",
        "--action",
        action,
        "--quantity",
        quantity,
        "--order-type",
        order_type,
    ]

    if order_type == "LMT" and price is not None:
        cli_args += ["--limit-price", price]

    return cli_args


def parse_modern() -> list[str]:
    parser = argparse.ArgumentParser(description="Place an order")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--client-id", type=int)
    parser.add_argument("--account")
    parser.add_argument("--timeout", type=float)
    parser.add_argument("--json", action="store_true")

    parser.add_argument("--symbol", required=True)
    parser.add_argument("--sec-type", default="STK")
    parser.add_argument("--exchange", default="SMART")
    parser.add_argument("--currency", default="USD")
    parser.add_argument("--primary-exchange", default="")
    parser.add_argument("--local-symbol", default="")
    parser.add_argument("--trading-class", default="")
    parser.add_argument("--expiry", default="")
    parser.add_argument("--strike", type=float, default=0.0)
    parser.add_argument("--right", default="")
    parser.add_argument("--multiplier", default="")
    parser.add_argument("--con-id", type=int, default=0)

    parser.add_argument("--action", required=True, choices=["BUY", "SELL"])
    parser.add_argument("--quantity", required=True, type=float)
    parser.add_argument("--order-type", default="MKT")
    parser.add_argument("--limit-price", type=float)
    parser.add_argument("--stop-price", type=float)
    parser.add_argument("--tif", default="")
    parser.add_argument("--outside-rth", action="store_true")
    parser.add_argument("--wait", type=float, default=8.0)

    args = parser.parse_args()

    cli_args = [
        "place-order",
        "--symbol",
        args.symbol,
        "--sec-type",
        args.sec_type,
        "--exchange",
        args.exchange,
        "--currency",
        args.currency,
        "--primary-exchange",
        args.primary_exchange,
        "--local-symbol",
        args.local_symbol,
        "--trading-class",
        args.trading_class,
        "--expiry",
        args.expiry,
        "--strike",
        str(args.strike),
        "--right",
        args.right,
        "--multiplier",
        args.multiplier,
        "--con-id",
        str(args.con_id),
        "--action",
        args.action,
        "--quantity",
        str(args.quantity),
        "--order-type",
        args.order_type,
        "--wait",
        str(args.wait),
    ]

    if args.limit_price is not None:
        cli_args += ["--limit-price", str(args.limit_price)]
    if args.stop_price is not None:
        cli_args += ["--stop-price", str(args.stop_price)]
    if args.tif:
        cli_args += ["--tif", args.tif]
    if args.outside_rth:
        cli_args += ["--outside-rth"]

    if args.host:
        cli_args += ["--host", args.host]
    if args.port is not None:
        cli_args += ["--port", str(args.port)]
    if args.client_id is not None:
        cli_args += ["--client-id", str(args.client_id)]
    if args.account:
        cli_args += ["--account", args.account]
    if args.timeout is not None:
        cli_args += ["--timeout", str(args.timeout)]
    if args.json:
        cli_args += ["--json"]

    return cli_args


def main() -> int:
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-"):
        if len(argv) < 3:
            print("Usage: python place_order.py <symbol> <action> <quantity> [type] [price]", file=sys.stderr)
            return 2
        return ibkr_main(parse_legacy(argv))

    return ibkr_main(parse_modern())


if __name__ == "__main__":
    raise SystemExit(main())
