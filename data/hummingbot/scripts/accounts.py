#!/usr/bin/env python3
"""
Account and credential management via Hummingbot API.

Usage:
    python scripts/accounts.py list
    python scripts/accounts.py add <account_name>
    python scripts/accounts.py credentials <account_name> [<connector>]
    python scripts/accounts.py remove-credentials <account_name> <connector>
    python scripts/accounts.py connectors
"""

import asyncio
import argparse
import getpass
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def cmd_list(args):
    async with client() as c:
        accounts = await c.accounts.list_accounts()
        if not accounts:
            print("No accounts found.")
            return
        for a in accounts:
            print(f"  {a}")


async def cmd_add(args):
    async with client() as c:
        await c.accounts.add_account(args.account_name)
        print(f"✓ Account '{args.account_name}' created")


async def cmd_credentials(args):
    async with client() as c:
        if args.connector:
            # Add credentials for this account/connector
            config_map = await c.connectors.get_config_map(args.connector)
            fields = config_map if isinstance(config_map, list) else list(config_map.keys())
            print(f"Enter credentials for {args.connector} on account '{args.account_name}':")
            credentials = {}
            for field in fields:
                is_secret = any(k in field.lower() for k in ["secret", "key", "pass", "token"])
                if is_secret:
                    value = getpass.getpass(f"  {field}: ")
                else:
                    value = input(f"  {field}: ")
                credentials[field] = value

            await c.accounts.add_credential(args.account_name, args.connector, credentials)
            print(f"✓ Credentials saved for {args.connector} on '{args.account_name}'")
        else:
            # List credentials for this account
            result = await c.accounts.list_account_credentials(args.account_name)
            if not result:
                print(f"No credentials configured for '{args.account_name}'")
                return
            for conn in result:
                print(f"  {conn}")


async def cmd_remove_credentials(args):
    confirm = input(f"Remove {args.connector} credentials from '{args.account_name}'? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return
    async with client() as c:
        await c.accounts.delete_credential(args.account_name, args.connector)
        print(f"✓ Credentials removed for {args.connector} on '{args.account_name}'")


async def cmd_connectors(args):
    async with client() as c:
        connectors = await c.connectors.list_connectors()
        if not connectors:
            print("No connectors available.")
            return
        if isinstance(connectors, list):
            for conn in sorted(connectors):
                name = conn if isinstance(conn, str) else conn.get("name", str(conn))
                print(f"  {name}")
        else:
            print(json.dumps(connectors, indent=2))


COMMANDS = {
    "list": cmd_list,
    "add": cmd_add,
    "credentials": cmd_credentials,
    "remove-credentials": cmd_remove_credentials,
    "connectors": cmd_connectors,
}


def main():
    parser = argparse.ArgumentParser(description="Account management")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list", help="List all accounts")

    p_add = sub.add_parser("add", help="Create a new account")
    p_add.add_argument("account_name")

    p_creds = sub.add_parser("credentials", help="View or add exchange credentials")
    p_creds.add_argument("account_name", help="Account name")
    p_creds.add_argument("connector", nargs="?", help="Connector to add credentials for (omit to list)")

    p_rm = sub.add_parser("remove-credentials", help="Remove exchange credentials")
    p_rm.add_argument("account_name")
    p_rm.add_argument("connector")

    sub.add_parser("connectors", help="List all available connectors")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(COMMANDS[args.command](args))


if __name__ == "__main__":
    main()
