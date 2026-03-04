"""Sina全A股市场异动扫描: 涨幅/跌幅/量比排行，板块资金流向."""

from __future__ import annotations
import json
import logging
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://finance.sina.com.cn",
}

BASE_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"


class SinaMarketScanner:
    """全A股异动扫描 via Sina Finance."""

    async def get_top_gainers(self, count: int = 20) -> list[dict]:
        """涨幅排行 (排除新股首日)."""
        return await self._fetch_ranking("changepercent", 0, count)

    async def get_top_losers(self, count: int = 20) -> list[dict]:
        """跌幅排行."""
        return await self._fetch_ranking("changepercent", 1, count)

    async def get_top_volume_ratio(self, count: int = 20) -> list[dict]:
        """量比排行 (异常放量)."""
        return await self._fetch_ranking("volume_ratio", 0, count)

    async def get_top_turnover(self, count: int = 20) -> list[dict]:
        """换手率排行 (活跃度)."""
        return await self._fetch_ranking("turnover", 0, count)

    async def get_top_amount(self, count: int = 20) -> list[dict]:
        """成交额排行 (大资金关注)."""
        return await self._fetch_ranking("amount", 0, count)

    async def _fetch_ranking(self, sort_field: str, asc: int, count: int) -> list[dict]:
        params = {
            "page": 1,
            "num": min(count, 50),
            "sort": sort_field,
            "asc": asc,
            "node": "hs_a",
            "symbol": "",
            "_s_r_a": "page",
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(BASE_URL, params=params, headers=HEADERS)
                resp.raise_for_status()
                data = resp.json()

            results = []
            for item in data:
                code = item.get("code", "")
                # Skip new stock first day listing (change > 44%)
                chg = float(item.get("changepercent", 0))
                if abs(chg) > 44:
                    continue

                results.append({
                    "code": code,
                    "name": item.get("name", ""),
                    "price": float(item.get("trade", 0)),
                    "change_pct": chg,
                    "volume_ratio": float(item.get("volume_ratio", 0)),
                    "turnover_rate": float(item.get("turnover", 0)),
                    "amount": float(item.get("amount", 0)),
                    "amount_display": f"{float(item.get('amount', 0))/1e8:.1f}亿",
                })
            return results
        except Exception as e:
            logger.error(f"Sina market scan failed ({sort_field}): {e}")
            return []

    async def scan_anomalies(self, min_change: float = 5.0, min_amount: float = 5e8) -> dict:
        """Comprehensive anomaly scan: big movers + high volume."""
        gainers = await self.get_top_gainers(30)
        losers = await self.get_top_losers(15)
        top_amount = await self.get_top_amount(20)

        big_gainers = [s for s in gainers if abs(s["change_pct"]) >= min_change]
        big_losers = [s for s in losers if abs(s["change_pct"]) >= min_change]
        big_amount = [s for s in top_amount if s["amount"] >= min_amount]

        return {
            "big_gainers": big_gainers[:15],
            "big_losers": big_losers[:10],
            "high_amount": big_amount[:10],
            "stats": {
                "gainers_above_5pct": len(big_gainers),
                "losers_below_5pct": len(big_losers),
                "amount_above_5yi": len(big_amount),
            }
        }
