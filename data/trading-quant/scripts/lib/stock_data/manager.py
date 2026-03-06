"""Stock data manager with unified API, cache, and multi-source fallback."""

from __future__ import annotations

from datetime import date

import pandas as pd

from .cache import SQLiteKlineCache
from .chain import DataSourceChain
from .sources import BaoStockSource, EastMoneySource, PyTdxSource, SinaSource
from .utils import STANDARD_COLUMNS, normalize_code, normalize_kline_df


class StockDataManager:
    """Unified manager for daily/minute stock data from multiple sources."""

    PRIORITY = {
        "daily": ["sina", "baostock", "pytdx", "eastmoney"],
        "minute": ["sina", "pytdx", "eastmoney"],
    }

    def __init__(self, cache_db_path: str = "stock_data/cache.db") -> None:
        self.cache = SQLiteKlineCache(cache_db_path)
        self.chain = DataSourceChain(self.PRIORITY)
        self.sources = {
            "sina": SinaSource(),
            "baostock": BaoStockSource(),
            "pytdx": PyTdxSource(),
            "eastmoney": EastMoneySource(),
        }

    def _empty(self) -> pd.DataFrame:
        return pd.DataFrame(columns=STANDARD_COLUMNS)

    def get_daily(
        self,
        code: str,
        start: str,
        end: str | None = None,
        adjust: str = "",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        code = normalize_code(code)
        end = end or date.today().strftime("%Y-%m-%d")
        if use_cache:
            cached = self.cache.get(code=code, frequency="daily", adjust=adjust, start=start, end=end)
            if not cached.empty:
                return cached[STANDARD_COLUMNS].sort_values("date").reset_index(drop=True)

        def _fetch(source: str):
            adapter = self.sources[source]
            if not adapter.supports_daily:
                raise RuntimeError("daily unsupported")
            raw = adapter.get_daily(code, start=start, end=end, adjust=adjust)
            norm = normalize_kline_df(raw, code=code, source=source, frequency="daily", adjust=adjust)
            if norm.empty:
                raise RuntimeError("empty result")
            self.cache.upsert(norm)
            return norm

        _, df = self.chain.fetch("daily", _fetch)
        return df[STANDARD_COLUMNS]

    def get_minute(
        self,
        code: str,
        period: str = "5",
        adjust: str = "",
        use_cache: bool = False,
    ) -> pd.DataFrame:
        code = normalize_code(code)
        freq = f"{period}m"
        if use_cache:
            cached = self.cache.get(code=code, frequency=freq, adjust=adjust)
            if not cached.empty:
                return cached[STANDARD_COLUMNS].sort_values("date").reset_index(drop=True)

        def _fetch(source: str):
            adapter = self.sources[source]
            if not adapter.supports_minute:
                raise RuntimeError("minute unsupported")
            raw = adapter.get_minute(code=code, period=period, adjust=adjust)
            norm = normalize_kline_df(raw, code=code, source=source, frequency=freq, adjust=adjust)
            if norm.empty:
                raise RuntimeError("empty result")
            self.cache.upsert(norm)
            return norm

        _, df = self.chain.fetch("minute", _fetch)
        return df[STANDARD_COLUMNS]

    def get_daily_batch(
        self,
        codes: list[str],
        start: str,
        end: str | None = None,
        adjust: str = "",
        use_cache: bool = True,
    ) -> pd.DataFrame:
        frames = []
        for code in codes:
            try:
                frames.append(
                    self.get_daily(code=code, start=start, end=end, adjust=adjust, use_cache=use_cache)
                )
            except Exception:
                continue
        if not frames:
            return self._empty()
        return pd.concat(frames, ignore_index=True)[STANDARD_COLUMNS]

    def health_report(self) -> dict:
        return {
            "chain": self.chain.health_report(),
            "cache": self.cache.stats(),
            "priorities": self.PRIORITY,
        }
