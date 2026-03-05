"""同花顺(10jqka) A-share real-time quotes as fallback data source."""

from __future__ import annotations
import re
import json
import httpx
from data_sources.base import QuoteData, RealtimeSource


THS_FIELD_MAP = {
    "10": "price",        # 最新价
    "7": "open",          # 开盘价
    "8": "high",          # 最高价
    "9": "low",           # 最低价
    "13": "volume",       # 成交量
    "19": "amount",       # 成交额
    "199112": "change_pct",  # 涨跌幅
    "264648": "change",   # 涨跌额
    "1968584": "turnover_rate",  # 换手率
    "2942": "pe",         # 市盈率
}


class THSRealtimeSource(RealtimeSource):
    """同花顺 A-stock real-time quotes. Single-stock only, use as last fallback."""

    name = "ths"
    BASE = "https://d.10jqka.com.cn/v2/realhead/hs_{code}/last.js"
    HEADERS = {
        "Referer": "https://www.10jqka.com.cn",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    }

    def _market_prefix(self, code: str) -> str:
        code = code.strip().zfill(6)
        if code.startswith(("6", "5")):
            return code  # SH
        return code  # SZ (10jqka auto-detects)

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData | None]:
        results: list[QuoteData | None] = []
        async with httpx.AsyncClient(timeout=8, headers=self.HEADERS) as client:
            for code in codes:
                code = code.strip().zfill(6)
                url = self.BASE.format(code=code)
                try:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    text = resp.text

                    m = re.search(r'\((\{.*?\})\)', text)
                    if not m:
                        results.append(None)
                        continue

                    data = json.loads(m.group(1))
                    items = data.get("items", {})

                    def _tf(val, default=0.0):
                        try:
                            return float(val) if val and str(val).strip() else default
                        except (ValueError, TypeError):
                            return default

                    price = _tf(items.get("10"))
                    if not price:
                        results.append(None)
                        continue

                    change_pct = _tf(items.get("199112"))
                    pre_close = round(price / (1 + change_pct / 100), 2) if change_pct != 0 else price

                    results.append(QuoteData(
                        code=code,
                        name=items.get("name", ""),
                        price=price,
                        pre_close=pre_close,
                        open=_tf(items.get("7"), price),
                        high=_tf(items.get("8"), price),
                        low=_tf(items.get("9"), price),
                        volume=_tf(items.get("13")),
                        amount=_tf(items.get("19")),
                        change_pct=change_pct,
                        turnover_rate=_tf(items.get("1968584")),
                        volume_ratio=0,
                        source="ths",
                    ))
                except Exception:
                    results.append(None)
        return results
