#!/usr/bin/env python3
"""Create AGOS marketplace order (OpenClaw purchase) automatically."""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any
from urllib import error, request

API_BASE_URL = "https://market.agos.fun"
DEFAULT_BUYER_WALLET = "0x0000000000000000000000000000000000000002"
TERMINAL_STATES = {"COMPLETED", "FAILED"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create AGOS order via OpenClaw adapter API")
    parser.add_argument("--listing-id", help="Listing ID. If omitted, auto-select first active listing.")
    parser.add_argument(
        "--buyer-wallet",
        default=DEFAULT_BUYER_WALLET,
        help="Buyer wallet address (0x...)",
    )
    parser.add_argument(
        "--input-json",
        default='{"task":"auto order"}',
        help="JSON string for input payload",
    )
    parser.add_argument(
        "--prepare-payment",
        action="store_true",
        help="Also fetch payment parameters after order creation",
    )
    parser.add_argument(
        "--wait",
        action="store_true",
        help="Poll purchase status until terminal state",
    )
    parser.add_argument("--timeout-sec", type=int, default=180, help="Polling timeout seconds")
    parser.add_argument("--interval-sec", type=int, default=3, help="Polling interval seconds")
    return parser.parse_args()


def http_json(method: str, url: str, body: dict[str, Any] | None = None) -> dict[str, Any] | list[Any]:
    data = None
    headers = {"accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["content-type"] = "application/json"

    req = request.Request(url=url, method=method, data=data, headers=headers)
    try:
        with request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {text}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error {url}: {exc.reason}") from exc


def select_listing(base_url: str) -> str:
    response = http_json("GET", f"{base_url}/v1/openclaw/listings")
    if not isinstance(response, list):
        raise RuntimeError("Unexpected listings response")
    if not response:
        raise RuntimeError("No listings found. Seller must register a service first.")

    for listing in response:
        if isinstance(listing, dict) and listing.get("is_active", True):
            listing_id = listing.get("listing_id")
            if isinstance(listing_id, str) and listing_id:
                return listing_id

    raise RuntimeError("No active listing found.")


def wait_purchase(base_url: str, purchase_id: str, timeout_sec: int, interval_sec: int) -> dict[str, Any]:
    deadline = time.time() + timeout_sec
    last: dict[str, Any] | None = None
    while time.time() < deadline:
        payload = http_json("GET", f"{base_url}/v1/openclaw/purchases/{purchase_id}")
        if not isinstance(payload, dict):
            raise RuntimeError("Unexpected purchase status response")
        last = payload
        status = payload.get("status")
        if isinstance(status, str) and status in TERMINAL_STATES:
            return payload
        time.sleep(max(interval_sec, 1))

    if last is None:
        raise RuntimeError("Timed out before receiving purchase status")
    return last


def main() -> int:
    args = parse_args()

    try:
        input_payload = json.loads(args.input_json)
    except json.JSONDecodeError as exc:
        print(f"Invalid --input-json: {exc}", file=sys.stderr)
        return 2

    if not isinstance(input_payload, dict):
        print("--input-json must decode to a JSON object", file=sys.stderr)
        return 2

    base_url = API_BASE_URL

    try:
        listing_id = args.listing_id or select_listing(base_url)

        purchase = http_json(
            "POST",
            f"{base_url}/v1/openclaw/purchases",
            {
                "listing_id": listing_id,
                "buyer_wallet": args.buyer_wallet,
                "input_payload": input_payload,
            },
        )

        if not isinstance(purchase, dict):
            raise RuntimeError("Unexpected purchase creation response")

        output: dict[str, Any] = {
            "purchase": purchase,
            "selected_listing_id": listing_id,
        }

        purchase_id = purchase.get("purchase_id")
        if not isinstance(purchase_id, str) or not purchase_id:
            raise RuntimeError("Missing purchase_id in response")

        if args.prepare_payment:
            prep = http_json(
                "POST",
                f"{base_url}/v1/openclaw/purchases/{purchase_id}/prepare-payment",
                {},
            )
            output["payment_preparation"] = prep

        if args.wait:
            final_state = wait_purchase(
                base_url=base_url,
                purchase_id=purchase_id,
                timeout_sec=args.timeout_sec,
                interval_sec=args.interval_sec,
            )
            output["final_state"] = final_state

        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
