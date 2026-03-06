#!/usr/bin/env python3
"""
Add and manage wallets via hummingbot-api Gateway.

Usage:
    # List existing wallets
    python add_wallet.py list

    # Add wallet by private key
    python add_wallet.py add --private-key <BASE58_KEY>

    # Add wallet by private key (prompted, not visible in shell history)
    python add_wallet.py add

    # Get wallet balances
    python add_wallet.py balances --address <WALLET_ADDRESS>

    # Get wallet balances for all tokens
    python add_wallet.py balances --address <WALLET_ADDRESS> --all

Environment:
    HUMMINGBOT_API_URL - API base URL (default: http://localhost:8000)
    API_USER - API username (default: admin)
    API_PASS - API password (default: admin)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import base64


def load_env():
    """Load environment from .env files."""
    for path in ["hummingbot-api/.env", os.path.expanduser("~/.hummingbot/.env"), ".env"]:
        if os.path.exists(path):
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
            break


def get_api_config():
    """Get API configuration from environment."""
    load_env()
    return {
        "url": os.environ.get("HUMMINGBOT_API_URL", "http://localhost:8000"),
        "user": os.environ.get("API_USER", "admin"),
        "password": os.environ.get("API_PASS", "admin"),
    }


def api_request(method: str, endpoint: str, data=None) -> dict:
    """Make authenticated API request."""
    config = get_api_config()
    url = f"{config['url']}{endpoint}"

    credentials = base64.b64encode(f"{config['user']}:{config['password']}".encode()).decode()
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json",
    }

    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"Error: HTTP {e.code} - {e.reason}", file=sys.stderr)
        if error_body:
            try:
                print(json.dumps(json.loads(error_body), indent=2), file=sys.stderr)
            except json.JSONDecodeError:
                print(error_body, file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Error: Cannot connect to API at {config['url']}: {e.reason}", file=sys.stderr)
        sys.exit(1)


def list_wallets(args):
    """List wallets connected to Gateway."""
    result = api_request("GET", "/accounts/gateway/wallets")

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Result is a list directly from the API
    wallets = result if isinstance(result, list) else result.get("wallets", [])

    if not wallets:
        print("No wallets found.")
        print("")
        print("Add one with:")
        print("  python add_wallet.py add --private-key <BASE58_KEY>")
        return

    print("Connected Wallets")
    print("-" * 60)

    for w in wallets:
        if isinstance(w, dict):
            chain = w.get("chain", "")
            addresses = w.get("walletAddresses", [w.get("address", "")])
            if isinstance(addresses, str):
                addresses = [addresses]
            for addr in addresses:
                print(f"  [{chain}] {addr}")
        else:
            print(f"  {w}")


def add_wallet(args):
    """Add a wallet to Gateway."""
    private_key = args.private_key

    # Prompt for private key if not provided (avoids shell history exposure)
    if not private_key:
        try:
            import getpass
            private_key = getpass.getpass("Enter private key (base58): ")
        except (ImportError, EOFError):
            print("Error: --private-key is required in non-interactive mode", file=sys.stderr)
            sys.exit(1)

    if not private_key:
        print("Error: Private key cannot be empty", file=sys.stderr)
        sys.exit(1)

    data = {
        "chain": args.chain,
        "private_key": private_key,
    }

    print(f"Adding {args.chain} wallet...")
    result = api_request("POST", "/accounts/gateway/add-wallet", data)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    address = result.get("address", result.get("wallet", ""))
    if address:
        print(f"✓ Wallet added successfully")
        print(f"  Chain: {args.chain}")
        print(f"  Address: {address}")
    else:
        print(f"Response: {result}")


def get_balances(args):
    """Get wallet balances via portfolio state."""
    params = {
        "refresh": True,
        "skip_gateway": False,
    }

    if args.account:
        params["account_names"] = [args.account]

    result = api_request("POST", "/portfolio/state", params)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Portfolio state returns: {account_name: {connector_name: [token_balances]}}
    if not result:
        print("No portfolio data found.")
        return

    print("Wallet Balances")
    print("-" * 50)

    for account_name, connectors in result.items():
        print(f"\nAccount: {account_name}")
        for connector_name, tokens in connectors.items():
            # Filter to show only gateway connectors if address is specified
            if args.address and args.address not in connector_name:
                continue
            print(f"  Connector: {connector_name}")
            if isinstance(tokens, list):
                for token in tokens:
                    if isinstance(token, dict):
                        symbol = token.get("token", token.get("symbol", "?"))
                        balance = token.get("units", token.get("balance", token.get("amount", 0)))
                        value = token.get("value", token.get("value_usd", ""))
                        if float(balance) > 0 or args.all:
                            value_str = f" (${value:.2f})" if value else ""
                            print(f"    {symbol}: {balance}{value_str}")
            elif isinstance(tokens, dict):
                for symbol, balance in tokens.items():
                    if float(balance) > 0 or args.all:
                        print(f"    {symbol}: {balance}")


def main():
    parser = argparse.ArgumentParser(description="Add and manage wallets via hummingbot-api Gateway")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # list command
    list_parser = subparsers.add_parser("list", help="List connected wallets")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_parser.set_defaults(func=list_wallets)

    # add command
    add_parser = subparsers.add_parser("add", help="Add a wallet")
    add_parser.add_argument("--private-key", help="Private key (base58). Omit to be prompted securely.")
    add_parser.add_argument("--chain", default="solana", help="Blockchain (default: solana)")
    add_parser.add_argument("--json", action="store_true", help="Output as JSON")
    add_parser.set_defaults(func=add_wallet)

    # balances command
    bal_parser = subparsers.add_parser("balances", help="Get wallet balances")
    bal_parser.add_argument("--account", default="master_account", help="Account name (default: master_account)")
    bal_parser.add_argument("--address", help="Filter by wallet address (optional)")
    bal_parser.add_argument("--all", action="store_true", help="Show zero balances too")
    bal_parser.add_argument("--json", action="store_true", help="Output as JSON")
    bal_parser.set_defaults(func=get_balances)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
