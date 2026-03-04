"""
Base notifier abstract class for multi-channel notifications.

Defines the interface that all notifiers must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.models.anomaly import Anomaly


@dataclass
class NotificationResult:
    """Result of a notification operation."""

    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseNotifier(ABC):
    """
    Abstract base class for notification channels.

    All notifiers must implement these methods to provide
    consistent notification capabilities across different platforms.
    """

    def __init__(self, name: str):
        """Initialize base notifier.

        Args:
            name: Human-readable name for this notifier (e.g., "lark", "webhook")
        """
        self.name = name
        self._enabled = True
        self._last_notification_times: Dict[str, datetime] = {}
        self._notification_cooldown_seconds = 300  # 5 minutes

    @property
    def enabled(self) -> bool:
        """Check if this notifier is enabled."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable this notifier."""
        self._enabled = value

    @abstractmethod
    async def start(self) -> None:
        """Initialize the notifier (e.g., establish connections)."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Shutdown the notifier gracefully."""
        pass

    @abstractmethod
    async def send_anomaly(self, anomaly: Anomaly) -> NotificationResult:
        """
        Send notification for a detected anomaly.

        Args:
            anomaly: The detected anomaly

        Returns:
            NotificationResult indicating success/failure
        """
        pass

    @abstractmethod
    async def send_approval_request(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
        callback_url: Optional[str] = None,
    ) -> NotificationResult:
        """
        Send notification requesting approval for an action.

        Args:
            plan_id: Action plan ID
            action_type: Type of action
            target: Target of the action
            risk_score: Risk score of the action
            summary: Summary of the action
            callback_url: Optional URL for approval callbacks

        Returns:
            NotificationResult indicating success/failure
        """
        pass

    @abstractmethod
    async def send_remediation_status(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int] = None,
        error: Optional[str] = None,
    ) -> NotificationResult:
        """
        Send notification for remediation action status.

        Args:
            action_type: Type of remediation action
            target: Target of the action
            status: Action status
            duration_seconds: Duration of the action
            error: Error message if failed

        Returns:
            NotificationResult indicating success/failure
        """
        pass

    async def send_prediction_alert(
        self,
        metric_name: str,
        current_value: float,
        predicted_value: float,
        threshold: float,
        eta_hours: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> NotificationResult:
        """
        Send notification for a trend prediction.

        This is optional - subclasses can override if they support it.
        Default implementation returns a "not implemented" result.

        Args:
            metric_name: Name of the metric
            current_value: Current metric value
            predicted_value: Predicted future value
            threshold: Threshold that will be breached
            eta_hours: Hours until predicted breach
            labels: Metric labels

        Returns:
            NotificationResult indicating success/failure
        """
        return NotificationResult(
            success=False,
            error=f"Prediction alerts not implemented for {self.name}",
        )

    def should_notify(self, key: str) -> bool:
        """
        Check if we should send a notification (deduplication).

        Args:
            key: Unique key for this notification type

        Returns:
            True if notification should be sent
        """
        now = datetime.utcnow()
        last_time = self._last_notification_times.get(key)

        if last_time:
            elapsed = (now - last_time).total_seconds()
            if elapsed < self._notification_cooldown_seconds:
                return False

        self._last_notification_times[key] = now
        return True

    def reset_cooldown(self, key: str) -> None:
        """Reset cooldown for a specific notification key."""
        self._last_notification_times.pop(key, None)

    def clear_all_cooldowns(self) -> None:
        """Clear all notification cooldowns."""
        self._last_notification_times.clear()
