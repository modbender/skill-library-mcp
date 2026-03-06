"""
CLI entry point — run with `python -m agentfinobs`.

Provides quick status checks and demo capabilities from the terminal.
"""

from __future__ import annotations

import argparse
import json
import sys
import time


def cmd_status(args):
    """Show current agent financial status from a JSONL log file."""
    from . import MetricsEngine, SpendTracker

    tracker = SpendTracker(agent_id="cli", persist_dir=None)

    # Load from file
    from .types import AgentTx, TxStatus
    import json as _json

    count = 0
    txs = []
    try:
        with open(args.file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                d = _json.loads(line)
                tx = AgentTx(
                    tx_id=d.get("tx_id", ""),
                    agent_id=d.get("agent_id", ""),
                    task_id=d.get("task_id", ""),
                    amount=d.get("amount", 0),
                    revenue=d.get("revenue", 0),
                    status=TxStatus(d.get("status", "pending")),
                    created_at=d.get("created_at", 0),
                    counterparty=d.get("counterparty", ""),
                    description=d.get("description", ""),
                )
                txs.append(tx)
                count += 1
    except FileNotFoundError:
        print(f"File not found: {args.file}", file=sys.stderr)
        return 1

    if not txs:
        print("No transactions found.")
        return 0

    engine = MetricsEngine(budget_total=args.budget)
    snap = engine.compute(txs)

    # Pretty output
    print(f"=== agentfinobs status ===")
    print(f"File:        {args.file}")
    print(f"Transactions: {snap.tx_count}")
    print(f"Total Spent:  ${snap.total_spent:.2f}")
    print(f"Total Revenue: ${snap.total_revenue:.2f}")
    print(f"Total PnL:    ${snap.total_pnl:+.2f}")
    if snap.roi_pct is not None:
        print(f"ROI:          {snap.roi_pct:+.1f}%")
    if snap.win_rate_pct is not None:
        print(f"Win Rate:     {snap.win_rate_pct:.1f}%")
    print(f"Burn Rate:    ${snap.burn_rate_per_hour:.2f}/hr")
    if snap.estimated_runway_hours is not None:
        print(f"Runway:       {snap.estimated_runway_hours:.1f}h")

    if snap.spend_by_counterparty:
        print(f"\n--- Spend by Counterparty ---")
        for cp, amt in sorted(snap.spend_by_counterparty.items(), key=lambda x: -x[1]):
            print(f"  {cp:30s} ${amt:.2f}")

    if snap.spend_by_rail:
        print(f"\n--- Spend by Rail ---")
        for rail, amt in sorted(snap.spend_by_rail.items(), key=lambda x: -x[1]):
            print(f"  {rail:30s} ${amt:.2f}")

    return 0


def cmd_demo(args):
    """Run a quick demo showing the SDK in action."""
    from . import ObservabilityStack, ConsoleExporter, PaymentRail
    import random

    print("=== agentfinobs demo ===\n")

    obs = ObservabilityStack.create(
        agent_id="demo-agent",
        budget_rules=[
            {"name": "hourly", "max_amount": 50, "window_seconds": 3600},
            {"name": "session", "max_amount": 20, "window_seconds": 0,
             "halt_on_breach": True},
        ],
        total_budget=100.0,
        exporters=[ConsoleExporter(color=True)],
    )

    rails = [PaymentRail.X402_USDC, PaymentRail.STRIPE_ACP, PaymentRail.VISA_TAP]
    counterparties = ["openai", "anthropic", "coingecko", "polymarket"]
    tasks = ["research", "trade-signal", "analysis", "report"]

    print("Recording 8 transactions...\n")
    txs = []
    for i in range(8):
        cost = round(random.uniform(0.5, 5.0), 2)
        tx = obs.track(
            amount=cost,
            task_id=random.choice(tasks),
            rail=random.choice(rails),
            counterparty=random.choice(counterparties),
            description=f"Demo tx #{i+1}",
        )
        txs.append(tx)

    print("\nSettling with random outcomes...\n")
    for tx in txs:
        revenue = round(tx.amount * random.uniform(0.5, 2.0), 2)
        obs.settle(tx.tx_id, revenue=revenue)

    snap = obs.snapshot()
    print(f"\n=== Final Metrics ===")
    print(f"Transactions: {snap.tx_count}")
    print(f"Total Spent:  ${snap.total_spent:.2f}")
    print(f"Total Revenue: ${snap.total_revenue:.2f}")
    print(f"PnL:          ${snap.total_pnl:+.2f}")
    if snap.roi_pct is not None:
        print(f"ROI:          {snap.roi_pct:+.1f}%")

    ok, reason = obs.can_spend(5.0)
    print(f"\nCan spend $5? {'YES' if ok else 'NO: ' + reason}")

    return 0


def cmd_version(args):
    from . import __version__
    print(f"agentfinobs {__version__}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="agentfinobs",
        description="Agent Financial Observability CLI",
    )
    sub = parser.add_subparsers(dest="command")

    # status
    p_status = sub.add_parser("status", help="Show financial status from a JSONL log")
    p_status.add_argument("file", help="Path to transactions JSONL file")
    p_status.add_argument("--budget", type=float, default=None, help="Total budget for runway calc")
    p_status.set_defaults(func=cmd_status)

    # demo
    p_demo = sub.add_parser("demo", help="Run a quick demo")
    p_demo.set_defaults(func=cmd_demo)

    # version
    p_ver = sub.add_parser("version", help="Show version")
    p_ver.set_defaults(func=cmd_version)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
