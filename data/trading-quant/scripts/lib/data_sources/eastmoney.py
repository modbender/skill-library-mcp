"""EastMoney real-time quote source via push2.eastmoney.com API."""

from __future__ import annotations

import logging
from datetime import datetime

import httpx

from .base import QuoteData, RealtimeSource

logger = logging.getLogger(__name__)

_EM_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"


def _code_to_secid(code: str) -> str:
    market = 1 if code.startswith(("5", "6", "9")) else 0
    return f"{market}.{code}"


class EastMoneyRealtimeSource(RealtimeSource):
    """Fetches real-time quotes from EastMoney push API.

    Uses the public push2 endpoint; moderate rate limit tolerance.
    """

    name = "eastmoney"

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=15.0,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
            )
        return self._client

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData]:
        client = await self._get_client()
        secids = ",".join(_code_to_secid(c) for c in codes)
        params = {
            "fltt": "2",
            "fields": "f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f14,f15,f16,f17,f18",
            "secids": secids,
        }
        resp = await client.get(_EM_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        results = []
        raw_data = data.get("data")
        if raw_data is None:
            return results
        for item in raw_data.get("diff", []) or []:
            def _ef(val, default=0.0):
                if val is None or val == "-" or val == "":
                    return default
                try:
                    return float(val)
                except (ValueError, TypeError):
                    return default

            try:
                code = str(item.get("f12", ""))
                price = _ef(item.get("f2"))
                if not code or price == 0:
                    continue
                results.append(QuoteData(
                    code=code,
                    name=str(item.get("f14", "")),
                    price=price,
                    change_pct=_ef(item.get("f3")),
                    open=_ef(item.get("f17"), price),
                    high=_ef(item.get("f15"), price),
                    low=_ef(item.get("f16"), price),
                    pre_close=_ef(item.get("f18")),
                    volume=_ef(item.get("f5")) * 100,
                    amount=_ef(item.get("f6")),
                    turnover_rate=_ef(item.get("f8")),
                    volume_ratio=_ef(item.get("f10")),
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    source="eastmoney",
                ))
            except Exception as e:
                logger.debug(f"Parse error for eastmoney item: {e}")
                continue
        return results

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
