"""
Lark (Feishu) notifier with interactive card support.

Supports:
- Interactive approval cards with buttons
- Anomaly notifications
- Remediation status updates
- Card message updates after actions
"""

import hashlib
import hmac
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.action.notifiers.base_notifier import BaseNotifier, NotificationResult
from src.config.settings import get_settings
from src.models.anomaly import Anomaly

logger = structlog.get_logger()


class LarkNotifier(BaseNotifier):
    """
    Lark (Feishu) notifier with interactive card support.

    Features:
    - Interactive approval cards with approve/reject buttons
    - Rich card layouts for anomaly notifications
    - Message updates after user actions
    - Signature verification for callbacks
    """

    def __init__(
        self,
        webhook_url: Optional[str] = None,
        app_id: Optional[str] = None,
        app_secret: Optional[str] = None,
        verification_token: Optional[str] = None,
        encrypt_key: Optional[str] = None,
    ):
        super().__init__(name="lark")
        settings = get_settings()

        self.webhook_url = webhook_url or settings.lark.webhook_url
        self.app_id = app_id or settings.lark.app_id
        self.app_secret = app_secret or settings.lark.app_secret
        self.verification_token = verification_token or settings.lark.verification_token
        self.encrypt_key = encrypt_key or settings.lark.encrypt_key

        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._enabled = settings.lark.enabled and bool(self.webhook_url)

        # Store message IDs for updates
        self._message_id_cache: Dict[str, str] = {}

    async def start(self) -> None:
        """Initialize the HTTP client and obtain access token if needed."""
        self._client = httpx.AsyncClient(timeout=30)

        if self.app_id and self.app_secret:
            await self._refresh_access_token()

        logger.info(
            "Lark notifier started",
            webhook_configured=bool(self.webhook_url),
            api_configured=bool(self._access_token),
        )

    async def stop(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
        self._message_id_cache.clear()
        logger.info("Lark notifier stopped")

    async def send_anomaly(self, anomaly: Anomaly) -> NotificationResult:
        """Send anomaly notification as a rich card."""
        if not self.should_notify(f"anomaly:{anomaly.metric_key}"):
            return NotificationResult(
                success=False,
                error="Skipped due to cooldown",
            )

        card = self._build_anomaly_card(anomaly)
        return await self._send_card_message(card, f"anomaly:{anomaly.id}")

    async def send_approval_request(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
        callback_url: Optional[str] = None,
    ) -> NotificationResult:
        """Send interactive approval request card with buttons."""
        card = self._build_approval_card(
            plan_id, action_type, target, risk_score, summary, callback_url
        )
        result = await self._send_card_message(card, f"approval:{plan_id}")

        if result.success and result.message_id:
            self._message_id_cache[plan_id] = result.message_id

        return result

    async def send_remediation_status(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int] = None,
        error: Optional[str] = None,
    ) -> NotificationResult:
        """Send remediation status notification."""
        card = self._build_remediation_card(
            action_type, target, status, duration_seconds, error
        )
        return await self._send_card_message(
            card, f"remediation:{action_type}:{target}"
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
        """Send prediction alert as a card."""
        key = f"prediction:{metric_name}"
        if not self.should_notify(key):
            return NotificationResult(
                success=False,
                error="Skipped due to cooldown",
            )

        card = self._build_prediction_card(
            metric_name, current_value, predicted_value, threshold, eta_hours, labels
        )
        return await self._send_card_message(card, key)

    async def update_approval_card(
        self,
        plan_id: str,
        status: str,
        approver: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> NotificationResult:
        """Update an approval card after action is taken."""
        message_id = self._message_id_cache.get(plan_id)
        if not message_id:
            return NotificationResult(
                success=False,
                error=f"No message found for plan {plan_id}",
            )

        card = self._build_approval_result_card(plan_id, status, approver, reason)
        return await self._update_card_message(message_id, card)

    def verify_callback_signature(
        self,
        timestamp: str,
        nonce: str,
        body: str,
        signature: str,
    ) -> bool:
        """Verify Lark callback signature."""
        if not self.verification_token:
            logger.warning("No verification token configured")
            return False

        # Lark signature: sha256(timestamp + nonce + verification_token + body)
        content = f"{timestamp}{nonce}{self.verification_token}{body}"
        expected_signature = hashlib.sha256(content.encode()).hexdigest()

        return hmac.compare_digest(expected_signature, signature)

    async def _send_card_message(
        self, card: Dict[str, Any], identifier: str
    ) -> NotificationResult:
        """Send a card message via webhook."""
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
            payload = {
                "msg_type": "interactive",
                "card": card,
            }

            response = await self._send_with_retry(payload)
            data = response.json()

            if data.get("code") == 0 or data.get("StatusCode") == 0:
                logger.info(
                    "Lark card message sent",
                    identifier=identifier,
                )
                return NotificationResult(
                    success=True,
                    message_id=data.get("data", {}).get("message_id"),
                    metadata={"response": data},
                )
            else:
                logger.warning(
                    "Lark card message failed",
                    identifier=identifier,
                    error=data.get("msg") or data.get("StatusMessage"),
                )
                return NotificationResult(
                    success=False,
                    error=data.get("msg") or data.get("StatusMessage") or "Unknown error",
                )

        except Exception as e:
            logger.error(
                "Failed to send Lark card message",
                identifier=identifier,
                error=str(e),
            )
            return NotificationResult(
                success=False,
                error=str(e),
            )

    async def _update_card_message(
        self, message_id: str, card: Dict[str, Any]
    ) -> NotificationResult:
        """Update an existing card message via API."""
        if not self._access_token:
            return NotificationResult(
                success=False,
                error="No access token available for message updates",
            )

        try:
            import json as json_lib

            await self._ensure_access_token()

            url = f"https://open.feishu.cn/open-apis/im/v1/messages/{message_id}"
            headers = {
                "Authorization": f"Bearer {self._access_token}",
                "Content-Type": "application/json",
            }
            payload = {
                "content": json_lib.dumps(card),
            }

            response = await self._client.patch(url, json=payload, headers=headers)
            data = response.json()

            if data.get("code") == 0:
                return NotificationResult(
                    success=True,
                    message_id=message_id,
                )
            else:
                return NotificationResult(
                    success=False,
                    error=data.get("msg", "Unknown error"),
                )

        except Exception as e:
            logger.error(
                "Failed to update Lark message",
                message_id=message_id,
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
    async def _send_with_retry(self, payload: Dict[str, Any]) -> httpx.Response:
        """Send message with retry logic."""
        return await self._client.post(
            self.webhook_url,
            json=payload,
            headers={"Content-Type": "application/json"},
        )

    async def _refresh_access_token(self) -> None:
        """Refresh Lark access token."""
        if not self.app_id or not self.app_secret:
            return

        try:
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret,
            }

            response = await self._client.post(url, json=payload)
            data = response.json()

            if data.get("code") == 0:
                self._access_token = data.get("tenant_access_token")
                # Token expires in 2 hours, refresh at 1.5 hours
                self._token_expires_at = time.time() + 5400
                logger.info("Lark access token refreshed")
            else:
                logger.error(
                    "Failed to get Lark access token",
                    error=data.get("msg"),
                )

        except Exception as e:
            logger.error("Failed to refresh Lark access token", error=str(e))

    async def _ensure_access_token(self) -> None:
        """Ensure access token is valid."""
        if time.time() >= self._token_expires_at:
            await self._refresh_access_token()

    def _build_anomaly_card(self, anomaly: Anomaly) -> Dict[str, Any]:
        """Build card for anomaly notification."""
        direction = "above" if anomaly.deviation > 0 else "below"
        severity_colors = {
            "low": "yellow",
            "medium": "orange",
            "high": "red",
            "critical": "red",
        }

        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"Anomaly Detected: {anomaly.metric_name}",
                    "tag": "plain_text",
                },
                "template": severity_colors.get(anomaly.severity.value, "orange"),
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Category:** {anomaly.category.value}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Severity:** {anomaly.severity.value.upper()}",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Current Value:** {anomaly.current_value:.4f}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Baseline:** {anomaly.baseline_value:.4f}",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Deviation:** {abs(anomaly.deviation):.2f}σ {direction}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Duration:** {anomaly.duration_minutes} min",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"Detected at: {anomaly.detected_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        },
                    ],
                },
            ],
        }

    def _build_approval_card(
        self,
        plan_id: str,
        action_type: str,
        target: str,
        risk_score: float,
        summary: str,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build interactive approval card with buttons."""
        # Determine risk level color
        if risk_score >= 0.8:
            risk_color = "red"
            risk_label = "CRITICAL"
        elif risk_score >= 0.6:
            risk_color = "orange"
            risk_label = "HIGH"
        else:
            risk_color = "yellow"
            risk_label = "MEDIUM"

        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"Approval Required: {action_type}",
                    "tag": "plain_text",
                },
                "template": risk_color,
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "content": f"**Plan ID:** `{plan_id}`",
                        "tag": "lark_md",
                    },
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Target:** {target}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Risk:** {risk_score:.2f} ({risk_label})",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "content": f"**Summary:**\n{summary}",
                        "tag": "lark_md",
                    },
                },
                {"tag": "hr"},
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {
                                "content": "Approve",
                                "tag": "plain_text",
                            },
                            "type": "primary",
                            "value": {
                                "action": "approve",
                                "plan_id": plan_id,
                            },
                        },
                        {
                            "tag": "button",
                            "text": {
                                "content": "Reject",
                                "tag": "plain_text",
                            },
                            "type": "danger",
                            "value": {
                                "action": "reject",
                                "plan_id": plan_id,
                            },
                        },
                    ],
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"Created at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                        },
                    ],
                },
            ],
        }

    def _build_approval_result_card(
        self,
        plan_id: str,
        status: str,
        approver: Optional[str] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build card showing approval result (for card update)."""
        if status == "approved":
            color = "green"
            status_text = "APPROVED"
        elif status == "rejected":
            color = "red"
            status_text = "REJECTED"
        else:
            color = "grey"
            status_text = status.upper()

        elements = [
            {
                "tag": "div",
                "text": {
                    "content": f"**Plan ID:** `{plan_id}`",
                    "tag": "lark_md",
                },
            },
            {
                "tag": "div",
                "text": {
                    "content": f"**Status:** {status_text}",
                    "tag": "lark_md",
                },
            },
        ]

        if approver:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"**By:** {approver}",
                    "tag": "lark_md",
                },
            })

        if reason:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"**Reason:** {reason}",
                    "tag": "lark_md",
                },
            })

        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": f"Updated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
                },
            ],
        })

        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"Approval {status_text}",
                    "tag": "plain_text",
                },
                "template": color,
            },
            "elements": elements,
        }

    def _build_remediation_card(
        self,
        action_type: str,
        target: str,
        status: str,
        duration_seconds: Optional[int] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Build card for remediation status."""
        status_colors = {
            "success": "green",
            "failed": "red",
            "executing": "blue",
            "rolled_back": "orange",
        }

        elements = [
            {
                "tag": "div",
                "fields": [
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**Action:** {action_type}",
                            "tag": "lark_md",
                        },
                    },
                    {
                        "is_short": True,
                        "text": {
                            "content": f"**Target:** {target}",
                            "tag": "lark_md",
                        },
                    },
                ],
            },
            {
                "tag": "div",
                "text": {
                    "content": f"**Status:** {status.upper()}",
                    "tag": "lark_md",
                },
            },
        ]

        if duration_seconds:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"**Duration:** {duration_seconds}s",
                    "tag": "lark_md",
                },
            })

        if error:
            elements.append({
                "tag": "div",
                "text": {
                    "content": f"**Error:** {error}",
                    "tag": "lark_md",
                },
            })

        elements.append({
            "tag": "note",
            "elements": [
                {
                    "tag": "plain_text",
                    "content": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                },
            ],
        })

        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"Remediation: {action_type}",
                    "tag": "plain_text",
                },
                "template": status_colors.get(status, "grey"),
            },
            "elements": elements,
        }

    def _build_prediction_card(
        self,
        metric_name: str,
        current_value: float,
        predicted_value: float,
        threshold: float,
        eta_hours: float,
        labels: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Build card for prediction alert."""
        return {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "content": f"Trend Alert: {metric_name}",
                    "tag": "plain_text",
                },
                "template": "orange",
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Current:** {current_value:.4f}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Predicted:** {predicted_value:.4f}",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**Threshold:** {threshold:.4f}",
                                "tag": "lark_md",
                            },
                        },
                        {
                            "is_short": True,
                            "text": {
                                "content": f"**ETA:** {eta_hours:.1f} hours",
                                "tag": "lark_md",
                            },
                        },
                    ],
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        },
                    ],
                },
            ],
        }
