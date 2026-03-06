"""US stock real-time quotes via Tencent API (qt.gtimg.cn)."""

from __future__ import annotations
import re
import httpx
from data_sources.base import QuoteData, RealtimeSource


class TencentUSRealtimeSource(RealtimeSource):
    """Tencent US stock quotes. Fast, free, no rate limit."""

    name = "tencent_us"
    BASE = "https://qt.gtimg.cn/q="

    async def fetch_quotes(self, symbols: list[str]) -> list[QuoteData | None]:
        codes = ",".join(f"us{s.strip().upper()}" for s in symbols)
        url = self.BASE + codes
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
            raw = resp.content.decode("gbk", errors="replace")

        results: list[QuoteData | None] = []
        for symbol in symbols:
            sym = symbol.strip().upper()
            pattern = f'v_us{sym}="(.*?)";'
            m = re.search(pattern, raw)
            if not m or not m.group(1).strip():
                results.append(None)
                continue
            try:
                fields = m.group(1).split("~")
                if len(fields) < 50:
                    results.append(None)
                    continue
                name = fields[1]
                ticker = fields[2].split(".")[0] if "." in fields[2] else fields[2]
                price = float(fields[3]) if fields[3] else 0
                pre_close = float(fields[4]) if fields[4] else 0
                open_p = float(fields[5]) if fields[5] else 0
                volume = float(fields[6]) if fields[6] else 0
                high = float(fields[33]) if len(fields) > 33 and fields[33] else 0
                low = float(fields[34]) if len(fields) > 34 and fields[34] else 0
                change_pct = float(fields[32]) if len(fields) > 32 and fields[32] else 0
                amount = float(fields[37]) if len(fields) > 37 and fields[37] else 0
                market_cap = float(fields[44]) if len(fields) > 44 and fields[44] else 0
                pe = float(fields[39]) if len(fields) > 39 and fields[39] else 0

                results.append(QuoteData(
                    code=sym,
                    name=name,
                    price=price,
                    pre_close=pre_close,
                    open=open_p,
                    high=high,
                    low=low,
                    volume=volume,
                    amount=amount,
                    change_pct=change_pct,
                    turnover_rate=0,
                    volume_ratio=0,
                    pe=pe,
                    market_cap=market_cap,
                    source="tencent_us",
                ))
            except Exception:
                results.append(None)
        return results
