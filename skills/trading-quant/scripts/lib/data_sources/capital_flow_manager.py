"""资金流数据源管理器 - 多级降级链路.

降级顺序:
1. 分钟级资金流：同花顺 → 东方财富 → 腾讯 (外盘/内盘)
2. 主力资金净流入：东方财富 → AKShare(T+1) → 腾讯 (内外盘差)
"""

from __future__ import annotations
import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)


class CapitalFlowManager:
    """资金流数据管理器 - 自动降级."""

    def __init__(self):
        self._ths = None
        self._em = None
        self._tencent = None
        self._ak = None

    def _get_ths(self):
        if self._ths is None:
            from .ths_market import THSMarketScanner
            self._ths = THSMarketScanner()
        return self._ths

    def _get_em(self):
        if self._em is None:
            from .eastmoney_market import EastMoneyMarketData
            self._em = EastMoneyMarketData()
        return self._em

    def _get_tencent(self):
        if self._tencent is None:
            from .tencent import TencentRealtimeSource
            self._tencent = TencentRealtimeSource()
        return self._tencent

    def _get_ak(self):
        """懒加载 AKShare."""
        if self._ak is None:
            try:
                import akshare as ak
                self._ak = ak
            except ImportError:
                logger.warning("AKShare not installed")
                self._ak = None
        return self._ak

    async def _retry_request(self, func, max_retries: int = 2, base_delay: float = 1.0):
        """带指数退避的重试机制."""
        last_error = None
        for attempt in range(max_retries + 1):
            try:
                return await func()
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
                    logger.warning(f"Request failed, retrying in {delay}s (attempt {attempt+1}/{max_retries}): {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {max_retries+1} attempts failed: {e}")
        
        return {"error": str(last_error), "retries": max_retries}

    async def get_capital_flows_batch(self, codes: list[str]) -> dict[str, dict]:
        """批量获取资金流数据 (高效版).
        
        Args:
            codes: 股票代码列表
            
        Returns:
            {code: flow_data, ...}
        """
        results = {}
        
        # 1. 先尝试同花顺批量 (最快)
        ths_codes = codes[:10]  # 同花顺限制每次最多 10 只
        for code in ths_codes:
            try:
                flow = await self._get_ths().get_capital_flow(code)
                if "error" not in flow and flow.get("data_points", 0) > 0:
                    results[code] = flow
                    results[code]["source"] = "ths"
            except Exception as e:
                logger.warning(f"THS flow failed for {code}: {e}")
        
        # 2. 对其余股票，仅获取主力资金 (东方财富/AKShare)
        remaining = [c for c in codes if c not in results]
        for code in remaining[:5]:  # 限制最多 5 只，防超时
            try:
                # 东方财富主力资金 (带重试)
                async def fetch_em():
                    em = await self._get_em().get_main_flow(code)
                    return em if em and "error" not in em else None
                
                em_main = await self._retry_request(fetch_em, max_retries=1, base_delay=0.5)
                if em_main:
                    results[code] = {"main_force": em_main, "source": "em_main"}
                    continue
                
                # AKShare 历史数据
                ak = self._get_ak()
                if ak:
                    try:
                        df = ak.stock_individual_fund_flow(stock=code, market='sz' if code.startswith(('0', '3')) else 'sh')
                        if len(df) > 0:
                            latest = df.iloc[-1]
                            results[code] = {
                                "main_force": {
                                    "main_net_inflow_wan": round(latest.get("主力净流入 - 净额", 0) / 1e4, 2),
                                    "super_big_net_wan": round(latest.get("超大单净流入 - 净额", 0) / 1e4, 2),
                                    "big_net_wan": round(latest.get("大单净流入 - 净额", 0) / 1e4, 2),
                                    "signal": "主力流入" if latest.get("主力净流入 - 净额", 0) > 0 else "主力流出",
                                    "source": "akshare_T+1",
                                    "date": latest.get("日期", ""),
                                },
                                "source": "akshare"
                            }
                    except Exception as e:
                        logger.warning(f"AKShare failed for {code}: {e}")
            except Exception as e:
                logger.warning(f"Main force failed for {code}: {e}")
        
        # 3. 剩余股票标记为缺失
        for code in codes:
            if code not in results:
                results[code] = {"main_force": None, "source": "missing"}
        
        return results

    async def get_capital_flow(self, code: str) -> dict:
        """获取资金流数据 (带降级).
        
        降级链路:
        1. 同花顺分钟级资金流 (最详细)
        2. 东方财富分钟级资金流 (备用)
        3. 腾讯内外盘差 (简化版)
        4. AKShare 历史资金流 (T+1, 盘后参考)
        
        Returns:
            {
                "code": "002202",
                "source": "ths" | "em" | "tencent" | "akshare",
                "name": "金风科技",
                "total_amount": 53.58 亿，
                "data_points": 121,
                "amount_surge_last_10min": false,
                "last_10min_flow": [...],
                "main_force": {  # 主力资金
                    "main_net_inflow_wan": -10653,
                    "super_big_net_wan": -15104,
                    "big_net_wan": 4451,
                    "signal": "主力流出"
                },
            }
        """
        code = code.strip().zfill(6)
        result = {"code": code, "source": "unknown"}

        # 1. 尝试同花顺分钟级资金流 (主数据源)
        try:
            ths_flow = await self._get_ths().get_capital_flow(code)
            if "error" not in ths_flow and ths_flow.get("data_points", 0) > 0:
                result.update(ths_flow)
                result["source"] = "ths"
                logger.info(f"Capital flow from THS for {code}")
        except Exception as e:
            logger.warning(f"THS capital flow failed for {code}: {e}")

        # 2. 获取东方财富主力资金 (带重试)
        async def fetch_em_main():
            em_main = await self._get_em().get_main_flow(code)
            if em_main and "error" not in em_main:
                return em_main
            return None
        
        try:
            em_main = await self._retry_request(fetch_em_main, max_retries=2, base_delay=1.0)
            if em_main and "error" not in em_main:
                result["main_force"] = em_main
                if result.get("source") == "unknown":
                    result["source"] = "em_main"
                logger.info(f"Main force from EM for {code}")
        except Exception as e:
            logger.warning(f"EM main force failed for {code}: {e}")

        # 3. 如果东方财富失败，尝试 AKShare 历史数据 (T+1)
        if result.get("main_force") is None:
            ak = self._get_ak()
            if ak:
                try:
                    # AKShare 获取历史资金流
                    df = ak.stock_individual_fund_flow(stock=code, market='sz' if code.startswith(('0', '3')) else 'sh')
                    if len(df) > 0:
                        # 取最新数据 (最后一行)
                        latest = df.iloc[-1]
                        result["main_force"] = {
                            "main_net_inflow_wan": round(latest.get("主力净流入 - 净额", 0) / 1e4, 2),
                            "super_big_net_wan": round(latest.get("超大单净流入 - 净额", 0) / 1e4, 2),
                            "big_net_wan": round(latest.get("大单净流入 - 净额", 0) / 1e4, 2),
                            "signal": "主力流入" if latest.get("主力净流入 - 净额", 0) > 0 else "主力流出",
                            "source": "akshare_T+1",
                            "date": latest.get("日期", ""),
                        }
                        if result.get("source") == "unknown":
                            result["source"] = "akshare"
                        logger.info(f"Main force from AKShare for {code} (T+1)")
                except Exception as e:
                    logger.warning(f"AKShare main force failed for {code}: {e}")

        # 4. 如果都失败，尝试东方财富分钟级资金流
        if result.get("source") == "unknown" or result.get("data_points", 0) == 0:
            try:
                em_flow = await self._get_em().get_minute_flow(code)
                if "error" not in em_flow and em_flow.get("data_points", 0) > 0:
                    # 保留已有的 main_force
                    main_force = result.get("main_force")
                    result.update(em_flow)
                    result["main_force"] = main_force or result.get("main_force")
                    result["source"] = "em"
                    logger.info(f"Capital flow from EM for {code}")
            except Exception as e:
                logger.warning(f"EM capital flow failed for {code}: {e}")

        # 5. 如果都失败，尝试腾讯内外盘差作为简化版
        if result.get("source") == "unknown":
            try:
                tencent_quote = await self._get_tencent().fetch_quotes([code])
                if tencent_quote and len(tencent_quote) > 0:
                    q = tencent_quote[0]
                    outer_vol = getattr(q, 'outer_vol', 0) if hasattr(q, 'outer_vol') else 0
                    inner_vol = getattr(q, 'inner_vol', 0) if hasattr(q, 'inner_vol') else 0
                    
                    result.update({
                        "code": code,
                        "name": q.name,
                        "total_amount": q.amount,
                        "data_points": 1,
                        "last_price": q.price,
                        "change_pct": q.change_pct,
                        "outer_vol": int(outer_vol),
                        "inner_vol": int(inner_vol),
                        "outer_inner_diff": int(outer_vol - inner_vol),
                        "source": "tencent",
                        "note": "腾讯简化版 (内外盘差)",
                    })
                    logger.info(f"Capital flow from Tencent for {code}")
            except Exception as e:
                logger.warning(f"Tencent capital flow failed for {code}: {e}")

        # 6. 如果全部失败，返回错误
        if result.get("source") == "unknown":
            result["error"] = "all capital flow sources failed"
            logger.error(f"All capital flow sources failed for {code}")

        return result

    async def get_capital_flows_batch(self, codes: list[str]) -> dict[str, dict]:
        """批量获取资金流数据 (高效版).
        
        Args:
            codes: 股票代码列表
            
        Returns:
            {code: flow_data, ...}
        """
        results = {}
        
        # 1. 先尝试同花顺批量 (最快)
        ths_codes = codes[:10]  # 同花顺限制每次最多 10 只
        for code in ths_codes:
            try:
                flow = await self._get_ths().get_capital_flow(code)
                if "error" not in flow and flow.get("data_points", 0) > 0:
                    results[code] = flow
                    results[code]["source"] = "ths"
            except Exception as e:
                logger.warning(f"THS flow failed for {code}: {e}")
        
        # 2. 对其余股票，仅获取主力资金 (东方财富/AKShare)
        remaining = [c for c in codes if c not in results]
        for code in remaining[:5]:  # 限制最多 5 只，防超时
            try:
                # 东方财富主力资金 (带重试)
                async def fetch_em():
                    em = await self._get_em().get_main_flow(code)
                    return em if em and "error" not in em else None
                
                em_main = await self._retry_request(fetch_em, max_retries=1, base_delay=0.5)
                if em_main:
                    results[code] = {"main_force": em_main, "source": "em_main"}
                    continue
                
                # AKShare 历史数据
                ak = self._get_ak()
                if ak:
                    try:
                        df = ak.stock_individual_fund_flow(stock=code, market='sz' if code.startswith(('0', '3')) else 'sh')
                        if len(df) > 0:
                            latest = df.iloc[-1]
                            results[code] = {
                                "main_force": {
                                    "main_net_inflow_wan": round(latest.get("主力净流入 - 净额", 0) / 1e4, 2),
                                    "super_big_net_wan": round(latest.get("超大单净流入 - 净额", 0) / 1e4, 2),
                                    "big_net_wan": round(latest.get("大单净流入 - 净额", 0) / 1e4, 2),
                                    "signal": "主力流入" if latest.get("主力净流入 - 净额", 0) > 0 else "主力流出",
                                    "source": "akshare_T+1",
                                    "date": latest.get("日期", ""),
                                },
                                "source": "akshare"
                            }
                    except Exception as e:
                        logger.warning(f"AKShare failed for {code}: {e}")
            except Exception as e:
                logger.warning(f"Main force failed for {code}: {e}")
        
        # 3. 剩余股票标记为缺失
        for code in codes:
            if code not in results:
                results[code] = {"main_force": None, "source": "missing"}
        
        return results

    async def close(self):
        """关闭连接."""
        if self._tencent:
            await self._tencent.close()
        if self._ths:
            if hasattr(self._ths, 'close'):
                await self._ths.close()
        if self._em:
            if hasattr(self._em, 'close'):
                await self._em.close()
