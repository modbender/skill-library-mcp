"""AKShare source adapter for US snapshots fallback."""

from __future__ import annotations

import pandas as pd

from .base import DataSource
from ..utils import utc_now_str


class AKShareUSSource(DataSource):
    """Fetch US spot quotes through AKShare endpoints."""

    name = "akshare"
    supports_snapshot = True

    def _ak(self):
        try:
            import akshare as ak

            return ak
        except Exception as exc:
            raise RuntimeError("akshare unavailable") from exc

    def _spot_df(self) -> pd.DataFrame:
        ak = self._ak()
        for fn in ("stock_us_spot_em", "stock_us_spot"):
            if hasattr(ak, fn):
                try:
                    df = getattr(ak, fn)()
                    if df is not None and not df.empty:
                        return df
                except Exception:
                    continue
        return pd.DataFrame()

    def get_snapshots(self, symbols: list[str]) -> pd.DataFrame:
        spot = self._spot_df()
        now_s = utc_now_str()
        if spot.empty:
            return pd.DataFrame(
                [{"symbol": s, "last": None, "prev": None, "pct": None, "quote_time": now_s, "status": "error"} for s in symbols]
            )

        code_col = next((c for c in ["代码", "symbol", "Symbol", "代码.Code"] if c in spot.columns), None)
        last_col = next((c for c in ["最新价", "close", "Close", "最新", "现价"] if c in spot.columns), None)
        prev_col = next((c for c in ["昨收", "pre_close", "Prev Close"] if c in spot.columns), None)
        pct_col = next((c for c in ["涨跌幅", "change_percent", "Change %"] if c in spot.columns), None)

        if code_col is None or last_col is None:
            return pd.DataFrame(
                [{"symbol": s, "last": None, "prev": None, "pct": None, "quote_time": now_s, "status": "error"} for s in symbols]
            )

        t = spot.copy()
        t["symbol"] = (
            t[code_col].astype(str).str.strip().str.upper().str.split(".").str[-1].str.replace("$", "", regex=False)
        )
        t["last"] = pd.to_numeric(t[last_col], errors="coerce")
        t["prev"] = pd.to_numeric(t[prev_col], errors="coerce") if prev_col else pd.NA
        t["pct"] = pd.to_numeric(t[pct_col], errors="coerce") if pct_col else pd.NA
        if prev_col is None and pct_col is not None:
            pct_factor = 1.0 + (t["pct"] / 100.0)
            t.loc[pct_factor != 0, "prev"] = t["last"] / pct_factor

        t = t.dropna(subset=["last"]).drop_duplicates(subset=["symbol"], keep="first")
        by_symbol = {r.symbol: r for r in t[["symbol", "last", "prev", "pct"]].itertuples(index=False)}

        rows = []
        for symbol in symbols:
            row = by_symbol.get(symbol)
            if row is None:
                rows.append(
                    {"symbol": symbol, "last": None, "prev": None, "pct": None, "quote_time": now_s, "status": "error"}
                )
            else:
                rows.append(
                    {
                        "symbol": symbol,
                        "last": row.last,
                        "prev": row.prev,
                        "pct": row.pct,
                        "quote_time": now_s,
                        "status": "ok",
                    }
                )
        return pd.DataFrame(rows)
