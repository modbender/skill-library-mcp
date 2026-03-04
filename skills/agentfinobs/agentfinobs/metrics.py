"""
MetricsEngine — real-time financial analytics for agents.

Computes ROI, cost per task, burn rate, throughput, and more from
the SpendTracker's transaction stream.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .types import AgentTx, TxStatus


@dataclass
class Snapshot:
    """Point-in-time metrics snapshot."""
    timestamp: float = field(default_factory=time.time)

    # Volume
    tx_count: int = 0
    total_spent: float = 0.0
    total_revenue: float = 0.0
    total_pnl: float = 0.0

    # Rates
    avg_cost_per_tx: float = 0.0
    avg_cost_per_task: float = 0.0
    roi_pct: float | None = None      # (revenue - cost) / cost * 100
    win_rate_pct: float | None = None

    # Burn
    burn_rate_per_hour: float = 0.0   # $/hour average
    estimated_runway_hours: float | None = None  # at current burn rate

    # Distribution
    spend_by_task: dict[str, float] = field(default_factory=dict)
    spend_by_rail: dict[str, float] = field(default_factory=dict)
    spend_by_counterparty: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "tx_count": self.tx_count,
            "total_spent": round(self.total_spent, 4),
            "total_revenue": round(self.total_revenue, 4),
            "total_pnl": round(self.total_pnl, 4),
            "avg_cost_per_tx": round(self.avg_cost_per_tx, 4),
            "avg_cost_per_task": round(self.avg_cost_per_task, 4),
            "roi_pct": round(self.roi_pct, 2) if self.roi_pct is not None else None,
            "win_rate_pct": round(self.win_rate_pct, 2) if self.win_rate_pct is not None else None,
            "burn_rate_per_hour": round(self.burn_rate_per_hour, 4),
            "estimated_runway_hours": (
                round(self.estimated_runway_hours, 1)
                if self.estimated_runway_hours is not None
                else None
            ),
            "spend_by_task": {k: round(v, 4) for k, v in self.spend_by_task.items()},
            "spend_by_rail": {k: round(v, 4) for k, v in self.spend_by_rail.items()},
            "spend_by_counterparty": {k: round(v, 4) for k, v in self.spend_by_counterparty.items()},
        }


class MetricsEngine:
    """
    Computes financial metrics from a list of transactions.

    Usage::

        engine = MetricsEngine(budget_total=1000.0)
        snapshot = engine.compute(tracker.recent(500))
    """

    def __init__(self, budget_total: float | None = None):
        self.budget_total = budget_total  # for runway estimation

    def compute(self, txs: list[AgentTx]) -> Snapshot:
        """Compute a full metrics snapshot from a set of transactions."""
        snap = Snapshot()
        if not txs:
            return snap

        snap.tx_count = len(txs)
        snap.total_spent = sum(tx.amount for tx in txs)
        snap.total_revenue = sum(tx.revenue for tx in txs)
        snap.total_pnl = snap.total_revenue - snap.total_spent

        # Averages
        snap.avg_cost_per_tx = snap.total_spent / snap.tx_count

        task_ids = {tx.task_id for tx in txs if tx.task_id}
        if task_ids:
            snap.avg_cost_per_task = snap.total_spent / len(task_ids)

        # ROI
        if snap.total_spent > 0:
            snap.roi_pct = (snap.total_pnl / snap.total_spent) * 100

        # Win rate (settled txs only)
        settled = [tx for tx in txs if tx.status in (TxStatus.CONFIRMED, TxStatus.FAILED)]
        if settled:
            wins = sum(1 for tx in settled if tx.pnl > 0)
            snap.win_rate_pct = (wins / len(settled)) * 100

        # Burn rate
        sorted_txs = sorted(txs, key=lambda t: t.created_at)
        time_span = sorted_txs[-1].created_at - sorted_txs[0].created_at
        if time_span > 0:
            hours = time_span / 3600
            snap.burn_rate_per_hour = snap.total_spent / hours

        # Runway
        if snap.burn_rate_per_hour > 0 and self.budget_total is not None:
            remaining = max(0, self.budget_total - snap.total_spent)
            snap.estimated_runway_hours = remaining / snap.burn_rate_per_hour

        # Distributions
        for tx in txs:
            key = tx.task_id or "_no_task"
            snap.spend_by_task[key] = snap.spend_by_task.get(key, 0) + tx.amount

            rail_key = tx.rail.value
            snap.spend_by_rail[rail_key] = snap.spend_by_rail.get(rail_key, 0) + tx.amount

            if tx.counterparty:
                snap.spend_by_counterparty[tx.counterparty] = (
                    snap.spend_by_counterparty.get(tx.counterparty, 0) + tx.amount
                )

        return snap

    def compute_window(
        self, txs: list[AgentTx], window_seconds: float
    ) -> Snapshot:
        """Compute metrics for only the last `window_seconds`."""
        cutoff = time.time() - window_seconds
        filtered = [tx for tx in txs if tx.created_at >= cutoff]
        return self.compute(filtered)
