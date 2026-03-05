"""Tencent Finance real-time quote source (qt.gtimg.cn).

Most reliable free data source for A-share real-time quotes.
Provides 88 fields per stock including turnover rate, volume ratio,
bid/ask depth, and inner/outer volume.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime

import httpx

from .base import QuoteData, RealtimeSource

logger = logging.getLogger(__name__)

_QT_URL = "https://qt.gtimg.cn/q="
_QUOTE_PATTERN = re.compile(r'"([^"]+)"')


def _code_to_tencent(code: str) -> str:
    prefix = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return prefix + code



def _safe_float(parts: list[str], idx: int, default: float = 0.0) -> float:
    """Safely parse a float from parts list, returning default on any failure."""
    try:
        if idx < len(parts) and parts[idx] and parts[idx].strip():
            return float(parts[idx])
    except (ValueError, TypeError):
        pass
    return default

def _parse_tencent_parts(parts: list[str]) -> QuoteData | None:
    """Parse fields from tencent qt.gtimg.cn response.

    Field indices:
      [0] market, [1] name, [2] code, [3] price, [4] pre_close, [5] open,
      [6] volume(shou), [7] outer_vol, [8] inner_vol,
      [9] bid1, [10] bid1_vol, ..., [19] ask1, [20] ask1_vol,
      [30] datetime, [31] change_val, [32] change_pct, [33] high, [34] low,
      [37] amount(wan), [38] turnover_rate%, [49] volume_ratio
    """
    if len(parts) < 35:
        return None

    try:
        price = _safe_float(parts, 3)
        if price == 0:
            return None

        code = parts[2] if len(parts) > 2 else ""
        name = parts[1].strip() if len(parts) > 1 else ""

        return QuoteData(
            code=code,
            name=name,
            price=price,
            change_pct=_safe_float(parts, 32),
            open=_safe_float(parts, 5, price),
            high=_safe_float(parts, 33, price),
            low=_safe_float(parts, 34, price),
            pre_close=_safe_float(parts, 4),
            volume=_safe_float(parts, 6) * 100,
            amount=_safe_float(parts, 37) * 10000,
            turnover_rate=_safe_float(parts, 38),
            volume_ratio=_safe_float(parts, 49),
            bid1=_safe_float(parts, 9),
            ask1=_safe_float(parts, 19),
            pe=_safe_float(parts, 39),
            pb=_safe_float(parts, 46),
            market_cap=_safe_float(parts, 44),
            timestamp=parts[30] if len(parts) > 30 and parts[30] else datetime.now().strftime("%Y%m%d%H%M%S"),
            source="tencent",
            # 主力相关字段
            outer_vol=_safe_float(parts, 7),  # 外盘 (手)
            inner_vol=_safe_float(parts, 8),  # 内盘 (手)
        )
    except Exception as e:
        logger.debug("Parse error for tencent data: %s", e)
        return None


class TencentRealtimeSource(RealtimeSource):
    """Fetches real-time quotes from Tencent Finance (qt.gtimg.cn).

    Advantages over Sina/EastMoney:
    - 88 fields per stock (richest among free sources)
    - Includes turnover_rate and volume_ratio natively
    - Inner/outer volume for capital flow analysis
    - Relatively lenient rate limiting
    """

    name = "tencent"

    def __init__(self):
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=10.0,
                headers={
                    "Referer": "https://stockapp.finance.qq.com",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                },
            )
        return self._client

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData]:
        client = await self._get_client()
        tencent_codes = [_code_to_tencent(c) for c in codes]

        results = []
        batch_size = 100
        for i in range(0, len(tencent_codes), batch_size):
            batch = tencent_codes[i : i + batch_size]
            url = _QT_URL + ",".join(batch)
            resp = await client.get(url)
            resp.raise_for_status()

            for line in resp.text.strip().split(";"):
                line = line.strip()
                if not line:
                    continue
                m = _QUOTE_PATTERN.search(line)
                if not m:
                    continue
                parts = m.group(1).split("~")
                q = _parse_tencent_parts(parts)
                if q:
                    results.append(q)
        return results

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
