#!/usr/bin/env python3
"""Portable Python CLI for Nomi API access used by the ClawHub skill package."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib import error, request

BASE_URL = "https://api.nomi.ai/v1"
DEFAULT_TIMEOUT_SECONDS = 120.0
AVATAR_OUTPUT_DIR = Path("nomi") / "avatars"


class NomiCliError(Exception):
    """Raised for expected CLI failures."""


def _timeout_seconds() -> float:
    raw = os.environ.get("NOMI_CLIENT_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS))
    try:
        return float(raw)
    except ValueError:
        print(
            f"Warning: Invalid NOMI_CLIENT_TIMEOUT value '{raw}'. Using default {DEFAULT_TIMEOUT_SECONDS}s.",
            file=sys.stderr,
        )
        return DEFAULT_TIMEOUT_SECONDS


def _require_api_key() -> str:
    api_key = os.environ.get("NOMI_API_KEY", "")
    if not api_key:
        raise NomiCliError(
            "NOMI_API_KEY environment variable is not set.\nFix: export NOMI_API_KEY=your_api_key"
        )
    return api_key


def _api_call(
    method: str,
    path: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
    accept: str = "application/json",
) -> tuple[bytes, str]:
    url = f"{BASE_URL}{path}"
    body: bytes | None = None
    headers = {
        "Authorization": api_key,
        "Accept": accept,
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = request.Request(url, data=body, headers=headers, method=method)

    try:
        with request.urlopen(req, timeout=_timeout_seconds()) as response:
            content = response.read()
            content_type = response.headers.get("Content-Type", "")
            return content, content_type
    except error.HTTPError as exc:
        err_body = exc.read().decode("utf-8", "replace")
        raise NomiCliError(f"API request failed ({exc.code}): {err_body}") from exc
    except error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        raise NomiCliError(f"Network error: {reason}") from exc


def _api_json(
    method: str,
    path: str,
    api_key: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content, _ = _api_call(method, path, api_key, payload=payload, accept="application/json")
    if not content:
        return {}
    try:
        return json.loads(content.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise NomiCliError("API returned invalid JSON.") from exc


def _print_json(data: dict[str, Any]) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _safe_avatar_output(uuid: str, output_name: str | None) -> Path:
    """Return a safe local avatar output path under ./nomi/avatars.

    Rejects absolute paths and any path traversal attempt by accepting only
    a bare filename. This prevents arbitrary filesystem writes.
    """
    default_name = f"nomi-{uuid}-avatar.webp"
    raw_name = output_name or default_name

    if "/" in raw_name or "\\" in raw_name:
        raise NomiCliError("Avatar output must be a filename only (no path separators).")

    name = Path(raw_name).name
    if name in {"", ".", ".."} or name.startswith("."):
        raise NomiCliError("Avatar output filename is invalid.")

    avatar_dir = Path.cwd() / AVATAR_OUTPUT_DIR
    avatar_dir.mkdir(parents=True, exist_ok=True)
    return avatar_dir / name


def _cmd_list(args: argparse.Namespace, api_key: str) -> int:
    _print_json(_api_json("GET", "/nomis", api_key))
    return 0


def _cmd_get(args: argparse.Namespace, api_key: str) -> int:
    _print_json(_api_json("GET", f"/nomis/{args.uuid}", api_key))
    return 0


def _cmd_avatar(args: argparse.Namespace, api_key: str) -> int:
    content, content_type = _api_call("GET", f"/nomis/{args.uuid}/avatar", api_key, accept="image/*")
    if "image/" not in content_type:
        raise NomiCliError(f"Unexpected content type for avatar: {content_type or 'unknown'}")
    output = _safe_avatar_output(args.uuid, args.output)
    output.write_bytes(content)
    print(f"Avatar saved to: {output}")
    return 0


def _cmd_chat(args: argparse.Namespace, api_key: str) -> int:
    payload = {"messageText": args.message}
    _print_json(_api_json("POST", f"/nomis/{args.uuid}/chat", api_key, payload=payload))
    return 0


def _cmd_reply(args: argparse.Namespace, api_key: str) -> int:
    payload = {"messageText": args.message}
    response = _api_json("POST", f"/nomis/{args.uuid}/chat", api_key, payload=payload)
    print(response.get("replyMessage", {}).get("text", ""))
    return 0


def _cmd_room_list(args: argparse.Namespace, api_key: str) -> int:
    _print_json(_api_json("GET", "/rooms", api_key))
    return 0


def _cmd_room_get(args: argparse.Namespace, api_key: str) -> int:
    _print_json(_api_json("GET", f"/rooms/{args.room_uuid}", api_key))
    return 0


def _cmd_room_create(args: argparse.Namespace, api_key: str) -> int:
    payload = {
        "name": args.name,
        "nomiUuids": args.nomi_uuids,
        "backchannelingEnabled": args.backchanneling_enabled,
        "note": args.note,
    }
    _print_json(_api_json("POST", "/rooms", api_key, payload=payload))
    return 0


def _cmd_room_update(args: argparse.Namespace, api_key: str) -> int:
    payload: dict[str, Any] = {}
    if args.name is not None:
        payload["name"] = args.name
    if args.nomi_uuids is not None:
        payload["nomiUuids"] = args.nomi_uuids
    if not payload:
        raise NomiCliError("room update requires at least one of --name or --nomi-uuids.")
    _print_json(_api_json("PUT", f"/rooms/{args.room_uuid}", api_key, payload=payload))
    return 0


def _cmd_room_delete(args: argparse.Namespace, api_key: str) -> int:
    _api_json("DELETE", f"/rooms/{args.room_uuid}", api_key)
    print(f"Room {args.room_uuid} deleted")
    return 0


def _cmd_room_chat(args: argparse.Namespace, api_key: str) -> int:
    payload = {"messageText": args.message}
    _print_json(_api_json("POST", f"/rooms/{args.room_uuid}/chat", api_key, payload=payload))
    return 0


def _cmd_room_request(args: argparse.Namespace, api_key: str) -> int:
    payload = {"nomiUuid": args.nomi_uuid}
    _print_json(_api_json("POST", f"/rooms/{args.room_uuid}/chat/request", api_key, payload=payload))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="nomi", description="Nomi API CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list", help="List all Nomis")
    p_list.set_defaults(handler=_cmd_list)

    p_get = subparsers.add_parser("get", help="Get Nomi details")
    p_get.add_argument("uuid", help="Nomi UUID")
    p_get.set_defaults(handler=_cmd_get)

    p_avatar = subparsers.add_parser("avatar", help="Download Nomi avatar")
    p_avatar.add_argument("uuid", help="Nomi UUID")
    p_avatar.add_argument("output", nargs="?", help="Output filename (saved under ./nomi/avatars)")
    p_avatar.set_defaults(handler=_cmd_avatar)

    p_chat = subparsers.add_parser("chat", help="Send a message to a Nomi")
    p_chat.add_argument("uuid", help="Nomi UUID")
    p_chat.add_argument("message", help="Message text")
    p_chat.set_defaults(handler=_cmd_chat)

    p_reply = subparsers.add_parser("reply", help="Send a message and print reply text only")
    p_reply.add_argument("uuid", help="Nomi UUID")
    p_reply.add_argument("message", help="Message text")
    p_reply.set_defaults(handler=_cmd_reply)

    p_room = subparsers.add_parser("room", help="Room operations")
    room_subparsers = p_room.add_subparsers(dest="room_command", required=True)

    p_room_list = room_subparsers.add_parser("list", help="List all rooms")
    p_room_list.set_defaults(handler=_cmd_room_list)

    p_room_get = room_subparsers.add_parser("get", help="Get room details")
    p_room_get.add_argument("room_uuid", help="Room UUID")
    p_room_get.set_defaults(handler=_cmd_room_get)

    p_room_create = room_subparsers.add_parser("create", help="Create a room")
    p_room_create.add_argument("name", help="Room name")
    p_room_create.add_argument("nomi_uuids", nargs="+", help="Nomi UUIDs")
    p_room_create.add_argument(
        "--no-backchannel",
        dest="backchanneling_enabled",
        action="store_false",
        help="Disable backchanneling",
    )
    p_room_create.set_defaults(backchanneling_enabled=True)
    p_room_create.add_argument("--note", default="Created via CLI", help="Room note")
    p_room_create.set_defaults(handler=_cmd_room_create)

    p_room_update = room_subparsers.add_parser("update", help="Update a room")
    p_room_update.add_argument("room_uuid", help="Room UUID")
    p_room_update.add_argument("--name", help="New room name")
    p_room_update.add_argument("--nomi-uuids", nargs="+", help="Replacement Nomi UUID list")
    p_room_update.set_defaults(handler=_cmd_room_update)

    p_room_delete = room_subparsers.add_parser("delete", help="Delete a room")
    p_room_delete.add_argument("room_uuid", help="Room UUID")
    p_room_delete.set_defaults(handler=_cmd_room_delete)

    p_room_chat = room_subparsers.add_parser("chat", help="Send a message to a room")
    p_room_chat.add_argument("room_uuid", help="Room UUID")
    p_room_chat.add_argument("message", help="Message text")
    p_room_chat.set_defaults(handler=_cmd_room_chat)

    p_room_request = room_subparsers.add_parser("request", help="Request a specific Nomi reply in a room")
    p_room_request.add_argument("room_uuid", help="Room UUID")
    p_room_request.add_argument("nomi_uuid", help="Nomi UUID")
    p_room_request.set_defaults(handler=_cmd_room_request)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        api_key = _require_api_key()
        return int(args.handler(args, api_key))
    except NomiCliError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
