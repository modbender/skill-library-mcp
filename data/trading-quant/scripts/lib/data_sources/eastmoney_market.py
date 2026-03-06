"""东方财富市场数据: 融资融券余额 / 龙虎榜 / 个股主力净流入."""

from __future__ import annotations
import logging
import httpx

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Referer": "https://data.eastmoney.com",
}


class EastMoneyMarketData:
    """东方财富市场数据源. 所有接口有 10s 超时 + 异常保护."""

    MAX_RETRIES = 2
    MARGIN_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    LHB_URL = "https://datacenter-web.eastmoney.com/api/data/v1/get"
    MAIN_FLOW_URL = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
    MARKET_OVERVIEW_URL = "https://push2.eastmoney.com/api/qt/ulist.np/get"

    async def get_margin_balance(self, date: str = "", code: str = "") -> dict:
        """获取全市场融资融券余额.
        
        Args:
            date: YYYY-MM-DD, 空则取最新
            code: 股票代码(如 000001), 空则取全市场top
        """
        params = {
            "reportName": "RPTA_WEB_RZRQ_GGMX",
            "columns": "ALL",
            "pageSize": 50,
            "pageNumber": 1,
            "sortColumns": "RZYE",
            "sortTypes": -1,
            "source": "WEB",
            "client": "WEB",
        }
        filters = []
        if code:
            filters.append(f'(SCODE="{code}")')
        if filters:
            params["filter"] = "".join(filters)
        
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                resp = await client.get(self.MARGIN_URL, params=params)
                data = resp.json()
                if not data.get("success"):
                    return {"error": "margin API failed", "raw": str(data.get("message", ""))[:100]}
                
                result = data.get("result", {})
                items = result.get("data", [])
                
                total_rzye = sum(float(i.get("RZYE", 0)) for i in items[:50])
                total_rqye = sum(float(i.get("RQYE", 0)) for i in items[:50])
                
                return {
                    "total_rzye_billion": round(total_rzye / 1e8, 2),
                    "total_rqye_billion": round(total_rqye / 1e8, 2),
                    "top5": [{
                        "code": i.get("SCODE", ""),
                        "name": i.get("SNAME", ""),
                        "rzye": round(float(i.get("RZYE", 0)) / 1e8, 2),
                        "rzmre": round(float(i.get("RZMRE", 0)) / 1e8, 2),
                    } for i in items[:5]],
                    "count": result.get("count", 0),
                }
        except Exception as e:
            logger.warning(f"Margin data failed: {e}")
            return {"error": str(e)}

    async def get_lhb(self, date: str = "") -> dict:
        """获取龙虎榜数据. 不传 date 时自动获取最近交易日."""
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                if not date:
                    probe = {
                        "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
                        "columns": "TRADE_DATE",
                        "pageSize": 1,
                        "pageNumber": 1,
                        "sortColumns": "TRADE_DATE",
                        "sortTypes": -1,
                        "source": "WEB",
                        "client": "WEB",
                    }
                    r = await client.get(self.LHB_URL, params=probe)
                    d = r.json()
                    items0 = (d.get("result") or {}).get("data", [])
                    if items0:
                        raw_date = items0[0].get("TRADE_DATE", "")
                        date = raw_date[:10] if raw_date else ""
                    if not date:
                        return {"error": "cannot determine latest trading date"}
                
                params = {
                    "reportName": "RPT_DAILYBILLBOARD_DETAILSNEW",
                    "columns": "ALL",
                    "pageSize": 20,
                    "pageNumber": 1,
                    "sortColumns": "BILLBOARD_NET_AMT",
                    "sortTypes": -1,
                    "source": "WEB",
                    "client": "WEB",
                    "filter": f"(TRADE_DATE='{date}')",
                }
                resp = await client.get(self.LHB_URL, params=params)
                data = resp.json()
                if not data.get("success"):
                    return {"error": "LHB API failed", "date": date}
                    return {"error": "LHB API failed"}
                
                result = data.get("result", {})
                items = result.get("data", [])
                
                seen = set()
                deduped = []
                for i in items:
                    code = i.get("SECURITY_CODE", "")
                    if code not in seen:
                        seen.add(code)
                        deduped.append(i)
                
                return {
                    "date": date,
                    "count": result.get("count", 0),
                    "items": [{
                        "code": i.get("SECURITY_CODE", ""),
                        "name": i.get("SECURITY_NAME_ABBR", ""),
                        "change_pct": round(float(i.get("CHANGE_RATE", 0) or 0), 2),
                        "close_price": float(i.get("CLOSE_PRICE", 0) or 0),
                        "reason": i.get("EXPLAIN", ""),
                        "explanation": i.get("EXPLANATION", ""),
                        "buy_amount_yi": round(float(i.get("BILLBOARD_BUY_AMT", 0) or 0) / 1e8, 2),
                        "sell_amount_yi": round(float(i.get("BILLBOARD_SELL_AMT", 0) or 0) / 1e8, 2),
                        "net_amount_yi": round(float(i.get("BILLBOARD_NET_AMT", 0) or 0) / 1e8, 2),
                    } for i in deduped[:10]],
                }
        except Exception as e:
            logger.warning(f"LHB data failed: {e}")
            return {"error": str(e)}

    async def get_main_flow(self, code: str) -> dict:
        """获取个股主力资金净流入(日级别).
        
        Args:
            code: 6位股票代码
        """
        code = code.strip().zfill(6)
        secid = f"1.{code}" if code.startswith(("6", "5")) else f"0.{code}"
        
        params = {
            "secid": secid,
            "lmt": 5,
            "klt": 101,
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                resp = await client.get(self.MAIN_FLOW_URL, params=params)
                data = resp.json()
                
                klines = data.get("data", {}).get("klines", [])
                if not klines:
                    return {"code": code, "error": "no flow data"}
                
                latest = klines[-1].split(",")
                if len(latest) < 4:
                    return {"code": code, "error": "incomplete data"}
                
                def sf(s):
                    try: return float(s)
                    except: return 0.0
                
                # Fields: date, main_net, small_net, mid_net, big_net, super_big_net (some may be absent)
                main_net = sf(latest[1]) if len(latest) > 1 else 0
                small_net = sf(latest[2]) if len(latest) > 2 else 0
                mid_net = sf(latest[3]) if len(latest) > 3 else 0
                big_net = sf(latest[4]) if len(latest) > 4 else 0
                super_big_net = sf(latest[5]) if len(latest) > 5 else 0
                
                return {
                    "code": code,
                    "date": latest[0],
                    "main_net_inflow_wan": round(main_net / 1e4, 2),
                    "super_big_net_wan": round(super_big_net / 1e4, 2),
                    "big_net_wan": round(big_net / 1e4, 2),
                    "mid_net_wan": round(mid_net / 1e4, 2),
                    "small_net_wan": round(small_net / 1e4, 2),
                    "signal": "主力流入" if main_net > 0 else ("主力流出" if main_net < 0 else "中性"),
                }
        except Exception as e:
            logger.warning(f"Main flow failed for {code}: {e}")
            return {"code": code, "error": str(e)}

    _sentiment_cache = None
    _sentiment_cache_ts = 0

    async def get_market_sentiment(self, extra_data: dict = None) -> dict:
        import time
        now = time.time()
        if self._sentiment_cache and (now - self._sentiment_cache_ts) < 60:
            return self._sentiment_cache
        """获取大盘指数强弱 + 涨跌家数."""
        fields = "f1,f2,f3,f4,f5,f6,f7,f12,f14"
        params = {
            "fltt": 2,
            "secids": "1.000300,1.000905,1.000016,0.399006",
            "fields": fields,
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                resp = await client.get(self.MARKET_OVERVIEW_URL, params=params)
                data = resp.json()
                
                indices = {}
                for item in data.get("data", {}).get("diff", []):
                    code = item.get("f12", "")
                    indices[code] = {
                        "name": item.get("f14", ""),
                        "price": item.get("f2", 0),
                        "change_pct": item.get("f3", 0),
                        "volume": item.get("f5", 0),
                        "amount": item.get("f6", 0),
                    }
                
                hs300_pct = indices.get("000300", {}).get("change_pct", 0)
                
                sentiment_score = 50.0
                signals = []
                
                if hs300_pct > 1.5:
                    sentiment_score += 15
                    signals.append(f"沪深300强势+{hs300_pct}%")
                elif hs300_pct > 0.5:
                    sentiment_score += 8
                    signals.append(f"沪深300偏强+{hs300_pct}%")
                elif hs300_pct < -1.5:
                    sentiment_score -= 15
                    signals.append(f"沪深300弱势{hs300_pct}%")
                elif hs300_pct < -0.5:
                    sentiment_score -= 8
                    signals.append(f"沪深300偏弱{hs300_pct}%")
                else:
                    signals.append(f"沪深300震荡{hs300_pct}%")
                
                # 涨跌停对比(从THS获取的数据,如有)
                limit_up = extra_data.get("limit_up_count", 0) if extra_data else 0
                limit_down = extra_data.get("limit_down_count", 0) if extra_data else 0
                if limit_up > 0 or limit_down > 0:
                    ratio = limit_up / max(limit_down, 1)
                    if ratio > 5:
                        sentiment_score += 5
                        signals.append(f"涨跌停比{limit_up}:{limit_down}(极多)")
                    elif ratio > 2:
                        sentiment_score += 3
                        signals.append(f"涨跌停比{limit_up}:{limit_down}(偏多)")
                    elif ratio < 0.3:
                        sentiment_score -= 5
                        signals.append(f"涨跌停比{limit_up}:{limit_down}(极空)")
                    elif ratio < 0.5:
                        sentiment_score -= 3
                        signals.append(f"涨跌停比{limit_up}:{limit_down}(偏空)")

                result = {
                    "score": max(20, min(80, round(sentiment_score, 1))),
                    "signals": signals,
                    "indices": indices,
                }
                EastMoneyMarketData._sentiment_cache = result
                EastMoneyMarketData._sentiment_cache_ts = now
                return result
        except Exception as e:
            logger.warning(f"Market sentiment failed: {e}")
            if self._sentiment_cache:
                return self._sentiment_cache
            return {"score": 50.0, "signals": ["大盘数据获取失败(中性)"], "indices": {}}

    async def get_minute_flow(self, code: str, lmt: int = 120) -> dict:
        """获取个股分钟级资金流数据 (东方财富降级链路).
        
        Args:
            code: 6 位股票代码
            lmt: 返回 K 线数量 (默认 120 条=2 小时)
        """
        code = code.strip().zfill(6)
        secid = f"1.{code}" if code.startswith(("6", "5")) else f"0.{code}"
        
        params = {
            "secid": secid,
            "lmt": lmt,
            "klt": 1,  # 1 分钟 K 线
            "fields1": "f1,f2,f3,f7",
            "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
            "ut": "b2884a393a59ad64002292a3e90d46a5",
        }
        
        try:
            async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
                resp = await client.get(self.MAIN_FLOW_URL, params=params)
                data = resp.json()
                
                klines = data.get("data", {}).get("klines", [])
                if not klines:
                    return {"code": code, "error": "no minute flow data"}
                
                latest = klines[-1].split(",")
                if len(latest) < 4:
                    return {"code": code, "error": "incomplete data"}
                
                def sf(s):
                    try: return float(s)
                    except: return 0.0
                
                main_net = sf(latest[1])
                small_net = sf(latest[2])
                mid_net = sf(latest[3])
                big_net = sf(latest[4]) if len(latest) > 4 else 0
                super_big_net = sf(latest[5]) if len(latest) > 5 else 0
                
                total_amount = sum(abs(sf(k.split(",")[1])) for k in klines)
                
                last_10 = klines[-10:] if len(klines) >= 10 else klines
                last_10_flow = [{"time": k.split(",")[0][-4:], "main_net": round(sf(k.split(",")[1]) / 1e4, 2)} for k in last_10]
                
                recent_amount = sum(abs(sf(k.split(",")[1])) for k in last_10)
                avg_amount = total_amount / len(klines) * 10 if klines else 0
                amount_surge = recent_amount > avg_amount * 1.5 if avg_amount else False
                
                return {
                    "code": code,
                    "name": data.get("data", {}).get("name", ""),
                    "last_price": float(data.get("data", {}).get("price", 0)),
                    "change_pct": round(float(data.get("data", {}).get("chg", 0)), 2),
                    "total_amount": round(total_amount / 1e8, 2),
                    "data_points": len(klines),
                    "amount_surge_last_10min": amount_surge,
                    "last_10min_flow": last_10_flow[-3:] if last_10_flow else [],
                    "main_force": {
                        "main_net_inflow_wan": round(main_net / 1e4, 2),
                        "super_big_net_wan": round(super_big_net / 1e4, 2),
                        "big_net_wan": round(big_net / 1e4, 2),
                        "mid_net_wan": round(mid_net / 1e4, 2),
                        "small_net_wan": round(small_net / 1e4, 2),
                        "signal": "主力流入" if main_net > 0 else ("主力流出" if main_net < 0 else "中性"),
                    },
                    "source": "em_minute",
                }
        except Exception as e:
            logger.warning(f"EM minute flow failed for {code}: {e}")
            return {"code": code, "error": str(e)}
