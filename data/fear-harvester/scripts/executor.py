#!/usr/bin/env python3
"""
FearHarvester Executor — paper/live DCA execution engine.

Usage:
    uv run python scripts/executor.py --dry-run        # simulate only
    uv run python scripts/executor.py --paper          # paper trading
    uv run python scripts/executor.py --live           # real money (requires API keys)
    uv run python scripts/executor.py --status         # show current positions
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import requests

STATE_FILE = Path(__file__).parent.parent / "data" / "executor_state.json"

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"positions": [], "total_invested": 0.0, "mode": "paper", "last_action": None}

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_fear_greed() -> dict:
    resp = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5)
    d = resp.json()["data"][0]
    return {"value": int(d["value"]), "label": d["value_classification"]}

def get_btc_price() -> float:
    resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=5)
    return float(resp.json()["price"])

def decide(fg_value: int, state: dict, config: dict) -> str:
    """Return action: DCA_BUY | REBALANCE_YIELD | HOLD"""
    if fg_value <= config["buy_threshold"]:
        invested = state["total_invested"]
        max_invest = config["max_capital"]
        if invested < max_invest:
            return "DCA_BUY"
    elif fg_value >= config["sell_threshold"]:
        if state["positions"]:
            return "REBALANCE_YIELD"
    return "HOLD"

def execute_dca_buy(price: float, fg: int, state: dict, config: dict, dry_run: bool) -> str:
    dca_amount = config["dca_amount_usd"]
    btc_qty = dca_amount / price
    pos = {
        "timestamp": datetime.now().isoformat(),
        "entry_price": price,
        "btc_qty": btc_qty,
        "usd_amount": dca_amount,
        "fg_at_entry": fg,
        "status": "open",
    }
    if not dry_run:
        state["positions"].append(pos)
        state["total_invested"] += dca_amount
        state["last_action"] = f"DCA_BUY ${dca_amount:.0f} @ ${price:,.0f} (F&G={fg})"
        save_state(state)
    return f"{'[DRY RUN] ' if dry_run else ''}DCA BUY ${dca_amount:.0f} BTC @ ${price:,.2f} | qty={btc_qty:.6f} | F&G={fg}"

def execute_rebalance(price: float, fg: int, state: dict, dry_run: bool) -> str:
    total_btc = sum(p["btc_qty"] for p in state["positions"] if p["status"] == "open")
    total_value = total_btc * price
    total_cost = sum(p["usd_amount"] for p in state["positions"] if p["status"] == "open")
    pnl_pct = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

    if not dry_run:
        for p in state["positions"]:
            if p["status"] == "open":
                p["status"] = "closed"
                p["exit_price"] = price
                p["exit_timestamp"] = datetime.now().isoformat()
                p["pnl_pct"] = ((price - p["entry_price"]) / p["entry_price"]) * 100
        state["total_invested"] = 0.0
        state["last_action"] = f"REBALANCE ${total_value:,.0f} ({pnl_pct:+.1f}%) @ F&G={fg}"
        save_state(state)
    return f"{'[DRY RUN] ' if dry_run else ''}REBALANCE {total_btc:.4f} BTC → ${total_value:,.0f} | PnL={pnl_pct:+.1f}% | F&G={fg}"

def show_status(state: dict) -> None:
    open_pos = [p for p in state["positions"] if p["status"] == "open"]
    price = get_btc_price()
    fg = get_fear_greed()
    print(f"\n📊 FearHarvester Status")
    print(f"   F&G: {fg['value']} ({fg['label']})")
    print(f"   BTC: ${price:,.2f}")
    print(f"   Open positions: {len(open_pos)}")
    if open_pos:
        total_btc = sum(p["btc_qty"] for p in open_pos)
        total_cost = sum(p["usd_amount"] for p in open_pos)
        current_value = total_btc * price
        pnl = current_value - total_cost
        pnl_pct = (pnl / total_cost * 100) if total_cost > 0 else 0
        avg_entry = total_cost / total_btc if total_btc > 0 else 0
        print(f"   Total BTC: {total_btc:.6f}")
        print(f"   Avg entry: ${avg_entry:,.2f}")
        print(f"   Current value: ${current_value:,.2f}")
        print(f"   PnL: ${pnl:+,.2f} ({pnl_pct:+.1f}%)")
    print(f"   Last action: {state.get('last_action', 'none')}")

def main() -> None:
    parser = argparse.ArgumentParser(description="FearHarvester DCA Executor")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only, no state changes")
    parser.add_argument("--paper", action="store_true", help="Paper trading mode")
    parser.add_argument("--live", action="store_true", help="Live trading (requires API keys)")
    parser.add_argument("--status", action="store_true", help="Show current positions")
    parser.add_argument("--buy-threshold", type=int, default=10, help="F&G buy threshold (default: 10)")
    parser.add_argument("--sell-threshold", type=int, default=50, help="F&G sell threshold (default: 50)")
    parser.add_argument("--dca-amount", type=float, default=500.0, help="USD per DCA buy (default: 500)")
    parser.add_argument("--max-capital", type=float, default=5000.0, help="Max total capital (default: 5000)")
    args = parser.parse_args()

    config = {
        "buy_threshold": args.buy_threshold,
        "sell_threshold": args.sell_threshold,
        "dca_amount_usd": args.dca_amount,
        "max_capital": args.max_capital,
    }

    state = load_state()

    if args.status:
        show_status(state)
        return

    fg = get_fear_greed()
    price = get_btc_price()
    action = decide(fg["value"], state, config)
    dry_run = args.dry_run or (not args.live)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] F&G={fg['value']} ({fg['label']}) | BTC=${price:,.2f} | Action={action}")

    if action == "DCA_BUY":
        result = execute_dca_buy(price, fg["value"], state, config, dry_run)
        print(f"✅ {result}")
    elif action == "REBALANCE_YIELD":
        result = execute_rebalance(price, fg["value"], state, dry_run)
        print(f"💰 {result}")
    else:
        print(f"✋ HOLD — F&G={fg['value']} not in buy/sell zone")

if __name__ == "__main__":
    main()
