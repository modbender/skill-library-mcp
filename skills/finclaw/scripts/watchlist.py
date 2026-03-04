#!/usr/bin/env python3
"""Watchlist management."""

import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.db import get_connection
from lib.formatters import detect_asset_type, fmt_price
from scripts.quote import get_quote


def create_watchlist(name):
    conn = get_connection()
    try:
        conn.execute("INSERT INTO watchlists (name) VALUES (?)", (name,)); conn.commit()
        return f"Watchlist '{name}' created."
    except Exception as e:
        return f"Watchlist '{name}' already exists." if "UNIQUE" in str(e) else f"Error: {e}"
    finally: conn.close()


def delete_watchlist(name):
    conn = get_connection()
    try:
        wl = conn.execute("SELECT id FROM watchlists WHERE name=?", (name,)).fetchone()
        if not wl: return f"Watchlist '{name}' not found."
        conn.execute("DELETE FROM watchlist_items WHERE watchlist_id=?", (wl["id"],))
        conn.execute("DELETE FROM watchlists WHERE id=?", (wl["id"],)); conn.commit()
        return f"Watchlist '{name}' deleted."
    finally: conn.close()


def add_to_watchlist(name, symbol):
    symbol = symbol.upper()
    conn = get_connection()
    try:
        wl = conn.execute("SELECT id FROM watchlists WHERE name=?", (name,)).fetchone()
        if not wl:
            wl_id = conn.execute("INSERT INTO watchlists (name) VALUES (?)", (name,)).lastrowid
        else: wl_id = wl["id"]
        conn.execute("INSERT OR IGNORE INTO watchlist_items (watchlist_id, symbol, asset_type) VALUES (?,?,?)",
                     (wl_id, symbol, detect_asset_type(symbol))); conn.commit()
        return f"Added {symbol} to '{name}'."
    finally: conn.close()


def remove_from_watchlist(name, symbol):
    conn = get_connection()
    try:
        wl = conn.execute("SELECT id FROM watchlists WHERE name=?", (name,)).fetchone()
        if not wl: return f"Watchlist '{name}' not found."
        conn.execute("DELETE FROM watchlist_items WHERE watchlist_id=? AND symbol=?", (wl["id"], symbol.upper())); conn.commit()
        return f"Removed {symbol.upper()} from '{name}'."
    finally: conn.close()


def list_watchlists():
    conn = get_connection()
    try:
        wls = conn.execute("SELECT w.*, COUNT(wi.id) as count FROM watchlists w LEFT JOIN watchlist_items wi ON w.id=wi.watchlist_id GROUP BY w.id ORDER BY w.name").fetchall()
        if not wls: return "No watchlists."
        return "**Watchlists**\n\n" + "\n".join(f"  • {w['name']} ({w['count']} symbols)" for w in wls)
    finally: conn.close()


def show_watchlist(name, with_prices=False):
    conn = get_connection()
    try:
        wl = conn.execute("SELECT id FROM watchlists WHERE name=?", (name,)).fetchone()
        if not wl: return f"Watchlist '{name}' not found."
        items = conn.execute("SELECT * FROM watchlist_items WHERE watchlist_id=? ORDER BY symbol", (wl["id"],)).fetchall()
        if not items: return f"Watchlist '{name}' is empty."
        lines = [f"**Watchlist: {name}**\n"]
        for item in items:
            if with_prices:
                try:
                    q = get_quote(item["symbol"])
                    c = q.get("currency", "USD")
                    chg = f" ({'+' if q.get('change_pct', 0) >= 0 else ''}{q.get('change_pct', 0):.2f}%)" if q.get("change_pct") is not None else ""
                    lines.append(f"  {item['symbol']} — {fmt_price(q['price'], c)}{chg}")
                except: lines.append(f"  {item['symbol']} — _unavailable_")
            else: lines.append(f"  {item['symbol']} ({item['asset_type']})")
        return "\n".join(lines)
    finally: conn.close()


def main():
    parser = argparse.ArgumentParser(description="Watchlist management")
    parser.add_argument("action", choices=["create", "delete", "add", "remove", "list", "show"])
    parser.add_argument("--name", "-n"); parser.add_argument("--symbol", "-s")
    parser.add_argument("--prices", action="store_true")
    args = parser.parse_args()

    if args.action == "create":
        if not args.name: print("Error: --name required"); sys.exit(1)
        print(create_watchlist(args.name))
    elif args.action == "delete":
        if not args.name: print("Error: --name required"); sys.exit(1)
        print(delete_watchlist(args.name))
    elif args.action == "add":
        if not args.name or not args.symbol: print("Error: --name and --symbol required"); sys.exit(1)
        print(add_to_watchlist(args.name, args.symbol))
    elif args.action == "remove":
        if not args.name or not args.symbol: print("Error: --name and --symbol required"); sys.exit(1)
        print(remove_from_watchlist(args.name, args.symbol))
    elif args.action == "list": print(list_watchlists())
    elif args.action == "show":
        if not args.name: print("Error: --name required"); sys.exit(1)
        print(show_watchlist(args.name, args.prices))


if __name__ == "__main__":
    main()
