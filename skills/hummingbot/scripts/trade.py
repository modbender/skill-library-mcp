#!/usr/bin/env python3
"""
Trading operations via Hummingbot API.

Usage:
    python scripts/trade.py order <account> <connector> <pair> <side> <amount> [--price P] [--type limit|market]
    python scripts/trade.py orders [--account ACCOUNT] [--connector CONNECTOR]
    python scripts/trade.py cancel <account> <connector> <order_id>
    python scripts/trade.py positions [--account ACCOUNT]
    python scripts/trade.py history [--limit 50] [--account ACCOUNT]
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def cmd_order(args):
    order_type = args.type.upper()
    if order_type == "LIMIT" and args.price is None:
        print("Error: --price is required for limit orders")
        sys.exit(1)

    print(f"⚠️  Placing {order_type} {args.side.upper()} order:")
    print(f"   {args.amount} {args.pair} on {args.connector} ({args.account})")
    if args.price:
        print(f"   Price: {args.price}")
    confirm = input("Confirm? [y/N] ").strip().lower()
    if confirm != "y":
        print("Cancelled.")
        return

    async with client() as c:
        result = await c.trading.place_order(
            account=args.account,
            connector=args.connector,
            trading_pair=args.pair,
            side=args.side.upper(),
            amount=float(args.amount),
            order_type=order_type,
            price=float(args.price) if args.price else None,
        )
        print(f"✓ Order placed")
        if isinstance(result, dict):
            order_id = result.get("order_id", result.get("id", "?"))
            print(f"  Order ID: {order_id}")


async def cmd_orders(args):
    async with client() as c:
        orders = await c.trading.get_active_orders()
        if not orders:
            print("No active orders.")
            return
        rows = []
        for o in orders:
            if args.account and o.get("account") != args.account:
                continue
            if args.connector and o.get("connector") != args.connector:
                continue
            rows.append({
                "id": str(o.get("order_id", o.get("id", "?")))[:16],
                "pair": o.get("trading_pair", "?"),
                "side": o.get("side", "?"),
                "type": o.get("type", "?"),
                "amount": f"{o.get('amount', 0):.6f}",
                "price": f"{o.get('price', 0):.4f}",
                "account": o.get("account", "?"),
                "connector": o.get("connector", "?"),
            })
        if rows:
            print_table(rows, ["id", "pair", "side", "type", "amount", "price", "connector", "account"])
        else:
            print("No matching orders.")


async def cmd_cancel(args):
    async with client() as c:
        await c.trading.cancel_order(
            account=args.account,
            connector=args.connector,
            order_id=args.order_id,
        )
        print(f"✓ Order {args.order_id} cancelled")


async def cmd_positions(args):
    async with client() as c:
        positions = await c.trading.get_positions()
        if not positions:
            print("No open positions.")
            return
        rows = []
        for p in positions:
            if args.account and p.get("account") != args.account:
                continue
            rows.append({
                "pair": p.get("trading_pair", "?"),
                "side": p.get("side", "?"),
                "amount": f"{p.get('amount', 0):.4f}",
                "entry": f"{p.get('entry_price', 0):.4f}",
                "unrealized_pnl": f"{p.get('unrealized_pnl', 0):+.4f}",
                "leverage": p.get("leverage", 1),
                "account": p.get("account", "?"),
            })
        if rows:
            print_table(rows, ["pair", "side", "amount", "entry", "unrealized_pnl", "leverage", "account"])
        else:
            print("No matching positions.")


async def cmd_history(args):
    async with client() as c:
        trades = await c.trading.get_trades()
        items = trades.get("data", trades) if isinstance(trades, dict) else trades
        rows = []
        for t in items[:args.limit]:
            if args.account and t.get("account") != args.account:
                continue
            rows.append({
                "time": str(t.get("timestamp", t.get("created_at", "?")))[:19],
                "pair": t.get("trading_pair", "?"),
                "side": t.get("side", "?"),
                "amount": f"{t.get('amount', 0):.6f}",
                "price": f"{t.get('price', 0):.4f}",
                "fee": f"{t.get('fee_amount', 0):.6f}",
            })
        if rows:
            print_table(rows, ["time", "pair", "side", "amount", "price", "fee"])
        else:
            print("No trade history found.")


COMMANDS = {
    "order": cmd_order,
    "orders": cmd_orders,
    "cancel": cmd_cancel,
    "positions": cmd_positions,
    "history": cmd_history,
}


def main():
    parser = argparse.ArgumentParser(description="Trading operations")
    sub = parser.add_subparsers(dest="command")

    p_order = sub.add_parser("order", help="Place an order")
    p_order.add_argument("account", help="Account name")
    p_order.add_argument("connector", help="Exchange connector")
    p_order.add_argument("pair", help="Trading pair (e.g. BTC-USDT)")
    p_order.add_argument("side", choices=["buy", "sell"])
    p_order.add_argument("amount", help="Order amount")
    p_order.add_argument("--price", help="Limit price")
    p_order.add_argument("--type", default="market", choices=["market", "limit"])

    p_orders = sub.add_parser("orders", help="List active orders")
    p_orders.add_argument("--account")
    p_orders.add_argument("--connector")

    p_cancel = sub.add_parser("cancel", help="Cancel an order")
    p_cancel.add_argument("account")
    p_cancel.add_argument("connector")
    p_cancel.add_argument("order_id")

    p_pos = sub.add_parser("positions", help="View open positions (perpetuals)")
    p_pos.add_argument("--account")

    p_hist = sub.add_parser("history", help="Trade history")
    p_hist.add_argument("--limit", type=int, default=50)
    p_hist.add_argument("--account")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(COMMANDS[args.command](args))


if __name__ == "__main__":
    main()
