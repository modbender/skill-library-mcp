"""
Multi-agent observability example.

Shows how multiple agents can share a single ObservabilityStack,
each tagged with their own agent_id, while all metrics flow into
one unified dashboard.

Run:
    python examples/multi_agent.py
"""

import random
import threading
import time

from agentfinobs import ObservabilityStack, ConsoleExporter, PaymentRail


def agent_worker(obs: ObservabilityStack, agent_id: str, n_txs: int):
    """Simulate an agent that does work and spends money."""
    rails = [PaymentRail.X402_USDC, PaymentRail.STRIPE_ACP]

    for i in range(n_txs):
        cost = round(random.uniform(0.10, 3.00), 2)

        ok, reason = obs.can_spend(cost)
        if not ok:
            print(f"[{agent_id}] BLOCKED: {reason}")
            return

        tx = obs.track(
            amount=cost,
            agent_id=agent_id,
            task_id=f"{agent_id}-task-{i}",
            rail=random.choice(rails),
            counterparty="shared-api",
            description=f"Agent {agent_id} work item #{i+1}",
        )

        time.sleep(random.uniform(0.005, 0.02))

        revenue = round(cost * random.uniform(0.5, 2.0), 2)
        obs.settle(tx.tx_id, revenue=revenue)


def main():
    # Shared stack with a combined budget
    obs = ObservabilityStack.create(
        agent_id="multi-agent-system",
        budget_rules=[
            {"name": "combined_limit", "max_amount": 100, "window_seconds": 0},
        ],
        total_budget=200.0,
        exporters=[ConsoleExporter(color=True)],
    )

    # Launch 3 agents concurrently
    agents = ["researcher", "trader", "analyst"]
    threads = []

    print("=== Multi-Agent Observability Demo ===\n")
    print(f"Launching {len(agents)} agents concurrently...\n")

    for agent_id in agents:
        t = threading.Thread(
            target=agent_worker,
            args=(obs, agent_id, 5),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Combined metrics
    snap = obs.snapshot()
    print(f"\n{'=' * 50}")
    print("COMBINED METRICS (all agents)")
    print(f"{'=' * 50}")
    print(f"  Total txs:     {snap.tx_count}")
    print(f"  Total spent:   ${snap.total_spent:.2f}")
    print(f"  Total revenue: ${snap.total_revenue:.2f}")
    print(f"  Combined PnL:  ${snap.total_pnl:+.2f}")

    # Per-agent breakdown
    print(f"\n--- Spend by Task (agent) ---")
    for task, amount in sorted(snap.spend_by_task.items()):
        print(f"  {task:35s} ${amount:.2f}")


if __name__ == "__main__":
    main()
