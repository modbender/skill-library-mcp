#!/usr/bin/env python3
"""
Display asset balances across connected exchanges.

Usage:
    # Show all balances
    python balance.py

    # Show balances for a specific connector
    python balance.py binance

    # Show only non-zero balances
    python balance.py --non-zero

    # Show total portfolio value
    python balance.py --total
"""

import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def show_balances(connector: str = None, non_zero: bool = False, show_total: bool = False):
    """Display asset balances."""
    async with client() as c:
        if show_total:
            total = await c.portfolio.get_total_value()
            print(f"Total Portfolio Value: ${total:,.2f}")
            return

        # Get portfolio state
        state = await c.portfolio.get_state()

        if not state:
            print("No balances found. Connect to an exchange first with: python connect.py <exchange> -i")
            return

        rows = []
        total_value = 0

        for account, exchanges in state.items():
            for exchange, tokens in exchanges.items():
                # Filter by connector if specified
                if connector and exchange != connector:
                    continue

                for token_data in tokens:
                    balance = token_data.get("balance", 0)
                    value = token_data.get("value", 0)

                    # Skip zero balances if requested
                    if non_zero and balance == 0:
                        continue

                    rows.append({
                        "exchange": exchange,
                        "token": token_data.get("token", "?"),
                        "balance": f"{balance:.6f}",
                        "value_usd": f"${value:,.2f}",
                    })
                    total_value += value

        if not rows:
            if connector:
                print(f"No balances found for {connector}")
            else:
                print("No balances found")
            return

        # Sort by value descending
        rows.sort(key=lambda x: float(x["value_usd"].replace("$", "").replace(",", "")), reverse=True)

        print_table(rows, ["exchange", "token", "balance", "value_usd"])

        if total_value > 0:
            print(f"\nTotal: ${total_value:,.2f}")


def main():
    parser = argparse.ArgumentParser(description="Display asset balances")
    parser.add_argument("connector", nargs="?", help="Filter by connector")
    parser.add_argument("--non-zero", action="store_true", help="Show only non-zero balances")
    parser.add_argument("--total", action="store_true", help="Show only total portfolio value")
    args = parser.parse_args()

    try:
        asyncio.run(show_balances(args.connector, args.non_zero, args.total))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
