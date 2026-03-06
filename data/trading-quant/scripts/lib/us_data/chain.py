"""Source chain with per-source throttle and circuit breaker."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable


@dataclass
class SourceStat:
    success: int = 0
    fail: int = 0
    total_latency: float = 0.0
    last_success: float | None = None
    fail_streak: int = 0
    open_until: float = 0.0
    last_call: float = 0.0

    @property
    def avg_latency(self) -> float:
        return self.total_latency / self.success if self.success else 0.0


class DataSourceChain:
    """Execute source calls by priority with reliability controls."""

    THROTTLE_SECONDS = 2
    CIRCUIT_FAIL_THRESHOLD = 3
    CIRCUIT_RECOVER_SECONDS = 600

    def __init__(self, priorities: dict[str, list[str]]):
        self.priorities = priorities
        self.stats: dict[str, SourceStat] = {}

    def _stat(self, source: str) -> SourceStat:
        if source not in self.stats:
            self.stats[source] = SourceStat()
        return self.stats[source]

    def _available(self, source: str, now: float) -> bool:
        st = self._stat(source)
        if st.open_until > now:
            return False
        wait = self.THROTTLE_SECONDS - (now - st.last_call)
        if wait > 0:
            time.sleep(wait)
        return True

    def fetch(self, category: str, fetcher: Callable[[str], object]):
        errors: list[str] = []
        for source in self.priorities.get(category, []):
            if not self._available(source, now=time.time()):
                continue
            st = self._stat(source)
            st.last_call = time.time()
            started = time.time()
            try:
                result = fetcher(source)
                st.success += 1
                st.total_latency += time.time() - started
                st.last_success = time.time()
                st.fail_streak = 0
                return source, result
            except Exception as exc:
                st.fail += 1
                st.fail_streak += 1
                errors.append(f"{source}: {exc}")
                if st.fail_streak >= self.CIRCUIT_FAIL_THRESHOLD:
                    st.open_until = time.time() + self.CIRCUIT_RECOVER_SECONDS
        raise RuntimeError("all sources failed; " + " | ".join(errors))

    def health_report(self) -> dict:
        now = time.time()
        report = {}
        for source, st in self.stats.items():
            report[source] = {
                "success": st.success,
                "fail": st.fail,
                "avg_latency": round(st.avg_latency, 4),
                "last_success": st.last_success,
                "circuit_open": st.open_until > now,
                "open_until": st.open_until if st.open_until > now else None,
            }
        return report
