#!/usr/bin/env python3
"""
Market data via Hummingbot API.

Usage:
    python scripts/market.py price <connector> <pair> [pair ...]
    python scripts/market.py orderbook <connector> <pair> [--depth 10]
    python scripts/market.py candles <connector> <pair> [--interval 1m] [--limit 20]
    python scripts/market.py funding <connector> <pair>
"""

import asyncio
import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from hbot_client import client, print_table


async def cmd_price(args):
    async with client() as c:
        prices = await c.market_data.get_prices(args.connector, args.pairs)
        rows = [{"pair": pair, "price": f"{price:.6f}"} for pair, price in prices.items()]
        print_table(rows, ["pair", "price"])


async def cmd_orderbook(args):
    async with client() as c:
        ob = await c.market_data.get_order_book(args.connector, args.pair, depth=args.depth)
        bids = ob.get("bids", [])[:args.depth]
        asks = ob.get("asks", [])[:args.depth]
        print(f"Order Book: {args.pair} on {args.connector}")
        print(f"\n{'ASKS':>20}")
        for price, qty in reversed(asks):
            print(f"  {price:>14.6f}  {qty:.6f}")
        print(f"  {'--- spread ---':^20}")
        for price, qty in bids:
            print(f"  {price:>14.6f}  {qty:.6f}")
        print(f"{'BIDS':>20}")


async def cmd_candles(args):
    async with client() as c:
        candles = await c.market_data.get_candles(
            args.connector, args.pair, args.interval, max_records=args.limit
        )
        if not candles:
            print("No candle data returned.")
            return
        rows = []
        for c_data in candles[-args.limit:]:
            rows.append({
                "time": c_data[0] if isinstance(c_data, list) else c_data.get("timestamp", ""),
                "open":  f"{(c_data[1] if isinstance(c_data, list) else c_data.get('open', 0)):.4f}",
                "high":  f"{(c_data[2] if isinstance(c_data, list) else c_data.get('high', 0)):.4f}",
                "low":   f"{(c_data[3] if isinstance(c_data, list) else c_data.get('low', 0)):.4f}",
                "close": f"{(c_data[4] if isinstance(c_data, list) else c_data.get('close', 0)):.4f}",
                "volume":f"{(c_data[5] if isinstance(c_data, list) else c_data.get('volume', 0)):.2f}",
            })
        print(f"Candles: {args.pair} on {args.connector} [{args.interval}]")
        print_table(rows, ["time", "open", "high", "low", "close", "volume"])


async def cmd_funding(args):
    async with client() as c:
        info = await c.market_data.get_funding_info(args.connector, args.pair)
        if isinstance(info, dict):
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print(info)


COMMANDS = {
    "price": cmd_price,
    "orderbook": cmd_orderbook,
    "candles": cmd_candles,
    "funding": cmd_funding,
}


def main():
    parser = argparse.ArgumentParser(description="Market data")
    sub = parser.add_subparsers(dest="command")

    p_price = sub.add_parser("price", help="Current price for trading pair(s)")
    p_price.add_argument("connector", help="Exchange connector (e.g. binance_paper_trade)")
    p_price.add_argument("pairs", nargs="+", help="Trading pair(s) e.g. BTC-USDT ETH-USDT")

    p_ob = sub.add_parser("orderbook", help="Order book snapshot")
    p_ob.add_argument("connector")
    p_ob.add_argument("pair")
    p_ob.add_argument("--depth", type=int, default=10)

    p_candles = sub.add_parser("candles", help="OHLCV candles")
    p_candles.add_argument("connector")
    p_candles.add_argument("pair")
    p_candles.add_argument("--interval", default="1m", help="Candle interval (1m, 5m, 1h, 1d)")
    p_candles.add_argument("--limit", type=int, default=20, help="Number of candles")

    p_fund = sub.add_parser("funding", help="Funding rate info (perpetuals)")
    p_fund.add_argument("connector")
    p_fund.add_argument("pair")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    asyncio.run(COMMANDS[args.command](args))


if __name__ == "__main__":
    main()
