"""同花顺 A-share market scanning APIs: 涨停/跌停/炸板池 + 分钟级资金流."""

from __future__ import annotations
import json
import logging
import re
from dataclasses import dataclass
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://data.10jqka.com.cn",
}


@dataclass
class LimitStock:
    """A stock in the limit up/down/fried plate pool."""
    code: str
    name: str
    market_type: str
    change_tag: str
    is_again_limit: bool
    high_days: Optional[int] = None


@dataclass
class CapitalFlowPoint:
    """A single minute-level capital flow data point."""
    time: str
    price: float
    amount: float
    avg_price: float
    volume: int


class THSMarketScanner:
    """同花顺市场扫描: 涨停池/跌停池/炸板池/资金流."""

    LIMIT_UP_URL = "https://data.10jqka.com.cn/dataapi/limit_up/limit_up_pool"
    LIMIT_DOWN_URL = "https://data.10jqka.com.cn/dataapi/limit_up/lower_limit_pool"
    FRIED_PLATE_URL = "https://data.10jqka.com.cn/dataapi/limit_up/fried_plate_pool"
    CAPITAL_URL = "https://d.10jqka.com.cn/v4/time/hs_{code}/capital.js"

    async def get_limit_up_pool(self, page: int = 1, limit: int = 100) -> dict:
        """获取涨停池数据."""
        return await self._fetch_limit_pool(self.LIMIT_UP_URL, page, limit, "limit_up")

    async def get_limit_down_pool(self, page: int = 1, limit: int = 100) -> dict:
        """获取跌停池数据."""
        return await self._fetch_limit_pool(self.LIMIT_DOWN_URL, page, limit, "limit_down")

    async def get_fried_plate_pool(self, page: int = 1, limit: int = 100) -> dict:
        """获取炸板池数据."""
        return await self._fetch_limit_pool(self.FRIED_PLATE_URL, page, limit, "fried_plate")

    async def _fetch_limit_pool(self, url: str, page: int, limit: int, pool_type: str) -> dict:
        params = {"page": page, "limit": limit}
        async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        if data.get("status_code") != 0:
            return {"error": data.get("status_msg", "unknown error"), "pool_type": pool_type}

        raw_info = data.get("data", {}).get("info", [])
        page_info = data.get("data", {}).get("page", {})

        stocks = []
        for item in raw_info:
            stocks.append({
                "code": item.get("code", ""),
                "name": item.get("name", ""),
                "market_type": item.get("market_type", ""),
                "change_tag": item.get("change_tag", ""),
                "is_again_limit": bool(item.get("is_again_limit", 0)),
                "is_new": bool(item.get("is_new", 0)),
                "high_days": item.get("high_days_value"),
            })

        return {
            "pool_type": pool_type,
            "total": page_info.get("total", 0),
            "count": len(stocks),
            "stocks": stocks,
        }

    async def get_capital_flow(self, code: str) -> dict:
        """获取单股分钟级资金流数据."""
        code = code.strip().zfill(6)
        url = self.CAPITAL_URL.format(code=code)
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Referer": "https://www.10jqka.com.cn",
        }
        async with httpx.AsyncClient(timeout=10, headers=headers) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            text = resp.text

        m = re.search(r'\((\{.*\})\)', text, re.DOTALL)
        if not m:
            return {"error": "parse failed", "code": code}

        raw = json.loads(m.group(1))
        stock_data = raw.get(f"hs_{code}", {})
        name = stock_data.get("name", "")
        pre_close = float(stock_data.get("pre", 0))
        data_str = stock_data.get("data", "")

        if not data_str:
            return {"code": code, "name": name, "pre_close": pre_close, "flow": [], "note": "no data"}

        def _mf(s, default=0.0):
            try:
                return float(s) if s and s.strip() else default
            except (ValueError, TypeError):
                return default

        flow_points = []
        for line in data_str.split(";"):
            parts = line.split(",")
            if len(parts) >= 5:
                try:
                    flow_points.append({
                        "time": parts[0],
                        "price": _mf(parts[1]),
                        "amount": _mf(parts[2]),
                        "avg_price": _mf(parts[3]),
                        "volume": int(_mf(parts[4])),
                    })
                except (ValueError, TypeError):
                    continue

        total_amount = sum(p["amount"] for p in flow_points)
        last_price = flow_points[-1]["price"] if flow_points else 0
        change_pct = round((last_price - pre_close) / pre_close * 100, 2) if pre_close else 0

        recent_10 = flow_points[-10:] if len(flow_points) >= 10 else flow_points
        recent_amount = sum(p["amount"] for p in recent_10)
        avg_amount = total_amount / len(flow_points) * 10 if flow_points else 0
        amount_surge = recent_amount > avg_amount * 1.5 if avg_amount else False

        return {
            "code": code,
            "name": name,
            "pre_close": pre_close,
            "last_price": last_price,
            "change_pct": change_pct,
            "total_amount": round(total_amount, 0),
            "data_points": len(flow_points),
            "amount_surge_last_10min": amount_surge,
            "last_10min_flow": recent_10[-3:] if recent_10 else [],
        }
