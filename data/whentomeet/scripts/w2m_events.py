#!/usr/bin/env python3
"""WhenToMeet v1 events CLI for agent skills.

Non-interactive, structured output, no external dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BASE_URL = "https://whentomeet.io/api/trpc"


def fail(message: str, code: int = 2) -> int:
    print(f"Error: {message}", file=sys.stderr)
    return code


def get_api_key() -> str | None:
    key = os.environ.get("WHENTOMEET_API_KEY", "").strip()
    return key or None


def parse_slots_json(slots_json: str) -> list[dict[str, Any]]:
    try:
        value = json.loads(slots_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--slots-json is not valid JSON: {exc}") from exc

    if not isinstance(value, list) or len(value) == 0:
        raise ValueError("--slots-json must be a non-empty JSON array")

    for idx, slot in enumerate(value):
        if not isinstance(slot, dict):
            raise ValueError(f"slot #{idx + 1} must be an object")
        if "startTime" not in slot or "endTime" not in slot:
            raise ValueError(
                f"slot #{idx + 1} must contain startTime and endTime")
        if not isinstance(slot["startTime"], str) or not isinstance(slot["endTime"], str):
            raise ValueError(
                f"slot #{idx + 1} startTime/endTime must be strings")

    return value


def encode_input(json_payload: dict[str, Any]) -> str:
    payload = {"json": json_payload}
    raw = json.dumps(payload, separators=(",", ":"))
    return urllib.parse.quote(raw, safe="")


def request_trpc(method: str, procedure: str, api_key: str, json_payload: dict[str, Any] | None = None) -> tuple[int, dict[str, str], Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
    }

    data: bytes | None = None
    url = f"{BASE_URL}/{procedure}"

    if method == "GET":
        encoded = encode_input(json_payload or {})
        url = f"{url}?input={encoded}"
    else:
        headers["Content-Type"] = "application/json"
        body = {"json": json_payload or {}}
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url=url, method=method, headers=headers, data=data)

    try:
        with urllib.request.urlopen(req) as response:
            body_bytes = response.read()
            status = response.getcode()
            headers_map = {k: v for (k, v) in response.headers.items()}
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            return status, headers_map, body
    except urllib.error.HTTPError as exc:
        body_bytes = exc.read()
        headers_map = {
            k: v for (k, v) in exc.headers.items()} if exc.headers else {}
        body: Any
        try:
            body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
        except Exception:
            body = {"raw": body_bytes.decode("utf-8", errors="replace")}
        return exc.code, headers_map, body


def rate_limit_headers(headers_map: dict[str, str]) -> dict[str, str | None]:
    return {
        "limit": headers_map.get("X-RateLimit-Limit"),
        "remaining": headers_map.get("X-RateLimit-Remaining"),
        "reset": headers_map.get("X-RateLimit-Reset"),
    }


def print_result(status: int, headers_map: dict[str, str], body: Any) -> int:
    output = {
        "status": status,
        "ok": 200 <= status < 300,
        "rateLimit": rate_limit_headers(headers_map),
        "body": body,
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0 if output["ok"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scripts/w2m_events.py",
        description="WhenToMeet v1 events helper CLI (create/list/get/delete).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create event")
    create_parser.add_argument("--title", required=True, help="Event title")
    create_parser.add_argument(
        "--slots-json", required=True, help="JSON array of slots with startTime/endTime")
    create_parser.add_argument(
        "--description", default=None, help="Optional event description")
    create_parser.add_argument(
        "--modification-policy",
        default="EVERYONE",
        choices=["EVERYONE", "ORGANIZER"],
        help="Who can modify event",
    )

    subparsers.add_parser("list", help="List events")

    get_parser = subparsers.add_parser("get", help="Get event")
    get_parser.add_argument("--event-id", required=True, help="Event UUID")

    delete_parser = subparsers.add_parser("delete", help="Delete event")
    delete_parser.add_argument("--event-id", required=True, help="Event UUID")
    delete_parser.add_argument(
        "--confirm",
        action="store_true",
        help="Required for delete operations",
    )

    encode_parser = subparsers.add_parser(
        "encode-input", help="URL-encode GET input payload")
    encode_parser.add_argument(
        "--json",
        required=True,
        help="JSON object to wrap as {\"json\": <value>} and URL-encode",
    )

    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "encode-input":
        try:
            parsed = json.loads(args.json)
        except json.JSONDecodeError as exc:
            return fail(f"--json is not valid JSON: {exc}")
        if not isinstance(parsed, dict):
            return fail("--json must decode to a JSON object")
        print(encode_input(parsed))
        return 0

    api_key = get_api_key()
    if not api_key:
        return fail("WHENTOMEET_API_KEY is required")

    if args.command == "create":
        try:
            slots = parse_slots_json(args.slots_json)
        except ValueError as exc:
            return fail(str(exc))

        payload: dict[str, Any] = {
            "title": args.title,
            "slots": slots,
            "modificationPolicy": args.modification_policy,
        }
        if args.description:
            payload["description"] = args.description

        status, headers_map, body = request_trpc(
            "POST", "v1.event.create", api_key, payload)
        return print_result(status, headers_map, body)

    if args.command == "list":
        status, headers_map, body = request_trpc(
            "GET", "v1.event.list", api_key, {})
        return print_result(status, headers_map, body)

    if args.command == "get":
        payload = {"eventId": args.event_id}
        status, headers_map, body = request_trpc(
            "GET", "v1.event.get", api_key, payload)
        return print_result(status, headers_map, body)

    if args.command == "delete":
        if not args.confirm:
            return fail("delete requires --confirm")
        payload = {"eventId": args.event_id}
        status, headers_map, body = request_trpc(
            "POST", "v1.event.delete", api_key, payload)
        return print_result(status, headers_map, body)

    return fail(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
