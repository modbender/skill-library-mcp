"""Sina/akshare based source adapter."""

from __future__ import annotations

import pandas as pd

from .base import DataSource
from ..utils import to_sina_symbol


class SinaSource(DataSource):
    """Use akshare as Sina-compatible source for daily and minute bars."""

    name = "sina"
    supports_daily = True
    supports_minute = True

    def _ak(self):
        try:
            import akshare as ak

            return ak
        except Exception as exc:
            raise RuntimeError("akshare unavailable") from exc

    def get_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        ak = self._ak()
        symbol = to_sina_symbol(code)
        # 新浪源：覆盖更稳定，支持股票与ETF；返回全量后本地按区间过滤。
        df = ak.stock_zh_a_daily(symbol=symbol, adjust=adjust)
        if df is None or df.empty:
            return pd.DataFrame()
        if "date" in df.columns:
            d = pd.to_datetime(df["date"], errors="coerce")
            s = pd.to_datetime(start)
            e = pd.to_datetime(end)
            df = df[(d >= s) & (d <= e)].copy()
        return df

    def get_minute(self, code: str, period: str = "5", adjust: str = "") -> pd.DataFrame:
        ak = self._ak()
        return ak.stock_zh_a_minute(symbol=to_sina_symbol(code), period=str(period), adjust=adjust)
