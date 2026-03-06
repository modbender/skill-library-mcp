#!/usr/bin/env python3
"""Trading Quant CLI — wraps MCP server tools for OpenClaw exec calls.

Supports persistent service mode for faster model inference.
"""

import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))


# Persistent service configuration
_PERSISTENT_SOCKET = "/tmp/trading_quant_persistent.sock"
_PERSISTENT_PID = "/tmp/trading_quant_persistent.pid"


def _is_persistent_server_running() -> bool:
    """Check if persistent server is running."""
    if not os.path.exists(_PERSISTENT_PID):
        return False
    try:
        with open(_PERSISTENT_PID, 'r') as f:
            pid = int(f.read().strip())
        os.kill(pid, 0)
        return os.path.exists(_PERSISTENT_SOCKET)
    except (ValueError, OSError, ProcessLookupError):
        return False


async def _call_persistent_sentiment(texts: list[str]) -> dict:
    """Call persistent server for fast sentiment analysis."""
    import asyncio

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_unix_connection(_PERSISTENT_SOCKET),
            timeout=5.0
        )

        request = {"command": "sentiment", "texts": texts}
        writer.write(json.dumps(request).encode())
        await writer.drain()

        data = await asyncio.wait_for(reader.read(65536), timeout=30.0)
        writer.close()

        response = json.loads(data.decode())
        if response.get("status") == "ok":
            return {"used_persistent": True, **response}
        return {"used_persistent": False, "error": response.get("error")}
    except Exception as e:
        return {"used_persistent": False, "error": str(e)}


try:
    from utils.cache import (
        save_daily_snapshot, get_nb_consecutive_outflow_days,
        calc_consecutive_from_klines
    )
except ImportError:
    def save_daily_snapshot(d, data): pass
    def get_consecutive_up_days(): return 0
    def get_consecutive_down_days(): return 0
    def get_nb_consecutive_outflow_days(): return 0
    async def calc_consecutive_from_klines(): return {"consecutive_up_days": 0, "consecutive_down_days": 0}

os.environ.setdefault("PYTHONPATH", os.path.join(os.path.dirname(__file__), "lib"))


async def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: quant.py <tool> [args...]"}))
        sys.exit(1)

    tool = sys.argv[1]
    args = sys.argv[2:]

    from data_sources.manager import DataManager
    from data_sources.tencent import TencentRealtimeSource
    from data_sources.tencent_us import TencentUSRealtimeSource
    from data_sources.tencent_hk import TencentHKRealtimeSource
    from data_sources.sina_commodity import SinaCommoditySource
    from data_sources.ths_market import THSMarketScanner
    from data_sources.eastmoney_northbound import NorthboundFlowSource
    from data_sources.sina_market import SinaMarketScanner
    from data_sources.eastmoney_news import EastMoneyNewsFetcher
    from data_sources.multi_news import aggregate_news
    from data_sources.eastmoney_market import EastMoneyMarketData
    from analysis.scoring import compute_stock_score

    dm = DataManager()

    if tool == "stock_analysis":
        codes = args[0].split(",") if args else []
        if not codes:
            codes_from_wl = _load_watchlist_codes("priority") + _load_watchlist_codes("observe")
            codes = codes_from_wl[:20]
        src = TencentRealtimeSource()
        quotes = await src.fetch_quotes(codes)
        results = []
        news_fetcher = EastMoneyNewsFetcher()
        em_market = EastMoneyMarketData()
        try:
            market_sentiment = await em_market.get_market_sentiment()
        except Exception:
            market_sentiment = None

        # Pre-fetch: capital flows for abnormal stocks (once, outside loop)
        abnormal_codes = [q.code for q in quotes
                          if q.amount > 3e9 or q.volume_ratio > 2.0]
        flow_results = {}
        if abnormal_codes:
            from data_sources.capital_flow_manager import CapitalFlowManager
            flow_mgr = CapitalFlowManager()
            flow_results = await flow_mgr.get_capital_flows_batch(abnormal_codes)
            await flow_mgr.close()

        # Pre-fetch: news for non-ETF stocks (parallel)
        
        async def _fetch_news(q):
            try:
                news = await news_fetcher.get_stock_news(q.code, q.name or "", limit=5)
                if news:
                    avg_s = sum(n.sentiment for n in news) / len(news)
                    return q.code, {"news_sentiment": round(avg_s, 2), "news_count": len(news),
                                    "top_news": [n.title for n in news[:2]]}
            except Exception:
                pass
            return q.code, {}
        news_tasks = [_fetch_news(q) for q in quotes]
        news_map = dict(await asyncio.gather(*news_tasks))

        # Pre-compute: market context (once)
        market_extra = {}
        if market_sentiment:
            market_extra["market_sentiment"] = market_sentiment
            kline_cons = await calc_consecutive_from_klines()
            market_extra["consecutive_up_days"] = kline_cons.get("consecutive_up_days", 0)
            market_extra["consecutive_down_days"] = kline_cons.get("consecutive_down_days", 0)
            market_extra["nb_consecutive_outflow_days"] = get_nb_consecutive_outflow_days()

        for q in quotes:
            df = dm.get_daily_klines(q.code)
            news_extra = {**news_map.get(q.code, {}), **market_extra}
            main_force_data = flow_results.get(q.code, {}).get("main_force") if q.code in flow_results else None
            score = compute_stock_score(q, df, extra=news_extra, capital_flow_data=main_force_data)
            d = score.to_dict()
            tech = d.get("score", {}).get("technical", {})
            indicators = tech.get("indicators", {})
            d["open"] = q.open
            d["high"] = q.high
            d["low"] = q.low
            if indicators:
                key_levels = {}
                for k in ("ma5", "ma10", "ma20", "ma60"):
                    if k in indicators and indicators[k] > 0:
                        key_levels[k] = round(indicators[k], 2)
                if key_levels:
                    d["key_levels"] = key_levels
            results.append(d)
        await src.close()
        print(json.dumps({"stocks": results, "count": len(results)}, ensure_ascii=False))

    elif tool == "us_stock":
        symbols = args[0].split(",") if args else (_load_watchlist_codes("us") or ["AAPL","NVDA","TSLA","SPY","QQQ"])
        src = TencentUSRealtimeSource()
        results = []
        try:
            quotes = await src.fetch_quotes(symbols)
            for q in (quotes or []):
                if q:
                    results.append({
                        "code": q.code, "name": q.name, "price": q.price,
                        "change_pct": q.change_pct, "pe": q.pe,
                        "market_cap": q.market_cap, "source": q.source
                    })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Tencent US failed: {e}, trying yfinance")

        ok_codes = {r["code"] for r in results}
        missing = [s for s in symbols if s not in ok_codes]
        if missing:
            try:
                import yfinance as yf
                tickers = yf.Tickers(" ".join(missing))
                for sym in missing:
                    try:
                        info = tickers.tickers[sym].fast_info
                        price = float(info.get("lastPrice", info.get("previousClose", 0)))
                        prev = float(info.get("previousClose", price))
                        chg = round((price - prev) / prev * 100, 2) if prev > 0 else 0
                        results.append({
                            "code": sym, "name": sym, "price": price,
                            "change_pct": chg, "pe": 0, "market_cap": 0, "source": "yfinance"
                        })
                    except Exception:
                        pass
            except Exception:
                pass
        print(json.dumps({"stocks": results, "count": len(results)}, ensure_ascii=False))

    elif tool == "hk_stock":
        codes = args[0].split(",") if args else (_load_watchlist_codes("hk") or ["00700","09988","03690"])
        src = TencentHKRealtimeSource()
        quotes = await src.fetch_quotes(codes)
        results = []
        for q in (quotes or []):
            if q:
                results.append({
                    "code": q.code, "name": q.name, "price": q.price,
                    "change_pct": q.change_pct, "pe": q.pe, "pb": q.pb,
                    "source": q.source
                })
        print(json.dumps({"stocks": results, "count": len(results)}, ensure_ascii=False))

    elif tool == "commodity":
        codes = args[0].split(",") if args else (_load_watchlist_codes("commodity") or ["XAU","XAG","WTI","BRENT","COPPER","COPPER_CN","ALUMINUM","IRON_ORE"])
        src = SinaCommoditySource()
        quotes = await src.fetch_quotes(codes)
        results = []
        for q in (quotes or []):
            if q:
                item = {
                    "code": q.code, "name": q.name, "price": q.price,
                    "change_pct": q.change_pct, "open": q.open, "high": q.high,
                    "low": q.low, "pre_close": q.pre_close, "source": q.source,
                }
                if q.high > 0 and q.low > 0:
                    item["daily_range_pct"] = round((q.high - q.low) / q.low * 100, 2)
                if abs(q.change_pct) >= 3:
                    item["alert"] = "large_move"
                results.append(item)
        summary = {"bullish": 0, "bearish": 0}
        for r in results:
            if r["change_pct"] > 0.5:
                summary["bullish"] += 1
            elif r["change_pct"] < -0.5:
                summary["bearish"] += 1
        print(json.dumps({"commodities": results, "count": len(results), "sentiment": summary}, ensure_ascii=False))

    elif tool == "market_anomaly":
        scanner = THSMarketScanner()
        up = await scanner.get_limit_up_pool()
        down = await scanner.get_limit_down_pool()
        up_count = (up.get("total") or 0) if up else 0
        down_count = (down.get("total") or 0) if down else 0
        first_limit = sum(1 for s in (up.get("stocks", []) if up else []) if s.get("change_tag") == "FIRST_LIMIT")
        again_limit = sum(1 for s in (up.get("stocks", []) if up else []) if s.get("is_again_limit"))
        sentiment = "very_bullish" if up_count > 80 and down_count < 5 else (
            "bullish" if up_count > 40 and down_count < 10 else (
                "bearish" if down_count > 30 else "neutral"
            ))
        stats = {
            "limit_up_total": up_count, "limit_down_total": down_count,
            "first_limit": first_limit, "again_limit": again_limit,
            "market_sentiment": sentiment,
            "up_down_ratio": f"{up_count}:{down_count}",
        }
        up_stocks = up.get("stocks", []) if up else []
        industry_map = await _batch_get_industries([s.get("code", "") for s in up_stocks])
        sector_names = {}
        for s in up_stocks:
            code = s.get("code", "")
            name = s.get("name", "")
            industry = industry_map.get(code, "")
            if industry:
                s["industry"] = industry
                sector_names.setdefault(industry, []).append(name)
        hot_sectors = sorted(sector_names.items(), key=lambda x: -len(x[1]))[:8]
        stats["hot_sectors"] = [{"sector": s, "count": len(names), "samples": names[:3]} for s, names in hot_sectors]
        print(json.dumps({"limit_up": up, "limit_down": down, "stats": stats}, ensure_ascii=False))

    elif tool == "capital_flow":
        codes = args[0].split(",") if args else []
        from data_sources.capital_flow_manager import CapitalFlowManager
        manager = CapitalFlowManager()
        results = {}
        for code in codes[:5]:
            results[code] = await manager.get_capital_flow(code)
        await manager.close()
        print(json.dumps(results, ensure_ascii=False, default=str))
    
    elif tool == "ak_test":
        """测试 AKShare 数据源."""
        codes = args[0].split(",") if args else []
        try:
            import akshare as ak
            results = {}
            for code in codes[:5]:
                market = 'sz' if code.startswith(('0', '3')) else 'sh'
                df = ak.stock_individual_fund_flow(stock=code, market=market)
                if len(df) > 0:
                    latest = df.iloc[-1]
                    results[code] = {
                        "date": latest.get("日期", ""),
                        "close": latest.get("收盘价", 0),
                        "change_pct": latest.get("涨跌幅", 0),
                        "main_net_inflow": latest.get("主力净流入 - 净额", 0),
                        "super_big_net": latest.get("超大单净流入 - 净额", 0),
                        "big_net": latest.get("大单净流入 - 净额", 0),
                    }
            print(json.dumps({"akshare": results, "count": len(results)}, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"error": str(e)}, ensure_ascii=False))

    elif tool == "northbound_flow":
        src = NorthboundFlowSource()
        data = await src.get_realtime_flow()
        print(json.dumps(data, ensure_ascii=False))

    elif tool == "global_overview":
        # A-shares
        a_src = TencentRealtimeSource()
        a_codes = (_load_watchlist_codes("priority") + _load_watchlist_codes("observe"))[:20]
        a_quotes = await a_src.fetch_quotes(a_codes) if a_codes else []
        await a_src.close()
        # US
        us_src = TencentUSRealtimeSource()
        us_syms = _load_watchlist_codes("us")[:9]
        us_quotes = await us_src.fetch_quotes(us_syms) if us_syms else []
        # HK
        hk_src = TencentHKRealtimeSource()
        hk_codes = _load_watchlist_codes("hk")[:6]
        hk_quotes = await hk_src.fetch_quotes(hk_codes) if hk_codes else []
        # Commodities
        comm_src = SinaCommoditySource()
        comm_codes = _load_watchlist_codes("commodity")[:20]
        comm_quotes = await comm_src.fetch_quotes(comm_codes) if comm_codes else []

        def _fmt(q, include_fundamentals=False):
            if not q: return None
            r = {"code": q.code, "name": q.name, "price": q.price, "change_pct": q.change_pct}
            if include_fundamentals and q.pe > 0:
                r["pe"] = q.pe
            if include_fundamentals and q.pb > 0:
                r["pb"] = q.pb
            if q.volume > 0:
                r["volume"] = q.volume
            return r

        result = {
            "a_shares": [_fmt(q, True) for q in a_quotes if q],
            "us_stocks": [_fmt(q, True) for q in us_quotes if q],
            "hk_stocks": [_fmt(q, True) for q in hk_quotes if q],
            "commodities": [_fmt(q) for q in comm_quotes if q],
        }
        print(json.dumps(result, ensure_ascii=False))

    elif tool == "system_health":
        report = dm.health_report()
        print(json.dumps(report, ensure_ascii=False))

    elif tool == "warm_klines":
        codes = args[0].split(",") if args else _load_watchlist_codes("priority")
        result = dm.warm_klines(codes)
        print(json.dumps(result, ensure_ascii=False))

    elif tool == "weekly_review":
        codes = args[0].split(",") if args else []
        if not codes:
            codes = (_load_watchlist_codes("priority") + _load_watchlist_codes("observe"))[:20]
        import pandas as pd
        import datetime

        src = TencentRealtimeSource()
        quotes = await src.fetch_quotes(codes)
        results = []
        for q in (quotes or []):
            if not q:
                continue
            df = dm.get_daily_klines(q.code)
            score = compute_stock_score(q, df)
            d = score.to_dict()
            if df is not None and len(df) >= 2:
                bs_df = df[df["source"] == "baostock"].copy()
                if len(bs_df) >= 2:
                    bs_df["date"] = pd.to_datetime(bs_df["date"])
                    bs_df = bs_df.sort_values("date")
                    today = datetime.date.today()
                    monday = today - datetime.timedelta(days=today.weekday())
                    week_start_rows = bs_df[bs_df["date"].dt.date >= monday]
                    if len(week_start_rows) > 0:
                        week_open = float(week_start_rows.iloc[0]["open"])
                        d["week_open"] = week_open
                        d["week_change_pct"] = round((q.price - week_open) / week_open * 100, 2)
                    else:
                        last_close = float(bs_df.iloc[-1]["close"])
                        d["week_open"] = last_close
                        d["week_change_pct"] = round((q.price - last_close) / last_close * 100, 2)
            if "week_change_pct" not in d:
                d["week_change_pct"] = d.get("change_pct", 0)
                d["week_change_note"] = "日涨跌幅(K线数据不足)"
            tech = d.get("score", {}).get("technical", {})
            indicators = tech.get("indicators", {})
            if indicators:
                key_levels = {}
                for k in ("ma5", "ma10", "ma20", "ma60"):
                    if k in indicators and indicators[k] > 0:
                        key_levels[k] = round(indicators[k], 2)
                if key_levels:
                    d["key_levels"] = key_levels
            results.append(d)
        await src.close()

        us_src = TencentUSRealtimeSource()
        us_syms = _load_watchlist_codes("us")[:9]
        us_quotes = await us_src.fetch_quotes(us_syms) if us_syms else []
        us_data = []
        for q in (us_quotes or []):
            if q:
                item = {"code": q.code, "name": q.name, "price": q.price,
                        "change_pct": q.change_pct, "source": q.source}
                if q.pe > 0:
                    item["pe"] = q.pe
                if q.market_cap > 0:
                    item["market_cap"] = q.market_cap
                us_data.append(item)

        hk_src = TencentHKRealtimeSource()
        hk_codes = _load_watchlist_codes("hk")[:6]
        hk_quotes = await hk_src.fetch_quotes(hk_codes) if hk_codes else []
        hk_data = []
        for q in (hk_quotes or []):
            if q:
                item = {"code": q.code, "name": q.name, "price": q.price,
                        "change_pct": q.change_pct, "source": q.source}
                if q.pe > 0:
                    item["pe"] = q.pe
                hk_data.append(item)

        comm_src = SinaCommoditySource()
        comm_codes = _load_watchlist_codes("commodity")[:20]
        comm_quotes = await comm_src.fetch_quotes(comm_codes) if comm_codes else []
        comm_data = []
        for q in (comm_quotes or []):
            if q:
                item = {"code": q.code, "name": q.name, "price": q.price,
                        "change_pct": q.change_pct, "source": q.source}
                if abs(q.change_pct) >= 3:
                    item["alert"] = "large_move"
                comm_data.append(item)

        nb_src = NorthboundFlowSource()
        nb_data = await nb_src.get_realtime_flow()

        output = {
            "a_shares": {"stocks": results, "count": len(results), "note": "week_change_pct = 周涨跌幅"},
            "us_stocks": {"stocks": us_data, "note": "change_pct = 最新交易日涨跌幅"},
            "hk_stocks": {"stocks": hk_data, "note": "change_pct = 最新交易日涨跌幅"},
            "commodities": {"stocks": comm_data, "note": "change_pct = 最新涨跌幅"},
            "northbound": nb_data,
            "report_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        print(json.dumps(output, ensure_ascii=False))

    elif tool == "market_scan":
        scanner = SinaMarketScanner()
        result = await scanner.scan_anomalies()
        sector_map = {}
        for group_key in ("big_gainers", "big_losers", "high_amount"):
            for s in result.get(group_key, []):
                name = s.get("name", "")
                for keyword, sector in [
                    ("电", "电力/电气"), ("光", "光伏/光学"), ("锂", "锂电"),
                    ("铜", "铜/有色"), ("银", "白银/有色"), ("金", "黄金/贵金属"),
                    ("钢", "钢铁"), ("油", "石油/化工"), ("芯", "半导体"),
                    ("AI", "人工智能"), ("算", "算力"), ("军", "军工"),
                    ("药", "医药"), ("电池", "新能源"), ("风", "风电"),
                    ("核", "核电"), ("矿", "矿业"), ("煤", "煤炭"),
                    ("券", "券商"), ("银行", "银行"), ("保险", "保险"),
                    ("汽车", "汽车"), ("酒", "白酒/消费"), ("食", "食品/消费"),
                    ("储", "存储/半导体"), ("航", "航天/军工"), ("船", "造船"),
                ]:
                    if keyword in name:
                        sector_map.setdefault(sector, []).append(name)
                        break
        hot_sectors = sorted(sector_map.items(), key=lambda x: -len(x[1]))[:8]
        result["sector_heatmap"] = [
            {"sector": s, "count": len(names), "samples": names[:3]}
            for s, names in hot_sectors
        ]
        print(json.dumps(result, ensure_ascii=False))

    elif tool == "top_amount":
        scanner = SinaMarketScanner()
        result = await scanner.get_top_amount(int(args[0]) if args else 20)
        print(json.dumps({"top_amount": result, "count": len(result)}, ensure_ascii=False))

    elif tool == "news_sentiment":
        if args:
            fetcher = EastMoneyNewsFetcher()
            code = args[0]
            name = args[1] if len(args) > 1 else ""
            news = await fetcher.get_stock_news(code, name, limit=10)
            avg_score = sum(n.sentiment for n in news) / len(news) if news else 0
            bullish = sum(1 for n in news if n.sentiment > 0)
            bearish = sum(1 for n in news if n.sentiment < 0)
            headlines = [{"title": n.title, "sentiment": n.sentiment, "time": n.time, "keywords": n.keywords[:3]} for n in news[:5]]
            print(json.dumps({
                "code": code, "name": name,
                "sentiment": "bullish" if avg_score > 0.3 else ("bearish" if avg_score < -0.3 else "neutral"),
                "score": round(avg_score, 2),
                "bullish_count": bullish, "bearish_count": bearish,
                "news_count": len(news), "headlines": headlines,
            }, ensure_ascii=False))
        else:
            result = await aggregate_news(20)
            print(json.dumps(result, ensure_ascii=False))

    elif tool == "gold_analysis":
        from data_sources.sina_commodity import SinaCommoditySource
        comm_src = SinaCommoditySource()
        gold_codes = ["XAU", "XAG", "GOLD_CN", "SILVER_CN"]
        etf_codes = ["518880", "518800", "159934"]
        quotes = await comm_src.fetch_quotes(gold_codes)
        etf_src = TencentRealtimeSource()
        etf_quotes = await etf_src.fetch_quotes(etf_codes)
        await etf_src.close()

        result = {"precious_metals": [], "etf_flows": [], "analysis_time": ""}
        import datetime
        result["analysis_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        for q in quotes:
            if q is None:
                continue
            item = {
                "code": q.code, "name": q.name, "price": q.price,
                "change_pct": q.change_pct, "open": q.open, "high": q.high, "low": q.low,
                "pre_close": q.pre_close,
            }
            if q.high > 0 and q.low > 0:
                daily_range = q.high - q.low
                pivot = (q.high + q.low + q.price) / 3
                item["pivot"] = round(pivot, 2)
                item["support_1"] = round(2 * pivot - q.high, 2)
                item["resistance_1"] = round(2 * pivot - q.low, 2)
                item["support_2"] = round(pivot - daily_range, 2)
                item["resistance_2"] = round(pivot + daily_range, 2)
                item["daily_range_pct"] = round(daily_range / q.price * 100, 2)

            if q.pre_close > 0:
                if q.price > q.pre_close * 1.01:
                    item["trend"] = "bullish"
                elif q.price < q.pre_close * 0.99:
                    item["trend"] = "bearish"
                else:
                    item["trend"] = "neutral"
            result["precious_metals"].append(item)

        for eq in etf_quotes:
            if eq is None:
                continue
            etf_item = {
                "code": eq.code, "name": eq.name, "price": eq.price,
                "change_pct": eq.change_pct,
                "volume_ratio": eq.volume_ratio,
                "turnover_rate": eq.turnover_rate,
            }
            if eq.volume_ratio > 1.5:
                etf_item["flow_signal"] = "资金流入(量比%.1f)" % eq.volume_ratio
            elif eq.volume_ratio < 0.5:
                etf_item["flow_signal"] = "资金流出(量比%.1f)" % eq.volume_ratio
            else:
                etf_item["flow_signal"] = "正常"
            result["etf_flows"].append(etf_item)

        # Overall sentiment
        gold = next((m for m in result["precious_metals"] if m["code"] == "XAU"), None)
        silver = next((m for m in result["precious_metals"] if m["code"] == "XAG"), None)
        if gold and silver:
            gold_silver_ratio = gold["price"] / silver["price"] if silver["price"] > 0 else 0
            result["gold_silver_ratio"] = round(gold_silver_ratio, 2)
            if gold_silver_ratio > 80:
                result["ratio_signal"] = "金银比偏高(>80), 白银相对低估或避险情绪浓厚"
            elif gold_silver_ratio < 60:
                result["ratio_signal"] = "金银比偏低(<60), 工业需求旺盛"
            else:
                result["ratio_signal"] = "金银比正常区间(60-80)"

        print(json.dumps(result, ensure_ascii=False))

    elif tool == "margin_data":
        em = EastMoneyMarketData()
        code = args[0] if args else ""
        result = await em.get_margin_balance(code=code)
        print(json.dumps(result, ensure_ascii=False))

    elif tool == "lhb":
        em = EastMoneyMarketData()
        date = args[0] if args else ""
        result = await em.get_lhb(date)
        if not result or result.get("error"):
            try:
                import akshare as ak
                df = ak.stock_lhb_stock_statistic_em(symbol="近一月")
                if not df.empty:
                    items = []
                    for _, row in df.head(15).iterrows():
                        items.append({
                            "code": row.get("代码", ""),
                            "name": row.get("名称", ""),
                            "last_date": str(row.get("最近上榜日", "")),
                            "times": int(row.get("上榜次数", 0)),
                            "net_amount_yi": round(float(row.get("龙虎榜净买额", 0)) / 1e8, 2),
                            "buy_amount_yi": round(float(row.get("龙虎榜买入额", 0)) / 1e8, 2),
                            "pct_1m": row.get("近1个月涨跌幅", None),
                        })
                    result = {"source": "akshare_fallback", "period": "近一月", "count": len(df), "items": items}
            except Exception as e2:
                result = result or {"error": f"both sources failed: {e2}"}
        print(json.dumps(result, ensure_ascii=False, default=str))

    elif tool == "main_flow":
        em = EastMoneyMarketData()
        codes = args[0].split(",") if args else []
        results = {}
        for code in codes[:10]:
            results[code] = await em.get_main_flow(code)
        print(json.dumps(results, ensure_ascii=False))

    elif tool == "save_daily":
        from data_sources.eastmoney_market import EastMoneyMarketData
        from data_sources.eastmoney_northbound import NorthboundFlowSource
        em = EastMoneyMarketData()
        nb_src = NorthboundFlowSource()
        from datetime import datetime as dt
        today = dt.now().strftime("%Y-%m-%d")
        mkt = await em.get_market_sentiment()
        nb = await nb_src.get_realtime_flow()
        hs300_pct = mkt.get("indices", {}).get("000300", {}).get("change_pct", 0)
        nb_net = 0
        if isinstance(nb, dict):
            nb_net = nb.get("total_net_flow", nb.get("total_net", nb.get("net_inflow", 0)))
            if isinstance(nb_net, str):
                try: nb_net = float(nb_net)
                except (ValueError, TypeError): nb_net = 0
        snapshot = {
            "hs300_pct": hs300_pct,
            "northbound_net": nb_net,
            "sentiment_score": mkt.get("score", 50),
        }
        save_daily_snapshot(today, snapshot)
        print(json.dumps({"saved": today, "snapshot": snapshot}, ensure_ascii=False))

    elif tool == "sentiment":
        """使用 FinBERT 分析文本情感"""
        from analysis.sentiment import get_sentiment_analyzer

        if not args:
            print(json.dumps({"error": "Usage: quant.py sentiment <text>"}, ensure_ascii=False))
            sys.exit(1)

        text = " ".join(args)
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze(text)

        print(json.dumps({
            "text": text[:100] + "..." if len(text) > 100 else text,
            "sentiment": {
                "score": result.score,
                "label": result.label,
                "confidence": result.confidence,
                "method": result.method
            }
        }, ensure_ascii=False))

    elif tool == "sentiment_batch":
        """批量分析多条文本情感（JSON数组输入）"""
        import json as json_module
        from analysis.sentiment import get_sentiment_analyzer, calculate_aggregate_sentiment

        if not args:
            print(json.dumps({"error": "Usage: quant.py sentiment_batch '[\"text1\", \"text2\"]'"}, ensure_ascii=False))
            sys.exit(1)

        try:
            texts = json_module.loads(args[0])
            if not isinstance(texts, list):
                raise ValueError("Input must be a JSON array")
        except Exception as e:
            print(json.dumps({"error": f"Invalid JSON array: {e}"}, ensure_ascii=False))
            sys.exit(1)

        analyzer = get_sentiment_analyzer()
        results = analyzer.analyze_batch(texts)

        aggregate = calculate_aggregate_sentiment(results)

        print(json.dumps({
            "count": len(texts),
            "aggregate": aggregate,
            "results": [r.to_dict() for r in results]
        }, ensure_ascii=False))


    elif tool == "intraday_snapshot":
        import time as _time
        from data_sources.eastmoney_northbound import NorthboundFlowSource
        from data_sources.eastmoney_news import EastMoneyNewsFetcher
        from datetime import datetime

        t_start = _time.time()
        wl_codes = _load_watchlist_codes("priority") + _load_watchlist_codes("observe")
        wl_codes = [c for c in wl_codes if len(c) == 6][:25]

        snapshot = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": "intraday_snapshot",
            "market_status": "trading" if 9 <= datetime.now().hour < 15 else "closed",
        }

        if not wl_codes:
            snapshot["error"] = "watchlist empty"
            print(json.dumps(snapshot, ensure_ascii=False, indent=2))
            return

        src = TencentRealtimeSource()
        scanner = THSMarketScanner()
        nb_source = NorthboundFlowSource()

        async def _fetch_quotes():
            return await src.fetch_quotes(wl_codes)

        async def _fetch_market():
            try:
                lu, ld, fr = await asyncio.gather(
                    scanner.get_limit_up_pool(),
                    scanner.get_limit_down_pool(),
                    scanner.get_fried_plate_pool(),
                    return_exceptions=True,
                )
                r = {}
                r["limit_up"] = lu.get("total", 0) if not isinstance(lu, Exception) else 0
                r["limit_down"] = ld.get("total", 0) if not isinstance(ld, Exception) else 0
                r["fried_plate"] = fr.get("total", 0) if not isinstance(fr, Exception) else 0
                r["hot_sectors"] = lu.get("sectors", [])[:5] if not isinstance(lu, Exception) and lu.get("sectors") else []
                return r
            except Exception as e:
                return {"error": str(e)}

        async def _fetch_nb():
            try:
                return await nb_source.get_realtime_flow()
            except Exception as e:
                return {"error": str(e)}

        async def _fetch_news():
            try:
                return await aggregate_news(limit_per_source=15)
            except Exception as e:
                return {"error": str(e)}

        quotes, mkt_data, nb_data, news_data = await asyncio.gather(
            _fetch_quotes(), _fetch_market(), _fetch_nb(), _fetch_news(),
            return_exceptions=True,
        )

        if isinstance(news_data, Exception):
            news_data = {"error": str(news_data)}

        nb_dict = nb_data if isinstance(nb_data, dict) and "error" not in nb_data else {}
        mkt_dict = mkt_data if isinstance(mkt_data, dict) else {}

        # Build news_raw: market news (title, time, source only, no sentiment)
        market_news_raw = []
        if isinstance(news_data, dict) and "error" not in news_data:
            seen = set()
            for item in news_data.get("critical_news", []) + news_data.get("important_news", []) + news_data.get("top_sentiment_movers", []):
                t = item.get("title", "")
                if t and t[:40] not in seen:
                    seen.add(t[:40])
                    market_news_raw.append({
                        "title": t,
                        "time": item.get("time", ""),
                        "source": item.get("source", ""),
                    })
            market_news_raw = market_news_raw[:20]

        # Consecutive days from klines (for scoring extra, no sentiment)
        kline_cons = await calc_consecutive_from_klines()
        nb_outflow_days = get_nb_consecutive_outflow_days()

        scoring_extra = {
            "consecutive_up_days": kline_cons.get("consecutive_up_days", 0),
            "consecutive_down_days": kline_cons.get("consecutive_down_days", 0),
            "nb_consecutive_outflow_days": nb_outflow_days,
        }

        # Score all stocks (no news_sentiment, market_sentiment - LLM will judge)
        if isinstance(quotes, Exception):
            snapshot["stocks"] = {"error": str(quotes)}
            anomaly_codes = []
        else:
            quote_map = {q.code: q for q in quotes}
            scored = []
            anomaly_codes = []

            for code in wl_codes:
                q = quote_map.get(code)
                if not q:
                    scored.append({"code": code, "error": "no_quote"})
                    continue
                df = dm.get_daily_klines(code, days=60)
                avg_vol = 0.0
                avg_amt = 0.0
                if df is not None and len(df) >= 5:
                    avg_vol = float(df["volume"].tail(5).mean())
                    if "amount" in df.columns:
                        avg_amt = float(df["amount"].tail(5).mean())

                score = compute_stock_score(
                    quote=q, daily_df=df,
                    avg_volume=avg_vol, avg_amount=avg_amt,
                    extra=scoring_extra,
                )
                d = score.to_dict()
                # intraday: sentiment/market -> null, partial_total (65% tech+capital+fund)
                _s = d.get("score", {})
                _tech = _s.get("technical", {})
                _cap = _s.get("capital", {})
                _fund = _s.get("fundamental", {})
                _pt = (_tech.get("score") or 50) * 0.25 + (_cap.get("score") or 50) * 0.30 + (_fund.get("score") or 50) * 0.10
                d["score"] = dict(_s)
                d["score"]["sentiment"] = {"score": None, "signals": ["待LLM根据新闻判断"]}
                d["score"]["market"] = {"score": None, "signals": ["待LLM根据新闻判断"]}
                d["score"]["total"] = round(_pt, 1)
                d["score"]["partial_total"] = round(_pt, 1)
                d["score"]["llm_pending_weight"] = 0.35
                d["open"] = q.open
                d["high"] = q.high
                d["low"] = q.low
                vol_ratio = round(q.volume / avg_vol, 1) if avg_vol > 0 and q.volume > 0 else 1.0
                d["volume_ratio"] = vol_ratio
                is_anomaly = (
                    abs(d.get("change_pct", 0)) >= 1.5
                    or vol_ratio >= 1.8
                    or d.get("signal", "") in ("STRONG_BUY", "STRONG_SELL")
                )
                d["is_anomaly"] = is_anomaly
                if is_anomaly:
                    anomaly_codes.append(code)
                scored.append(d)

            snapshot["stocks"] = scored
            snapshot["anomaly_count"] = len(anomaly_codes)

            if anomaly_codes:
                async def _fetch_flow(c):
                    try:
                        return await scanner.get_capital_flow(c)
                    except Exception as e:
                        return {"code": c, "error": str(e)}
                flows = await asyncio.gather(*[_fetch_flow(c) for c in anomaly_codes[:6]])
                flow_map = {}
                for fl in flows:
                    if isinstance(fl, dict) and "code" in fl:
                        flow_map[fl["code"]] = fl
                snapshot["capital_flows"] = flow_map

        # Fetch stock-specific news for anomaly codes
        stock_news_raw = {}
        quote_map = {} if isinstance(quotes, Exception) else {q.code: q for q in quotes}
        if anomaly_codes and quote_map:
            news_fetcher = EastMoneyNewsFetcher()
            async def _fetch_stock_news(c):
                try:
                    q = quote_map.get(c)
                    name = q.name if q else ""
                    items = await news_fetcher.get_stock_news(c, name=name, limit=5)
                    return c, [{"title": n.title, "time": n.time, "source": n.source} for n in items]
                except Exception as e:
                    return c, []

            stock_results = await asyncio.gather(*[_fetch_stock_news(c) for c in anomaly_codes[:6]])
            for code, items in stock_results:
                if items:
                    stock_news_raw[code] = items

        snapshot["market"] = mkt_dict
        snapshot["northbound"] = nb_dict if nb_dict else {"error": "unavailable"}
        snapshot["news_raw"] = {
            "market": market_news_raw,
            "stocks": stock_news_raw,
        }

        valid_scores = [s for s in snapshot.get("stocks", []) if isinstance(s, dict) and "score" in s]
        if valid_scores:
            totals = [s["score"]["total"] for s in valid_scores if "total" in s.get("score", {})]
            if totals:
                snapshot["summary"] = {
                    "avg_score": round(sum(totals) / len(totals), 1),
                    "max_score": round(max(totals), 1),
                    "min_score": round(min(totals), 1),
                    "bullish_count": sum(1 for s in valid_scores if s.get("signal") in ("STRONG_BUY", "BUY")),
                    "bearish_count": sum(1 for s in valid_scores if s.get("signal") in ("STRONG_SELL", "SELL")),
                    "neutral_count": sum(1 for s in valid_scores if s.get("signal") in ("WATCH", "HOLD")),
                    "dimensions": "tech25%+capital30%+fund10%=65% | sentiment20%+market15%=35%(待LLM)",
                }

        elapsed = round(_time.time() - t_start, 1)
        snapshot["performance"] = {"data_fetch_seconds": elapsed}
        await src.close()
        print(json.dumps(snapshot, ensure_ascii=False, indent=2))

    elif tool == "sentiment_model_info":
        """查看情感分析模型信息"""
        from analysis.sentiment import get_sentiment_analyzer

        analyzer = get_sentiment_analyzer()
        info = analyzer.get_model_info()

        print(json.dumps({
            "model_info": info,
            "available_methods": ["finbert", "rule_based", "empty"],
            "status": "ready" if info["loaded"] else "not_loaded"
        }, ensure_ascii=False))

    elif tool == "sentiment_warmup":
        """预热情感分析模型"""
        from analysis.sentiment import get_sentiment_analyzer

        analyzer = get_sentiment_analyzer()
        success = analyzer.warmup()

        print(json.dumps({
            "success": success,
            "model_info": analyzer.get_model_info()
        }, ensure_ascii=False))


    else:
        print(json.dumps({"error": f"Unknown tool: {tool}", "available": [
            "stock_analysis", "weekly_review", "us_stock", "hk_stock", "commodity",
            "market_anomaly", "market_scan", "top_amount", "capital_flow",
            "northbound_flow", "global_overview", "system_health", "warm_klines",
            "news_sentiment", "gold_analysis", "margin_data", "lhb", "main_flow", "save_daily"
        ]}))

async def _batch_get_industries(codes: list) -> dict:
    """批量获取股票行业分类(东财 ulist API). 返回 {code: industry}."""
    if not codes:
        return {}
    import httpx
    codes = [c.strip().zfill(6) for c in codes if c.strip()]
    secids = ",".join(
        f"{'1' if c.startswith(('6', '5')) else '0'}.{c}" for c in codes
    )
    url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
    params = {
        "fltt": 2,
        "secids": secids,
        "fields": "f12,f100",
        "ut": "b2884a393a59ad64002292a3e90d46a5",
    }
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://quote.eastmoney.com"}
    try:
        async with httpx.AsyncClient(timeout=10, headers=headers) as c:
            resp = await c.get(url, params=params)
            data = resp.json()
            result = {}
            for item in data.get("data", {}).get("diff", []):
                code = str(item.get("f12", ""))
                industry = item.get("f100", "")
                if code and industry:
                    result[code] = industry
            return result
    except Exception:
        return {}

def _load_watchlist_codes(category="priority"):
    wl_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "knowledge", "watchlist.json")
    try:
        with open(wl_path) as f:
            wl = json.load(f)
        items = wl.get(category, [])
        codes = []
        for item in items:
            if isinstance(item, dict):
                codes.append(item.get("code", ""))
            elif isinstance(item, str):
                codes.append(item)
        return [c for c in codes if c]
    except Exception:
        return []

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        import traceback
        print(json.dumps({"error": str(e), "trace": traceback.format_exc()[-300:]}, ensure_ascii=False))
        sys.exit(1)
