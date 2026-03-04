#!/usr/bin/env python3
"""
Add position to portfolio.
Usage: python3 add_position.py <symbol> <buy_price> <quantity> [name]
"""
import sys
from datetime import datetime
from utils import load_positions, save_positions, find_position, get_price


def add_position(symbol, buy_price, quantity, name=None):
    """Add a new position to the portfolio."""
    # Load existing positions
    positions = load_positions()

    # Check if position already exists
    existing = find_position(symbol, positions)
    if existing:
        print(f"Position for {symbol} already exists:")
        print(f"  Buy Price: ${existing['buy_price']:.2f}")
        print(f"  Quantity: {existing['quantity']}")
        print(f"Use update_position.py to modify existing positions.")
        return False

    # Get current price
    current_price = get_price(symbol)
    if current_price is None:
        print(f"Warning: Could not fetch current price for {symbol}")

    # Validate inputs
    try:
        buy_price = float(buy_price)
        quantity = float(quantity)
    except ValueError:
        print("Error: buy_price and quantity must be numbers")
        return False

    if buy_price <= 0 or quantity <= 0:
        print("Error: buy_price and quantity must be positive")
        return False

    # If name not provided, use the symbol
    if not name:
        name = symbol

    # Create position
    position = {
        'symbol': symbol.upper(),
        'name': name,
        'buy_price': buy_price,
        'quantity': quantity,
        'buy_date': datetime.now().strftime('%Y-%m-%d'),
        'current_price': current_price,
        'last_updated': datetime.now().isoformat() + 'Z'
    }

    # Add to positions
    positions.append(position)
    save_positions(positions)

    # Display result
    print(f"\nAdded position: {symbol.upper()} - {name}")
    print(f"  Buy Price: ${buy_price:.2f}")
    print(f"  Quantity: {quantity}")
    print(f"  Cost: ${buy_price * quantity:,.2f}")
    if current_price:
        print(f"  Current Price: ${current_price:.2f}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 add_position.py <symbol> <buy_price> <quantity> [name]")
        print("\nExample:")
        print("  python3 add_position.py SPY 150.50 100 \"S&P 500 ETF\"")
        sys.exit(1)

    symbol = sys.argv[1]
    buy_price = sys.argv[2]
    quantity = sys.argv[3]
    name = sys.argv[4] if len(sys.argv) > 4 else None

    add_position(symbol, buy_price, quantity, name)
