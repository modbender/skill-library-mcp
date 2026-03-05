"""US market data manager with batch snapshot API and failover."""

from __future__ import annotations

import pandas as pd

from .cache import SQLiteSnapshotCache
from .chain import DataSourceChain
from .sources import AKShareUSSource, YFinanceSource
from .utils import SNAPSHOT_COLUMNS, normalize_snapshot_df, normalize_us_symbol, utc_now_str


class USDataManager:
    """Unified manager for US batch snapshots."""

    PRIORITY = {
        "snapshot": ["yfinance", "akshare"],
        "snapshot_fallback": ["akshare"],
    }

    def __init__(self, cache_db_path: str = "us_data/cache.db") -> None:
        self.cache = SQLiteSnapshotCache(cache_db_path)
        self.chain = DataSourceChain(self.PRIORITY)
        self.sources = {
            "yfinance": YFinanceSource(),
            "akshare": AKShareUSSource(),
        }

    def _empty(self) -> pd.DataFrame:
        return pd.DataFrame(columns=SNAPSHOT_COLUMNS)

    def _error_rows(self, symbols: list[str], source: str) -> pd.DataFrame:
        now_s = utc_now_str()
        return pd.DataFrame(
            [
                {
                    "symbol": s,
                    "last": None,
                    "prev": None,
                    "pct": None,
                    "quote_time": now_s,
                    "source": source,
                    "status": "error",
                }
                for s in symbols
            ]
        )

    def get_snapshots(self, symbols: list[str], use_cache: bool = True) -> pd.DataFrame:
        if not symbols:
            return self._empty()

        ordered_symbols = []
        seen = set()
        for symbol in symbols:
            n = normalize_us_symbol(symbol)
            if n not in seen:
                ordered_symbols.append(n)
                seen.add(n)

        result_map: dict[str, dict] = {}
        remaining = ordered_symbols[:]

        if use_cache:
            cached = self.cache.get_latest_batch(ordered_symbols)
            if not cached.empty:
                cached = normalize_snapshot_df(cached, source="cache")
                for row in cached.itertuples(index=False):
                    if row.status == "ok":
                        result_map[row.symbol] = row._asdict()
                remaining = [s for s in ordered_symbols if s not in result_map]

        if remaining:
            def _fetch(source: str) -> pd.DataFrame:
                adapter = self.sources[source]
                df = normalize_snapshot_df(adapter.get_snapshots(remaining), source=source)
                if df.empty:
                    raise RuntimeError("empty result")
                if (df["status"] == "ok").sum() == 0:
                    raise RuntimeError("no successful symbols")
                return df

            try:
                primary_source, primary_df = self.chain.fetch("snapshot", _fetch)
            except Exception:
                primary_source, primary_df = "none", self._error_rows(remaining, source="none")

            for row in primary_df.itertuples(index=False):
                if row.status == "ok":
                    result_map[row.symbol] = row._asdict()

            unresolved = [s for s in remaining if s not in result_map]
            if unresolved:
                def _fetch_fallback(source: str) -> pd.DataFrame:
                    adapter = self.sources[source]
                    df = normalize_snapshot_df(adapter.get_snapshots(unresolved), source=source)
                    if df.empty:
                        raise RuntimeError("empty result")
                    if (df["status"] == "ok").sum() == 0:
                        raise RuntimeError("no successful symbols")
                    return df

                try:
                    _, fallback_df = self.chain.fetch("snapshot_fallback", _fetch_fallback)
                    for row in fallback_df.itertuples(index=False):
                        if row.status == "ok":
                            result_map[row.symbol] = row._asdict()
                except Exception:
                    pass

            for sym in ordered_symbols:
                if sym not in result_map:
                    result_map[sym] = {
                        "symbol": sym,
                        "last": None,
                        "prev": None,
                        "pct": None,
                        "quote_time": utc_now_str(),
                        "source": primary_source,
                        "status": "error",
                    }

        out = pd.DataFrame([result_map[s] for s in ordered_symbols], columns=SNAPSHOT_COLUMNS)
        ok_df = out[out["status"] == "ok"][SNAPSHOT_COLUMNS]
        if not ok_df.empty:
            self.cache.upsert(ok_df)
        return out

    def health_report(self) -> dict:
        return {
            "chain": self.chain.health_report(),
            "cache": self.cache.stats(),
            "priorities": self.PRIORITY,
        }
