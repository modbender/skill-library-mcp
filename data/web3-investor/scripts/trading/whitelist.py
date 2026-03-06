#!/usr/bin/env python3
"""
Manage address whitelist for Safe Vault.

Usage:
    python whitelist.py --list
    python whitelist.py --add 0x... --name "Aave Pool" --max-amount 500
    python whitelist.py --remove 0x...
    python whitelist.py --enable
    python whitelist.py --disable
"""

import argparse
import json
import os
import sys

WHITELIST_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "whitelist.json")


def load_whitelist() -> dict:
    """Load whitelist from file."""
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH) as f:
            return json.load(f)
    return {"enabled": True, "addresses": []}


def save_whitelist(whitelist: dict):
    """Save whitelist to file."""
    os.makedirs(os.path.dirname(WHITELIST_PATH), exist_ok=True)
    with open(WHITELIST_PATH, "w") as f:
        json.dump(whitelist, f, indent=2)


def list_whitelist():
    """List all whitelisted addresses."""
    whitelist = load_whitelist()
    
    print(f"Whitelist Status: {'🟢 ENABLED' if whitelist.get('enabled', True) else '🔴 DISABLED'}")
    print()
    
    addresses = whitelist.get("addresses", [])
    if not addresses:
        print("No addresses in whitelist.")
        return
    
    print(f"{'Address':<44} {'Name':<20} {'Max Amount (USD)':<15}")
    print("-" * 80)
    
    for entry in addresses:
        addr = entry.get("address", "")
        name = entry.get("name", "N/A")
        max_amount = entry.get("max_amount_usd", "default")
        print(f"{addr:<44} {name:<20} {max_amount}")


def add_address(address: str, name: str = "", max_amount: float = None):
    """Add address to whitelist."""
    whitelist = load_whitelist()
    
    # Check if already exists
    address_lower = address.lower()
    for entry in whitelist.get("addresses", []):
        if entry.get("address", "").lower() == address_lower:
            print(f"Address {address} already in whitelist.")
            return
    
    # Add new entry
    entry = {
        "address": address,
        "name": name,
        "added_at": __import__("datetime").datetime.utcnow().isoformat()
    }
    
    if max_amount is not None:
        entry["max_amount_usd"] = max_amount
    
    whitelist.setdefault("addresses", []).append(entry)
    save_whitelist(whitelist)
    
    print(f"✅ Added {address} to whitelist")
    if name:
        print(f"   Name: {name}")
    if max_amount is not None:
        print(f"   Max Amount: ${max_amount}")


def remove_address(address: str):
    """Remove address from whitelist."""
    whitelist = load_whitelist()
    
    address_lower = address.lower()
    original_count = len(whitelist.get("addresses", []))
    
    whitelist["addresses"] = [
        entry for entry in whitelist.get("addresses", [])
        if entry.get("address", "").lower() != address_lower
    ]
    
    if len(whitelist["addresses"]) == original_count:
        print(f"Address {address} not found in whitelist.")
        return
    
    save_whitelist(whitelist)
    print(f"✅ Removed {address} from whitelist")


def enable_whitelist():
    """Enable whitelist checking."""
    whitelist = load_whitelist()
    whitelist["enabled"] = True
    save_whitelist(whitelist)
    print("✅ Whitelist enabled")


def disable_whitelist():
    """Disable whitelist checking (not recommended)."""
    whitelist = load_whitelist()
    whitelist["enabled"] = False
    save_whitelist(whitelist)
    print("⚠️ Whitelist DISABLED - All addresses allowed")


def main():
    parser = argparse.ArgumentParser(description="Manage Safe Vault whitelist")
    parser.add_argument("--list", action="store_true", help="List whitelisted addresses")
    parser.add_argument("--add", metavar="ADDRESS", help="Add address to whitelist")
    parser.add_argument("--remove", metavar="ADDRESS", help="Remove address from whitelist")
    parser.add_argument("--name", default="", help="Name for the address")
    parser.add_argument("--max-amount", type=float, help="Maximum amount in USD")
    parser.add_argument("--enable", action="store_true", help="Enable whitelist")
    parser.add_argument("--disable", action="store_true", help="Disable whitelist")
    
    args = parser.parse_args()
    
    if args.list:
        list_whitelist()
    elif args.add:
        add_address(args.add, args.name, args.max_amount)
    elif args.remove:
        remove_address(args.remove)
    elif args.enable:
        enable_whitelist()
    elif args.disable:
        disable_whitelist()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()