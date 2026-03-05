"""Unified data manager bridging real-time sources and existing stock_data module."""

from __future__ import annotations

import logging
import sys
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import pandas as pd

from .base import FallbackChain, QuoteData
from .sina import SinaRealtimeSource
from .tencent import TencentRealtimeSource
from .eastmoney import EastMoneyRealtimeSource
from .ths import THSRealtimeSource
from cache.memory_cache import MemoryCache
from config import get_config, get_workspace_root

logger = logging.getLogger(__name__)

MIN_KLINE_ROWS = 20


class DataManager:
    """Central data manager.

    Real-time quotes: async FallbackChain (Tencent > Sina > EastMoney)
    Historical K-lines: delegates to existing stock_data.StockDataManager (sync)
    Caching: MemoryCache for hot path, SQLite via stock_data for cold path
    """

    def __init__(self):
        self._realtime_chain = FallbackChain()
        self._realtime_chain.add_source(TencentRealtimeSource())
        self._realtime_chain.add_source(SinaRealtimeSource())
        self._realtime_chain.add_source(EastMoneyRealtimeSource())
        self._realtime_chain.add_source(THSRealtimeSource())

        cfg = get_config()
        self._cache = MemoryCache(
            max_size=2000,
            default_ttl=cfg.get("cache_ttl", {}).get("realtime", 30),
        )

        self._history_mgr = None
        self._history_init_attempted = False
        self._warmed_codes: set[str] = set()

    def _get_history_manager(self):
        """Lazy-init the existing stock_data.StockDataManager."""
        if self._history_mgr is not None:
            return self._history_mgr
        if self._history_init_attempted:
            return None
        self._history_init_attempted = True
        try:
            ws = get_workspace_root()
            if str(ws) not in sys.path:
                sys.path.insert(0, str(ws))
            from stock_data.manager import StockDataManager
            self._history_mgr = StockDataManager(
                cache_db_path=str(ws / "stock_data" / "cache.db")
            )
            logger.info("StockDataManager initialized from existing stock_data module")
            return self._history_mgr
        except Exception as e:
            logger.warning(f"Failed to init StockDataManager: {e}")
            return None

    async def get_realtime_quotes(self, codes: list[str]) -> list[QuoteData]:
        cache_key = "rt:" + "_".join(sorted(codes))
        cached = self._cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Cache hit for realtime {len(codes)} codes")
            return cached

        result = await self._realtime_chain.fetch_quotes(codes)
        if result:
            self._cache.set(cache_key, result, ttl=get_config()["cache_ttl"]["realtime"])
        return result

    def get_daily_klines(
        self,
        code: str,
        days: int = 200,
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get daily K-lines. Auto-warms from source if cached data insufficient."""
        mgr = self._get_history_manager()
        if mgr is None:
            logger.error("No history manager available")
            return pd.DataFrame()

        end = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")

        # First try cache
        try:
            df = mgr.get_daily(code=code, start=start, end=end, adjust=adjust, use_cache=True)
        except Exception as e:
            logger.warning(f"get_daily cached failed for {code}: {e}")
            df = pd.DataFrame()

        # Auto-warm: if cache insufficient and not already warmed this session
        if len(df) < MIN_KLINE_ROWS and code not in self._warmed_codes:
            self._warmed_codes.add(code)
            logger.info(f"Auto-warming {code}: cache has {len(df)} rows, fetching from source")
            try:
                df = mgr.get_daily(code=code, start=start, end=end, adjust=adjust, use_cache=False)
                logger.info(f"Warmed {code}: got {len(df)} rows from source")
            except Exception as e:
                logger.warning(f"Warm fetch failed for {code}: {e}")

        return df

    def get_minute_klines(
        self,
        code: str,
        period: str = "5",
        adjust: str = "",
    ) -> pd.DataFrame:
        """Get minute K-lines via existing stock_data module."""
        mgr = self._get_history_manager()
        if mgr is None:
            return pd.DataFrame()
        try:
            return mgr.get_minute(code=code, period=period, adjust=adjust, use_cache=False)
        except Exception as e:
            logger.warning(f"get_minute failed for {code}: {e}")
            return pd.DataFrame()

    def warm_klines(self, codes: list[str], days: int = 200) -> dict:
        """Proactively fetch and cache K-lines for all given codes.

        Returns summary: {code: row_count} for each code.
        """
        mgr = self._get_history_manager()
        if mgr is None:
            return {"error": "No history manager available"}

        end = date.today().strftime("%Y-%m-%d")
        start = (date.today() - timedelta(days=days)).strftime("%Y-%m-%d")

        results = {}
        total_t0 = time.time()

        for code in codes:
            try:
                df = mgr.get_daily(code=code, start=start, end=end, adjust="", use_cache=False)
                rows = len(df)
                results[code] = rows
                self._warmed_codes.add(code)
                if rows < MIN_KLINE_ROWS:
                    logger.warning(f"Warm: {code} only got {rows} rows")
            except Exception as e:
                results[code] = f"error: {e}"
                logger.warning(f"Warm failed for {code}: {e}")

        elapsed = (time.time() - total_t0) * 1000
        logger.info(f"Warmed {len(codes)} codes in {elapsed:.0f}ms")
        return {
            "codes_warmed": len(codes),
            "elapsed_ms": round(elapsed),
            "details": results,
        }

    def health_report(self) -> dict:
        report = {
            "realtime_chain": self._realtime_chain.health_report(),
            "memory_cache": self._cache.stats(),
            "warmed_codes": len(self._warmed_codes),
        }
        mgr = self._get_history_manager()
        if mgr:
            report["history"] = mgr.health_report()
        return report

    async def close(self):
        for source in self._realtime_chain.sources:
            if hasattr(source, "close"):
                await source.close()
