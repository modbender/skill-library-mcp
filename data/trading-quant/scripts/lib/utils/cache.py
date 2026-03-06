"""JSON 文件缓存系统: 支持普通 KV 缓存 + 按日历史记录."""

import json
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

CACHE_DIR = os.path.expanduser("~/.openclaw/workspace-trading/cache")
DAILY_LOG_FILE = os.path.join(CACHE_DIR, "daily_market_log.json")

_kline_consecutive_cache = {"data": None, "ts": 0, "ttl": 600}  # 10 min cache


def ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def cache_set(key: str, data: dict, ttl_seconds: int = 3600):
    """写入 KV 缓存."""
    ensure_cache_dir()
    entry = {"data": data, "ts": time.time(), "ttl": ttl_seconds}
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path, "w") as f:
            json.dump(entry, f, ensure_ascii=False)
    except Exception as e:
        logger.warning(f"Cache write failed for {key}: {e}")


def cache_get(key: str) -> Optional[dict]:
    """读取 KV 缓存, 过期返回 None."""
    path = os.path.join(CACHE_DIR, f"{key}.json")
    try:
        with open(path) as f:
            entry = json.load(f)
        if time.time() - entry["ts"] > entry["ttl"]:
            return None
        return entry["data"]
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return None


def save_daily_snapshot(date: str, data: dict):
    """保存某日市场快照. date 格式 YYYY-MM-DD.
    
    data 示例: {
        "hs300_pct": 0.5,       # 沪深300涨跌%
        "northbound_net": 50.0, # 北向净流入(亿)
        "limit_up": 40,
        "limit_down": 5,
        "sentiment_score": 55,
    }
    """
    ensure_cache_dir()
    log = _load_daily_log()
    log[date] = data
    # 只保留最近 60 天
    sorted_dates = sorted(log.keys())
    if len(sorted_dates) > 60:
        for d in sorted_dates[:-60]:
            del log[d]
    try:
        with open(DAILY_LOG_FILE, "w") as f:
            json.dump(log, f, ensure_ascii=False, indent=1)
    except Exception as e:
        logger.warning(f"Daily log save failed: {e}")


def get_consecutive_up_days() -> int:
    """从历史日志计算沪深300连涨天数. 返回正数=连涨, 0=无数据."""
    log = _load_daily_log()
    if not log:
        return 0
    dates = sorted(log.keys(), reverse=True)
    count = 0
    for d in dates:
        pct = log[d].get("hs300_pct") or 0
        if pct > 0:
            count += 1
        else:
            break
    return count


def get_consecutive_down_days() -> int:
    """从历史日志计算沪深300连跌天数."""
    log = _load_daily_log()
    if not log:
        return 0
    dates = sorted(log.keys(), reverse=True)
    count = 0
    for d in dates:
        pct = log[d].get("hs300_pct") or 0
        if pct < 0:
            count += 1
        else:
            break
    return count


def get_nb_consecutive_outflow_days() -> int:
    """从历史日志计算北向资金连续净流出天数."""
    log = _load_daily_log()
    if not log:
        return 0
    dates = sorted(log.keys(), reverse=True)
    count = 0
    for d in dates:
        nb = log[d].get("northbound_net") or 0
        if nb < 0:
            count += 1
        else:
            break
    return count


def _load_daily_log() -> dict:
    try:
        with open(DAILY_LOG_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


async def calc_consecutive_from_klines() -> dict:
    """从沪深300日K线计算连涨/连跌天数(新浪接口, 10min缓存).
    
    Returns: {"consecutive_up_days": int, "consecutive_down_days": int}
    """
    global _kline_consecutive_cache
    if _kline_consecutive_cache["data"] and time.time() - _kline_consecutive_cache["ts"] < _kline_consecutive_cache["ttl"]:
        return _kline_consecutive_cache["data"]
    try:
        import httpx
        url = "https://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData"
        params = {"symbol": "sh000300", "scale": "240", "ma": "no", "datalen": "30"}
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}
        async with httpx.AsyncClient(timeout=10, headers=headers) as c:
            resp = await c.get(url, params=params)
            data = json.loads(resp.text)
            if not data or len(data) < 2:
                return {"consecutive_up_days": 0, "consecutive_down_days": 0}
            
            up_count = 0
            down_count = 0
            for i in range(len(data) - 1, 0, -1):
                change = float(data[i]["close"]) - float(data[i-1]["close"])
                if change > 0:
                    if down_count > 0:
                        break
                    up_count += 1
                elif change < 0:
                    if up_count > 0:
                        break
                    down_count += 1
                else:
                    break
            
            result = {"consecutive_up_days": up_count, "consecutive_down_days": down_count}
            _kline_consecutive_cache["data"] = result
            _kline_consecutive_cache["ts"] = time.time()
            return result
    except Exception as e:
        logger.warning(f"K-line consecutive calc failed: {e}")
        return {"consecutive_up_days": 0, "consecutive_down_days": 0}
