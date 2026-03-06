#!/usr/bin/env python3
"""
Portfolio management via Hummingbot API.

Usage:
    python scripts/portfolio.py state [--account ACCOUNT]
    python scripts/portfolio.py value
    python scripts/portfolio.py distribution
    python scripts/portfolio.py token TOKEN
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def cmd_state(args):
    async with client() as c:
        state = await c.portfolio.get_state()
        rows = []
        for account, exchanges in state.items():
            if args.account and account != args.account:
                continue
            for exchange, tokens in exchanges.items():
                for token_data in tokens:
                    rows.append({
                        "account": account,
                        "exchange": exchange,
                        "token": token_data.get("token", "?"),
                        "balance": f"{token_data.get('balance', 0):.6f}",
                        "value_usd": f"${token_data.get('value', 0):,.2f}",
                    })
        if rows:
            print_table(rows, ["account", "exchange", "token", "balance", "value_usd"])
        else:
            print("No balances found.")


async def cmd_value(args):
    async with client() as c:
        total = await c.portfolio.get_total_value()
        print(f"Total portfolio value: ${total:,.2f}")


async def cmd_distribution(args):
    async with client() as c:
        dist = await c.portfolio.get_distribution()
        if not dist:
            print("No holdings found.")
            return
        rows = sorted(
            [{"token": t, "percent": f"{p:.2f}%"} for t, p in dist.items()],
            key=lambda x: float(x["percent"].rstrip("%")),
            reverse=True,
        )
        print_table(rows, ["token", "percent"])


async def cmd_token(args):
    async with client() as c:
        holdings = await c.portfolio.get_token_holdings(args.token.upper())
        if not holdings:
            print(f"No holdings found for {args.token.upper()}")
            return
        for item in holdings:
            print(f"  {item.get('account')} / {item.get('exchange')}: "
                  f"{item.get('balance', 0):.6f} {args.token.upper()} "
                  f"(${item.get('value', 0):,.2f})")


COMMANDS = {
    "state": cmd_state,
    "value": cmd_value,
    "distribution": cmd_distribution,
    "token": cmd_token,
}


def main():
    parser = argparse.ArgumentParser(description="Portfolio management")
    sub = parser.add_subparsers(dest="command")

    p_state = sub.add_parser("state", help="Full portfolio state")
    p_state.add_argument("--account", help="Filter by account name")

    sub.add_parser("value", help="Total portfolio value in USD")
    sub.add_parser("distribution", help="Token distribution (%)")

    p_token = sub.add_parser("token", help="Holdings for a specific token")
    p_token.add_argument("token", help="Token symbol (e.g. BTC)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(COMMANDS[args.command](args))


if __name__ == "__main__":
    main()
