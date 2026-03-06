#!/usr/bin/env python3
"""CLI tool for OpenClaw to manage GoList shared lists."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_BASE_URL = "https://go-list.app/api"
STATE_FILE_ENV = "OPENCLAW_STATE_FILE"
DEFAULT_STATE_FILE = Path.home() / ".openclaw_golist_state.json"


class CliError(Exception):
    """Raised when user-facing CLI errors occur."""


@dataclass
class KnownList:
    id: str
    name: str


@dataclass
class RuntimeState:
    device_id: str | None = None
    active_list_id: str | None = None
    known_lists: list[KnownList] = field(default_factory=list)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def resolve_state_file() -> Path:
    configured = os.environ.get(STATE_FILE_ENV)
    return Path(configured).expanduser() if configured else DEFAULT_STATE_FILE


def parse_known_lists(raw: Any) -> list[KnownList]:
    if not isinstance(raw, list):
        return []

    parsed: list[KnownList] = []
    for entry in raw:
        if not isinstance(entry, dict):
            continue
        list_id = entry.get("id")
        name = entry.get("name")
        if isinstance(list_id, str) and list_id and isinstance(name, str) and name:
            parsed.append(KnownList(id=list_id, name=name))
    return parsed


def load_state() -> RuntimeState:
    state = RuntimeState(device_id=os.environ.get("GOLIST_DEVICE_ID"))

    state_path = resolve_state_file()
    if not state_path.exists():
        return state

    with state_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    state.device_id = state.device_id or payload.get("device_id")
    state.active_list_id = payload.get("active_list_id") or payload.get("list_id")
    state.known_lists = parse_known_lists(payload.get("known_lists"))

    legacy_list_id = payload.get("list_id")
    if isinstance(legacy_list_id, str) and legacy_list_id and not find_known_list_by_id(state, legacy_list_id):
        state.known_lists.append(KnownList(id=legacy_list_id, name="Shared list"))

    return state


def save_state(state: RuntimeState) -> None:
    state_path = resolve_state_file()
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "device_id": state.device_id,
                "active_list_id": state.active_list_id,
                "known_lists": [
                    {
                        "id": known_list.id,
                        "name": known_list.name,
                    }
                    for known_list in state.known_lists
                ],
            },
            handle,
            indent=2,
        )


def ensure_device_id(state: RuntimeState) -> str:
    if state.device_id:
        return state.device_id
    state.device_id = str(uuid.uuid4())
    save_state(state)
    return state.device_id


def build_headers(device_id: str, include_json: bool = True) -> dict[str, str]:
    headers = {
        "X-Device-Id": device_id,
    }
    if include_json:
        headers["Content-Type"] = "application/json"
    return headers


def api_request(
    method: str,
    path: str,
    device_id: str,
    body: dict[str, Any] | None = None,
    query: dict[str, str] | None = None,
) -> Any:
    url = f"{API_BASE_URL}{path}"
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    data: bytes | None = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        method=method,
        headers=build_headers(device_id=device_id, include_json=body is not None),
        data=data,
    )

    try:
        with urllib.request.urlopen(request) as response:
            response_text = response.read().decode("utf-8")
            if not response_text:
                return None
            return json.loads(response_text)
    except urllib.error.HTTPError as exc:
        response_text = exc.read().decode("utf-8")
        detail = response_text.strip() or exc.reason
        raise CliError(f"API request failed ({exc.code}): {detail}") from exc
    except urllib.error.URLError as exc:
        raise CliError(f"Could not reach GoList API: {exc.reason}") from exc


def find_known_list_by_id(state: RuntimeState, list_id: str) -> KnownList | None:
    for known_list in state.known_lists:
        if known_list.id == list_id:
            return known_list
    return None


def find_known_list_by_name(state: RuntimeState, name: str) -> KnownList | None:
    normalized_name = name.strip().lower()
    for known_list in state.known_lists:
        if known_list.name.strip().lower() == normalized_name:
            return known_list
    return None


def upsert_known_list(state: RuntimeState, list_id: str, name: str) -> KnownList:
    existing = find_known_list_by_id(state, list_id)
    if existing:
        existing.name = name
        return existing

    new_known_list = KnownList(id=list_id, name=name)
    state.known_lists.append(new_known_list)
    return new_known_list


def resolve_list_reference(state: RuntimeState, list_ref: str | None) -> KnownList:
    if list_ref:
        by_id = find_known_list_by_id(state, list_ref)
        if by_id:
            return by_id

        by_name = find_known_list_by_name(state, list_ref)
        if by_name:
            return by_name

        raise CliError(f"Unknown list reference: {list_ref}")

    if state.active_list_id:
        active = find_known_list_by_id(state, state.active_list_id)
        if active:
            return active

        raise CliError(
            "Active list is missing from known lists. Run `join` with a share token or `create-list` to configure one."
        )

    raise CliError("No active list set. Use `create-list` or `join` first.")


def fetch_list(device_id: str, list_id: str) -> dict[str, Any]:
    payload = api_request("GET", f"/v1/lists/{list_id}", device_id=device_id)
    if not isinstance(payload, dict):
        raise CliError("Unexpected API response while reading list.")
    return payload


def create_list(state: RuntimeState, list_name: str) -> KnownList:
    device_id = ensure_device_id(state)
    list_id = str(uuid.uuid4())

    api_request("PUT", f"/v1/lists/{list_id}", device_id=device_id, body={"name": list_name})

    known_list = upsert_known_list(state, list_id, list_name)
    state.active_list_id = list_id
    save_state(state)
    return known_list


def redeem_share_token(state: RuntimeState, share_token: str) -> KnownList:
    device_id = ensure_device_id(state)

    payload = api_request("POST", f"/v1/share-tokens/{share_token}/redeem", device_id=device_id)

    list_id = payload.get("listId") if isinstance(payload, dict) else None
    if not list_id:
        raise CliError("Token redemption succeeded but response did not include listId.")

    fetched = fetch_list(device_id=device_id, list_id=list_id)
    fetched_name = fetched.get("name")
    resolved_name = fetched_name if isinstance(fetched_name, str) and fetched_name else "Shared list"

    known_list = upsert_known_list(state, list_id, resolved_name)
    state.active_list_id = list_id
    save_state(state)
    return known_list


def cmd_bootstrap(state: RuntimeState, args: argparse.Namespace) -> None:
    known_list = redeem_share_token(state=state, share_token=args.share_token)
    print(
        json.dumps(
            {
                "deviceId": state.device_id,
                "activeList": {"id": known_list.id, "name": known_list.name},
            },
            indent=2,
        )
    )


def cmd_create_list(state: RuntimeState, args: argparse.Namespace) -> None:
    known_list = create_list(state=state, list_name=args.name)
    print(json.dumps({"deviceId": state.device_id, "activeList": {"id": known_list.id, "name": known_list.name}}, indent=2))


def cmd_join(state: RuntimeState, args: argparse.Namespace) -> None:
    share_token = args.share_token or args.share_token_arg or os.environ.get("GOLIST_SHARE_TOKEN")
    if not share_token:
        raise CliError("A share token is required. Pass one as an argument, --share-token, or GOLIST_SHARE_TOKEN.")

    known_list = redeem_share_token(state=state, share_token=share_token)
    print(json.dumps({"deviceId": state.device_id, "activeList": {"id": known_list.id, "name": known_list.name}}, indent=2))


def cmd_use_list(state: RuntimeState, args: argparse.Namespace) -> None:
    selected = resolve_list_reference(state, args.list)
    state.active_list_id = selected.id
    save_state(state)
    print(json.dumps({"activeList": {"id": selected.id, "name": selected.name}}, indent=2))


def cmd_lists(state: RuntimeState, _args: argparse.Namespace) -> None:
    known_lists = [{"id": known_list.id, "name": known_list.name} for known_list in state.known_lists]
    print(json.dumps({"activeListId": state.active_list_id, "lists": known_lists}, indent=2))


def cmd_show(state: RuntimeState, args: argparse.Namespace) -> None:
    device_id = ensure_device_id(state)
    known_list = resolve_list_reference(state, args.list)
    payload = fetch_list(device_id=device_id, list_id=known_list.id)

    items = payload.get("items", [])
    non_deleted_items = [item for item in items if not item.get("deleted")]

    fetched_name = payload.get("name")
    if isinstance(fetched_name, str) and fetched_name:
        upsert_known_list(state, known_list.id, fetched_name)
        save_state(state)

    print(json.dumps({"listId": known_list.id, "name": payload.get("name"), "items": non_deleted_items}, indent=2))


def find_item_by_name(list_payload: dict[str, Any], name: str) -> dict[str, Any] | None:
    items = list_payload.get("items")
    if not isinstance(items, list):
        return None

    normalized_name = name.strip().lower()
    for item in items:
        if not isinstance(item, dict):
            continue
        item_name = item.get("name")
        if isinstance(item_name, str) and item_name.strip().lower() == normalized_name:
            return item
    return None


def cmd_upsert(state: RuntimeState, args: argparse.Namespace) -> None:
    device_id = ensure_device_id(state)
    known_list = resolve_list_reference(state, args.list)
    list_payload = fetch_list(device_id=device_id, list_id=known_list.id)

    existing_item = find_item_by_name(list_payload, args.name)
    item_id = existing_item.get("id") if isinstance(existing_item, dict) else None
    if not isinstance(item_id, str) or not item_id:
        item_id = str(uuid.uuid4())

    body: dict[str, Any] = {
        "name": args.name,
        "deleted": bool(args.deleted),
        "updatedAt": now_iso(),
    }
    if args.quantity is not None:
        body["quantityOrUnit"] = args.quantity

    payload = api_request("PUT", f"/v1/lists/{known_list.id}/items/{item_id}", device_id=device_id, body=body)

    print(json.dumps({"listId": known_list.id, "itemId": item_id, "response": payload}, indent=2))


def cmd_delete(state: RuntimeState, args: argparse.Namespace) -> None:
    device_id = ensure_device_id(state)
    known_list = resolve_list_reference(state, args.list)
    list_payload = fetch_list(device_id=device_id, list_id=known_list.id)

    existing_item = find_item_by_name(list_payload, args.name)
    if not existing_item:
        raise CliError(f"Could not find item named '{args.name}' in list '{known_list.name}'.")

    item_id = existing_item.get("id")
    item_name = existing_item.get("name")
    if not isinstance(item_id, str) or not isinstance(item_name, str):
        raise CliError("Found item but it is missing required fields in API response.")

    body = {
        "name": item_name,
        "deleted": True,
        "updatedAt": now_iso(),
    }

    payload = api_request("PUT", f"/v1/lists/{known_list.id}/items/{item_id}", device_id=device_id, body=body)

    print(json.dumps({"listId": known_list.id, "itemId": item_id, "response": payload}, indent=2))


def cmd_share(state: RuntimeState, args: argparse.Namespace) -> None:
    device_id = ensure_device_id(state)
    known_list = resolve_list_reference(state, args.list)
    payload = api_request("POST", f"/v1/lists/{known_list.id}/share-tokens", device_id=device_id)

    if not isinstance(payload, dict):
        raise CliError("Unexpected API response while creating share token.")

    share_token = payload.get("shareToken")
    if not isinstance(share_token, str) or not share_token:
        raise CliError("Share token response was missing shareToken.")

    print(
        json.dumps(
            {
                "list": {"id": known_list.id, "name": known_list.name},
                "shareToken": share_token,
                "shareUrl": f"https://go-list.app/?shareToken={share_token}",
            },
            indent=2,
        )
    )


def cmd_sync(state: RuntimeState, args: argparse.Namespace) -> None:
    device_id = ensure_device_id(state)
    known_list = resolve_list_reference(state, args.list)

    payload = api_request(
        "GET",
        f"/v1/lists/{known_list.id}/items",
        device_id=device_id,
        query={"updatedAfter": args.updated_after},
    )

    print(json.dumps(payload, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="OpenClaw GoList multi-list CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    bootstrap_parser = subparsers.add_parser("bootstrap", help="Redeem share token and set active list")
    bootstrap_parser.add_argument("--share-token", default=os.environ.get("GOLIST_SHARE_TOKEN"), help="Share token UUID")
    bootstrap_parser.set_defaults(func=cmd_bootstrap)

    create_list_parser = subparsers.add_parser("create-list", help="Create a new list and set it active")
    create_list_parser.add_argument("name", help="List name")
    create_list_parser.set_defaults(func=cmd_create_list)

    join_parser = subparsers.add_parser("join", help="Join an existing shared list with a share token")
    join_parser.add_argument("share_token_arg", nargs="?", help="Share token UUID")
    join_parser.add_argument("--share-token", dest="share_token", help="Share token UUID")
    join_parser.set_defaults(func=cmd_join)

    use_list_parser = subparsers.add_parser("use-list", help="Set active list by saved list id or name")
    use_list_parser.add_argument("list", help="Saved list id or name")
    use_list_parser.set_defaults(func=cmd_use_list)

    lists_parser = subparsers.add_parser("lists", help="Show known lists and active list")
    lists_parser.set_defaults(func=cmd_lists)

    show_parser = subparsers.add_parser("show", help="Fetch list and print non-deleted items")
    show_parser.add_argument("--list", help="Optional list id or name. Defaults to active list")
    show_parser.set_defaults(func=cmd_show)

    upsert_parser = subparsers.add_parser("upsert", help="Create/update an item by name")
    upsert_parser.add_argument("name", help="Item name")
    upsert_parser.add_argument("--quantity", help="Optional quantity/unit text")
    upsert_parser.add_argument("--deleted", action="store_true", help="Optionally mark the item as deleted (default: false)")
    upsert_parser.add_argument("--list", help="Optional list id or name. Defaults to active list")
    upsert_parser.set_defaults(func=cmd_upsert)

    delete_parser = subparsers.add_parser("delete", help="Soft-delete an item by name")
    delete_parser.add_argument("name", help="Existing item name")
    delete_parser.add_argument("--list", help="Optional list id or name. Defaults to active list")
    delete_parser.set_defaults(func=cmd_delete)

    share_parser = subparsers.add_parser("share", help="Create share token for a list")
    share_parser.add_argument("--list", help="Optional list id or name. Defaults to active list")
    share_parser.set_defaults(func=cmd_share)

    sync_parser = subparsers.add_parser("sync", help="Fetch items updated after a timestamp")
    sync_parser.add_argument("updated_after", help="ISO timestamp")
    sync_parser.add_argument("--list", help="Optional list id or name. Defaults to active list")
    sync_parser.set_defaults(func=cmd_sync)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    state = load_state()

    if args.command == "bootstrap" and not args.share_token:
        print("A share token is required. Set --share-token or GOLIST_SHARE_TOKEN.", file=sys.stderr)
        return 1

    try:
        args.func(state, args)
        return 0
    except CliError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
