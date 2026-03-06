"""
agentfinobs — Agent Financial Observability SDK

"Datadog for Agent Payments"

Monitor, budget, and analyze spending across any AI agent,
regardless of payment rail (x402, Stripe/ACP, Visa TAP, etc.)

Quick start::

    from agentfinobs import ObservabilityStack

    obs = ObservabilityStack.create(
        agent_id="my-agent",
        budget_rules=[
            {"name": "hourly", "max_amount": 50, "window_seconds": 3600},
            {"name": "daily", "max_amount": 200, "window_seconds": 86400,
             "halt_on_breach": True},
        ],
        total_budget=1000.0,
        dashboard_port=9400,
    )

    # Record a spend
    tx = obs.track(amount=1.50, task_id="task-1", description="API call")

    # Settle with outcome
    obs.settle(tx.tx_id, revenue=2.00)

    # Check before spending
    ok, reason = obs.can_spend(50.0)

    # Get metrics snapshot
    snapshot = obs.snapshot()
"""

from .types import (
    AgentTx,
    Alert,
    AlertSeverity,
    BudgetRule,
    PaymentRail,
    TxStatus,
)
from .tracker import SpendTracker
from .budget import BudgetManager
from .metrics import MetricsEngine, Snapshot
from .anomaly import AnomalyDetector
from .dashboard import Dashboard
from .exporters import (
    BaseExporter,
    JsonlExporter,
    WebhookExporter,
    ConsoleExporter,
    MultiExporter,
)


class ObservabilityStack:
    """
    All-in-one convenience class that wires together the full stack:
    SpendTracker + BudgetManager + MetricsEngine + AnomalyDetector + Dashboard.
    """

    def __init__(
        self,
        tracker: SpendTracker,
        budget: BudgetManager,
        metrics: MetricsEngine,
        anomaly: AnomalyDetector,
        dashboard: Dashboard | None = None,
    ):
        self.tracker = tracker
        self.budget = budget
        self.metrics = metrics
        self.anomaly = anomaly
        self.dashboard = dashboard

    @classmethod
    def create(
        cls,
        agent_id: str = "default",
        budget_rules: list[dict] | None = None,
        total_budget: float | None = None,
        persist_dir: str | None = None,
        dashboard_port: int | None = None,
        anomaly_z_threshold: float = 3.0,
        exporters: list[BaseExporter] | None = None,
    ) -> "ObservabilityStack":
        """
        Factory that creates and wires the full stack in one call.

        Args:
            exporters: Optional list of exporters (JsonlExporter, WebhookExporter, etc.)
                       These receive every tx in real-time for shipping to external systems.
        """
        tracker = SpendTracker(
            agent_id=agent_id, persist_dir=persist_dir, exporters=exporters,
        )
        budget = BudgetManager()
        metrics = MetricsEngine(budget_total=total_budget)
        anomaly = AnomalyDetector(z_threshold=anomaly_z_threshold)

        # Wire listeners
        tracker.add_listener(budget.on_tx)
        tracker.add_listener(anomaly.on_tx)

        # Budget rules
        for rule_dict in (budget_rules or []):
            budget.add_rule(BudgetRule(
                name=rule_dict["name"],
                max_amount=rule_dict["max_amount"],
                window_seconds=rule_dict.get("window_seconds", 0),
                severity=AlertSeverity(rule_dict.get("severity", "warning")),
                halt_on_breach=rule_dict.get("halt_on_breach", False),
            ))

        # Dashboard
        dash = None
        if dashboard_port:
            dash = Dashboard(tracker, budget, metrics, anomaly)
            dash.start(port=dashboard_port)

        return cls(
            tracker=tracker,
            budget=budget,
            metrics=metrics,
            anomaly=anomaly,
            dashboard=dash,
        )

    # ── Convenience methods ────────────────────────────────────────────

    def track(self, **kwargs) -> AgentTx:
        """Record a transaction. Shortcut for tracker.record()."""
        return self.tracker.record(**kwargs)

    def settle(self, tx_id: str, revenue: float, status: TxStatus = TxStatus.CONFIRMED) -> AgentTx | None:
        """Settle a transaction. Shortcut for tracker.settle()."""
        return self.tracker.settle(tx_id, revenue, status)

    def can_spend(self, amount: float) -> tuple[bool, str]:
        """Pre-check spending against budget rules."""
        return self.budget.check_can_spend(amount)

    def snapshot(self) -> Snapshot:
        """Get current metrics snapshot."""
        return self.metrics.compute(self.tracker.recent(10_000))

    def snapshot_1h(self) -> Snapshot:
        return self.metrics.compute_window(self.tracker.recent(10_000), 3600)

    def snapshot_24h(self) -> Snapshot:
        return self.metrics.compute_window(self.tracker.recent(10_000), 86400)


__all__ = [
    "ObservabilityStack",
    "SpendTracker",
    "BudgetManager",
    "MetricsEngine",
    "AnomalyDetector",
    "Dashboard",
    "Snapshot",
    "AgentTx",
    "Alert",
    "AlertSeverity",
    "BudgetRule",
    "PaymentRail",
    "TxStatus",
    # Exporters
    "BaseExporter",
    "JsonlExporter",
    "WebhookExporter",
    "ConsoleExporter",
    "MultiExporter",
]

__version__ = "0.1.0"
