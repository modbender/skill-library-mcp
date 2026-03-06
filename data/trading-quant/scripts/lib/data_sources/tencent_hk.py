"""Hong Kong stock real-time quotes via Tencent API (qt.gtimg.cn)."""

from __future__ import annotations
import re
from dataclasses import dataclass
import httpx
from data_sources.base import QuoteData, RealtimeSource


class TencentHKRealtimeSource(RealtimeSource):
    """Tencent HK stock quotes. Code format: 00700, 09988, etc."""

    name = "tencent_hk"
    BASE = "https://qt.gtimg.cn/q="

    def _build_codes(self, codes: list[str]) -> str:
        parts = []
        for c in codes:
            c = c.strip().zfill(5)
            parts.append(f"r_hk{c}")
        return ",".join(parts)

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData | None]:
        url = self.BASE + self._build_codes(codes)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            text = resp.text

        results: list[QuoteData | None] = []
        for code in codes:
            code5 = code.strip().zfill(5)
            pattern = f"v_r_hk{code5}=\"(.*?)\";"
            m = re.search(pattern, text)
            if not m or not m.group(1).strip():
                results.append(None)
                continue
            try:
                def _hf(fields, idx, default=0.0):
                    try:
                        return float(fields[idx]) if idx < len(fields) and fields[idx] and fields[idx].strip() else default
                    except (ValueError, TypeError):
                        return default

                fields = m.group(1).split("~")
                if len(fields) < 35:
                    results.append(None)
                    continue
                price = _hf(fields, 3)
                if price == 0:
                    results.append(None)
                    continue

                results.append(QuoteData(
                    code=code5,
                    name=fields[1].strip() if len(fields) > 1 else "",
                    price=price,
                    pre_close=_hf(fields, 4),
                    open=_hf(fields, 5, price),
                    high=_hf(fields, 33, price),
                    low=_hf(fields, 34, price),
                    volume=_hf(fields, 6),
                    amount=_hf(fields, 37),
                    change_pct=_hf(fields, 32),
                    turnover_rate=_hf(fields, 38),
                    volume_ratio=0,
                    pe=_hf(fields, 39),
                    pb=_hf(fields, 46),
                    market_cap=_hf(fields, 44),
                    source="tencent_hk",
                ))
            except Exception:
                results.append(None)
        return results
