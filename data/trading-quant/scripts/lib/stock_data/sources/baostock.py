"""BaoStock source adapter (daily only)."""

from __future__ import annotations

import pandas as pd

from .base import DataSource
from ..utils import to_baostock_symbol


class BaoStockSource(DataSource):
    """Fetch daily bars using baostock."""

    name = "baostock"
    supports_daily = True
    supports_minute = False

    def get_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        try:
            import baostock as bs
        except Exception as exc:
            raise RuntimeError("baostock unavailable") from exc

        adjust_map = {"": "3", "qfq": "2", "hfq": "1"}
        lg = bs.login()
        if lg.error_code != "0":
            raise RuntimeError(f"baostock login failed: {lg.error_msg}")
        try:
            rs = bs.query_history_k_data_plus(
                to_baostock_symbol(code),
                "date,open,high,low,close,volume,amount",
                start_date=start,
                end_date=end,
                frequency="d",
                adjustflag=adjust_map.get(adjust, "3"),
            )
            rows = []
            while rs.next():
                rows.append(rs.get_row_data())
            return pd.DataFrame(rows, columns=rs.fields)
        finally:
            bs.logout()

    def get_minute(self, code: str, period: str = "5", adjust: str = "") -> pd.DataFrame:
        raise NotImplementedError("baostock minute is not enabled in MVP")
