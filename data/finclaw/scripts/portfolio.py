#!/usr/bin/env python3
"""Portfolio management: add, sell, remove, list, summary."""

import sys, os, json, argparse
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.formatters import detect_asset_type, fmt_price


def add_position(symbol, shares, price, name=None, fees=0, transaction_date=None, notes=None):
    symbol = symbol.upper()
    asset_type = detect_asset_type(symbol)
    currency = "TRY" if asset_type == "stock_bist" else "USD"
    tx_date = transaction_date or date.today().isoformat()
    conn = get_connection()
    try:
        existing = conn.execute("SELECT id FROM positions WHERE symbol=?", (symbol,)).fetchone()
        if existing:
            pos_id = existing["id"]
        else:
            pos_id = conn.execute("INSERT INTO positions (symbol, name, asset_type, currency, notes) VALUES (?, ?, ?, ?, ?)",
                                  (symbol, name or symbol, asset_type, currency, notes)).lastrowid
        conn.execute("INSERT INTO transactions (position_id, symbol, action, shares, price, fees, transaction_date) VALUES (?, ?, 'buy', ?, ?, ?, ?)",
                     (pos_id, symbol, shares, price, fees, tx_date))
        conn.execute("UPDATE positions SET updated_at=CURRENT_TIMESTAMP WHERE id=?", (pos_id,))
        conn.commit()
        return f"Bought {shares} {symbol} @ {fmt_price(price, currency)}\nTotal: {fmt_price(shares * price + fees, currency)} (fees: {fmt_price(fees, currency)})"
    finally: conn.close()


def sell_position(symbol, shares, price, fees=0, transaction_date=None):
    symbol = symbol.upper()
    tx_date = transaction_date or date.today().isoformat()
    conn = get_connection()
    try:
        pos = conn.execute("SELECT id, currency FROM positions WHERE symbol=?", (symbol,)).fetchone()
        if not pos: return f"Error: No position for {symbol}"
        bought = conn.execute("SELECT COALESCE(SUM(shares),0) as t FROM transactions WHERE position_id=? AND action='buy'", (pos["id"],)).fetchone()["t"]
        sold = conn.execute("SELECT COALESCE(SUM(shares),0) as t FROM transactions WHERE position_id=? AND action='sell'", (pos["id"],)).fetchone()["t"]
        if shares > bought - sold: return f"Error: Only {bought - sold} shares available"
        conn.execute("INSERT INTO transactions (position_id, symbol, action, shares, price, fees, transaction_date) VALUES (?, ?, 'sell', ?, ?, ?, ?)",
                     (pos["id"], symbol, shares, price, fees, tx_date))
        conn.commit()
        return f"Sold {shares} {symbol} @ {fmt_price(price, pos['currency'])}\nProceeds: {fmt_price(shares * price - fees, pos['currency'])}"
    finally: conn.close()


def remove_position(symbol):
    symbol = symbol.upper()
    conn = get_connection()
    try:
        pos = conn.execute("SELECT id FROM positions WHERE symbol=?", (symbol,)).fetchone()
        if not pos: return f"Error: No position for {symbol}"
        conn.execute("DELETE FROM transactions WHERE position_id=?", (pos["id"],))
        conn.execute("DELETE FROM positions WHERE id=?", (pos["id"],))
        conn.commit()
        return f"Removed {symbol} and all transactions."
    finally: conn.close()


def list_positions():
    conn = get_connection()
    try:
        positions = conn.execute(
            "SELECT p.*, COALESCE((SELECT SUM(shares) FROM transactions WHERE position_id=p.id AND action='buy'),0) as bought, "
            "COALESCE((SELECT SUM(shares) FROM transactions WHERE position_id=p.id AND action='sell'),0) as sold "
            "FROM positions p ORDER BY p.symbol").fetchall()
        if not positions: return "No positions in portfolio."
        lines = ["**Portfolio Positions**\n"]
        for p in positions:
            holding = p["bought"] - p["sold"]
            if holding <= 0: continue
            avg = conn.execute("SELECT COALESCE(SUM(shares*price)/NULLIF(SUM(shares),0),0) as avg FROM transactions WHERE position_id=? AND action='buy'",
                               (p["id"],)).fetchone()["avg"]
            lines.append(f"  {p['symbol']} — {holding} shares @ avg {fmt_price(avg, p['currency'])} ({p['asset_type']})")
        return "\n".join(lines) if len(lines) > 1 else "No open positions."
    finally: conn.close()


def portfolio_summary():
    conn = get_connection()
    try:
        positions = conn.execute("SELECT * FROM positions ORDER BY symbol").fetchall()
        if not positions: return "Portfolio is empty."
        lines = ["**Portfolio Summary**\n"]
        total = 0
        for p in positions:
            buys = conn.execute("SELECT COALESCE(SUM(shares),0) as s, COALESCE(SUM(shares*price),0) as c FROM transactions WHERE position_id=? AND action='buy'", (p["id"],)).fetchone()
            sells = conn.execute("SELECT COALESCE(SUM(shares),0) as s, COALESCE(SUM(shares*price),0) as c FROM transactions WHERE position_id=? AND action='sell'", (p["id"],)).fetchone()
            holding = buys["s"] - sells["s"]
            if holding <= 0: continue
            cost = buys["c"] - sells["c"]
            avg = cost / holding if holding else 0
            total += cost
            lines.append(f"  **{p['symbol']}**: {holding} shares, cost: {fmt_price(cost, p['currency'])}, avg: {fmt_price(avg, p['currency'])}")
        lines.append(f"\n**Total Invested**: {fmt_price(total, 'USD')}")
        return "\n".join(lines)
    finally: conn.close()


def main():
    parser = argparse.ArgumentParser(description="Portfolio management")
    parser.add_argument("action", choices=["add", "sell", "remove", "list", "summary"])
    parser.add_argument("--symbol", "-s"); parser.add_argument("--shares", "-n", type=float)
    parser.add_argument("--price", "-p", type=float); parser.add_argument("--name")
    parser.add_argument("--fees", type=float, default=0); parser.add_argument("--date")
    parser.add_argument("--notes")
    args = parser.parse_args()

    if args.action == "add":
        if not all([args.symbol, args.shares, args.price]): print("Error: --symbol, --shares, --price required"); sys.exit(1)
        print(add_position(args.symbol, args.shares, args.price, args.name, args.fees, args.date, args.notes))
    elif args.action == "sell":
        if not all([args.symbol, args.shares, args.price]): print("Error: --symbol, --shares, --price required"); sys.exit(1)
        print(sell_position(args.symbol, args.shares, args.price, args.fees, args.date))
    elif args.action == "remove":
        if not args.symbol: print("Error: --symbol required"); sys.exit(1)
        print(remove_position(args.symbol))
    elif args.action == "list": print(list_positions())
    elif args.action == "summary": print(portfolio_summary())


if __name__ == "__main__":
    main()
