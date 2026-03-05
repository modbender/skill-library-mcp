"""
Notification manager for sending alerts via HTTP webhook.

Supports:
- Anomaly notifications
- Prediction alerts
- Remediation status updates
- Approval requests
"""

from datetime import datetime
from string import Template
from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.config.settings import get_settings
from src.models.anomaly import Anomaly, AnomalyBatch

logger = structlog.get_logger()


class NotificationManager:
    """
    Manages notifications via HTTP webhook.

    Features:
    - Template-based message formatting
    - Retry logic for reliability
    - Rate limiting
    - Deduplication
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        retry_attempts: Optional[int] = None,
    ):
        settings = get_settings()
        self.webhook_url = webhook_url or settings.notification.webhook.url
        self.timeout_seconds = timeout_seconds or settings.notification.webhook.timeout_seconds
        self.retry_attempts = retry_attempts or settings.notification.webhook.retry_attempts

        self._client: httpx.Optional[AsyncClient] = None
        self._last_notification_times: Dict[str, datetime] = {}
        self._notification_cooldown_seconds = 300  # 5 minutes between duplicate notifications

    async def start(self) -> None:
        """Initialize the notification manager."""
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        logger.info("Notification manager started", webhook_configured=bool(self.webhook_url))

    async def stop(self) -> None:
        """Shutdown the notification manager."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Notification manager stopped")

    async def notify_anomaly(self, anomaly: Anomaly) -> bool:
        """
        Send notification for a detected anomaly.

        Args:
            anomaly: The detected anomaly

        Returns:
            True if notification was sent successfully
        """
        if not self._should_notify(f"anomaly:{anomaly.metric_key}"):
            logger.debug(
                "Skipping duplicate notification",
                anomaly_id=anomaly.id,
            )
            return False

        message = self._format_anomaly_message(anomaly)
        return await self._send_notification(message, "anomaly", anomaly.id)

    async def notify_anomaly_batch(self, batch: AnomalyBatch) -> int:
        """
        Send notifications for a batch of anomalies.

        Args:
            batch: Batch of detected anomalies

        Returns:
            Number of notifications sent
        """
        sent_count = 0
        for anomaly in batch.anomalies:
            if await self.notify_anomaly(anomaly):
                sent_count += 1
        return sent_count

    async def notify_prediction(
        self,
        metric_name: str,
        current_value: float,
        predicted_value: float,
        threshold: float,
        eta_hours: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Send notification for a trend prediction.

        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            predicted_value: Predicted future value
            threshold: Threshold that will be breached
            eta_hours: Hours until predicted breach
            labels: Metric labels

        Returns:
            True if notification was sent successfully
        """
        key = f"prediction:{metric_name}"
        if not self._should_notify(key):
            return False

        message = self._format_prediction_message(
            metric_name, current_value, predicted_value, threshold, eta_hours, labels
        )
        return await self._send_notification(message, "prediction", metric_name)

    async def notify_remediation(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int] = None,
        error: Optional[str] = None,
    ) -> bool:
        """
        Send notification for remediation action status.

        Args:
            action_type: Type of remediation action
            target: Target of the action
            status: Action status
            duration_seconds: Duration of the action
            error: Error message if failed

        Returns:
            True if notification was sent successfully
        """
        message = self._format_remediation_message(
            action_type, target, status, duration_seconds, error
        )
        return await self._send_notification(message, "remediation", f"{action_type}:{target}")

    async def notify_approval_request(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
    ) -> bool:
        """
        Send notification requesting approval for an action.

        Args:
            plan_id: Action plan ID
            action_type: Type of action
            target: Target of the action
            risk_score: Risk score of the action
            summary: Summary of the action

        Returns:
            True if notification was sent successfully
        """
        message = self._format_approval_message(
            plan_id, action_type, target, risk_score, summary
        )
        return await self._send_notification(message, "approval", plan_id)

    async def _send_notification(
        self,
        message: Dict[str, Any],
        notification_type: str,
        identifier: str,
    ) -> bool:
        """Send notification to webhook."""
        if not self.webhook_url:
            logger.warning("No webhook URL configured, skipping notification")
            return False

        if not self._client:
            logger.warning("Notification manager not started")
            return False

        try:
            response = await self._send_with_retry(message)
            success = response.status_code < 400

            if success:
                logger.info(
                    "Notification sent",
                    type=notification_type,
                    identifier=identifier,
                    status=response.status_code,
                )
            else:
                logger.warning(
                    "Notification failed",
                    type=notification_type,
                    identifier=identifier,
                    status=response.status_code,
                    response=response.text[:200],
                )

            return success

        except Exception as e:
            logger.error(
                "Failed to send notification",
                type=notification_type,
                identifier=identifier,
                error=str(e),
            )
            return False

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _send_with_retry(self, message: Dict[str, Any]) -> httpx.Response:
        """Send notification with retry logic."""
        return await self._client.post(
            self.webhook_url,
            json=message,
            headers={"Content-Type": "application/json"},
        )

    def _should_notify(self, key: str) -> bool:
        """Check if we should send a notification (deduplication)."""
        now = datetime.utcnow()
        last_time = self._last_notification_times.get(key)

        if last_time:
            elapsed = (now - last_time).total_seconds()
            if elapsed < self._notification_cooldown_seconds:
                return False

        self._last_notification_times[key] = now
        return True

    def _format_anomaly_message(self, anomaly: Anomaly) -> Dict[str, Any]:
        """Format anomaly notification message."""
        direction = "above" if anomaly.deviation > 0 else "below"
        severity_emoji = {
            "low": "🟡",
            "medium": "🟠",
            "high": "🔴",
            "critical": "🚨",
        }

        return {
            "type": "anomaly",
            "id": anomaly.id,
            "severity": anomaly.severity.value,
            "timestamp": anomaly.detected_at.isoformat(),
            "title": f"{severity_emoji.get(anomaly.severity.value, '⚠️')} Anomaly Detected: {anomaly.metric_name}",
            "message": (
                f"**Metric**: {anomaly.metric_name}\n"
                f"**Category**: {anomaly.category.value}\n"
                f"**Current Value**: {anomaly.current_value:.4f}\n"
                f"**Baseline Value**: {anomaly.baseline_value:.4f}\n"
                f"**Deviation**: {abs(anomaly.deviation):.2f} sigma {direction} "
                f"({anomaly.deviation_percent:+.1f}%)\n"
                f"**Duration**: {anomaly.duration_minutes} minutes\n"
                f"**Type**: {anomaly.anomaly_type.value}"
            ),
            "labels": anomaly.labels,
            "metadata": {
                "deviation": anomaly.deviation,
                "deviation_percent": anomaly.deviation_percent,
                "ensemble_score": anomaly.ensemble_score,
                "category": anomaly.category.value,
            },
        }

    def _format_prediction_message(
        self,
        metric_name: str,
        current_value: float,
        predicted_value: float,
        threshold: float,
        eta_hours: float,
        labels: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        """Format prediction notification message."""
        return {
            "type": "prediction",
            "timestamp": datetime.utcnow().isoformat(),
            "title": f"⚠️ Trend Alert: {metric_name}",
            "message": (
                f"**Metric**: {metric_name}\n"
                f"**Current Value**: {current_value:.4f}\n"
                f"**Predicted Value**: {predicted_value:.4f}\n"
                f"**Threshold**: {threshold:.4f}\n"
                f"**ETA**: {eta_hours:.1f} hours"
            ),
            "labels": labels or {},
            "metadata": {
                "current_value": current_value,
                "predicted_value": predicted_value,
                "threshold": threshold,
                "eta_hours": eta_hours,
            },
        }

    def _format_remediation_message(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int],
        error: Optional[str],
    ) -> Dict[str, Any]:
        """Format remediation notification message."""
        status_emoji = {
            "success": "✅",
            "failed": "❌",
            "executing": "🔄",
            "rolled_back": "↩️",
        }

        message_parts = [
            f"**Action**: {action_type}",
            f"**Target**: {target}",
            f"**Status**: {status}",
        ]

        if duration_seconds:
            message_parts.append(f"**Duration**: {duration_seconds}s")

        if error:
            message_parts.append(f"**Error**: {error}")

        return {
            "type": "remediation",
            "timestamp": datetime.utcnow().isoformat(),
            "title": f"{status_emoji.get(status, '🔧')} Remediation: {action_type}",
            "message": "\n".join(message_parts),
            "metadata": {
                "action_type": action_type,
                "target": target,
                "status": status,
                "duration_seconds": duration_seconds,
                "error": error,
            },
        }

    def _format_approval_message(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
    ) -> Dict[str, Any]:
        """Format approval request message."""
        return {
            "type": "approval_request",
            "timestamp": datetime.utcnow().isoformat(),
            "plan_id": plan_id,
            "title": f"🔐 Approval Required: {action_type}",
            "message": (
                f"**Plan ID**: {plan_id}\n"
                f"**Action**: {action_type}\n"
                f"**Target**: {target}\n"
                f"**Risk Score**: {risk_score:.2f}\n"
                f"**Summary**: {summary}"
            ),
            "metadata": {
                "plan_id": plan_id,
                "action_type": action_type,
                "target": target,
                "risk_score": risk_score,
            },
        }
