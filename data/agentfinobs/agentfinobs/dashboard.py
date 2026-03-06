"""
Dashboard — lightweight HTTP server exposing metrics as JSON.

Zero external dependencies — uses only stdlib http.server.
Designed to be consumed by Grafana, custom UIs, or curl.

Usage::

    dashboard = Dashboard(tracker, budget, metrics_engine, anomaly)
    dashboard.start(port=9400)  # non-blocking, runs in background thread
"""

from __future__ import annotations

import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .anomaly import AnomalyDetector
    from .budget import BudgetManager
    from .metrics import MetricsEngine
    from .tracker import SpendTracker

logger = logging.getLogger("agentfinobs.dashboard")


class Dashboard:
    """Background HTTP server serving agent financial metrics."""

    def __init__(
        self,
        tracker: SpendTracker,
        budget: BudgetManager,
        metrics_engine: MetricsEngine,
        anomaly_detector: AnomalyDetector,
    ):
        self.tracker = tracker
        self.budget = budget
        self.metrics = metrics_engine
        self.anomaly = anomaly_detector
        self._server: HTTPServer | None = None
        self._thread: threading.Thread | None = None

    def start(self, host: str = "0.0.0.0", port: int = 9400):
        """Start dashboard in a background daemon thread."""
        dashboard = self  # capture for handler closure

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = self.path.rstrip("/")
                routes = {
                    "": dashboard._index,
                    "/healthz": dashboard._healthz,
                    "/metrics": dashboard._metrics_all,
                    "/metrics/1h": dashboard._metrics_1h,
                    "/metrics/24h": dashboard._metrics_24h,
                    "/budget": dashboard._budget_status,
                    "/alerts": dashboard._alerts,
                    "/txs/recent": dashboard._recent_txs,
                    "/anomaly/stats": dashboard._anomaly_stats,
                }
                handler_fn = routes.get(path)
                if handler_fn is None:
                    self.send_error(404, "Not found")
                    return
                self._json_response(handler_fn())

            def _json_response(self, data):
                body = json.dumps(data, indent=2).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass  # suppress default access logs

        self._server = HTTPServer((host, port), Handler)
        self._thread = threading.Thread(
            target=self._server.serve_forever,
            daemon=True,
            name="agentfinobs-dashboard",
        )
        self._thread.start()
        logger.info(f"Dashboard running on http://{host}:{port}")

    def stop(self):
        if self._server:
            self._server.shutdown()
            logger.info("Dashboard stopped")

    # ── Route handlers ─────────────────────────────────────────────────

    def _index(self) -> dict:
        return {
            "service": "agentfinobs",
            "version": "0.1.0",
            "endpoints": [
                "/healthz",
                "/metrics",
                "/metrics/1h",
                "/metrics/24h",
                "/budget",
                "/alerts",
                "/txs/recent",
                "/anomaly/stats",
            ],
        }

    def _healthz(self) -> dict:
        return {
            "status": "halted" if self.budget.is_halted else "ok",
            "halt_reason": self.budget.halt_reason,
            "tx_count": self.tracker.count,
        }

    def _metrics_all(self) -> dict:
        txs = self.tracker.recent(10_000)
        return self.metrics.compute(txs).to_dict()

    def _metrics_1h(self) -> dict:
        txs = self.tracker.recent(10_000)
        return self.metrics.compute_window(txs, 3600).to_dict()

    def _metrics_24h(self) -> dict:
        txs = self.tracker.recent(10_000)
        return self.metrics.compute_window(txs, 86400).to_dict()

    def _budget_status(self) -> dict:
        return {
            "halted": self.budget.is_halted,
            "halt_reason": self.budget.halt_reason,
            "headroom": self.budget.headroom(),
        }

    def _alerts(self) -> dict:
        budget_alerts = [a.to_dict() for a in self.budget.get_alerts(20)]
        anomaly_alerts = [a.to_dict() for a in self.anomaly.get_alerts(20)]
        return {
            "budget_alerts": budget_alerts,
            "anomaly_alerts": anomaly_alerts,
        }

    def _recent_txs(self) -> dict:
        txs = self.tracker.recent(50)
        return {"transactions": [tx.to_dict() for tx in txs]}

    def _anomaly_stats(self) -> dict:
        return self.anomaly.stats()
