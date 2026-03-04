"""
Webhook notifier for generic HTTP webhook notifications.

Refactored from the original notification_manager to implement BaseNotifier.
"""

from datetime import datetime
from typing import Any, Dict, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.action.notifiers.base_notifier import BaseNotifier, NotificationResult
from src.config.settings import get_settings
from src.models.anomaly import Anomaly

logger = structlog.get_logger()


class WebhookNotifier(BaseNotifier):
    """
    HTTP Webhook notifier.

    Sends notifications via HTTP POST to a configured webhook URL.
    Compatible with Slack, Discord, and other webhook-based services.
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        retry_attempts: Optional[int] = None,
    ):
        super().__init__(name="webhook")
        settings = get_settings()
        self.webhook_url = webhook_url or settings.notification.webhook.url
        self.timeout_seconds = timeout_seconds or settings.notification.webhook.timeout_seconds
        self.retry_attempts = retry_attempts or settings.notification.webhook.retry_attempts

        self._client: Optional[httpx.AsyncClient] = None
        self._enabled = bool(self.webhook_url)

    async def start(self) -> None:
        """Initialize the HTTP client."""
        self._client = httpx.AsyncClient(timeout=self.timeout_seconds)
        logger.info(
            "Webhook notifier started",
            webhook_configured=bool(self.webhook_url),
        )

    async def stop(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        logger.info("Webhook notifier stopped")

    async def send_anomaly(self, anomaly: Anomaly) -> NotificationResult:
        """Send notification for a detected anomaly."""
        if not self.should_notify(f"anomaly:{anomaly.metric_key}"):
            return NotificationResult(
                success=False,
                error="Skipped due to cooldown",
            )

        message = self._format_anomaly_message(anomaly)
        return await self._send_notification(message, "anomaly", anomaly.id)

    async def send_approval_request(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
        callback_url: Optional[str] = None,
    ) -> NotificationResult:
        """Send notification requesting approval for an action."""
        message = self._format_approval_message(
            plan_id, action_type, target, risk_score, summary
        )
        return await self._send_notification(message, "approval", plan_id)

    async def send_remediation_status(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int] = None,
        error: Optional[str] = None,
    ) -> NotificationResult:
        """Send notification for remediation action status."""
        message = self._format_remediation_message(
            action_type, target, status, duration_seconds, error
        )
        return await self._send_notification(
            message, "remediation", f"{action_type}:{target}"
        )

    async def send_prediction_alert(
        self,
        metric_name: str,
        current_value: float,
        predicted_value: float,
        threshold: float,
        eta_hours: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> NotificationResult:
        """Send notification for a trend prediction."""
        key = f"prediction:{metric_name}"
        if not self.should_notify(key):
            return NotificationResult(
                success=False,
                error="Skipped due to cooldown",
            )

        message = self._format_prediction_message(
            metric_name, current_value, predicted_value, threshold, eta_hours, labels
        )
        return await self._send_notification(message, "prediction", metric_name)

    async def _send_notification(
        self,
        message: Dict[str, Any],
        notification_type: str,
        identifier: str,
    ) -> NotificationResult:
        """Send notification to webhook."""
        if not self.webhook_url:
            return NotificationResult(
                success=False,
                error="No webhook URL configured",
            )

        if not self._client:
            return NotificationResult(
                success=False,
                error="Notifier not started",
            )

        try:
            response = await self._send_with_retry(message)
            success = response.status_code < 400

            if success:
                logger.info(
                    "Webhook notification sent",
                    type=notification_type,
                    identifier=identifier,
                    status=response.status_code,
                )
                return NotificationResult(
                    success=True,
                    message_id=identifier,
                )
            else:
                logger.warning(
                    "Webhook notification failed",
                    type=notification_type,
                    identifier=identifier,
                    status=response.status_code,
                    response=response.text[:200],
                )
                return NotificationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:100]}",
                )

        except Exception as e:
            logger.error(
                "Failed to send webhook notification",
                type=notification_type,
                identifier=identifier,
                error=str(e),
            )
            return NotificationResult(
                success=False,
                error=str(e),
            )

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
