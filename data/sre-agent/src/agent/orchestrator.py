"""
SRE Agent Orchestrator - Main agent loop.

Coordinates the collection, detection, and notification cycle.
"""

import asyncio
import signal
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import structlog

from src.action.notification_manager import NotificationManager
from src.cognition.anomaly_detector import AnomalyDetector
from src.cognition.baseline_engine import BaselineEngine
from src.config.infrastructure import (
    InfrastructureManager,
    ServiceType,
    ServiceStatus,
    get_infrastructure_manager,
    initialize_infrastructure,
)
from src.config.settings import get_settings
from src.perception.logs_collector import LogsCollector
from src.perception.metrics_collector import MetricsCollector
from src.perception.normalizer import DataNormalizer

logger = structlog.get_logger()


class SREAgentOrchestrator:
    """
    Main orchestrator for the SRE Agent.

    Manages the core loop:
    1. Collect metrics, logs, events
    2. Detect anomalies
    3. Send notifications
    4. (Future) Generate predictions
    5. (Future) Execute remediation
    """

    def __init__(self):
        self.settings = get_settings()
        self._running = False
        self._shutdown_event = asyncio.Event()

        # Infrastructure manager
        self._infra_manager: Optional[InfrastructureManager] = None

        # Initialize components
        self._metrics_collector: Optional[MetricsCollector] = None
        self._logs_collector: Optional[LogsCollector] = None
        self._normalizer = DataNormalizer()
        self._baseline_engine = BaselineEngine()
        self._anomaly_detector = AnomalyDetector(self._baseline_engine)
        self._notification_manager = NotificationManager()

        # Timing
        self._check_interval = self.settings.anomaly_detection.check_interval_seconds
        self._baseline_update_interval = timedelta(
            hours=self.settings.baseline.learning_interval_hours
        )
        self._last_baseline_update: Optional[datetime] = None

    async def start(self) -> None:
        """Start the SRE Agent."""
        logger.info(
            "Starting SRE Agent",
            version=self.settings.app_version,
            environment=self.settings.environment,
        )

        try:
            await self._initialize_components()
            await self._run_main_loop()
        except asyncio.CancelledError:
            logger.info("Agent cancelled")
        except Exception as e:
            logger.error("Agent error", error=str(e))
            raise
        finally:
            await self._shutdown_components()

    async def stop(self) -> None:
        """Stop the SRE Agent gracefully."""
        logger.info("Stopping SRE Agent...")
        self._running = False
        self._shutdown_event.set()

    async def _initialize_components(self) -> None:
        """Initialize all components."""
        logger.info("Initializing components...")

        # Initialize infrastructure manager (handles auto-creation if needed)
        self._infra_manager = get_infrastructure_manager()
        await self._infra_manager.initialize()

        # Get URLs from infrastructure manager
        prometheus_url = self._infra_manager.get_url(ServiceType.PROMETHEUS)
        loki_url = self._infra_manager.get_url(ServiceType.LOKI)

        # Initialize collectors with discovered URLs
        if prometheus_url:
            self._metrics_collector = MetricsCollector(url=prometheus_url)
            try:
                await self._metrics_collector.connect()
            except Exception as e:
                logger.warning("Failed to connect to Prometheus", error=str(e))
        else:
            logger.warning("Prometheus not configured or unavailable")

        if loki_url:
            self._logs_collector = LogsCollector(url=loki_url)
            try:
                await self._logs_collector.connect()
            except Exception as e:
                logger.warning("Failed to connect to Loki", error=str(e))
        else:
            logger.warning("Loki not configured or unavailable")

        # Initialize notification manager
        await self._notification_manager.start()

        # Load initial baselines if available
        await self._maybe_update_baselines(force=True)

        logger.info("Components initialized")

    async def _shutdown_components(self) -> None:
        """Shutdown all components."""
        logger.info("Shutting down components...")

        if self._metrics_collector:
            await self._metrics_collector.disconnect()

        if self._logs_collector:
            await self._logs_collector.disconnect()

        await self._notification_manager.stop()

        logger.info("Components shutdown complete")

    async def _run_main_loop(self) -> None:
        """Main agent loop."""
        self._running = True
        logger.info(
            "Starting main loop",
            check_interval_seconds=self._check_interval,
        )

        while self._running:
            try:
                cycle_start = datetime.utcnow()

                # Run detection cycle
                await self._run_detection_cycle()

                # Check if baselines need update
                await self._maybe_update_baselines()

                # Calculate sleep time
                cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
                sleep_time = max(0, self._check_interval - cycle_duration)

                if sleep_time > 0:
                    try:
                        await asyncio.wait_for(
                            self._shutdown_event.wait(),
                            timeout=sleep_time,
                        )
                        # If we get here, shutdown was requested
                        break
                    except asyncio.TimeoutError:
                        # Normal timeout, continue loop
                        pass

            except Exception as e:
                logger.error("Error in main loop", error=str(e))
                await asyncio.sleep(5)  # Brief pause before retry

    async def _run_detection_cycle(self) -> None:
        """Run a single detection cycle."""
        logger.debug("Starting detection cycle")
        cycle_start = datetime.utcnow()

        # Define collection window
        end_time = cycle_start
        start_time = end_time - timedelta(minutes=5)

        # Collect metrics
        metrics = []
        if self._metrics_collector and self._metrics_collector.is_connected:
            try:
                metrics = await self._metrics_collector.collect(start_time, end_time)
            except Exception as e:
                logger.warning("Metrics collection failed", error=str(e))

        if not metrics:
            logger.debug("No metrics collected, skipping detection")
            return

        # Normalize metrics
        normalized_metrics = [
            self._normalizer.normalize_metric_series(m) for m in metrics
        ]

        # Detect anomalies
        batch = self._anomaly_detector.detect(normalized_metrics, cycle_start)

        # Log detection results
        cycle_duration = (datetime.utcnow() - cycle_start).total_seconds()
        logger.info(
            "Detection cycle complete",
            metrics_checked=batch.total_metrics_checked,
            anomalies_detected=batch.count,
            critical_anomalies=batch.critical_count,
            duration_seconds=f"{cycle_duration:.2f}",
        )

        # Send notifications for new anomalies
        if batch.anomalies:
            sent = await self._notification_manager.notify_anomaly_batch(batch)
            logger.info("Notifications sent", count=sent)

    async def _maybe_update_baselines(self, force: bool = False) -> None:
        """Update baselines if needed."""
        now = datetime.utcnow()

        # Check if update is needed
        if not force and self._last_baseline_update:
            elapsed = now - self._last_baseline_update
            if elapsed < self._baseline_update_interval:
                return

        logger.info("Updating baselines...")

        if not self._metrics_collector or not self._metrics_collector.is_connected:
            logger.warning("Cannot update baselines: metrics collector not connected")
            return

        # Collect historical data for baseline learning
        end_time = now
        start_time = end_time - timedelta(days=self.settings.baseline.min_history_days)

        try:
            metrics = await self._metrics_collector.collect(start_time, end_time)

            baselines_updated = 0
            for series in metrics:
                if len(series.data_points) >= 24:  # Minimum for meaningful baseline
                    baseline = self._baseline_engine.learn_baseline(series)
                    if baseline:
                        baselines_updated += 1

            self._last_baseline_update = now
            logger.info(
                "Baselines updated",
                count=baselines_updated,
            )

        except Exception as e:
            logger.error("Baseline update failed", error=str(e))

    def get_status(self) -> Dict[str, Any]:
        """Get agent status."""
        status = {
            "running": self._running,
            "active_anomalies": self._anomaly_detector.state.active_count,
            "baselines_loaded": len(self._baseline_engine.baselines.baselines),
            "last_baseline_update": (
                self._last_baseline_update.isoformat()
                if self._last_baseline_update
                else None
            ),
            "metrics_collector_connected": (
                self._metrics_collector.is_connected
                if self._metrics_collector
                else False
            ),
            "logs_collector_connected": (
                self._logs_collector.is_connected
                if self._logs_collector
                else False
            ),
        }

        # Add infrastructure status
        if self._infra_manager:
            status["infrastructure"] = self._infra_manager.get_all_status()

        return status

    def get_infrastructure_status(self) -> Dict[str, Any]:
        """Get infrastructure status."""
        if self._infra_manager:
            return self._infra_manager.get_all_status()
        return {}


def setup_logging() -> None:
    """Configure structured logging."""
    settings = get_settings()

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
            if settings.environment == "production"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


async def run_agent() -> None:
    """Run the SRE Agent."""
    agent = SREAgentOrchestrator()

    # Setup signal handlers
    loop = asyncio.get_event_loop()

    def handle_signal(sig: signal.Signals) -> None:
        logger.info("Received signal", signal=sig.name)
        asyncio.create_task(agent.stop())

    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: handle_signal(s))

    await agent.start()


def main() -> None:
    """Main entry point."""
    setup_logging()
    logger.info("SRE Agent starting...")

    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        logger.info("Agent interrupted")
    except Exception as e:
        logger.error("Agent failed", error=str(e))
        sys.exit(1)

    logger.info("SRE Agent stopped")


if __name__ == "__main__":
    main()
