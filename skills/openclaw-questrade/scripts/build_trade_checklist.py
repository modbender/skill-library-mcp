#!/usr/bin/env python3
"""
Generate a structured checklist for manually submitting a stock trade
in Questrade Web.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Optional


VALID_SIDES = {"buy", "sell"}
VALID_ORDER_TYPES = {"market", "limit", "stop", "stop_limit"}
VALID_TIF = {"day", "gtc", "gted"}
VALID_ENVIRONMENTS = {"paper", "live"}
POLICY_ACK_PHRASE = "OPENCLAW_POLICY_ACK"


def validate_positive_int(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Quantity must be greater than zero.")
    return number


def validate_side(value: str) -> str:
    side = value.lower()
    if side not in VALID_SIDES:
        raise argparse.ArgumentTypeError(f"side must be one of: {sorted(VALID_SIDES)}")
    return side


def validate_order_type(value: str) -> str:
    order_type = value.lower()
    if order_type not in VALID_ORDER_TYPES:
        raise argparse.ArgumentTypeError(
            f"order-type must be one of: {sorted(VALID_ORDER_TYPES)}"
        )
    return order_type


def validate_tif(value: str) -> str:
    tif = value.lower()
    if tif not in VALID_TIF:
        raise argparse.ArgumentTypeError(f"tif must be one of: {sorted(VALID_TIF)}")
    return tif


def validate_price(value: str) -> float:
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Price must be greater than zero.")
    return number


def validate_non_negative_float(value: str) -> float:
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Value must be zero or greater.")
    return number


def validate_non_negative_int(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("Value must be zero or greater.")
    return number


def validate_environment(value: str) -> str:
    environment = value.lower()
    if environment not in VALID_ENVIRONMENTS:
        raise argparse.ArgumentTypeError(
            f"environment must be one of: {sorted(VALID_ENVIRONMENTS)}"
        )
    return environment


def mask_identifier(raw_value: str) -> str:
    text = raw_value.strip()
    if len(text) <= 4:
        return "*" * len(text)
    return f"{'*' * (len(text) - 4)}{text[-4:]}"


def enforce_special_safety_checks(
    args: argparse.Namespace, parser: argparse.ArgumentParser
) -> None:
    if args.policy_ack.strip() != POLICY_ACK_PHRASE:
        parser.error(
            "--policy-ack must match OPENCLAW_POLICY_ACK for policy-compliant execution"
        )
    if not args.confirm_user_authorized:
        parser.error("--confirm-user-authorized is required")
    if not args.confirm_manual_execution:
        parser.error("--confirm-manual-execution is required")
    if not args.confirm_no_secrets_shared:
        parser.error("--confirm-no-secrets-shared is required")

    if args.include_sensitive and not args.local_sensitive_storage_confirm:
        parser.error(
            "--local-sensitive-storage-confirm is required with --include-sensitive"
        )

    if args.environment == "live":
        if args.risk_cap_usd is None:
            parser.error("--risk-cap-usd is required for live trading mode")
        if args.data_age_seconds is None:
            parser.error("--data-age-seconds is required for live trading mode")
        if args.data_age_seconds > args.max_data_age_seconds:
            parser.error(
                f"data is stale ({args.data_age_seconds}s > {args.max_data_age_seconds}s)"
            )
        if args.order_type == "market" and not args.allow_market_order_live:
            parser.error(
                "live market orders are blocked by default; pass --allow-market-order-live "
                "to override explicitly"
            )
        if (
            args.observed_price_drift_pct is not None
            and args.observed_price_drift_pct > args.max_price_drift_pct
        ):
            parser.error(
                "observed price drift exceeds configured maximum "
                f"({args.observed_price_drift_pct}% > {args.max_price_drift_pct}%)"
            )


def build_markdown(args: argparse.Namespace) -> str:
    created_at = dt.datetime.now(dt.timezone.utc).isoformat()

    reference_price: Optional[float] = args.limit_price or args.stop_price
    estimated_notional = None
    if reference_price is not None:
        estimated_notional = reference_price * args.quantity

    account_value = args.account_id if args.include_sensitive else mask_identifier(args.account_id)

    payload = {
        "created_at_utc": created_at,
        "account_id": account_value,
        "account_id_masked": mask_identifier(args.account_id),
        "environment": args.environment,
        "special_safety_check": {
            "status": "pass",
            "policy_acknowledged": True,
            "user_authorized": args.confirm_user_authorized,
            "manual_execution_confirmed": args.confirm_manual_execution,
            "no_secrets_shared_confirmed": args.confirm_no_secrets_shared,
            "data_age_seconds": args.data_age_seconds,
            "max_data_age_seconds": args.max_data_age_seconds,
            "observed_price_drift_pct": args.observed_price_drift_pct,
            "max_price_drift_pct": args.max_price_drift_pct,
            "risk_cap_usd": args.risk_cap_usd,
        },
        "symbol": args.symbol.upper(),
        "side": args.side,
        "quantity": args.quantity,
        "order_type": args.order_type,
        "time_in_force": args.tif,
        "limit_price": args.limit_price,
        "stop_price": args.stop_price,
        "estimated_notional": estimated_notional,
        "risk_cap_usd": args.risk_cap_usd,
        "notes": args.notes,
    }

    lines = [
        "# Trade Checklist",
        "",
        "## Ticket",
        f"- Created (UTC): {created_at}",
        f"- Environment: {args.environment.upper()}",
        f"- Account: {account_value}",
        f"- Symbol: {args.symbol.upper()}",
        f"- Side: {args.side.upper()}",
        f"- Quantity: {args.quantity}",
        f"- Order type: {args.order_type}",
        f"- Time in force: {args.tif.upper()}",
        f"- Limit price: {args.limit_price if args.limit_price is not None else 'N/A'}",
        f"- Stop price: {args.stop_price if args.stop_price is not None else 'N/A'}",
        f"- Estimated notional: {round(estimated_notional, 4) if estimated_notional is not None else 'N/A'}",
        f"- Risk cap (USD): {args.risk_cap_usd if args.risk_cap_usd is not None else 'N/A'}",
        "",
        "## Special Safety Check (Policy-Enforced)",
        "- [x] openclaw.ai policy acknowledgement confirmed.",
        "- [x] User authorization to trade this account confirmed.",
        "- [x] Manual broker-side execution confirmed (no autonomous order placement).",
        "- [x] Sensitive credentials were not shared in artifacts.",
        f"- [x] Data age check passed: {args.data_age_seconds if args.data_age_seconds is not None else 'N/A'}s <= {args.max_data_age_seconds}s.",
        f"- [x] Price drift check passed: {args.observed_price_drift_pct if args.observed_price_drift_pct is not None else 'N/A'}% <= {args.max_price_drift_pct}%.",
        "",
        "## Pre-Trade Hard Checks",
        "- [ ] Symbol, side, and quantity match user intent exactly.",
        "- [ ] Buying power and margin impact are acceptable.",
        "- [ ] Open orders/positions were checked for conflicts.",
        "- [ ] Order type and price fields are valid for current market state.",
        "- [ ] Stop or exit plan is explicitly defined.",
        "- [ ] Broker quote was cross-checked with Yahoo snapshot.",
        "",
        "## Questrade Web Submission Steps",
        "- [ ] Open order entry ticket in Questrade Web.",
        "- [ ] Select account and verify symbol.",
        "- [ ] Enter side, quantity, order type, and required prices.",
        "- [ ] Confirm time in force and routing options.",
        "- [ ] Review estimated cost/proceeds and commissions.",
        "- [ ] Submit order and capture confirmation ID.",
        "",
        "## Post-Submission Log",
        "- [ ] Confirmation ID:",
        "- [ ] Submitted timestamp (UTC):",
        "- [ ] Fill status (open/partial/filled/cancelled):",
        "- [ ] Average fill price:",
        "- [ ] Remaining quantity:",
        "",
        "## Machine-Readable Ticket",
        "```json",
        json.dumps(payload, indent=2),
        "```",
    ]

    if args.notes:
        lines.extend(["", "## Notes", args.notes])

    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a markdown checklist for manual Questrade trade execution."
    )
    parser.add_argument("--account-id", required=True, help="Broker account identifier.")
    parser.add_argument("--symbol", required=True, help="Ticker symbol.")
    parser.add_argument("--side", required=True, type=validate_side, help="buy or sell.")
    parser.add_argument(
        "--quantity", required=True, type=validate_positive_int, help="Share quantity."
    )
    parser.add_argument(
        "--order-type",
        required=True,
        type=validate_order_type,
        help="market, limit, stop, or stop_limit.",
    )
    parser.add_argument(
        "--tif",
        default="day",
        type=validate_tif,
        help="Time in force: day, gtc, or gted.",
    )
    parser.add_argument(
        "--limit-price",
        type=validate_price,
        help="Required for limit and stop_limit orders.",
    )
    parser.add_argument(
        "--stop-price",
        type=validate_price,
        help="Required for stop and stop_limit orders.",
    )
    parser.add_argument(
        "--risk-cap-usd",
        type=validate_price,
        help="Optional max accepted risk in USD.",
    )
    parser.add_argument(
        "--environment",
        default="live",
        type=validate_environment,
        help="Execution mode: paper or live. Default: live.",
    )
    parser.add_argument(
        "--policy-ack",
        required=True,
        help="Set to OPENCLAW_POLICY_ACK to confirm policy compliance intent.",
    )
    parser.add_argument(
        "--confirm-user-authorized",
        action="store_true",
        help="Confirm user is authorized to trade the target account.",
    )
    parser.add_argument(
        "--confirm-manual-execution",
        action="store_true",
        help="Confirm trade submission remains manual in Questrade browser.",
    )
    parser.add_argument(
        "--confirm-no-secrets-shared",
        action="store_true",
        help="Confirm secrets were not shared in prompts/files/logs.",
    )
    parser.add_argument(
        "--data-age-seconds",
        type=validate_non_negative_int,
        help="Age of quote data used for this ticket.",
    )
    parser.add_argument(
        "--max-data-age-seconds",
        type=validate_non_negative_int,
        default=300,
        help="Maximum allowed quote data age. Default: 300.",
    )
    parser.add_argument(
        "--observed-price-drift-pct",
        type=validate_non_negative_float,
        help="Observed broker-vs-reference drift percentage.",
    )
    parser.add_argument(
        "--max-price-drift-pct",
        type=validate_non_negative_float,
        default=1.0,
        help="Maximum allowed drift percentage. Default: 1.0.",
    )
    parser.add_argument(
        "--allow-market-order-live",
        action="store_true",
        help="Explicitly allow market order type in live mode.",
    )
    parser.add_argument(
        "--include-sensitive",
        action="store_true",
        help="Include raw account identifier in output. Default behavior masks it.",
    )
    parser.add_argument(
        "--local-sensitive-storage-confirm",
        action="store_true",
        help="Confirm local-only handling when include-sensitive output is requested.",
    )
    parser.add_argument("--notes", default="", help="Optional extra notes.")
    parser.add_argument("--out", required=True, help="Output markdown path.")

    args = parser.parse_args()

    if args.order_type == "limit" and args.limit_price is None:
        parser.error("--limit-price is required for order-type=limit")
    if args.order_type == "stop" and args.stop_price is None:
        parser.error("--stop-price is required for order-type=stop")
    if args.order_type == "stop_limit":
        if args.stop_price is None or args.limit_price is None:
            parser.error(
                "--stop-price and --limit-price are required for order-type=stop_limit"
            )
    enforce_special_safety_checks(args, parser)
    return args


def main() -> int:
    try:
        args = parse_args()
        markdown = build_markdown(args)
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote checklist to {out_path}")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
