"""Commodity (precious metals, crude oil) quotes via Sina Finance futures API."""

from __future__ import annotations
import re
from dataclasses import dataclass
import httpx
from data_sources.base import QuoteData, RealtimeSource


# Sina commodity code mapping
COMMODITY_MAP = {
    # 贵金属
    "XAU": ("hf_GC", "COMEX黄金"),
    "XAG": ("hf_SI", "COMEX白银"),
    "GOLD_CN": ("nf_AU0", "沪金主力"),
    "SILVER_CN": ("nf_AG0", "沪银主力"),
    # 原油
    "WTI": ("hf_CL", "WTI原油"),
    "BRENT": ("hf_OIL", "布伦特原油"),
    "CRUDE_CN": ("nf_SC0", "原油主力"),
    # 工业金属
    "COPPER": ("hf_HG", "COMEX铜"),
    "COPPER_CN": ("nf_CU0", "沪铜主力"),
    "ALUMINUM": ("nf_AL0", "沪铝主力"),
    "ZINC": ("nf_ZN0", "沪锌主力"),
    "NICKEL": ("nf_NI0", "沪镍主力"),
    "TIN": ("nf_SN0", "沪锡主力"),
    "LEAD": ("nf_PB0", "沪铅主力"),
    # 黑色系
    "REBAR": ("nf_RB0", "螺纹钢主力"),
    "IRON_ORE": ("nf_I0", "铁矿石主力"),
    # 农产品
    "SOYBEAN_MEAL": ("nf_M0", "豆粕主力"),
    "SOYBEAN_OIL": ("nf_Y0", "豆油主力"),
    "COTTON": ("nf_CF0", "棉花主力"),
}


class SinaCommoditySource(RealtimeSource):
    """Sina futures/commodity real-time quotes."""

    name = "sina_commodity"
    BASE = "https://hq.sinajs.cn/list="

    async def fetch_quotes(self, codes: list[str]) -> list[QuoteData | None]:
        sina_codes = []
        code_map = {}
        for c in codes:
            c_upper = c.upper().strip()
            if c_upper in COMMODITY_MAP:
                sina_code, _ = COMMODITY_MAP[c_upper]
                sina_codes.append(sina_code)
                code_map[sina_code] = c_upper
            else:
                sina_codes.append(c)
                code_map[c] = c

        url = self.BASE + ",".join(sina_codes)
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, headers={
                "Referer": "https://finance.sina.com.cn",
                "User-Agent": "Mozilla/5.0",
            })
            resp.raise_for_status()
            text = resp.text

        results: list[QuoteData | None] = []
        for i, sina_code in enumerate(sina_codes):
            orig_code = code_map.get(sina_code, codes[i] if i < len(codes) else sina_code)
            pattern = f"var hq_str_{sina_code}=\"(.*?)\";"
            m = re.search(pattern, text)
            if not m or not m.group(1).strip():
                results.append(None)
                continue
            try:
                fields = m.group(1).split(",")
                display_name = COMMODITY_MAP.get(orig_code, (None, orig_code))[1]

                if sina_code.startswith("hf_"):
                    price = float(fields[0]) if fields[0] else 0
                    prev_close = float(fields[7]) if len(fields) > 7 and fields[7] else 0
                    open_p = float(fields[8]) if len(fields) > 8 and fields[8] else 0
                    high = float(fields[4]) if len(fields) > 4 and fields[4] else 0
                    low = float(fields[5]) if len(fields) > 5 and fields[5] else 0
                else:
                    price = float(fields[8]) if len(fields) > 8 and fields[8] else 0
                    prev_close = float(fields[5]) if len(fields) > 5 and fields[5] else 0
                    open_p = float(fields[2]) if len(fields) > 2 and fields[2] else 0
                    high = float(fields[3]) if len(fields) > 3 and fields[3] else 0
                    low = float(fields[4]) if len(fields) > 4 and fields[4] else 0

                change_pct = ((price - prev_close) / prev_close * 100) if prev_close else 0

                results.append(QuoteData(
                    code=orig_code,
                    name=display_name,
                    price=price,
                    pre_close=prev_close,
                    open=open_p,
                    high=high,
                    low=low,
                    volume=0,
                    amount=0,
                    change_pct=round(change_pct, 2),
                    turnover_rate=0,
                    volume_ratio=0,
                    source="sina_commodity",
                ))
            except (ValueError, IndexError):
                results.append(None)
        return results
