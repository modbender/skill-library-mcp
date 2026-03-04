#!/usr/bin/env python3
"""Agent Metaverse Trading Skill - CLI wrapper for the virtual exchange."""

import argparse
import json
import os
import sys

import httpx

BASE_URL = os.environ.get("AGENT_METAVERSE_BASE_URL", "http://localhost:8000").rstrip("/")
API_KEY = os.environ.get("AGENT_METAVERSE_API_KEY", "")


def _client() -> httpx.Client:
    headers = {}
    if API_KEY:
        headers["X-API-Key"] = API_KEY
    return httpx.Client(base_url=BASE_URL, headers=headers, timeout=30.0)


def _require_auth():
    if not API_KEY:
        print(json.dumps({"error": "AGENT_METAVERSE_API_KEY not set. Run 'register' first."}))
        sys.exit(1)


def _output(data):
    print(json.dumps(data, indent=2))


def _handle_response(resp: httpx.Response):
    if resp.status_code >= 400:
        try:
            err = resp.json()
        except Exception:
            err = {"error": resp.text, "status_code": resp.status_code}
        _output(err)
        sys.exit(1)
    return resp.json()


# --- Commands ---

def cmd_register(args):
    with _client() as c:
        resp = c.post("/api/sdk/agents/register", json={
            "name": args.name,
            "description": args.description,
        })
        data = _handle_response(resp)
        _output(data)
        print(f"\nSet your API key:\n  export AGENT_METAVERSE_API_KEY={data['api_key']}", file=sys.stderr)


def cmd_prices(args):
    with _client() as c:
        resp = c.get("/api/prices")
        _output(_handle_response(resp))


def cmd_price_history(args):
    with _client() as c:
        resp = c.get(f"/api/prices/{args.pair}/history", params={"limit": args.limit})
        _output(_handle_response(resp))


def cmd_balance(args):
    _require_auth()
    with _client() as c:
        resp = c.get("/api/account/balance")
        _output(_handle_response(resp))


def cmd_buy(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/spot/order", json={
            "pair": args.pair,
            "side": "buy",
            "order_type": "market",
            "quantity": args.quantity,
        })
        _output(_handle_response(resp))


def cmd_sell(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/spot/order", json={
            "pair": args.pair,
            "side": "sell",
            "order_type": "market",
            "quantity": args.quantity,
        })
        _output(_handle_response(resp))


def cmd_limit_buy(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/spot/order", json={
            "pair": args.pair,
            "side": "buy",
            "order_type": "limit",
            "quantity": args.quantity,
            "price": args.price,
        })
        _output(_handle_response(resp))


def cmd_limit_sell(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/spot/order", json={
            "pair": args.pair,
            "side": "sell",
            "order_type": "limit",
            "quantity": args.quantity,
            "price": args.price,
        })
        _output(_handle_response(resp))


def cmd_orders(args):
    _require_auth()
    with _client() as c:
        resp = c.get("/api/spot/orders")
        _output(_handle_response(resp))


def cmd_cancel_order(args):
    _require_auth()
    with _client() as c:
        resp = c.delete(f"/api/spot/orders/{args.id}")
        _output(_handle_response(resp))


def cmd_open_long(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/futures/open", json={
            "pair": args.pair,
            "side": "long",
            "leverage": args.leverage,
            "quantity": args.quantity,
        })
        _output(_handle_response(resp))


def cmd_open_short(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/futures/open", json={
            "pair": args.pair,
            "side": "short",
            "leverage": args.leverage,
            "quantity": args.quantity,
        })
        _output(_handle_response(resp))


def cmd_positions(args):
    _require_auth()
    with _client() as c:
        resp = c.get("/api/futures/positions")
        _output(_handle_response(resp))


def cmd_close_position(args):
    _require_auth()
    with _client() as c:
        resp = c.post(f"/api/futures/close/{args.id}")
        _output(_handle_response(resp))


def cmd_swap_buy(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/amm/swap", json={
            "pair": args.pair,
            "side": "buy",
            "amount": args.amount,
        })
        _output(_handle_response(resp))


def cmd_swap_sell(args):
    _require_auth()
    with _client() as c:
        resp = c.post("/api/amm/swap", json={
            "pair": args.pair,
            "side": "sell",
            "amount": args.amount,
        })
        _output(_handle_response(resp))


def cmd_pools(args):
    with _client() as c:
        resp = c.get("/api/amm/pools")
        _output(_handle_response(resp))


def cmd_portfolio(args):
    _require_auth()
    with _client() as c:
        balances = _handle_response(c.get("/api/account/balance"))
        positions = _handle_response(c.get("/api/futures/positions"))
        prices = _handle_response(c.get("/api/prices"))

    pair_map = {"ETH": "ETHUSDT", "SOL": "SOLUSDT", "BTC": "BTCUSDT"}
    total_usdt = 0.0
    for b in balances:
        avail = float(b["available"])
        locked = float(b["locked"])
        if b["currency"] == "USDT":
            total_usdt += avail + locked
        else:
            pair = pair_map.get(b["currency"])
            if pair and pair in prices:
                total_usdt += (avail + locked) * float(prices[pair])

    total_pnl = sum(float(p.get("unrealized_pnl", 0)) for p in positions)
    total_margin = sum(float(p.get("margin", 0)) for p in positions)

    _output({
        "balances": balances,
        "positions": positions,
        "prices": prices,
        "summary": {
            "total_value_usdt": round(total_usdt + total_pnl, 2),
            "unrealized_pnl": round(total_pnl, 2),
            "locked_margin": round(total_margin, 2),
            "open_positions": len(positions),
        },
    })


def main():
    parser = argparse.ArgumentParser(
        description="Agent Metaverse Trading Skill",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # register
    p = sub.add_parser("register", help="Register a new agent")
    p.add_argument("--name", required=True, help="Agent name")
    p.add_argument("--description", default="", help="Agent description")

    # prices
    sub.add_parser("prices", help="Get current prices")

    # price-history
    p = sub.add_parser("price-history", help="Get price history for a pair")
    p.add_argument("--pair", required=True, help="Trading pair (ETHUSDT, SOLUSDT, BTCUSDT)")
    p.add_argument("--limit", type=int, default=50, help="Number of records")

    # balance
    sub.add_parser("balance", help="Get account balances")

    # buy
    p = sub.add_parser("buy", help="Market buy spot")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--quantity", type=float, required=True, help="Quantity to buy")

    # sell
    p = sub.add_parser("sell", help="Market sell spot")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--quantity", type=float, required=True, help="Quantity to sell")

    # limit-buy
    p = sub.add_parser("limit-buy", help="Limit buy spot")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--quantity", type=float, required=True, help="Quantity")
    p.add_argument("--price", type=float, required=True, help="Limit price")

    # limit-sell
    p = sub.add_parser("limit-sell", help="Limit sell spot")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--quantity", type=float, required=True, help="Quantity")
    p.add_argument("--price", type=float, required=True, help="Limit price")

    # orders
    sub.add_parser("orders", help="List spot orders")

    # cancel-order
    p = sub.add_parser("cancel-order", help="Cancel a pending order")
    p.add_argument("--id", required=True, help="Order ID")

    # open-long
    p = sub.add_parser("open-long", help="Open long futures position")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--leverage", type=int, required=True, help="Leverage (1-125)")
    p.add_argument("--quantity", type=float, required=True, help="Position size")

    # open-short
    p = sub.add_parser("open-short", help="Open short futures position")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--leverage", type=int, required=True, help="Leverage (1-125)")
    p.add_argument("--quantity", type=float, required=True, help="Position size")

    # positions
    sub.add_parser("positions", help="List open futures positions")

    # close-position
    p = sub.add_parser("close-position", help="Close a futures position")
    p.add_argument("--id", required=True, help="Position ID")

    # swap-buy
    p = sub.add_parser("swap-buy", help="AMM swap: spend USDT to buy base token")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--amount", type=float, required=True, help="USDT amount to spend")

    # swap-sell
    p = sub.add_parser("swap-sell", help="AMM swap: sell base token for USDT")
    p.add_argument("--pair", required=True, help="Trading pair")
    p.add_argument("--amount", type=float, required=True, help="Base token amount to sell")

    # pools
    sub.add_parser("pools", help="List AMM liquidity pools")

    # portfolio
    sub.add_parser("portfolio", help="Full portfolio summary")

    args = parser.parse_args()

    commands = {
        "register": cmd_register,
        "prices": cmd_prices,
        "price-history": cmd_price_history,
        "balance": cmd_balance,
        "buy": cmd_buy,
        "sell": cmd_sell,
        "limit-buy": cmd_limit_buy,
        "limit-sell": cmd_limit_sell,
        "orders": cmd_orders,
        "cancel-order": cmd_cancel_order,
        "open-long": cmd_open_long,
        "open-short": cmd_open_short,
        "positions": cmd_positions,
        "close-position": cmd_close_position,
        "swap-buy": cmd_swap_buy,
        "swap-sell": cmd_swap_sell,
        "pools": cmd_pools,
        "portfolio": cmd_portfolio,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
