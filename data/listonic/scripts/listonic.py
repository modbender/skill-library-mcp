#!/usr/bin/env python3
"""Listonic API CLI wrapper for OpenClaw skills.

Supports:
- Authentication via Listonic web-app OAuth flow
- Listing shopping lists and items
- Creating, renaming, deleting lists
- Adding, checking/unchecking, deleting list items

Config file: ~/.openclaw/credentials/listonic/config.json
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://api.listonic.com"
LOGIN_ENDPOINT = "/api/loginextended"
LISTS_ENDPOINT = "/api/lists"

# Defaults from reverse-engineered Listonic web integration
DEFAULT_CLIENT_ID = "listonicv2"
DEFAULT_CLIENT_SECRET = "fjdfsoj9874jdfhjkh34jkhffdfff"
DEFAULT_REDIRECT_URI = "https://listonicv2api.jestemkucharzem.pl"

CONFIG_PATH = Path.home() / ".openclaw" / "credentials" / "listonic" / "config.json"


class ListonicError(Exception):
    pass


def _load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise ListonicError(
            f"Listonic not configured. Create {CONFIG_PATH} with token or email/password auth."
        )

    try:
        cfg = json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as exc:
        raise ListonicError(f"Invalid JSON in {CONFIG_PATH}: {exc}") from exc

    has_token_mode = bool(cfg.get("refreshToken") or cfg.get("accessToken"))
    has_password_mode = bool(cfg.get("email") and cfg.get("password"))

    if not has_token_mode and not has_password_mode:
        raise ListonicError(
            f"Missing auth fields in {CONFIG_PATH}. Provide either refreshToken/accessToken or email/password."
        )

    return cfg


def _http_request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    params: dict[str, str] | None = None,
    json_body: dict[str, Any] | None = None,
    form_body: dict[str, str] | None = None,
    extra_headers: dict[str, str] | None = None,
) -> tuple[int, Any]:
    url = f"{API_BASE}{path}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    headers = {
        "Accept": "application/json",
    }

    body: bytes | None = None

    if json_body is not None:
        headers["Content-Type"] = "application/json"
        body = json.dumps(json_body).encode("utf-8")
    elif form_body is not None:
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        body = urllib.parse.urlencode(form_body).encode("utf-8")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    if extra_headers:
        headers.update(extra_headers)

    req = urllib.request.Request(url=url, method=method, headers=headers, data=body)

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            try:
                parsed = json.loads(raw) if raw else None
            except json.JSONDecodeError:
                parsed = raw
            return resp.status, parsed
    except urllib.error.HTTPError as err:
        raw = err.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            parsed = raw
        return err.code, parsed
    except urllib.error.URLError as err:
        raise ListonicError(f"Connection error: {err}") from err


def _refresh_access_token(cfg: dict[str, Any]) -> str | None:
    refresh_token = cfg.get("refreshToken")
    if not refresh_token:
        return None

    client_id = cfg.get("clientId", DEFAULT_CLIENT_ID)
    client_secret = cfg.get("clientSecret", DEFAULT_CLIENT_SECRET)
    client_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
        "utf-8"
    )

    status, data = _http_request(
        "POST",
        LOGIN_ENDPOINT,
        params={
            "provider": "password",
            "autoMerge": "1",
            "autoDestruct": "1",
        },
        form_body={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": client_id,
            "client_secret": client_secret,
        },
        extra_headers={
            "clientauthorization": f"Bearer {client_auth}",
        },
    )

    if status != 200 or not isinstance(data, dict):
        return None

    access = data.get("access_token")
    new_refresh = data.get("refresh_token")

    if access and (new_refresh and new_refresh != refresh_token):
        cfg["refreshToken"] = new_refresh
        try:
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(cfg, indent=2) + "\n")
        except OSError:
            # Non-fatal: continue with working access token
            pass

    return access


def _authenticate(cfg: dict[str, Any]) -> str:
    # 1) Prefer refresh token mode (best for Google-signin users)
    refreshed = _refresh_access_token(cfg)
    if refreshed:
        return refreshed

    # 2) Fallback to static access token (may expire quickly)
    access_token = cfg.get("accessToken")
    if access_token:
        return access_token

    # 3) Fallback to password auth
    if not (cfg.get("email") and cfg.get("password")):
        raise ListonicError(
            "No usable token auth found and email/password not configured."
        )

    client_id = cfg.get("clientId", DEFAULT_CLIENT_ID)
    client_secret = cfg.get("clientSecret", DEFAULT_CLIENT_SECRET)
    redirect_uri = cfg.get("redirectUri", DEFAULT_REDIRECT_URI)

    client_auth = base64.b64encode(f"{client_id}:{client_secret}".encode("utf-8")).decode(
        "utf-8"
    )

    status, data = _http_request(
        "POST",
        LOGIN_ENDPOINT,
        params={
            "provider": "password",
            "autoMerge": "1",
            "autoDestruct": "1",
        },
        form_body={
            "username": cfg["email"],
            "password": cfg["password"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
        },
        extra_headers={
            "clientauthorization": f"Bearer {client_auth}",
        },
    )

    if status != 200 or not isinstance(data, dict):
        raise ListonicError(f"Authentication failed ({status}): {data}")

    token = data.get("access_token")
    if not token:
        raise ListonicError("Authentication succeeded but no access_token returned")

    return token


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def _get_lists(token: str) -> list[dict[str, Any]]:
    status, data = _http_request(
        "GET",
        LISTS_ENDPOINT,
        token=token,
        params={
            "includeShares": "true",
            "archive": "false",
            "includeItems": "true",
        },
    )
    if status != 200:
        raise ListonicError(f"Failed to fetch lists ({status}): {data}")
    if not isinstance(data, list):
        raise ListonicError(f"Unexpected response for lists: {data}")
    return data


def _find_list_id(token: str, name_or_id: str) -> int:
    try:
        return int(name_or_id)
    except ValueError:
        pass

    lists = _get_lists(token)
    name_norm = name_or_id.strip().lower()
    exact = [lst for lst in lists if str(lst.get("Name", "")).strip().lower() == name_norm]

    if len(exact) == 1:
        return int(exact[0]["Id"])
    if len(exact) > 1:
        raise ListonicError(f"Multiple lists match '{name_or_id}'. Use numeric list_id.")

    partial = [
        lst
        for lst in lists
        if name_norm in str(lst.get("Name", "")).strip().lower()
    ]

    if len(partial) == 1:
        return int(partial[0]["Id"])
    if len(partial) > 1:
        names = ", ".join(f"{lst.get('Name')} ({lst.get('Id')})" for lst in partial[:5])
        raise ListonicError(
            f"Multiple partial matches for '{name_or_id}': {names}. Use numeric list_id."
        )

    raise ListonicError(f"List not found: {name_or_id}")


def cmd_lists(token: str, as_json: bool) -> None:
    lists = _get_lists(token)

    if as_json:
        _print_json(lists)
        return

    if not lists:
        print("No lists found")
        return

    for idx, lst in enumerate(lists, start=1):
        list_id = lst.get("Id")
        name = lst.get("Name", "(unnamed)")
        items = lst.get("Items", []) if isinstance(lst.get("Items"), list) else []
        unchecked = sum(1 for i in items if i.get("Checked", 0) in (0, False))
        checked = sum(1 for i in items if i.get("Checked", 0) in (1, True))
        print(f"{idx}. {name} (id: {list_id}) - {unchecked} open / {checked} done")


def cmd_items(token: str, list_ref: str, as_json: bool) -> None:
    list_id = _find_list_id(token, list_ref)
    status, data = _http_request("GET", f"{LISTS_ENDPOINT}/{list_id}/items", token=token)
    if status != 200:
        raise ListonicError(f"Failed to fetch items ({status}): {data}")

    if as_json:
        _print_json(data)
        return

    if not isinstance(data, list) or not data:
        print(f"No items in list {list_id}")
        return

    for idx, item in enumerate(data, start=1):
        item_id = item.get("IdAsNumber") or item.get("Id")
        name = item.get("Name", "(unnamed)")
        checked = item.get("Checked", 0) in (1, True)
        mark = "✅" if checked else "⬜"
        amount = item.get("Amount")
        unit = item.get("Unit")
        qty = ""
        if amount:
            qty = f" [{amount}{(' ' + str(unit)) if unit else ''}]"
        print(f"{idx}. {mark} {name}{qty} (item_id: {item_id})")


def cmd_add_list(token: str, name: str, as_json: bool) -> None:
    status, data = _http_request("POST", LISTS_ENDPOINT, token=token, json_body={"Name": name})
    if status not in (200, 201):
        raise ListonicError(f"Failed to create list ({status}): {data}")

    if as_json:
        _print_json(data)
    else:
        print(f"✅ Created list: {data.get('Name', name)} (id: {data.get('Id', '?')})")


def cmd_rename_list(token: str, list_ref: str, new_name: str, as_json: bool) -> None:
    list_id = _find_list_id(token, list_ref)
    status, data = _http_request(
        "PATCH", f"{LISTS_ENDPOINT}/{list_id}", token=token, json_body={"Name": new_name}
    )
    if status != 200:
        raise ListonicError(f"Failed to rename list ({status}): {data}")

    if as_json:
        _print_json({"ok": True, "list_id": list_id, "name": new_name, "raw": data})
    else:
        print(f"✅ Renamed list {list_id} to: {new_name}")


def cmd_delete_list(token: str, list_ref: str, as_json: bool) -> None:
    list_id = _find_list_id(token, list_ref)
    status, data = _http_request("DELETE", f"{LISTS_ENDPOINT}/{list_id}", token=token)
    if status != 200:
        raise ListonicError(f"Failed to delete list ({status}): {data}")

    if as_json:
        _print_json({"ok": True, "list_id": list_id, "raw": data})
    else:
        print(f"🗑️ Deleted list {list_id}")


def cmd_add_item(
    token: str,
    list_ref: str,
    name: str,
    amount: str | None,
    unit: str | None,
    as_json: bool,
) -> None:
    list_id = _find_list_id(token, list_ref)
    payload: dict[str, Any] = {"Name": name}
    if amount:
        payload["Amount"] = amount
    if unit:
        payload["Unit"] = unit

    status, data = _http_request(
        "POST", f"{LISTS_ENDPOINT}/{list_id}/items", token=token, json_body=payload
    )
    if status not in (200, 201):
        raise ListonicError(f"Failed to add item ({status}): {data}")

    if as_json:
        _print_json(data)
    else:
        item_id = data.get("IdAsNumber") or data.get("Id", "?")
        print(f"✅ Added item to list {list_id}: {name} (item_id: {item_id})")


def cmd_set_item_checked(
    token: str,
    list_ref: str,
    item_id: int,
    checked: bool,
    as_json: bool,
) -> None:
    list_id = _find_list_id(token, list_ref)
    status, data = _http_request(
        "PATCH",
        f"{LISTS_ENDPOINT}/{list_id}/items/{item_id}",
        token=token,
        json_body={"Checked": 1 if checked else 0},
    )
    if status != 200:
        raise ListonicError(f"Failed to update item ({status}): {data}")

    if as_json:
        _print_json({"ok": True, "list_id": list_id, "item_id": item_id, "checked": checked})
    else:
        print(f"✅ Item {item_id} in list {list_id} marked {'checked' if checked else 'unchecked'}")


def cmd_delete_item(token: str, list_ref: str, item_id: int, as_json: bool) -> None:
    list_id = _find_list_id(token, list_ref)
    status, data = _http_request(
        "DELETE",
        f"{LISTS_ENDPOINT}/{list_id}/items/{item_id}",
        token=token,
    )
    if status != 200:
        raise ListonicError(f"Failed to delete item ({status}): {data}")

    if as_json:
        _print_json({"ok": True, "list_id": list_id, "item_id": item_id, "raw": data})
    else:
        print(f"🗑️ Deleted item {item_id} from list {list_id}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Listonic API CLI")
    parser.add_argument("--json", action="store_true", help="Output raw JSON when possible")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("lists", help="List all shopping lists")

    p_items = sub.add_parser("items", help="List items in a list")
    p_items.add_argument("list", help="List ID or list name")

    p_add_list = sub.add_parser("add-list", help="Create a list")
    p_add_list.add_argument("name", help="List name")

    p_rename = sub.add_parser("rename-list", help="Rename a list")
    p_rename.add_argument("list", help="List ID or list name")
    p_rename.add_argument("name", help="New list name")

    p_delete_list = sub.add_parser("delete-list", help="Delete a list")
    p_delete_list.add_argument("list", help="List ID or list name")

    p_add_item = sub.add_parser("add-item", help="Add item to a list")
    p_add_item.add_argument("list", help="List ID or list name")
    p_add_item.add_argument("name", help="Item name")
    p_add_item.add_argument("--amount", help="Amount/quantity (e.g. 2, 500)")
    p_add_item.add_argument("--unit", help="Unit (e.g. kg, l, pcs)")

    p_check = sub.add_parser("check-item", help="Mark item as checked")
    p_check.add_argument("list", help="List ID or list name")
    p_check.add_argument("item_id", type=int, help="Item ID")

    p_uncheck = sub.add_parser("uncheck-item", help="Mark item as unchecked")
    p_uncheck.add_argument("list", help="List ID or list name")
    p_uncheck.add_argument("item_id", type=int, help="Item ID")

    p_delete_item = sub.add_parser("delete-item", help="Delete item from a list")
    p_delete_item.add_argument("list", help="List ID or list name")
    p_delete_item.add_argument("item_id", type=int, help="Item ID")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        cfg = _load_config()
        token = _authenticate(cfg)

        if args.command == "lists":
            cmd_lists(token, args.json)
        elif args.command == "items":
            cmd_items(token, args.list, args.json)
        elif args.command == "add-list":
            cmd_add_list(token, args.name, args.json)
        elif args.command == "rename-list":
            cmd_rename_list(token, args.list, args.name, args.json)
        elif args.command == "delete-list":
            cmd_delete_list(token, args.list, args.json)
        elif args.command == "add-item":
            cmd_add_item(token, args.list, args.name, args.amount, args.unit, args.json)
        elif args.command == "check-item":
            cmd_set_item_checked(token, args.list, args.item_id, True, args.json)
        elif args.command == "uncheck-item":
            cmd_set_item_checked(token, args.list, args.item_id, False, args.json)
        elif args.command == "delete-item":
            cmd_delete_item(token, args.list, args.item_id, args.json)
        else:
            parser.error(f"Unknown command: {args.command}")

        return 0

    except ListonicError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
