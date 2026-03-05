"""Data source abstraction layer with fallback chain and rate limiting."""

from __future__ import annotations

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class QuoteData:
    """Real-time quote snapshot for a single stock."""
    code: str
    name: str
    price: float
    change_pct: float
    open: float
    high: float
    low: float
    pre_close: float
    volume: float       # shares
    amount: float       # CNY
    turnover_rate: float = 0.0
    volume_ratio: float = 0.0
    bid1: float = 0.0
    ask1: float = 0.0
    pe: float = 0.0
    pb: float = 0.0
    market_cap: float = 0.0
    timestamp: str = ""
    source: str = ""
    # 主力相关字段
    outer_vol: float = 0.0  # 外盘成交量 (手)
    inner_vol: float = 0.0  # 内盘成交量 (手)


@dataclass
class SourceHealth:
    """Tracks health metrics for a single data source."""
    name: str
    success_count: int = 0
    fail_count: int = 0
    total_latency: float = 0.0
    last_success: float = 0.0
    last_fail: float = 0.0
    circuit_open: bool = False
    circuit_open_until: float = 0.0

    CIRCUIT_FAIL_THRESHOLD = 3
    CIRCUIT_RECOVER_SECONDS = 300

    consecutive_failures: int = 0

    def record_success(self, latency: float):
        self.success_count += 1
        self.total_latency += latency
        self.last_success = time.time()
        self.consecutive_failures = 0
        self.circuit_open = False

    def record_failure(self):
        self.fail_count += 1
        self.consecutive_failures += 1
        self.last_fail = time.time()
        if self.consecutive_failures >= self.CIRCUIT_FAIL_THRESHOLD:
            self.circuit_open = True
            self.circuit_open_until = time.time() + self.CIRCUIT_RECOVER_SECONDS
            logger.warning(f"Circuit breaker OPEN for {self.name}, recover at +{self.CIRCUIT_RECOVER_SECONDS}s")

    def is_available(self) -> bool:
        if not self.circuit_open:
            return True
        if time.time() >= self.circuit_open_until:
            self.circuit_open = False
            logger.info(f"Circuit breaker CLOSED (recovery) for {self.name}")
            return True
        return False

    @property
    def avg_latency(self) -> float:
        return self.total_latency / max(self.success_count, 1)


class RealtimeSource(ABC):
    """Abstract base for real-time quote providers."""

    name: str = "unknown"

    @abstractmethod
    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData]:
        """Fetch real-time quotes for given stock codes."""
        ...

    async def health_check(self) -> bool:
        try:
            result = await self.fetch_quotes(["000001"])
            return len(result) > 0
        except Exception:
            return False


class HistorySource(ABC):
    """Abstract base for historical data providers."""

    name: str = "unknown"

    @abstractmethod
    async def fetch_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        ...


@dataclass
class FallbackChain:
    """Manages ordered data source fallback with circuit breakers."""

    sources: list[RealtimeSource] = field(default_factory=list)
    health: dict[str, SourceHealth] = field(default_factory=dict)

    def add_source(self, source: RealtimeSource):
        self.sources.append(source)
        self.health[source.name] = SourceHealth(name=source.name)

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData]:
        last_error = None
        for source in self.sources:
            h = self.health[source.name]
            if not h.is_available():
                logger.debug(f"Skipping {source.name} (circuit open)")
                continue
            try:
                t0 = time.time()
                result = await source.fetch_quotes(codes)
                h.record_success(time.time() - t0)
                if result:
                    return result
            except Exception as e:
                h.record_failure()
                last_error = e
                logger.warning(f"{source.name} failed: {e}")
                continue
        logger.error(f"All sources exhausted for {codes[:3]}..., last error: {last_error}")
        return []

    def health_report(self) -> dict:
        return {
            name: {
                "success": h.success_count,
                "fail": h.fail_count,
                "avg_latency_ms": round(h.avg_latency * 1000, 1),
                "circuit_open": h.circuit_open,
            }
            for name, h in self.health.items()
        }
