#!/usr/bin/env python3
"""
Show portfolio summary with profit/loss calculation.
Usage: python3 portfolio_summary.py [--update]
"""
import sys
from datetime import datetime
from utils import (
    load_positions, load_alerts, get_price, format_currency,
    format_percentage, calculate_pnl, save_positions
)


def portfolio_summary(update_prices=False):
    """Display portfolio summary with profit/loss."""
    positions = load_positions()

    if not positions:
        print("No positions found. Add positions using add_position.py")
        return

    print("\n" + "=" * 100)
    print(f"{'Symbol':<10} {'Name':<25} {'Buy Price':<12} {'Current':<12} {'Quantity':<10}")
    print(f"{'Cost':<15} {'Value':<15} {'P/L ($)':<12} {'P/L (%)':<12}")
    print("=" * 100)

    total_cost = 0
    total_value = 0
    total_pnl = 0

    for pos in positions:
        symbol = pos['symbol'].upper()
        name = pos['name'][:24] if len(pos['name']) > 24 else pos['name']

        # Get current price
        if update_prices:
            current_price = get_price(symbol)
            if current_price:
                pos['current_price'] = current_price
                pos['last_updated'] = datetime.now().isoformat() + 'Z'
        else:
            current_price = pos.get('current_price', pos.get('buy_price'))

        # Calculate P/L
        pnl = calculate_pnl(pos, current_price)

        cost = pnl['cost']
        value = pnl['value']
        pnl_amount = pnl['pnl']
        pnl_pct = pnl['pnl_pct']

        # Update totals
        total_cost += cost
        total_value += value
        total_pnl += pnl_amount

        # Format output
        buy_price = f"${pos['buy_price']:,.2f}"
        current_str = f"${current_price:,.2f}" if current_price else "N/A"
        quantity = f"{pos['quantity']:.2f}"
        cost_str = f"${cost:,.2f}"
        value_str = f"${value:,.2f}" if value else "N/A"
        pnl_str = format_currency(pnl_amount)
        pnl_pct_str = format_percentage(pnl_pct)

        # Color P/L (positive=green-ish, negative=red-ish)
        if pnl_amount and pnl_amount > 0:
            pnl_pct_str = f"+{pnl_pct:.2f}%"
        elif pnl_amount and pnl_amount < 0:
            pnl_pct_str = f"{pnl_pct:.2f}%"

        print(f"{symbol:<10} {name:<25} {buy_price:<12} {current_str:<12} {quantity:<10}")
        print(f"{cost_str:<15} {value_str:<15} {pnl_str:<12} {pnl_pct_str:<12}")
        print("-" * 100)

    # Save updated positions if requested
    if update_prices:
        save_positions(positions)

    # Show totals
    print("=" * 100)
    print(f"{'':<67} {'Total:':<15} ${total_cost:,.2f}")
    print(f"{'':<67} {'Value:':<15} ${total_value:,.2f}")
    print(f"{'':<67} {'P/L ($):':<15} {format_currency(total_pnl)}")
    total_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0
    total_pct_str = f"+{total_pct:.2f}%" if total_pct >= 0 else f"{total_pct:.2f}%"
    print(f"{'':<67} {'P/L (%):':<15} {total_pct_str}")
    print("=" * 100)
    print(f"\nTotal positions: {len(positions)}")

    # Show active alerts
    alerts = load_alerts()
    active_alerts = [a for a in alerts if not a.get('triggered', False)]
    if active_alerts:
        print(f"\nActive alerts: {len(active_alerts)}")
        for alert in active_alerts:
            print(f"  - {alert['symbol']}: ${alert['target_price']:.2f} ({alert['condition']})")


if __name__ == "__main__":
    update = '--update' in sys.argv or '-u' in sys.argv
    portfolio_summary(update_prices=update)
