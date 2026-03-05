#!/usr/bin/env python3
"""
Get current price for a symbol.
Usage: python3 get_price.py <symbol>
"""
import sys
from utils import get_price


def get_price_cli(symbol):
    """Get and display current price for a symbol."""
    price = get_price(symbol)

    if price is None:
        print(f"Could not fetch price for {symbol}")
        return False

    print(f"{symbol.upper()}: ${price:.2f}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 get_price.py <symbol>")
        print("\nExample:")
        print("  python3 get_price.py SPY")
        sys.exit(1)

    symbol = sys.argv[1]
    get_price_cli(symbol)
