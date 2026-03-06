#!/usr/bin/env python3
"""
List all positions in the portfolio.
Usage: python3 list_positions.py
"""
from utils import load_positions, format_currency


def list_positions():
    """Display all positions in the portfolio."""
    positions = load_positions()

    if not positions:
        print("No positions found. Add positions using add_position.py")
        return

    print("\n" + "=" * 80)
    print(f"{'Symbol':<10} {'Name':<25} {'Buy Price':<12} {'Quantity':<10} {'Cost':<15}")
    print("=" * 80)

    total_cost = 0

    for pos in positions:
        cost = pos['buy_price'] * pos['quantity']
        total_cost += cost

        symbol = pos['symbol'].upper()
        name = pos['name'][:24] if len(pos['name']) > 24 else pos['name']
        buy_price = f"${pos['buy_price']:,.2f}"
        quantity = f"{pos['quantity']:.2f}"
        cost_str = f"${cost:,.2f}"

        print(f"{symbol:<10} {name:<25} {buy_price:<12} {quantity:<10} {cost_str:<15}")

    print("=" * 80)
    print(f"{'':<47} {'Total:':<10} ${total_cost:,.2f}")
    print("=" * 80)
    print(f"\nTotal positions: {len(positions)}")


if __name__ == "__main__":
    list_positions()
