"""Delivery-layer exception types for Codeflow.

The parser (parse-stream.py) must never crash the relay on transient delivery
failures. Delivery adapters may raise these so the delivery governor can apply
retry/rate-limit policy and emit lightweight delivery events into stream.jsonl.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class DeliveryError(Exception):
    platform: str
    op: str
    code: Optional[int] = None
    retry_after: Optional[float] = None
    reason: str = ""
    anchor: Optional[int] = None

    def __str__(self) -> str:  # pragma: no cover (debug convenience)
        parts: list[str] = []
        if self.platform:
            parts.append(self.platform)
        if self.op:
            parts.append(self.op)
        if self.code is not None:
            parts.append(str(self.code))
        if self.retry_after is not None:
            parts.append(f"retry_after={self.retry_after}")
        if self.reason:
            parts.append(self.reason)
        if self.anchor is not None:
            parts.append(f"anchor={self.anchor}")
        return " ".join(parts) if parts else "DeliveryError"


@dataclass(frozen=True, slots=True)
class DeliveryRateLimited(DeliveryError):
    """Raised when a platform returns an explicit rate-limit response (e.g., HTTP 429)."""
