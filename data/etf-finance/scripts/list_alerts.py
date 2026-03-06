#!/usr/bin/env python3
"""
List all price alerts.
Usage: python3 list_alerts.py
"""
from utils import load_alerts, get_price


def list_alerts():
    """Display all price alerts."""
    alerts = load_alerts()

    if not alerts:
        print("No alerts found. Add alerts using add_alert.py")
        return

    # Separate active and triggered alerts
    active_alerts = [a for a in alerts if not a.get('triggered', False)]
    triggered_alerts = [a for a in alerts if a.get('triggered', False)]

    print("\n" + "=" * 80)

    if active_alerts:
        print("ACTIVE ALERTS:")
        print("-" * 80)
        for alert in active_alerts:
            symbol = alert['symbol'].upper()
            condition_text = ">" if alert['condition'] == 'price_up' else "<"
            target = f"${alert['target_price']:.2f}"
            created = alert['created_at'][:10]

            # Get current price
            current = get_price(symbol)
            current_str = f"${current:.2f}" if current else "N/A"

            print(f"  {symbol} {condition_text} {target} | Current: {current_str} | Created: {created}")

    if triggered_alerts:
        print("\nTRIGGERED ALERTS:")
        print("-" * 80)
        for alert in triggered_alerts:
            symbol = alert['symbol'].upper()
            condition_text = ">" if alert['condition'] == 'price_up' else "<"
            target = f"${alert['target_price']:.2f}"
            triggered = alert.get('triggered_at', 'N/A')[:10]

            print(f"  {symbol} {condition_text} {target} | Triggered: {triggered}")

    print("=" * 80)
    print(f"Active alerts: {len(active_alerts)}")
    print(f"Triggered alerts: {len(triggered_alerts)}")


if __name__ == "__main__":
    list_alerts()
