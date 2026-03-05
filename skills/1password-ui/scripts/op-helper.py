#!/usr/bin/env python3
"""
1Password Helper Script

Provides a Python bridge for 1Password operations, used by skills
that need to read credentials from 1Password.

Usage:
    # Check status
    python3 op-helper.py status
    
    # Read a secret
    python3 op-helper.py read "Pipedream Connect" "client_secret" --vault Private
    
    # Read with Connect API
    OP_CONNECT_HOST=http://localhost:8080 OP_CONNECT_TOKEN=xxx python3 op-helper.py read ...

Supports both CLI (op) and Connect API modes automatically.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


def is_connect_mode() -> bool:
    """Check if 1Password Connect is configured."""
    return bool(os.environ.get("OP_CONNECT_HOST") and os.environ.get("OP_CONNECT_TOKEN"))


def connect_api_call(method: str, endpoint: str, body=None):
    """Make a call to 1Password Connect API."""
    host = os.environ["OP_CONNECT_HOST"].rstrip("/")
    token = os.environ["OP_CONNECT_TOKEN"]
    
    url = f"{host}/v1{endpoint}"
    data = json.dumps(body).encode("utf-8") if body else None
    
    req = Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        raise Exception(f"Connect API error {e.code}: {error_body}")


def op_command(args: list, timeout: int = 30) -> str:
    """Run an op CLI command."""
    op_path = shutil.which("op")
    if not op_path:
        raise Exception("1Password CLI (op) not found in PATH")
    
    result = subprocess.run(
        [op_path] + args,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    
    if result.returncode != 0:
        raise Exception(result.stderr.strip() or f"Command failed with code {result.returncode}")
    
    return result.stdout.strip()


def cmd_status():
    """Check 1Password status."""
    if is_connect_mode():
        try:
            vaults = connect_api_call("GET", "/vaults")
            print(json.dumps({
                "mode": "connect",
                "connected": True,
                "host": os.environ["OP_CONNECT_HOST"],
                "vaults": len(vaults)
            }))
        except Exception as e:
            print(json.dumps({
                "mode": "connect",
                "connected": False,
                "error": str(e)
            }))
    else:
        op_path = shutil.which("op")
        if not op_path:
            print(json.dumps({"mode": "cli", "installed": False, "signedIn": False}))
            return
        
        try:
            output = op_command(["whoami", "--format=json"])
            info = json.loads(output)
            print(json.dumps({
                "mode": "cli",
                "installed": True,
                "signedIn": True,
                "account": info.get("url") or info.get("account_uuid"),
                "email": info.get("email")
            }))
        except Exception as e:
            print(json.dumps({
                "mode": "cli",
                "installed": True,
                "signedIn": False,
                "error": str(e)
            }))


def cmd_read(item: str, field: str, vault: str = None):
    """Read a secret from 1Password."""
    if is_connect_mode():
        # Need to resolve vault and item IDs
        # For simplicity, assume vault is ID and item is title
        if not vault:
            raise Exception("--vault required for Connect mode")
        
        # List items to find by title
        items = connect_api_call("GET", f"/vaults/{vault}/items")
        item_match = next((i for i in items if i["title"] == item), None)
        if not item_match:
            raise Exception(f"Item '{item}' not found in vault")
        
        # Get full item with fields
        full_item = connect_api_call("GET", f"/vaults/{vault}/items/{item_match['id']}")
        
        # Find field
        field_match = next(
            (f for f in full_item.get("fields", []) if f.get("label") == field or f.get("id") == field),
            None
        )
        if not field_match or not field_match.get("value"):
            raise Exception(f"Field '{field}' not found or empty")
        
        print(field_match["value"])
    else:
        vault_path = vault or "Private"
        output = op_command(["read", f"op://{vault_path}/{item}/{field}"])
        print(output)


def cmd_list_vaults():
    """List available vaults."""
    if is_connect_mode():
        vaults = connect_api_call("GET", "/vaults")
        print(json.dumps(vaults))
    else:
        output = op_command(["vault", "list", "--format=json"])
        print(output)


def cmd_list_items(vault: str = None):
    """List items in a vault."""
    if is_connect_mode():
        if not vault:
            raise Exception("--vault required for Connect mode")
        items = connect_api_call("GET", f"/vaults/{vault}/items")
        print(json.dumps(items))
    else:
        args = ["item", "list", "--format=json"]
        if vault:
            args.extend(["--vault", vault])
        output = op_command(args)
        print(output)


def main():
    parser = argparse.ArgumentParser(description="1Password helper for OpenClaw skills")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # status
    subparsers.add_parser("status", help="Check 1Password status")
    
    # read
    read_parser = subparsers.add_parser("read", help="Read a secret")
    read_parser.add_argument("item", help="Item name or ID")
    read_parser.add_argument("field", help="Field name or ID")
    read_parser.add_argument("--vault", "-v", help="Vault name or ID")
    
    # vaults
    subparsers.add_parser("vaults", help="List vaults")
    
    # items
    items_parser = subparsers.add_parser("items", help="List items")
    items_parser.add_argument("--vault", "-v", help="Vault name or ID")
    
    args = parser.parse_args()
    
    try:
        if args.command == "status":
            cmd_status()
        elif args.command == "read":
            cmd_read(args.item, args.field, args.vault)
        elif args.command == "vaults":
            cmd_list_vaults()
        elif args.command == "items":
            cmd_list_items(args.vault)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
