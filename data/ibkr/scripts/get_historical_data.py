#!/usr/bin/env python3
"""Backward-compatible historical data wrapper.

Modern usage:
  python get_historical_data.py --symbol AAPL --sec-type STK --duration "30 D" --bar-size "1 day"

Legacy usage:
  python get_historical_data.py AAPL STK [exchange] [currency] [duration] [bar_size]
"""

from __future__ import annotations

import argparse
import sys
from ibkr_cli import main as ibkr_main


def parse_legacy(argv: list[str]) -> list[str]:
    # Legacy positional mode:
    # <symbol> <sec_type> [exchange] [currency] [duration] [bar_size]
    symbol = argv[0]
    sec_type = argv[1]
    exchange = argv[2] if len(argv) > 2 else "SMART"
    currency = argv[3] if len(argv) > 3 else "USD"
    duration = "30 D"
    bar_size = "1 day"
    tail = argv[4:]
    if len(tail) == 1:
        duration = tail[0]
    elif len(tail) == 2:
        duration = f"{tail[0]} {tail[1]}"
    elif len(tail) == 3:
        duration = f"{tail[0]} {tail[1]}"
        bar_size = tail[2]
    elif len(tail) >= 4:
        duration = f"{tail[0]} {tail[1]}"
        bar_size = f"{tail[2]} {tail[3]}"

    return [
        "historical",
        "--symbol",
        symbol,
        "--sec-type",
        sec_type,
        "--exchange",
        exchange,
        "--currency",
        currency,
        "--duration",
        duration,
        "--bar-size",
        bar_size,
    ]


def parse_modern() -> list[str]:
    parser = argparse.ArgumentParser(description="Fetch historical market data")
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--client-id", type=int)
    parser.add_argument("--account")
    parser.add_argument("--readonly", action="store_true")
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

    parser.add_argument("--end", default="")
    parser.add_argument("--duration", default="30 D")
    parser.add_argument("--bar-size", default="1 day")
    parser.add_argument("--what-to-show", default="")
    parser.add_argument("--use-rth", default="true")

    args = parser.parse_args()

    cli_args = [
        "historical",
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
        "--end",
        args.end,
        "--duration",
        args.duration,
        "--bar-size",
        args.bar_size,
        "--what-to-show",
        args.what_to_show,
        "--use-rth",
        args.use_rth,
    ]

    if args.host:
        cli_args += ["--host", args.host]
    if args.port is not None:
        cli_args += ["--port", str(args.port)]
    if args.client_id is not None:
        cli_args += ["--client-id", str(args.client_id)]
    if args.account:
        cli_args += ["--account", args.account]
    if args.readonly:
        cli_args += ["--readonly"]
    if args.timeout is not None:
        cli_args += ["--timeout", str(args.timeout)]
    if args.json:
        cli_args += ["--json"]

    return cli_args


def main() -> int:
    argv = sys.argv[1:]
    if argv and not argv[0].startswith("-"):
        if len(argv) < 2:
            print(
                "Usage: python get_historical_data.py <symbol> <type> [exchange] [currency] [duration] [bar_size]",
                file=sys.stderr,
            )
            return 2
        return ibkr_main(parse_legacy(argv))

    return ibkr_main(parse_modern())


if __name__ == "__main__":
    raise SystemExit(main())
