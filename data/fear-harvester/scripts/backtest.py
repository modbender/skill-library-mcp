#!/usr/bin/env python3
"""
FearHarvester Backtester
Tests the strategy: DCA when F&G < threshold, hold N days, sell at recovery.
"""

import json
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass
import statistics

FEAR_GREED_API = "https://api.alternative.me/fng/?limit=2000&format=json"
BINANCE_KLINES = "https://api.binance.com/api/v3/klines"

@dataclass
class Trade:
    entry_date: str
    entry_price: float
    fg_at_entry: int
    exit_date: str | None
    exit_price: float | None
    hold_days: int
    pnl_pct: float | None
    status: str  # "closed" or "open"

def fetch_fear_greed_history() -> list[dict]:
    """Fetch full Fear & Greed history from alternative.me."""
    resp = requests.get(FEAR_GREED_API, timeout=10)
    data = resp.json()["data"]
    return [{"date": d["timestamp"], "value": int(d["value"]), "label": d["value_classification"]} for d in data]

def fetch_btc_price_history() -> dict[str, float]:
    """Fetch BTC daily close prices from Binance."""
    # Fetch 2000 days of daily BTC data
    resp = requests.get(
        BINANCE_KLINES,
        params={"symbol": "BTCUSDT", "interval": "1d", "limit": 1000},
        timeout=10
    )
    klines = resp.json()
    prices = {}
    for k in klines:
        date = datetime.fromtimestamp(k[0]/1000).strftime("%Y-%m-%d")
        prices[date] = float(k[4])  # close price
    return prices

def run_backtest(
    fg_threshold: int = 10,
    hold_days: int = 90,
    dca_amount: float = 1000.0,
    starting_capital: float = 10000.0,
) -> dict:
    """
    Run the FearHarvester backtest.

    Strategy:
    - When F&G drops below fg_threshold: invest dca_amount
    - After hold_days: sell position
    - Track all trades, compute Sharpe, total return, max drawdown
    """
    # Fetch data
    fg_history = fetch_fear_greed_history()
    btc_prices = fetch_btc_price_history()

    trades = []
    cash = starting_capital
    btc_held = 0.0

    # Iterate through F&G history, match with prices
    for fg_day in sorted(fg_history, key=lambda x: x["date"]):
        date = datetime.fromtimestamp(int(fg_day["date"])).strftime("%Y-%m-%d")
        fg_val = fg_day["value"]

        if date not in btc_prices:
            continue

        price = btc_prices[date]

        # Entry signal: F&G below threshold
        if fg_val <= fg_threshold and cash >= dca_amount:
            btc_bought = dca_amount / price
            btc_held += btc_bought
            cash -= dca_amount

            # Calculate exit
            exit_date = (datetime.strptime(date, "%Y-%m-%d") + timedelta(days=hold_days)).strftime("%Y-%m-%d")
            exit_price = btc_prices.get(exit_date)

            if exit_price:
                pnl = (exit_price - price) / price * 100
                trades.append(Trade(
                    entry_date=date,
                    entry_price=price,
                    fg_at_entry=fg_val,
                    exit_date=exit_date,
                    exit_price=exit_price,
                    hold_days=hold_days,
                    pnl_pct=pnl,
                    status="closed"
                ))

    # Compute statistics
    closed = [t for t in trades if t.pnl_pct is not None]
    if not closed:
        return {"error": "No trades found"}

    returns = [t.pnl_pct for t in closed]
    winning = [r for r in returns if r > 0]

    avg_return = statistics.mean(returns)
    std_return = statistics.stdev(returns) if len(returns) > 1 else 0
    sharpe = avg_return / std_return if std_return > 0 else 0
    win_rate = len(winning) / len(returns) * 100
    max_drawdown = min(returns)
    best_trade = max(returns)

    return {
        "strategy": f"DCA when F&G <= {fg_threshold}, hold {hold_days}d",
        "total_trades": len(closed),
        "win_rate_pct": round(win_rate, 1),
        "avg_return_pct": round(avg_return, 1),
        "median_return_pct": round(statistics.median(returns), 1),
        "sharpe_ratio": round(sharpe, 2),
        "max_drawdown_pct": round(max_drawdown, 1),
        "best_trade_pct": round(best_trade, 1),
        "trades": [vars(t) for t in closed[:10]]  # first 10 for display
    }

if __name__ == "__main__":
    import sys
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    hold = int(sys.argv[2]) if len(sys.argv) > 2 else 90

    print(f"Running FearHarvester backtest: F&G <= {threshold}, hold {hold} days...")
    result = run_backtest(fg_threshold=threshold, hold_days=hold)

    print(f"\n{'='*50}")
    print(f"FEARH HARVESTER BACKTEST RESULTS")
    print(f"{'='*50}")
    print(f"Strategy: {result['strategy']}")
    print(f"Total Trades: {result['total_trades']}")
    print(f"Win Rate: {result['win_rate_pct']}%")
    print(f"Avg Return: {result['avg_return_pct']}%")
    print(f"Median Return: {result['median_return_pct']}%")
    print(f"Sharpe Ratio: {result['sharpe_ratio']}")
    print(f"Max Drawdown: {result['max_drawdown_pct']}%")
    print(f"Best Trade: {result['best_trade_pct']}%")
    print(f"\nSharpe {'✅ > 1.5 — DEPLOY' if result['sharpe_ratio'] > 1.5 else '⚠️ < 1.5 — NEEDS WORK'}")

    # Save results
    with open("/home/bowen/clawd/skills/fear-harvester/data/backtest_results.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print(f"\nResults saved to data/backtest_results.json")
