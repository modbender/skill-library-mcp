#!/usr/bin/env python3
"""
prob.trade OpenClaw Skill — Polymarket analytics & trading.

Analytics (no auth):
    python3 probtrade.py overview
    python3 probtrade.py hot [--limit N]
    python3 probtrade.py breaking [--limit N]
    python3 probtrade.py new [--limit N] [--days N]
    python3 probtrade.py search "query" [--limit N]
    python3 probtrade.py market <condition_id>
    python3 probtrade.py stats
    python3 probtrade.py traders [--limit N] [--sort pnl|roi|volume|winRate] [--period all|30d|7d|24h]

Trading (requires API key):
    python3 probtrade.py order --market <id> --side BUY --outcome Yes --type LIMIT --price 0.55 --amount 10
    python3 probtrade.py cancel --order-id <orderId>
    python3 probtrade.py positions
    python3 probtrade.py balance
    python3 probtrade.py orders
"""

import sys
import os
import json
import argparse

# Add lib to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))
from api_client import fetch, trading_request


def format_market(m: dict) -> dict:
    """Extract key fields from a market for display."""
    tokens = m.get("tokens", {})
    t1 = tokens.get("token1") or {}
    t2 = tokens.get("token2") or {}

    return {
        "condition_id": m.get("condition_id"),
        "question": m.get("question"),
        "yes_price": t1.get("price"),
        "no_price": t2.get("price"),
        "category": m.get("category"),
        "volume_24hr": m.get("volume_24hr"),
        "liquidity": m.get("liquidity", {}).get("total") if isinstance(m.get("liquidity"), dict) else None,
        "end_date": m.get("end_date_iso"),
        "url": f"https://app.prob.trade/markets/{m.get('condition_id')}",
    }


def format_trader(t: dict) -> dict:
    """Extract key fields from a trader for display."""
    return {
        "address": t.get("address"),
        "displayName": t.get("displayName"),
        "whaleTier": t.get("whaleTier"),
        "totalPnL": t.get("totalPnL"),
        "roi": t.get("roi"),
        "winRate": t.get("winRate"),
        "totalVolume": t.get("totalVolume"),
        "tradesCount": t.get("tradesCount"),
        "url": f"https://app.prob.trade/traders/{t.get('address')}",
    }


# ==================== Analytics Commands ====================

def cmd_overview(_args):
    data = fetch("/overview")
    output = {
        "stats": data.get("stats"),
        "hotMarkets": [format_market(m) for m in data.get("hotMarkets", [])],
        "breakingMarkets": [format_market(m) for m in data.get("breakingMarkets", [])],
        "newMarkets": [format_market(m) for m in data.get("newMarkets", [])],
    }
    print(json.dumps(output, indent=2))


def cmd_hot(args):
    data = fetch("/markets/hot", {"limit": args.limit, "grouped": "true" if args.grouped else None})
    if args.grouped:
        print(json.dumps(data.get("items", []), indent=2))
    else:
        markets = [format_market(m) for m in data.get("markets", [])]
        print(json.dumps(markets, indent=2))


def cmd_breaking(args):
    data = fetch("/markets/breaking", {"limit": args.limit})
    markets = [format_market(m) for m in data.get("markets", [])]
    print(json.dumps(markets, indent=2))


def cmd_new(args):
    data = fetch("/markets/new", {"limit": args.limit, "days": args.days})
    markets = [format_market(m) for m in data.get("markets", [])]
    print(json.dumps(markets, indent=2))


def cmd_search(args):
    data = fetch("/markets/search", {"q": args.query, "limit": args.limit})
    markets = [format_market(m) for m in data.get("markets", [])]
    result = {"query": data.get("query"), "count": data.get("count"), "markets": markets}
    print(json.dumps(result, indent=2))


def cmd_market(args):
    data = fetch(f"/markets/{args.condition_id}")
    print(json.dumps(data.get("market", {}), indent=2))


def cmd_stats(_args):
    data = fetch("/markets/stats")
    print(json.dumps(data, indent=2))


def cmd_traders(args):
    data = fetch("/traders/top", {
        "limit": args.limit,
        "sortBy": args.sort,
        "period": args.period,
    })
    traders = [format_trader(t) for t in data.get("traders", [])]
    result = {"traders": traders, "pagination": data.get("pagination")}
    print(json.dumps(result, indent=2))


# ==================== Trading Commands ====================

def cmd_order(args):
    body = {
        "market": args.market,
        "side": args.side.upper(),
        "outcome": args.outcome,
        "type": args.type.upper(),
        "amount": args.amount,
    }
    if args.type.upper() == "LIMIT":
        if args.price is None:
            print("Error: --price is required for LIMIT orders", file=sys.stderr)
            sys.exit(1)
        body["price"] = args.price

    data = trading_request("POST", "/order", body)
    print(json.dumps(data, indent=2))


def cmd_cancel(args):
    data = trading_request("DELETE", f"/order/{args.order_id}")
    print(json.dumps(data, indent=2))


def cmd_positions(_args):
    data = trading_request("GET", "/positions")
    print(json.dumps(data, indent=2))


def cmd_balance(_args):
    data = trading_request("GET", "/balance")
    print(json.dumps(data, indent=2))


def cmd_orders(_args):
    data = trading_request("GET", "/orders")
    print(json.dumps(data, indent=2))


# ==================== Main ====================

def main():
    parser = argparse.ArgumentParser(
        description="prob.trade — Polymarket analytics & trading"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Analytics ---

    sub = subparsers.add_parser("overview", help="Market overview snapshot")
    sub.set_defaults(func=cmd_overview)

    sub = subparsers.add_parser("hot", help="Hot/trending markets")
    sub.add_argument("--limit", type=int, default=20)
    sub.add_argument("--grouped", action="store_true", help="Group by event/cluster")
    sub.set_defaults(func=cmd_hot)

    sub = subparsers.add_parser("breaking", help="Markets with biggest price movements")
    sub.add_argument("--limit", type=int, default=20)
    sub.set_defaults(func=cmd_breaking)

    sub = subparsers.add_parser("new", help="Recently created markets")
    sub.add_argument("--limit", type=int, default=20)
    sub.add_argument("--days", type=int, default=7)
    sub.set_defaults(func=cmd_new)

    sub = subparsers.add_parser("search", help="Search markets by keyword")
    sub.add_argument("query", help="Search query")
    sub.add_argument("--limit", type=int, default=20)
    sub.set_defaults(func=cmd_search)

    sub = subparsers.add_parser("market", help="Get details for a specific market")
    sub.add_argument("condition_id", help="Polymarket condition ID (0x...)")
    sub.set_defaults(func=cmd_market)

    sub = subparsers.add_parser("stats", help="Market statistics and category breakdown")
    sub.set_defaults(func=cmd_stats)

    sub = subparsers.add_parser("traders", help="Top traders leaderboard")
    sub.add_argument("--limit", type=int, default=20)
    sub.add_argument("--sort", choices=["pnl", "roi", "volume", "winRate"], default="pnl")
    sub.add_argument("--period", choices=["all", "30d", "7d", "24h"], default="all")
    sub.set_defaults(func=cmd_traders)

    # --- Trading ---

    sub = subparsers.add_parser("order", help="Place an order (requires API key)")
    sub.add_argument("--market", required=True, help="Market condition_id (0x...)")
    sub.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"])
    sub.add_argument("--outcome", required=True, help="Yes or No")
    sub.add_argument("--type", required=True, choices=["MARKET", "LIMIT", "market", "limit"])
    sub.add_argument("--price", type=float, help="Price for LIMIT orders (0.01-0.99)")
    sub.add_argument("--amount", type=float, required=True, help="Amount in USDC")
    sub.set_defaults(func=cmd_order)

    sub = subparsers.add_parser("cancel", help="Cancel an order (requires API key)")
    sub.add_argument("--order-id", required=True, help="Order ID to cancel")
    sub.set_defaults(func=cmd_cancel)

    sub = subparsers.add_parser("positions", help="View open positions (requires API key)")
    sub.set_defaults(func=cmd_positions)

    sub = subparsers.add_parser("balance", help="View USDC balance (requires API key)")
    sub.set_defaults(func=cmd_balance)

    sub = subparsers.add_parser("orders", help="View open orders (requires API key)")
    sub.set_defaults(func=cmd_orders)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
