#!/usr/bin/env python3
"""
List available exchanges and add API keys.

Usage:
    # List all available connectors
    python connect.py

    # List connectors with connection status
    python connect.py --status

    # Add API keys for an exchange
    python connect.py binance --api-key YOUR_KEY --secret-key YOUR_SECRET

    # Add API keys for exchange requiring passphrase
    python connect.py kucoin --api-key YOUR_KEY --secret-key YOUR_SECRET --passphrase YOUR_PASS

    # Remove credentials for an exchange
    python connect.py binance --remove
"""

import argparse
import asyncio
import getpass
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client


async def list_connectors(show_status: bool = False):
    """List all available connectors."""
    async with client() as c:
        connectors = await c.connectors.list_connectors()

        if show_status:
            # Get accounts to check which connectors have credentials
            accounts = await c.accounts.list_accounts()
            connected = set()
            for account in accounts:
                try:
                    creds = await c.accounts.list_account_credentials(account)
                    for cred in creds:
                        connected.add(cred)
                except Exception:
                    pass

            print("Available Connectors:")
            print("-" * 50)
            for conn in sorted(connectors):
                status = "[connected]" if conn in connected else ""
                print(f"  {conn:30} {status}")
        else:
            print("Available Connectors:")
            print("-" * 50)
            for conn in sorted(connectors):
                print(f"  {conn}")

        print(f"\nTotal: {len(connectors)} connectors")


async def add_credentials(connector: str, api_key: str = None, secret_key: str = None,
                         passphrase: str = None, interactive: bool = False):
    """Add API credentials for a connector."""
    async with client() as c:
        # Get or create default account
        accounts = await c.accounts.list_accounts()
        if not accounts:
            await c.accounts.add_account("master_account")
            account_name = "master_account"
            print(f"Created account: master_account")
        else:
            account_name = accounts[0]
            print(f"Using account: {account_name}")

        if interactive:
            # Get config map to know what fields are needed
            try:
                config_map = await c.connectors.get_config_map(connector)
                fields = list(config_map.keys()) if isinstance(config_map, dict) else config_map
            except Exception:
                fields = ["api_key", "secret_key"]

            print(f"\nEnter credentials for {connector}:")
            credentials = {}
            for field in fields:
                is_secret = any(k in field.lower() for k in ["secret", "key", "pass", "token"])
                if is_secret:
                    value = getpass.getpass(f"  {field}: ")
                else:
                    value = input(f"  {field}: ")
                if value:
                    credentials[field] = value
        else:
            # Build credentials from arguments
            credentials = {}
            if api_key:
                credentials["api_key"] = api_key
            if secret_key:
                credentials["secret_key"] = secret_key
            if passphrase:
                credentials["passphrase"] = passphrase

        if not credentials:
            print("No credentials provided")
            return

        # Add credentials
        await c.accounts.add_credential(account_name, connector, credentials)
        print(f"Added credentials for {connector}")


async def remove_credentials(connector: str):
    """Remove API credentials for a connector."""
    async with client() as c:
        accounts = await c.accounts.list_accounts()
        if not accounts:
            print("No accounts found")
            return

        account_name = accounts[0]
        await c.accounts.delete_credential(account_name, connector)
        print(f"Removed credentials for {connector}")


def main():
    parser = argparse.ArgumentParser(description="List exchanges and manage API keys")
    parser.add_argument("connector", nargs="?", help="Connector name to configure")
    parser.add_argument("--status", action="store_true", help="Show connection status")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--secret-key", help="Secret key")
    parser.add_argument("--passphrase", help="Passphrase (for exchanges that require it)")
    parser.add_argument("--remove", action="store_true", help="Remove credentials")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    try:
        if args.connector:
            if args.remove:
                asyncio.run(remove_credentials(args.connector))
            elif args.api_key or args.secret_key or args.interactive:
                asyncio.run(add_credentials(
                    args.connector,
                    api_key=args.api_key,
                    secret_key=args.secret_key,
                    passphrase=args.passphrase,
                    interactive=args.interactive
                ))
            else:
                print(f"To add credentials for {args.connector}:")
                print(f"  python connect.py {args.connector} --api-key KEY --secret-key SECRET")
                print(f"  python connect.py {args.connector} -i  # interactive mode")
        else:
            asyncio.run(list_connectors(args.status))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
