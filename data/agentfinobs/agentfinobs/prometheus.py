"""
Prometheus exporter — expose agent financial metrics for Grafana.

Provides both a pull-mode exporter (serves /metrics endpoint) and
a push-mode exporter (calls export_tx on each transaction to update gauges).

Requires: pip install agentfinobs[prometheus]

Usage::

    from agentfinobs.prometheus import PrometheusExporter

    prom = PrometheusExporter(port=9401)
    tracker.add_listener(prom.on_tx)
    # Metrics now at http://localhost:9401/metrics
"""

from __future__ import annotations

import logging
import threading
import time
from typing import TYPE_CHECKING

from .exporters import BaseExporter

if TYPE_CHECKING:
    from .metrics import Snapshot
    from .types import AgentTx

logger = logging.getLogger("agentfinobs.prometheus")

# Lazy imports — only fail when actually used
_prometheus_available = None


def _check_prometheus():
    global _prometheus_available
    if _prometheus_available is None:
        try:
            import prometheus_client  # noqa: F401
            _prometheus_available = True
        except ImportError:
            _prometheus_available = False
    return _prometheus_available


class PrometheusExporter(BaseExporter):
    """
    Exposes agent financial metrics as Prometheus gauges/counters.

    Metrics exported:
      - agentfinobs_tx_total              (counter, labels: agent_id, rail, status)
      - agentfinobs_tx_amount_total       (counter, labels: agent_id, rail)
      - agentfinobs_tx_revenue_total      (counter, labels: agent_id)
      - agentfinobs_tx_pnl_total          (gauge, labels: agent_id)
      - agentfinobs_budget_headroom       (gauge, labels: agent_id, rule)
      - agentfinobs_burn_rate_per_hour    (gauge, labels: agent_id)
      - agentfinobs_roi_pct               (gauge, labels: agent_id)
      - agentfinobs_alert_total           (counter, labels: agent_id, severity)
    """

    def __init__(self, port: int = 9401, agent_id: str = "default"):
        if not _check_prometheus():
            raise ImportError(
                "PrometheusExporter requires prometheus_client. "
                "Install with: pip install agentfinobs[prometheus]"
            )

        import prometheus_client as prom

        # Unregister default collectors for a clean /metrics page
        for c in list(prom.REGISTRY._names_to_collectors.values()):
            try:
                prom.REGISTRY.unregister(c)
            except Exception:
                pass

        self._agent_id = agent_id
        self._registry = prom.REGISTRY

        # Counters
        self.tx_total = prom.Counter(
            "agentfinobs_tx_total",
            "Total transactions recorded",
            ["agent_id", "rail", "status"],
        )
        self.tx_amount_total = prom.Counter(
            "agentfinobs_tx_amount_total",
            "Total USD spent",
            ["agent_id", "rail"],
        )
        self.tx_revenue_total = prom.Counter(
            "agentfinobs_tx_revenue_total",
            "Total USD revenue",
            ["agent_id"],
        )

        # Gauges
        self.tx_pnl_total = prom.Gauge(
            "agentfinobs_tx_pnl_total",
            "Cumulative PnL (USD)",
            ["agent_id"],
        )
        self.burn_rate = prom.Gauge(
            "agentfinobs_burn_rate_per_hour",
            "Current burn rate (USD/hour)",
            ["agent_id"],
        )
        self.roi_pct = prom.Gauge(
            "agentfinobs_roi_pct",
            "Current ROI percentage",
            ["agent_id"],
        )
        self.budget_headroom = prom.Gauge(
            "agentfinobs_budget_headroom",
            "Remaining budget headroom (USD)",
            ["agent_id", "rule"],
        )
        self.alert_total = prom.Counter(
            "agentfinobs_alert_total",
            "Total alerts fired",
            ["agent_id", "severity"],
        )

        # Running totals for PnL
        self._total_spent = 0.0
        self._total_revenue = 0.0

        # Start HTTP server
        prom.start_http_server(port)
        logger.info(f"Prometheus metrics at http://0.0.0.0:{port}/metrics")

    def export_tx(self, tx: "AgentTx") -> None:
        """Update Prometheus metrics on each transaction."""
        aid = tx.agent_id or self._agent_id
        rail = tx.rail.value

        self.tx_total.labels(agent_id=aid, rail=rail, status=tx.status.value).inc()
        self.tx_amount_total.labels(agent_id=aid, rail=rail).inc(tx.amount)

        self._total_spent += tx.amount
        self._total_revenue += tx.revenue
        pnl = self._total_revenue - self._total_spent
        self.tx_pnl_total.labels(agent_id=aid).set(pnl)

        if tx.revenue > 0:
            self.tx_revenue_total.labels(agent_id=aid).inc(tx.revenue)

    def on_tx(self, tx: "AgentTx") -> None:
        """Alias for use as a SpendTracker listener."""
        self.export_tx(tx)

    def export_snapshot(self, snapshot: "Snapshot") -> None:
        """Update aggregate gauges from a snapshot."""
        aid = self._agent_id

        self.burn_rate.labels(agent_id=aid).set(snapshot.burn_rate_per_hour)
        if snapshot.roi_pct is not None:
            self.roi_pct.labels(agent_id=aid).set(snapshot.roi_pct)

    def update_budget(self, headroom: dict[str, float], agent_id: str | None = None):
        """Update budget headroom gauges. Call from BudgetManager."""
        aid = agent_id or self._agent_id
        for rule_name, remaining in headroom.items():
            self.budget_headroom.labels(agent_id=aid, rule=rule_name).set(remaining)

    def record_alert(self, severity: str, agent_id: str | None = None):
        """Increment alert counter."""
        aid = agent_id or self._agent_id
        self.alert_total.labels(agent_id=aid, severity=severity).inc()
