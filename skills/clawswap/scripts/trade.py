#!/usr/bin/env python3
"""ClawSwap Trader skill entry point."""

import asyncio
import json
import os
import sys

from clawswap import ClawSwapClient


def get_client() -> ClawSwapClient:
    private_key = os.environ.get("CLAWSWAP_PRIVATE_KEY")
    if not private_key:
        print("Error: CLAWSWAP_PRIVATE_KEY not set", file=sys.stderr)
        sys.exit(1)
    gateway_url = os.environ.get("CLAWSWAP_GATEWAY_URL", "https://gateway.clawswap.io")
    return ClawSwapClient(private_key=private_key, gateway_url=gateway_url)


async def cmd_trade(args: list[str]) -> None:
    """Execute a trade. Usage: trade <buy|sell> <ticker> <size> [price]"""
    if len(args) < 3:
        print("Usage: trade <buy|sell> <ticker> <size> [price]")
        return

    side, ticker, size = args[0], args[1].upper(), float(args[2])
    price = float(args[3]) if len(args) > 3 else None

    client = get_client()
    await client.authenticate()

    if price is not None:
        if side == "buy":
            order = await client.limit_buy(ticker, price=price, size=size)
        else:
            order = await client.limit_sell(ticker, price=price, size=size)
        print(f"Limit {side} {size} {ticker} @ ${price:.2f} — {order.status} ({order.order_id})")
    else:
        if side == "buy":
            order = await client.market_buy(ticker, size=size)
        else:
            order = await client.market_sell(ticker, size=size)
        filled = f" @ ${order.filled_at:.2f}" if order.filled_at else ""
        print(f"Market {side} {size} {ticker}{filled} — {order.status} ({order.order_id})")

    await client.close()


async def cmd_balance() -> None:
    """Check account balance and positions."""
    client = get_client()
    await client.authenticate()

    balance = await client.get_balance()
    print(f"Equity:           ${balance.equity:,.2f}")
    print(f"Margin used:      ${balance.margin_used:,.2f}")
    print(f"Available margin: ${balance.available_margin:,.2f}")

    if balance.positions:
        print(f"\nOpen positions ({len(balance.positions)}):")
        for p in balance.positions:
            pnl_str = f"+${p.unrealized_pnl:,.2f}" if p.unrealized_pnl >= 0 else f"-${abs(p.unrealized_pnl):,.2f}"
            print(f"  {p.ticker} {p.side} {p.size} @ ${p.entry_price:,.2f} (PnL: {pnl_str})")

    await client.close()


async def cmd_competitions(args: list[str]) -> None:
    """Manage competitions. Usage: competitions <list|join|leaderboard> [id]"""
    sub = args[0] if args else "list"
    client = get_client()
    await client.authenticate()

    if sub == "list":
        comps = await client.list_competitions()
        for c in comps:
            prize = f" — Prize: ${c.prize_pool_usdc:,.0f}" if c.prize_pool_usdc else ""
            print(f"[{c.status}] {c.name} ({c.id}){prize}")

    elif sub == "join" and len(args) > 1:
        await client.join_competition(args[1])
        print(f"Joined competition {args[1]}")

    elif sub == "leaderboard" and len(args) > 1:
        lb = await client.get_leaderboard(args[1])
        print(f"{lb.competition} ({lb.status}) — {lb.total_participants} participants")
        if lb.remaining:
            print(f"Remaining: {lb.remaining}")
        for entry in lb.leaderboard[:10]:
            print(f"  #{entry.rank} {entry.agent_id}: ${entry.equity:,.2f} ({entry.pnl_pct:+.1f}%)")

    else:
        print("Usage: competitions <list|join|leaderboard> [id]")

    await client.close()


async def cmd_points() -> None:
    """Check points, level, and streak."""
    client = get_client()
    await client.authenticate()

    points = await client.get_points()
    print(f"Level {points.level} ({points.level_name})")
    print(f"Total points: {points.total_points:,.1f}")
    print(f"Season: {points.season}")
    print(f"Fee: {points.fee_bps} bps")

    if points.streak:
        print(f"Streak: {points.streak.current} days (best: {points.streak.best})")

    if points.today:
        print(f"\nToday:")
        print(f"  Points: {points.today.points:.1f}")
        print(f"  PnL: {points.today.pnl_pct:+.1f}%")
        print(f"  Volume: ${points.today.volume:,.0f}")
        print(f"  Trades: {points.today.trades}")
        print(f"  Win rate: {points.today.win_rate:.0%}")

    await client.close()


async def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: trade.py <trade|balance|competitions|points> [args...]")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "trade": lambda: cmd_trade(args),
        "balance": cmd_balance,
        "competitions": lambda: cmd_competitions(args),
        "points": cmd_points,
    }

    handler = commands.get(command)
    if handler is None:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")
        sys.exit(1)

    await handler()


if __name__ == "__main__":
    asyncio.run(main())
