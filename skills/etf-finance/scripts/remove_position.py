#!/usr/bin/env python3
"""
Remove position from portfolio.
Usage: python3 remove_position.py <symbol>
"""
import sys
from utils import load_positions, save_positions, find_position


def remove_position(symbol):
    """Remove a position from the portfolio."""
    positions = load_positions()

    # Find the position
    existing = find_position(symbol, positions)
    if not existing:
        print(f"No position found for {symbol}")
        return False

    # Confirm removal
    print(f"Position found: {existing['symbol']} - {existing['name']}")
    print(f"  Buy Price: ${existing['buy_price']:.2f}")
    print(f"  Quantity: {existing['quantity']}")
    print(f"  Cost: ${existing['buy_price'] * existing['quantity']:,.2f}")

    confirm = input("\nRemove this position? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False

    # Remove the position
    positions = [p for p in positions if p['symbol'].upper() != symbol.upper()]
    save_positions(positions)

    print(f"Removed position: {symbol}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remove_position.py <symbol>")
        print("\nExample:")
        print("  python3 remove_position.py SPY")
        sys.exit(1)

    symbol = sys.argv[1]
    remove_position(symbol)
