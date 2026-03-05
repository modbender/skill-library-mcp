#!/usr/bin/env python3
"""
Update current prices for all positions.
Usage: python3 update_prices.py
"""
from datetime import datetime
from utils import load_positions, save_positions, get_price


def update_prices():
    """Update current prices for all positions."""
    positions = load_positions()

    if not positions:
        print("No positions to update.")
        return

    print(f"\nUpdating prices for {len(positions)} position(s)...")
    print("-" * 80)

    updated_count = 0
    failed_count = 0

    for pos in positions:
        symbol = pos['symbol'].upper()

        # Get current price
        current_price = get_price(symbol)

        if current_price is None:
            print(f"  {symbol}: Failed to fetch price")
            failed_count += 1
            continue

        old_price = pos.get('current_price', 'N/A')
        pos['current_price'] = current_price
        pos['last_updated'] = datetime.now().isoformat() + 'Z'

        # Calculate change if we have old price
        if old_price != 'N/A':
            change = current_price - old_price
            change_pct = (change / old_price) * 100 if old_price > 0 else 0
            change_sign = "+" if change >= 0 else ""
            print(f"  {symbol}: ${current_price:.2f} (was ${old_price:.2f}, {change_sign}{change:.2f}, {change_sign}{change_pct:.2f}%)")
        else:
            print(f"  {symbol}: ${current_price:.2f}")

        updated_count += 1

    # Save updated positions
    save_positions(positions)

    print("-" * 80)
    print(f"\nUpdated: {updated_count} position(s)")
    if failed_count > 0:
        print(f"Failed: {failed_count} position(s)")


if __name__ == "__main__":
    update_prices()
