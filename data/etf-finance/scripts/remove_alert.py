#!/usr/bin/env python3
"""
Remove alerts for a symbol.
Usage: python3 remove_alert.py <symbol>
"""
import sys
from utils import load_alerts, save_alerts, find_alert


def remove_alert(symbol):
    """Remove alerts for a symbol."""
    alerts = load_alerts()

    # Find alerts for this symbol
    symbol_alerts = find_alert(symbol, alerts)

    if not symbol_alerts:
        print(f"No alerts found for {symbol}")
        return False

    # Display alerts
    print(f"\nFound {len(symbol_alerts)} alert(s) for {symbol}:")
    for i, alert in enumerate(symbol_alerts, 1):
        condition_text = "above" if alert['condition'] == 'price_up' else "below"
        status = "Triggered" if alert.get('triggered', False) else "Active"
        print(f"  {i}. {condition_text} ${alert['target_price']:.2f} - {status}")

    # Confirm removal
    confirm = input("\nRemove all alerts for this symbol? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return False

    # Remove alerts
    alerts = [a for a in alerts if a['symbol'].upper() != symbol.upper()]
    save_alerts(alerts)

    print(f"Removed {len(symbol_alerts)} alert(s) for {symbol}")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 remove_alert.py <symbol>")
        print("\nExample:")
        print("  python3 remove_alert.py SPY")
        sys.exit(1)

    symbol = sys.argv[1]
    remove_alert(symbol)
