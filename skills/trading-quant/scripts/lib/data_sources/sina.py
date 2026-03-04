"""Sina Finance real-time quote source using raw HTTP API."""

from __future__ import annotations

import logging
import re
from datetime import datetime

import httpx

from .base import QuoteData, RealtimeSource

logger = logging.getLogger(__name__)

_SINA_URL = "https://hq.sinajs.cn/list="
_QUOTE_RE = re.compile(r'"(.+)"')


def _code_to_sina(code: str) -> str:
    prefix = "sh" if code.startswith(("5", "6", "9")) else "sz"
    return prefix + code


def _parse_sina_line(raw: str) -> "QuoteData | None":
    m = _QUOTE_RE.search(raw)
    if not m:
        return None
    parts = m.group(1).split(",")
    if len(parts) < 32:
        return None

    code_match = re.search(r"hq_str_(\w+)=", raw)
    if not code_match:
        return None
    sina_code = code_match.group(1)
    code = sina_code[2:]

    def _sf(s, default=0.0):
        try:
            return float(s) if s and s.strip() else default
        except (ValueError, TypeError):
            return default

    try:
        price = _sf(parts[3])
        if price == 0:
            return None
        pre_close = _sf(parts[2])
        change_pct = round((price - pre_close) / pre_close * 100, 2) if pre_close > 0 else 0

        return QuoteData(
            code=code,
            name=parts[0] if parts[0] else "",
            price=price,
            change_pct=change_pct,
            open=_sf(parts[1], price),
            high=_sf(parts[4], price),
            low=_sf(parts[5], price),
            pre_close=pre_close,
            volume=_sf(parts[8]),
            amount=_sf(parts[9]),
            bid1=_sf(parts[6]),
            ask1=_sf(parts[7]),
            timestamp=(parts[30] + " " + parts[31]) if len(parts) > 31 else "",
            source="sina",
        )
    except Exception as e:
        logger.debug("Parse error for %s: %s", sina_code, e)
        return None


class SinaRealtimeSource(RealtimeSource):
    name = "sina"

    def __init__(self):
        self._client = None

    async def _get_client(self):
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=10.0,
                headers={
                    "Referer": "https://finance.sina.com.cn",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
                },
            )
        return self._client

    async def fetch_quotes(self, codes: "list[str]") -> "list[QuoteData]":
        client = await self._get_client()
        sina_codes = [_code_to_sina(c) for c in codes]

        results = []
        batch_size = 200
        for i in range(0, len(sina_codes), batch_size):
            batch = sina_codes[i : i + batch_size]
            url = _SINA_URL + ",".join(batch)
            resp = await client.get(url)
            resp.raise_for_status()
            for line in resp.text.strip().split(chr(10)):
                q = _parse_sina_line(line)
                if q:
                    results.append(q)
        return results

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
