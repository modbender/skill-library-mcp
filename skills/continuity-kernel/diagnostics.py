from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DiagnosticsEvent:
    ts: str
    component: str
    code: str
    detail: str
    context: dict[str, Any]


class FailOpenDiagnostics:
    """Non-throwing diagnostics sink for fail-open paths.

    Tracks structured counters plus a bounded event buffer. All methods swallow
    their own exceptions to preserve fail-open behavior in the caller.
    """

    def __init__(self, keep_last: int = 50):
        self.keep_last = max(1, keep_last)
        self.counters: dict[str, int] = {}
        self.events: list[DiagnosticsEvent] = []

    @staticmethod
    def _key(component: str, code: str) -> str:
        return f"{component}.{code}"

    def emit(
        self,
        component: str,
        code: str,
        detail: str = "",
        context: dict[str, Any] | None = None,
    ) -> None:
        try:
            key = self._key(component, code)
            self.counters[key] = self.counters.get(key, 0) + 1
            self.events.append(
                DiagnosticsEvent(
                    ts=utc_now_iso(),
                    component=component,
                    code=code,
                    detail=detail,
                    context=context or {},
                )
            )
            if len(self.events) > self.keep_last:
                self.events = self.events[-self.keep_last :]
        except Exception:
            return

    def count(self, component: str, code: str) -> int:
        try:
            return self.counters.get(self._key(component, code), 0)
        except Exception:
            return 0

    def snapshot(self) -> dict[str, Any]:
        try:
            return {
                "counters": dict(self.counters),
                "events": [asdict(e) for e in self.events],
            }
        except Exception:
            return {"counters": {}, "events": []}
