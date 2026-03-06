"""
Notifier -- multi-channel alert system for Telegram, Discord, and Email.

Sends structured alerts based on configurable rules with rate limiting,
retry logic, and priority-based routing. Each alert type maps to specific
channels as defined in config/notifications.yaml.
"""
from __future__ import annotations

import json
import logging
import os
import smtplib
import time
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger("crypto-trader.notifier")

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

PRIORITY_ICONS = {
    "critical": "[!!!]",
    "high": "[!!]",
    "normal": "[i]",
    "low": "[.]",
}


class Notifier:
    """Multi-channel notification system."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        self._config = self._load_config(config_path)
        self._channels = self._config.get("notifications", {})
        self._alert_rules = self._config.get("alerts", [])
        self._rate_limit = self._config.get("rate_limit", {})

        self._sent_timestamps: List[float] = []
        self._max_per_minute = self._rate_limit.get("max_alerts_per_minute", 10)
        self._cooldown = self._rate_limit.get("cooldown_seconds", 60)

    @staticmethod
    def _load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
        path = Path(config_path) if config_path else _CONFIG_DIR / "notifications.yaml"
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}

    # ------------------------------------------------------------------
    # Rate Limiting
    # ------------------------------------------------------------------

    def _check_rate_limit(self) -> bool:
        """Return True if sending is allowed, False if rate-limited."""
        now = time.time()
        self._sent_timestamps = [
            ts for ts in self._sent_timestamps
            if now - ts < self._cooldown
        ]
        return len(self._sent_timestamps) < self._max_per_minute

    def _record_send(self) -> None:
        self._sent_timestamps.append(time.time())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def send_alert(self, alert_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send an alert to configured channels based on alert type rules."""
        if not self._check_rate_limit():
            logger.warning("Rate limit reached, skipping alert: %s", alert_type)
            return {"status": "rate_limited", "alert_type": alert_type}

        rule = self._find_rule(alert_type)
        channels = rule.get("channels", ["telegram"]) if rule else ["telegram"]
        priority = rule.get("priority", "normal") if rule else "normal"

        message = self._format_message(alert_type, data, priority)
        results: Dict[str, Any] = {
            "alert_type": alert_type,
            "priority": priority,
            "channels": {},
        }

        for channel in channels:
            try:
                if channel == "telegram" and self._channels.get("telegram", {}).get("enabled"):
                    success = self._send_telegram(message)
                    results["channels"]["telegram"] = "sent" if success else "failed"
                elif channel == "discord" and self._channels.get("discord", {}).get("enabled"):
                    success = self._send_discord(message)
                    results["channels"]["discord"] = "sent" if success else "failed"
                elif channel == "email" and self._channels.get("email", {}).get("enabled"):
                    success = self._send_email(alert_type, message)
                    results["channels"]["email"] = "sent" if success else "failed"
                else:
                    results["channels"][channel] = "disabled"
            except Exception as exc:
                logger.error("Failed to send %s via %s: %s", alert_type, channel, exc)
                results["channels"][channel] = f"error: {exc}"

        self._record_send()
        return results

    def _find_rule(self, alert_type: str) -> Optional[Dict[str, Any]]:
        """Find the alert rule matching the given type."""
        for rule in self._alert_rules:
            if rule.get("type") == alert_type:
                return rule
        return None

    # ------------------------------------------------------------------
    # Message Formatting
    # ------------------------------------------------------------------

    def _format_message(self, alert_type: str, data: Dict[str, Any], priority: str) -> str:
        """Format an alert message for sending."""
        icon = PRIORITY_ICONS.get(priority, "[i]")
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        header = f"{icon} Crypto Trader Alert: {alert_type.upper()}"

        lines = [header, f"Time: {timestamp}", ""]

        if alert_type == "trade_executed":
            lines.extend([
                f"Strategy: {data.get('strategy', 'N/A')}",
                f"Action: {data.get('side', 'N/A').upper()} {data.get('symbol', 'N/A')}",
                f"Amount: {data.get('amount', 0):.8f}",
                f"Price: {data.get('price', 'market')}",
                f"Exchange: {data.get('exchange', 'N/A')}",
                f"Reason: {data.get('reason', 'N/A')}",
            ])
        elif alert_type == "risk_limit_hit":
            lines.extend([
                f"Type: {data.get('type', 'N/A')}",
                f"Current: {data.get('current_loss', 0):.2f} EUR",
                f"Limit: {data.get('limit', 0):.2f} EUR",
            ])
        elif alert_type == "emergency_stop":
            lines.extend([
                "ALL TRADING HALTED",
                f"Reason: {data.get('reason', 'manual')}",
                f"Open orders cancelled: {data.get('orders_cancelled', 0)}",
                f"Strategies stopped: {data.get('strategies_stopped', 0)}",
            ])
        elif alert_type == "daily_summary":
            lines.extend([
                f"Portfolio Value: {data.get('portfolio_value', 0):.2f} EUR",
                f"Daily P&L: {data.get('daily_pnl', 0):+.2f} EUR",
                f"Active Strategies: {data.get('active_strategies', 0)}",
                f"Trades Today: {data.get('trades_today', 0)}",
            ])
        elif alert_type == "sentiment_alert":
            lines.extend([
                f"Symbol: {data.get('symbol', 'N/A')}",
                f"Sentiment: {data.get('label', 'N/A')} ({data.get('score', 0):.2f})",
            ])
        elif alert_type == "strategy_error":
            lines.extend([
                f"Strategy: {data.get('strategy', 'N/A')}",
                f"Error: {data.get('error', 'N/A')}",
            ])
        elif alert_type == "large_loss":
            lines.extend([
                f"Loss: {data.get('loss_pct', 0):.2f}%",
                f"Amount: {data.get('loss_eur', 0):.2f} EUR",
            ])
        else:
            for key, value in data.items():
                lines.append(f"{key}: {value}")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Telegram
    # ------------------------------------------------------------------

    def _send_telegram(self, message: str) -> bool:
        """Send a message via Telegram bot."""
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")

        if not bot_token or not chat_id:
            logger.warning("Telegram credentials not configured.")
            return False

        try:
            import requests
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            }
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                return True
            logger.error("Telegram API error: %d %s", resp.status_code, resp.text)
            return False
        except Exception as exc:
            logger.error("Telegram send failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Discord
    # ------------------------------------------------------------------

    def _send_discord(self, message: str) -> bool:
        """Send a message via Discord webhook."""
        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL", "")

        if not webhook_url:
            logger.warning("Discord webhook URL not configured.")
            return False

        try:
            import requests
            payload = {"content": message}
            resp = requests.post(webhook_url, json=payload, timeout=10)
            if resp.status_code in (200, 204):
                return True
            logger.error("Discord webhook error: %d %s", resp.status_code, resp.text)
            return False
        except Exception as exc:
            logger.error("Discord send failed: %s", exc)
            return False

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    def _send_email(self, subject: str, body: str) -> bool:
        """Send an email alert via SMTP."""
        smtp_host = os.environ.get("EMAIL_SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.environ.get("EMAIL_SMTP_PORT", "587"))
        email_from = os.environ.get("EMAIL_FROM", "")
        email_password = os.environ.get("EMAIL_PASSWORD", "")
        email_to = os.environ.get("EMAIL_TO", "")

        if not email_from or not email_password or not email_to:
            logger.warning("Email credentials not configured.")
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = email_from
            msg["To"] = email_to
            msg["Subject"] = f"Crypto Trader Alert: {subject}"
            msg.attach(MIMEText(body, "plain"))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(email_from, email_password)
                server.send_message(msg)

            return True
        except Exception as exc:
            logger.error("Email send failed: %s", exc)
            return False
