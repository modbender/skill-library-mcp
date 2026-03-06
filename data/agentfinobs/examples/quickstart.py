"""
agentfinobs quickstart — full SDK demo in 60 lines.

Run:
    python examples/quickstart.py
"""

import random
import time

from agentfinobs import (
    ObservabilityStack,
    ConsoleExporter,
    JsonlExporter,
    PaymentRail,
)


def main():
    # 1. Create the full observability stack
    obs = ObservabilityStack.create(
        agent_id="arb-bot-01",
        budget_rules=[
            {"name": "per_hour", "max_amount": 50, "window_seconds": 3600},
            {"name": "daily_hard", "max_amount": 500, "window_seconds": 86400,
             "halt_on_breach": True},
        ],
        total_budget=1000.0,
        exporters=[
            ConsoleExporter(),                   # see txs in terminal
            JsonlExporter("data/demo_txs.jsonl"),  # persist to disk
        ],
    )

    # 2. Simulate agent activity
    tasks = [
        ("research", "openai", PaymentRail.STRIPE_ACP),
        ("trade-signal", "anthropic", PaymentRail.X402_USDC),
        ("execute-trade", "polymarket", PaymentRail.POLYMARKET_CLOB),
        ("hedge-check", "coingecko", PaymentRail.X402_USDC),
    ]

    for i in range(12):
        task_id, counterparty, rail = random.choice(tasks)
        cost = round(random.uniform(0.50, 8.00), 2)

        # Pre-check budget
        ok, reason = obs.can_spend(cost)
        if not ok:
            print(f"\n*** BUDGET BLOCK: {reason}")
            break

        # Record the spend
        tx = obs.track(
            amount=cost,
            task_id=task_id,
            counterparty=counterparty,
            rail=rail,
            description=f"Auto task #{i+1}",
        )

        # Simulate some outcome
        time.sleep(0.01)
        revenue = round(cost * random.uniform(0.3, 2.5), 2)
        obs.settle(tx.tx_id, revenue=revenue)

    # 3. Print final metrics
    snap = obs.snapshot()
    print("\n" + "=" * 50)
    print("FINAL METRICS")
    print("=" * 50)
    print(f"  Transactions:  {snap.tx_count}")
    print(f"  Total Spent:   ${snap.total_spent:.2f}")
    print(f"  Total Revenue: ${snap.total_revenue:.2f}")
    print(f"  PnL:           ${snap.total_pnl:+.2f}")
    if snap.roi_pct is not None:
        print(f"  ROI:           {snap.roi_pct:+.1f}%")
    if snap.win_rate_pct is not None:
        print(f"  Win Rate:      {snap.win_rate_pct:.0f}%")
    print(f"  Burn Rate:     ${snap.burn_rate_per_hour:.2f}/hr")
    if snap.estimated_runway_hours is not None:
        print(f"  Runway:        {snap.estimated_runway_hours:.1f}h")

    print(f"\n  Budget headroom: {obs.budget.headroom()}")

    # 4. Show anomaly stats
    stats = obs.anomaly.stats()
    print(f"  Anomaly detector: n={stats['n']}, mean=${stats['mean']:.2f}")
    if stats.get("alerts"):
        print(f"  Anomaly alerts: {len(stats['alerts'])}")


if __name__ == "__main__":
    main()
