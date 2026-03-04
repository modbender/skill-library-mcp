#!/usr/bin/env python3
"""
Check price alerts and notify if triggered.
Usage: python3 check_alerts.py
"""
from datetime import datetime
from utils import load_alerts, save_alerts, get_price


def check_alerts():
    """Check all alerts and trigger if conditions are met."""
    alerts = load_alerts()
    positions = load_alerts()  # Reusing for alert storage

    if not alerts:
        print("No alerts to check.")
        return

    active_alerts = [a for a in alerts if not a.get('triggered', False)]

    if not active_alerts:
        print("No active alerts to check.")
        return

    print(f"\nChecking {len(active_alerts)} active alert(s)...")
    print("-" * 80)

    triggered_count = 0

    for alert in active_alerts:
        symbol = alert['symbol'].upper()
        target_price = alert['target_price']
        condition = alert['condition']

        # Get current price
        current_price = get_price(symbol)

        if current_price is None:
            print(f"  {symbol}: Could not fetch price")
            continue

        # Check if alert should trigger
        should_trigger = False
        condition_text = ""

        if condition == 'price_up' and current_price >= target_price:
            should_trigger = True
            condition_text = f"Price went above ${target_price:.2f}"
        elif condition == 'price_down' and current_price <= target_price:
            should_trigger = True
            condition_text = f"Price went below ${target_price:.2f}"

        if should_trigger:
            # Mark as triggered
            alert['triggered'] = True
            alert['triggered_at'] = datetime.now().isoformat() + 'Z'
            alert['triggered_price'] = current_price

            print(f"\n  ALERT TRIGGERED: {symbol}")
            print(f"  {condition_text}")
            print(f"  Current price: ${current_price:.2f}")
            print(f"  Target price: ${target_price:.2f}")

            triggered_count += 1
        else:
            condition_text = "above" if condition == 'price_up' else "below"
            diff = abs(current_price - target_price)
            print(f"  {symbol}: ${current_price:.2f} (target: ${target_price:.2f} {condition_text}, diff: ${diff:.2f})")

    # Save updated alerts
    if triggered_count > 0:
        save_alerts(alerts)
        print("\n" + "-" * 80)
        print(f"\n{triggered_count} alert(s) triggered!")
    else:
        print("\n" + "-" * 80)
        print("\nNo alerts triggered.")


if __name__ == "__main__":
    check_alerts()
