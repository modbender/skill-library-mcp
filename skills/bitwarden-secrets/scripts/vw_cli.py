#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from typing import Any, Dict


def run_bw(args):
    p = subprocess.run(["bw", *args], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError((p.stderr or p.stdout).strip())
    return p.stdout.strip()


def parse_json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return s


def ensure_session():
    if not os.getenv("BW_SESSION"):
        raise RuntimeError("BW_SESSION missing. Run: bw unlock, then export BW_SESSION.")


def safe_item_view(item: Dict[str, Any]) -> Dict[str, Any]:
    login = item.get("login") or {}
    uris = [u.get("uri") for u in (login.get("uris") or []) if isinstance(u, dict)]
    password = login.get("password")
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "username": login.get("username"),
        "uris": uris,
        "has_password": password is not None,
        "password_length": len(password) if isinstance(password, str) else None,
        "revisionDate": item.get("revisionDate"),
    }


def cmd_status():
    out = run_bw(["status"])
    print(out)


def cmd_sync():
    ensure_session()
    out = run_bw(["sync"])
    print(json.dumps({"success": True, "message": out}, ensure_ascii=False, indent=2))


def cmd_search(query: str):
    ensure_session()
    out = run_bw(["list", "items", "--search", query])
    items = parse_json(out)
    if not isinstance(items, list):
        raise RuntimeError(f"Unexpected response: {items}")
    print(json.dumps({"count": len(items), "items": [safe_item_view(i) for i in items]}, ensure_ascii=False, indent=2))


def cmd_get(item_id: str):
    ensure_session()
    out = run_bw(["get", "item", item_id])
    item = parse_json(out)
    if not isinstance(item, dict):
        raise RuntimeError(f"Unexpected response: {item}")
    print(json.dumps(safe_item_view(item), ensure_ascii=False, indent=2))


def cmd_reveal(item_id: str, field: str, confirm: str):
    ensure_session()
    if os.getenv("VW_REVEAL_ALLOW", "0") != "1":
        raise RuntimeError("Reveal blocked by policy. Set VW_REVEAL_ALLOW=1 for this shell, then retry with explicit confirm.")
    if confirm != "YES_REVEAL":
        raise RuntimeError("Reveal blocked. Pass --confirm YES_REVEAL for explicit consent.")

    out = run_bw(["get", "item", item_id])
    item = parse_json(out)
    if not isinstance(item, dict):
        raise RuntimeError(f"Unexpected response: {item}")

    login = item.get("login") or {}
    if field == "password":
        value = login.get("password")
    elif field == "username":
        value = login.get("username")
    elif field == "totp":
        value = login.get("totp")
    else:
        raise RuntimeError("Unsupported field. Use: password|username|totp")

    print(json.dumps({"id": item_id, "field": field, "value": value}, ensure_ascii=False, indent=2))


def main():
    p = argparse.ArgumentParser(description="Vaultwarden safe CLI wrapper")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status")
    sub.add_parser("sync")

    s = sub.add_parser("search")
    s.add_argument("--query", required=True)

    g = sub.add_parser("get")
    g.add_argument("--id", required=True)

    r = sub.add_parser("reveal")
    r.add_argument("--id", required=True)
    r.add_argument("--field", required=True)
    r.add_argument("--confirm", required=True)

    a = p.parse_args()
    try:
        if a.cmd == "status":
            cmd_status()
        elif a.cmd == "sync":
            cmd_sync()
        elif a.cmd == "search":
            cmd_search(a.query)
        elif a.cmd == "get":
            cmd_get(a.id)
        elif a.cmd == "reveal":
            cmd_reveal(a.id, a.field, a.confirm)
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
