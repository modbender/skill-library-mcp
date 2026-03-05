"""
AnomalyDetector — statistical anomaly detection for agent spending.

Uses simple z-score analysis on transaction amounts to flag unusual
spending. No ML dependencies — just math.
"""

from __future__ import annotations

import logging
import math
import time
from collections import deque

from .types import AgentTx, Alert, AlertSeverity

logger = logging.getLogger("agentfinobs.anomaly")


class AnomalyDetector:
    """
    Detects anomalous spending using a rolling z-score approach.

    Maintains a sliding window of recent transaction amounts. When a new
    tx is more than `z_threshold` standard deviations from the rolling
    mean, an alert fires.

    Usage::

        detector = AnomalyDetector(window_size=100, z_threshold=3.0)
        tracker.add_listener(detector.on_tx)

        # Check for alerts
        for alert in detector.get_alerts():
            print(alert.message)
    """

    def __init__(
        self,
        window_size: int = 200,
        z_threshold: float = 3.0,
        min_samples: int = 10,
        cooldown_seconds: float = 60.0,
    ):
        self.window_size = window_size
        self.z_threshold = z_threshold
        self.min_samples = min_samples
        self.cooldown_seconds = cooldown_seconds

        self._amounts: deque[float] = deque(maxlen=window_size)
        self._alerts: list[Alert] = []
        self._last_alert_time: float = 0

        # Running stats (Welford's online algorithm)
        self._n: int = 0
        self._mean: float = 0.0
        self._m2: float = 0.0

    def on_tx(self, tx: AgentTx):
        """Process a new transaction and check for anomalies."""
        amount = tx.amount
        self._update_stats(amount)
        self._amounts.append(amount)

        if self._n < self.min_samples:
            return

        z = self._z_score(amount)
        if z is not None and abs(z) > self.z_threshold:
            self._maybe_alert(tx, z)

    def get_alerts(self, last_n: int = 20) -> list[Alert]:
        return self._alerts[-last_n:]

    def stats(self) -> dict:
        """Current rolling statistics."""
        return {
            "n": self._n,
            "mean": round(self._mean, 4),
            "stddev": round(self._stddev(), 4),
            "window_size": self.window_size,
            "z_threshold": self.z_threshold,
        }

    # ── Internal ───────────────────────────────────────────────────────

    def _update_stats(self, x: float):
        """Welford's online algorithm for running mean/variance."""
        self._n += 1
        delta = x - self._mean
        self._mean += delta / self._n
        delta2 = x - self._mean
        self._m2 += delta * delta2

    def _stddev(self) -> float:
        if self._n < 2:
            return 0.0
        return math.sqrt(self._m2 / (self._n - 1))

    def _z_score(self, x: float) -> float | None:
        std = self._stddev()
        if std == 0:
            return None
        return (x - self._mean) / std

    def _maybe_alert(self, tx: AgentTx, z_score: float):
        now = time.time()
        if now - self._last_alert_time < self.cooldown_seconds:
            return

        self._last_alert_time = now
        alert = Alert(
            severity=AlertSeverity.WARNING,
            rule_name="anomaly_zscore",
            message=(
                f"Anomalous tx detected: ${tx.amount:.4f} "
                f"(z={z_score:+.2f}, mean=${self._mean:.4f}, "
                f"std=${self._stddev():.4f})"
            ),
            agent_id=tx.agent_id,
            context={
                "tx_id": tx.tx_id,
                "amount": tx.amount,
                "z_score": round(z_score, 2),
                "rolling_mean": round(self._mean, 4),
                "rolling_std": round(self._stddev(), 4),
            },
        )
        self._alerts.append(alert)
        logger.warning(f"[ANOMALY] {alert.message}")
