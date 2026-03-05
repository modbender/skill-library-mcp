#!/usr/bin/env python3
"""Agent-friendly CLI for Futu/MooMoo OpenD."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Iterable, List

from opend_core import OpenDClient, OpenDSettings


def _codes_from_args(codes: Iterable[str], codes_csv: str | None) -> List[str]:
    merged = list(codes)
    if codes_csv:
        merged.extend([c.strip() for c in codes_csv.split(",") if c.strip()])
    merged = [c for c in merged if c]
    if not merged:
        raise ValueError("At least one code is required")
    return merged


def _emit(output: str, payload):
    if output == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=True, default=str))
    else:
        print(payload)


def _client_from_args(args: argparse.Namespace) -> OpenDClient:
    settings = OpenDSettings(
        host=args.host,
        port=args.port,
        market=args.market,
        security_firm=args.security_firm,
        trd_env=args.trd_env,
        credential_method=args.credential_method,
    )
    return OpenDClient(settings)


def cmd_snapshot(args: argparse.Namespace):
    codes = _codes_from_args(args.code, args.codes)
    payload = _client_from_args(args).get_snapshot(codes)
    _emit(args.output, payload)


def cmd_accounts(args: argparse.Namespace):
    payload = _client_from_args(args).get_accounts()
    _emit(args.output, payload)


def cmd_positions(args: argparse.Namespace):
    payload = _client_from_args(args).get_positions(args.trd_env, acc_id=args.acc_id)
    _emit(args.output, payload)


def cmd_place_order(args: argparse.Namespace):
    payload = _client_from_args(args).place_order(
        code=args.code,
        price=args.price,
        qty=args.qty,
        side=args.side,
        order_type=args.order_type,
        trd_env=args.trd_env,
        acc_id=args.acc_id,
    )
    _emit(args.output, payload)


def cmd_cancel_order(args: argparse.Namespace):
    payload = _client_from_args(args).cancel_order(
        order_id=args.order_id,
        trd_env=args.trd_env,
        acc_id=args.acc_id,
    )
    _emit(args.output, payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenD CLI for agentic market/trading tasks")
    parser.add_argument("--host", default="127.0.0.1", help="OpenD host")
    parser.add_argument("--port", default=11111, type=int, help="OpenD port")
    parser.add_argument("--market", default="HK", choices=["HK", "US", "CN", "HKCC", "FUTURES"], help="Trade market filter")
    parser.add_argument(
        "--security-firm",
        default="FUTUSECURITIES",
        choices=["FUTUSECURITIES", "FUTUINC"],
        help="Broker security firm",
    )
    parser.add_argument("--trd-env", default="SIMULATE", choices=["SIMULATE", "REAL"], help="Trading environment")
    parser.add_argument(
        "--credential-method",
        default="openclaw",
        choices=["openclaw", "secret-ref", "env", "keyring", "config", "none"],
        help="How trade password is loaded",
    )
    parser.add_argument("--output", default="json", choices=["json", "text"], help="Output format")

    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Get market snapshot")
    snapshot.add_argument("--code", action="append", default=[], help="Single code, repeatable")
    snapshot.add_argument("--codes", help="Comma-separated codes")
    snapshot.set_defaults(func=cmd_snapshot)

    accounts = subparsers.add_parser("accounts", help="List accounts")
    accounts.set_defaults(func=cmd_accounts)

    positions = subparsers.add_parser("positions", help="Query positions")
    positions.add_argument("--acc-id", type=int, help="Explicit account id")
    positions.set_defaults(func=cmd_positions)

    order = subparsers.add_parser("place-order", help="Place order")
    order.add_argument("--code", required=True, help="Security code, e.g. HK.00700")
    order.add_argument("--price", required=True, type=float, help="Order price")
    order.add_argument("--qty", required=True, type=float, help="Order quantity")
    order.add_argument("--side", required=True, choices=["BUY", "SELL"], help="Order side")
    order.add_argument("--order-type", default="NORMAL", help="Order type enum name")
    order.add_argument("--acc-id", type=int, help="Explicit account id")
    order.set_defaults(func=cmd_place_order)

    cancel = subparsers.add_parser("cancel-order", help="Cancel existing order by order id")
    cancel.add_argument("--order-id", required=True, help="Order id to cancel")
    cancel.add_argument("--acc-id", type=int, help="Explicit account id")
    cancel.set_defaults(func=cmd_cancel_order)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
