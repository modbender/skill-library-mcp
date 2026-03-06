"""PyTDX source adapter (minute first, optional daily not required)."""

from __future__ import annotations

import pandas as pd

from .base import DataSource
from ..utils import normalize_code


class PyTdxSource(DataSource):
    """Fetch minute bars from pytdx with graceful failure if env/network unavailable."""

    name = "pytdx"
    supports_daily = False
    supports_minute = True

    def get_daily(self, code: str, start: str, end: str, adjust: str = "") -> pd.DataFrame:
        raise NotImplementedError("pytdx daily is optional and not implemented in MVP")

    def get_minute(self, code: str, period: str = "5", adjust: str = "") -> pd.DataFrame:
        try:
            from pytdx.hq import TdxHq_API
            from pytdx.params import TDXParams
        except Exception as exc:
            raise RuntimeError("pytdx unavailable") from exc

        code = normalize_code(code)
        market = 1 if code.startswith(("6", "9")) else 0
        ktype_map = {
            "1": TDXParams.KLINE_TYPE_1MIN,
            "5": TDXParams.KLINE_TYPE_5MIN,
            "15": TDXParams.KLINE_TYPE_15MIN,
            "30": TDXParams.KLINE_TYPE_30MIN,
            "60": TDXParams.KLINE_TYPE_1HOUR,
        }
        ktype = ktype_map.get(str(period), TDXParams.KLINE_TYPE_5MIN)

        api = TdxHq_API()
        server = ("119.147.212.81", 7709)
        if not api.connect(*server):
            raise RuntimeError("pytdx connect failed")
        try:
            data = api.get_security_bars(ktype, market, code, 0, 800)
            if not data:
                return pd.DataFrame()
            return api.to_df(data)
        finally:
            api.disconnect()
