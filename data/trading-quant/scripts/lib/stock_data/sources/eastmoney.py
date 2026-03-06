"""EastMoney placeholder adapter built on akshare, with graceful failure."""

from __future__ import annotations

import pandas as pd

from .base import DataSource


class EastMoneySource(DataSource):
    """Placeholder source using akshare stock_zh_a_hist/minute endpoints."""

    name = "eastmoney"
    supports_daily = True
    supports_minute = True

    def _ak(self):
        try:
            import akshare as ak

            return ak
        except Exception:
            return None

    def get_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        ak = self._ak()
        if ak is None:
            return pd.DataFrame()
        try:
            return ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start.replace("-", ""),
                end_date=end.replace("-", ""),
                adjust=adjust,
            )
        except Exception:
            return pd.DataFrame()

    def get_minute(self, code: str, period: str = "5", adjust: str = "") -> pd.DataFrame:
        ak = self._ak()
        if ak is None:
            return pd.DataFrame()
        try:
            return ak.stock_zh_a_minute(symbol=f"{'sh' if code.startswith(('6','9')) else 'sz'}{code}", period=str(period), adjust=adjust)
        except Exception:
            return pd.DataFrame()
