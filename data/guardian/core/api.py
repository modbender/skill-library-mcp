#!/usr/bin/env python3
"""Public Guardian v2 API for standalone library usage."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .scanner import GuardianScanner as _EngineScanner
from .settings import severity_min_score


@dataclass
class ScanResult:
    """Structured scan result returned by public API calls."""

    clean: bool
    blocked: bool
    score: int
    threats: List[Dict[str, Any]]
    channel: str
    timestamp: str
    top_threat: Optional[Dict[str, Any]] = None
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialize result into plain JSON-safe dictionary."""
        return asdict(self)


class GuardianScanner:
    """Configurable scanner for standalone applications."""

    def __init__(
        self,
        severity: str = "medium",
        db_path: Optional[str] = None,
        config_path: Optional[str] = None,
        webhook: Optional[str] = None,
        record_to_db: bool = False,
    ) -> None:
        self.webhook = webhook
        self._scanner = _EngineScanner(record_to_db=record_to_db, config_path=config_path, db_path=db_path)
        self._scanner.config["severity_threshold"] = severity
        self._scanner.threshold_score = severity_min_score(severity)

    def scan(self, text: str, channel: str = "api") -> ScanResult:
        """Scan text and optionally persist detections."""
        raw = self._scanner.scan_and_record(text, channel=channel) if self._scanner.db else self._scanner.scan(text, channel=channel)
        result = self._from_raw(raw, channel)
        if self.webhook and result.blocked:
            try:
                from integrations.webhook import GuardianWebhook

                GuardianWebhook(self.webhook).notify(result)
            except Exception:
                pass
        return result

    def close(self) -> None:
        """Close scanner resources."""
        self._scanner.close()

    @staticmethod
    def _from_raw(raw: Dict[str, Any], channel: str) -> ScanResult:
        clean = bool(raw.get("clean", True))
        blocked = bool(raw.get("blocked", False))
        score = int(raw.get("score", 0) or 0)
        threats = raw.get("threats", []) or []
        top = raw.get("top_threat")
        timestamp = str(raw.get("timestamp") or datetime.now(timezone.utc).isoformat())

        if clean:
            summary = "No threats detected."
        elif blocked:
            tid = (top or {}).get("id", "unknown")
            summary = f"Blocked due to threat {tid}."
        else:
            summary = "Potentially unsafe content detected."

        return ScanResult(
            clean=clean,
            blocked=blocked,
            score=score,
            threats=threats,
            top_threat=top,
            channel=str(raw.get("channel", channel)),
            timestamp=timestamp,
            summary=summary,
        )


def scan(text: str, channel: str = "api") -> ScanResult:
    """Zero-config one-shot scan entrypoint."""
    scanner = GuardianScanner(record_to_db=False)
    try:
        return scanner.scan(text=text, channel=channel)
    finally:
        scanner.close()
