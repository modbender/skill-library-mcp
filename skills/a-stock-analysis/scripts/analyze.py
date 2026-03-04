#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
A股实时行情与分时量能分析工具

数据源：新浪财经（统一接口）
支持：沪市(sh)、深市(sz) 股票

Usage:
    uv run analyze.py 600789              # 单只股票
    uv run analyze.py 600789 002446       # 多只股票
    uv run analyze.py 600789 --minute     # 分时量能分析
    uv run analyze.py 600789 --json       # JSON输出
"""

import argparse
import json
import re
import sys
import urllib.request
from datetime import datetime
from typing import Optional


def get_sina_symbol(code: str) -> str:
    """根据股票代码生成新浪格式代码"""
    code = code.upper().replace("SH", "").replace("SZ", "").replace(".", "")
    
    # 沪市: 6开头
    if code.startswith("6"):
        return "sh" + code
    # 深市: 0/3开头
    elif code.startswith(("0", "3")):
        return "sz" + code
    # 北交所: 8/4开头
    elif code.startswith(("8", "4")):
        return "bj" + code
    else:
        return "sh" + code


def fetch_realtime_sina(symbols: list[str]) -> dict[str, dict]:
    """从新浪获取实时行情（支持批量）
    
    新浪接口返回格式:
    var hq_str_sh600789="名称,今开,昨收,现价,最高,最低,买一,卖一,成交量(股),成交额(元),...";
    
    字段说明:
    0: 名称
    1: 今开
    2: 昨收  
    3: 现价
    4: 最高
    5: 最低
    6: 买一价
    7: 卖一价
    8: 成交量(股)
    9: 成交额(元)
    """
    result = {}
    
    try:
        codes_str = ",".join(symbols)
        url = f"https://hq.sinajs.cn/list={codes_str}"
        
        req = urllib.request.Request(url, headers={
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode("gbk")
        
        # 解析每行
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            
            # var hq_str_sh600789="数据";
            match = re.match(r'var hq_str_(\w+)="([^"]*)"', line)
            if not match:
                continue
            
            symbol = match.group(1)
            data_str = match.group(2)
            
            if not data_str:
                continue
            
            fields = data_str.split(",")
            if len(fields) < 32:
                continue
            
            name = fields[0]
            open_price = float(fields[1]) if fields[1] else None
            pre_close = float(fields[2]) if fields[2] else None
            price = float(fields[3]) if fields[3] else None
            high = float(fields[4]) if fields[4] else None
            low = float(fields[5]) if fields[5] else None
            volume = int(float(fields[8])) if fields[8] else 0  # 股
            amount = float(fields[9]) if fields[9] else 0  # 元
            
            if not price or price <= 0:
                continue
            
            # 计算涨跌
            change_amt = price - pre_close if pre_close else 0
            change_pct = (change_amt / pre_close * 100) if pre_close and pre_close > 0 else 0
            
            # 换手率需要总股本，这里先留空
            result[symbol] = {
                "code": symbol[2:],  # 去掉sh/sz前缀
                "name": name,
                "price": price,
                "open": open_price,
                "pre_close": pre_close,
                "high": high,
                "low": low,
                "volume": volume // 100,  # 转换为手
                "amount": amount,
                "change_amt": round(change_amt, 2),
                "change_pct": round(change_pct, 2),
                "turnover": None,  # 新浪实时接口不提供换手率
            }
            
    except Exception as e:
        print(f"新浪实时接口错误: {e}", file=sys.stderr)
    
    return result


def fetch_minute_data_sina(symbol: str, count: int = 250) -> list[dict]:
    """从新浪获取分时K线数据
    
    接口: CN_MarketDataService.getKLineData
    返回JSON数组，每条记录包含:
    - day: 时间 (2026-01-27 09:31:00)
    - open/high/low/close: OHLC价格
    - volume: 成交量(股)
    - amount: 成交额(元)
    """
    url = f"https://quotes.sina.cn/cn/api/jsonp_v2.php/var%20_{symbol}=/CN_MarketDataService.getKLineData?symbol={symbol}&scale=1&ma=no&datalen={count}"
    
    try:
        req = urllib.request.Request(url, headers={
            "Referer": "https://finance.sina.com.cn",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        text = resp.read().decode("utf-8")
        
        # 解析JSONP: var _xxx=([...])
        match = re.search(r"\(\[(.*)\]\)", text, re.DOTALL)
        if not match:
            return []
        
        data = json.loads("[" + match.group(1) + "]")
        result = []
        for item in data:
            result.append({
                "time": item["day"],
                "open": float(item["open"]),
                "high": float(item["high"]),
                "low": float(item["low"]),
                "close": float(item["close"]),
                "volume": int(item["volume"]),  # 股
                "amount": float(item["amount"]),  # 元
            })
        return result
        
    except Exception as e:
        print(f"新浪分时接口错误: {e}", file=sys.stderr)
    
    return []


def analyze_minute_volume(minute_data: list[dict]) -> dict:
    """分析分时量能"""
    if not minute_data:
        return {"error": "无分时数据"}
    
    # 过滤交易时段数据
    trading_data = [
        d for d in minute_data
        if d["volume"] > 0 and "09:25" <= d["time"][-8:-3] <= "15:00"
    ]
    
    if not trading_data:
        return {"error": "无有效交易数据"}
    
    # 统计各时段成交量
    total_vol = sum(d["volume"] for d in trading_data)
    
    def period_vol(start: str, end: str) -> int:
        return sum(
            d["volume"] for d in trading_data
            if start <= d["time"][-8:-3] < end
        )
    
    open_30 = period_vol("09:30", "10:00")
    mid_am = period_vol("10:00", "11:30")
    mid_pm = period_vol("13:00", "14:30")
    close_30 = period_vol("14:30", "15:01")
    
    # 放量时段 TOP 10
    sorted_by_vol = sorted(trading_data, key=lambda x: x["volume"], reverse=True)[:10]
    top_volumes = [
        {
            "time": d["time"][-8:],
            "price": d["close"],
            "volume": d["volume"] // 100,  # 转换为手
            "amount": d["amount"],
        }
        for d in sorted_by_vol
    ]
    
    # 主力动向判断
    signals = []
    if total_vol > 0:
        if close_30 / total_vol > 0.25:
            signals.append("尾盘大幅放量，可能有主力抢筹或出货")
        elif close_30 / total_vol > 0.15:
            signals.append("尾盘有一定放量")
        if open_30 / total_vol > 0.30:
            signals.append("早盘主力抢筹明显")
        if open_30 / total_vol > 0.40:
            signals.append("早盘放量异常，主力强势介入")
    
    # 检测涨停/跌停
    last_price = trading_data[-1]["close"] if trading_data else 0
    highest_vol_price = sorted_by_vol[0]["close"] if sorted_by_vol else 0
    if last_price > 0 and abs(last_price - highest_vol_price) < 0.01:
        signals.append("封板状态，关注封单量")
    
    return {
        "total_volume": total_vol // 100,  # 手
        "total_amount": sum(d["amount"] for d in trading_data),
        "distribution": {
            "open_30min": {
                "volume": open_30 // 100,
                "percent": round(open_30 / total_vol * 100, 1) if total_vol else 0,
            },
            "mid_am": {
                "volume": mid_am // 100,
                "percent": round(mid_am / total_vol * 100, 1) if total_vol else 0,
            },
            "mid_pm": {
                "volume": mid_pm // 100,
                "percent": round(mid_pm / total_vol * 100, 1) if total_vol else 0,
            },
            "close_30min": {
                "volume": close_30 // 100,
                "percent": round(close_30 / total_vol * 100, 1) if total_vol else 0,
            },
        },
        "top_volumes": top_volumes,
        "signals": signals,
    }


def format_realtime(data: dict) -> str:
    """格式化实时行情输出"""
    change_symbol = "+" if data["change_pct"] >= 0 else ""
    turnover_str = f"换手: {data['turnover']:.2f}%" if data.get("turnover") else ""
    
    lines = [
        f"{'='*60}",
        f"股票: {data['name']} ({data['code']})",
        f"{'='*60}",
        f"",
        f"【实时行情】",
        f"  现价: {data['price']:.2f}  涨跌: {change_symbol}{data['change_pct']:.2f}%",
        f"  今开: {data['open']:.2f}  最高: {data['high']:.2f}  最低: {data['low']:.2f}",
        f"  昨收: {data['pre_close']:.2f}  {turnover_str}",
        f"  成交量: {data['volume']/10000:.1f}万手  成交额: {data['amount']/100000000:.2f}亿",
    ]
    return "\n".join(lines)


def format_minute_analysis(analysis: dict, name: str = "") -> str:
    """格式化分时分析输出"""
    if "error" in analysis:
        return f"分时分析错误: {analysis['error']}"
    
    lines = [
        f"",
        f"【分时量能分析】{name}",
        f"  全天成交: {analysis['total_volume']}手 ({analysis['total_amount']/10000:.1f}万元)",
        f"",
        f"  成交分布:",
        f"    早盘30分(9:30-10:00): {analysis['distribution']['open_30min']['volume']}手 ({analysis['distribution']['open_30min']['percent']}%)",
        f"    上午中段(10:00-11:30): {analysis['distribution']['mid_am']['volume']}手 ({analysis['distribution']['mid_am']['percent']}%)",
        f"    下午中段(13:00-14:30): {analysis['distribution']['mid_pm']['volume']}手 ({analysis['distribution']['mid_pm']['percent']}%)",
        f"    尾盘30分(14:30-15:00): {analysis['distribution']['close_30min']['volume']}手 ({analysis['distribution']['close_30min']['percent']}%)",
        f"",
        f"  放量时段 TOP 10:",
    ]
    
    for item in analysis["top_volumes"]:
        lines.append(f"    {item['time']} 价格:{item['price']:.2f} 成交:{item['volume']}手 金额:{item['amount']/10000:.1f}万")
    
    if analysis["signals"]:
        lines.append(f"")
        lines.append(f"  【主力动向判断】")
        for signal in analysis["signals"]:
            lines.append(f"    🔥 {signal}")
    
    return "\n".join(lines)


def analyze_stock(code: str, with_minute: bool = False, realtime_cache: dict = None) -> dict:
    """分析单只股票"""
    sina_symbol = get_sina_symbol(code)
    
    # 获取实时行情（支持缓存以批量获取）
    if realtime_cache and sina_symbol in realtime_cache:
        realtime = realtime_cache[sina_symbol]
    else:
        realtime_data = fetch_realtime_sina([sina_symbol])
        realtime = realtime_data.get(sina_symbol)
    
    if not realtime:
        return {"error": f"无法获取 {code} 的行情数据"}
    
    result = {
        "code": code,
        "name": realtime["name"],
        "realtime": realtime,
        "updated_at": datetime.now().isoformat(),
    }
    
    # 分时分析
    if with_minute:
        minute_data = fetch_minute_data_sina(sina_symbol)
        minute_analysis = analyze_minute_volume(minute_data)
        result["minute_analysis"] = minute_analysis
    
    return result


def main():
    parser = argparse.ArgumentParser(description="A股实时行情与分时量能分析")
    parser.add_argument("codes", nargs="+", help="股票代码，如 600789 002446")
    parser.add_argument("--minute", "-m", action="store_true", help="包含分时量能分析")
    parser.add_argument("--json", "-j", action="store_true", help="JSON格式输出")
    
    args = parser.parse_args()
    
    # 批量获取实时行情
    sina_symbols = [get_sina_symbol(code) for code in args.codes]
    realtime_cache = fetch_realtime_sina(sina_symbols)
    
    results = []
    for code in args.codes:
        result = analyze_stock(code, with_minute=args.minute, realtime_cache=realtime_cache)
        results.append(result)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for result in results:
            if "error" in result:
                print(f"错误: {result['error']}")
                continue
            
            print(format_realtime(result["realtime"]))
            
            if args.minute and "minute_analysis" in result:
                print(format_minute_analysis(result["minute_analysis"], result["name"]))
            
            print()


if __name__ == "__main__":
    main()
