"""Guardian webhook notifier integration."""

from __future__ import annotations

import json
import urllib.request
from typing import Any, Dict

from core.api import ScanResult


class GuardianWebhook:
    """Posts Guardian scan results to a webhook URL as JSON."""

    def __init__(self, url: str, timeout: int = 5) -> None:
        self.url = url
        self.timeout = timeout

    def notify(self, result: ScanResult) -> int:
        """Send a threat-detected event to the configured webhook URL.

        Returns the HTTP response status code.
        """
        payload: Dict[str, Any] = {
            "event": "guardian.threat.detected",
            "clean": result.clean,
            "blocked": result.blocked,
            "score": result.score,
            "threats": result.threats,
            "channel": result.channel,
            "timestamp": result.timestamp,
            "summary": result.summary,
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout) as resp:
            return resp.status
