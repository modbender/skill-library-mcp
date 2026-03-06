"""yfinance source adapter for batch US snapshots."""

from __future__ import annotations

import pandas as pd

from .base import DataSource
from ..utils import utc_now_str


class YFinanceSource(DataSource):
    """Fetch batch daily close snapshot from yfinance."""

    name = "yfinance"
    supports_snapshot = True

    def _yf(self):
        try:
            import yfinance as yf

            return yf
        except Exception as exc:
            raise RuntimeError("yfinance unavailable") from exc

    def get_snapshots(self, symbols: list[str]) -> pd.DataFrame:
        yf = self._yf()
        if not symbols:
            return pd.DataFrame(columns=["symbol", "last", "prev", "pct", "quote_time", "status"])

        data = yf.download(
            tickers=" ".join(symbols),
            period="5d",
            interval="1d",
            auto_adjust=False,
            progress=False,
            group_by="ticker",
            threads=True,
        )

        rows: list[dict] = []
        now_s = utc_now_str()
        is_multi = isinstance(data.columns, pd.MultiIndex)

        for symbol in symbols:
            try:
                frame = data[symbol] if is_multi else data
                close = pd.to_numeric(frame.get("Close"), errors="coerce").dropna()
                if close.empty:
                    raise RuntimeError("no close")
                last = float(close.iloc[-1])
                prev = float(close.iloc[-2]) if len(close) >= 2 else None
                pct = ((last - prev) / prev * 100.0) if prev not in (None, 0) else None
                quote_time = pd.to_datetime(close.index[-1], errors="coerce")
                rows.append(
                    {
                        "symbol": symbol,
                        "last": last,
                        "prev": prev,
                        "pct": pct,
                        "quote_time": quote_time.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(quote_time) else now_s,
                        "status": "ok",
                    }
                )
            except Exception:
                rows.append(
                    {
                        "symbol": symbol,
                        "last": None,
                        "prev": None,
                        "pct": None,
                        "quote_time": now_s,
                        "status": "error",
                    }
                )
        return pd.DataFrame(rows)
