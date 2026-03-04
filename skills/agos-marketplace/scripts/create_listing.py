#!/usr/bin/env python3
"""Create AGOS marketplace listing (service manifest) automatically."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from urllib import error, request

API_BASE_URL = "https://market.agos.fun"
DEFAULT_SUPPLIER_WALLET = "0x0000000000000000000000000000000000000001"
SAFE_SUPPLIER_ENDPOINT = "https://market.agos.fun/v1/openclaw/supplier-task"

DEFAULT_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "task": {"type": "string"}
    },
    "required": ["task"]
}

DEFAULT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "result": {"type": "string"}
    },
    "required": ["result"]
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create AGOS listing (service)")
    parser.add_argument("--service-id", help="Service/listing id. If omitted, auto-generate.")
    parser.add_argument("--name", default="Auto Service", help="Service name")
    parser.add_argument("--description", default="Auto-created service listing", help="Service description")
    parser.add_argument("--price-usdt", default="1.0", help="Price in USDT string")
    parser.add_argument("--supplier-wallet", default=DEFAULT_SUPPLIER_WALLET, help="Supplier wallet 0x...")
    parser.add_argument(
        "--input-schema-json",
        default=json.dumps(DEFAULT_INPUT_SCHEMA),
        help="JSON object for input_schema",
    )
    parser.add_argument(
        "--output-schema-json",
        default=json.dumps(DEFAULT_OUTPUT_SCHEMA),
        help="JSON object for output_schema",
    )
    parser.add_argument("--version", default="1.0.0", help="Service version")
    parser.add_argument("--inactive", action="store_true", help="Create listing as inactive")
    parser.add_argument("--dry-run", action="store_true", help="Print payload without API call")
    return parser.parse_args()


def parse_json_object(raw: str, flag_name: str) -> dict:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Invalid {flag_name}: {exc}") from exc

    if not isinstance(value, dict):
        raise RuntimeError(f"{flag_name} must decode to JSON object")
    return value


def make_service_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    return f"svc_auto_{stamp}"


def http_post_json(url: str, body: dict) -> dict:
    req = request.Request(
        url=url,
        method="POST",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if not isinstance(data, dict):
                raise RuntimeError("Unexpected API response")
            return data
    except error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} {url}: {text}") from exc
    except error.URLError as exc:
        raise RuntimeError(f"Network error {url}: {exc.reason}") from exc


def main() -> int:
    args = parse_args()
    service_id = args.service_id or make_service_id()

    try:
        input_schema = parse_json_object(args.input_schema_json, "--input-schema-json")
        output_schema = parse_json_object(args.output_schema_json, "--output-schema-json")

        payload = {
            "service_id": service_id,
            "name": args.name,
            "description": args.description,
            "input_schema": input_schema,
            "output_schema": output_schema,
            "price_usdt": args.price_usdt,
            "endpoint": SAFE_SUPPLIER_ENDPOINT,
            "supplier_wallet": args.supplier_wallet,
            "version": args.version,
            "is_active": not args.inactive,
        }

        if args.dry_run:
            print(json.dumps({"dry_run": True, "payload": payload}, ensure_ascii=False, indent=2))
            return 0

        base_url = API_BASE_URL
        created = http_post_json(f"{base_url}/v1/services", payload)

        print(
            json.dumps(
                {
                    "service": created,
                    "service_id": created.get("service_id", service_id),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
