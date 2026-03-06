#!/usr/bin/env python3
"""
Add price alert for a symbol.
Usage: python3 add_alert.py <symbol> <target_price> <condition>
Condition: 'price_up' (above) or 'price_down' (below)
"""
import sys
from datetime import datetime
from utils import load_alerts, save_alerts, get_price, find_alert


def add_alert(symbol, target_price, condition):
    """Add a price alert for a symbol."""
    alerts = load_alerts()

    # Validate condition
    if condition not in ['price_up', 'price_down']:
        print("Error: condition must be 'price_up' or 'price_down'")
        return False

    # Validate target price
    try:
        target_price = float(target_price)
    except ValueError:
        print("Error: target_price must be a number")
        return False

    # Check for existing alerts
    existing = find_alert(symbol, alerts)
    for alert in existing:
        if alert['target_price'] == target_price and alert['condition'] == condition and not alert.get('triggered', False):
            print(f"Alert already exists: {symbol} ${target_price:.2f} ({condition})")
            return False

    # Get current price for reference
    current_price = get_price(symbol)
    if current_price is None:
        print(f"Warning: Could not fetch current price for {symbol}")

    # Create alert
    alert = {
        'symbol': symbol.upper(),
        'target_price': target_price,
        'condition': condition,
        'created_at': datetime.now().isoformat() + 'Z',
        'triggered': False,
        'triggered_at': None
    }

    # Add to alerts
    alerts.append(alert)
    save_alerts(alerts)

    # Display result
    condition_text = "above" if condition == 'price_up' else "below"
    print(f"\nAdded alert for {symbol.upper()}")
    print(f"  Alert when price goes {condition_text} ${target_price:.2f}")
    if current_price:
        print(f"  Current price: ${current_price:.2f}")

    return True


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python3 add_alert.py <symbol> <target_price> <condition>")
        print("\nCondition options:")
        print("  price_up - Alert when price goes above target")
        print("  price_down - Alert when price goes below target")
        print("\nExample:")
        print("  python3 add_alert.py SPY 160.00 price_up")
        print("  python3 add_alert.py SPY 140.00 price_down")
        sys.exit(1)

    symbol = sys.argv[1]
    target_price = sys.argv[2]
    condition = sys.argv[3]

    add_alert(symbol, target_price, condition)
