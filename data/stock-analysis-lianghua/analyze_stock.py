#!/usr/bin/env python3
"""
通用股票技术分析脚本
基于 tradingagents/agents/analysts/market_analyst.py 的分析逻辑，
使用 YFinance 获取行情 + stockstats 计算技术指标。
无需 LLM API Key，可独立运行。

用法:
    python analyze_stock.py META                      # 分析 META，日期默认今天
    python analyze_stock.py AAPL --date 2025-02-20    # 分析 AAPL 指定日期
    python analyze_stock.py 0700.HK --days 60         # 分析腾讯，回看 60 天
    python analyze_stock.py TSLA --indicators rsi,macd,atr  # 指定指标
"""
import argparse
import glob
import os
import sys
import time as _time
from datetime import datetime, timedelta

import pandas as pd
import requests
import yfinance as yf
from stockstats import wrap

import warnings
warnings.filterwarnings("ignore")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_DIRS = [
    os.path.join(SCRIPT_DIR, "tradingagents", "dataflows", "data_cache"),
    os.path.join(SCRIPT_DIR, "FR1-data", "market_data", "price_data"),
]

# ── 默认技术指标（market_analyst.py 中推荐的 8 个互补指标） ──
DEFAULT_INDICATORS = [
    "close_50_sma",
    "close_200_sma",
    "close_10_ema",
    "macd",
    "macds",
    "macdh",
    "rsi",
    "atr",
]

ALL_SUPPORTED_INDICATORS = [
    "close_50_sma", "close_200_sma", "close_10_ema",
    "macd", "macds", "macdh",
    "rsi",
    "boll", "boll_ub", "boll_lb",
    "atr",
    "vwma",
]


# ═══════════════════════════ 数据获取 ═══════════════════════════

def _find_cached_file(symbol: str) -> str | None:
    """在缓存目录中查找已有的数据文件，优先选最新的。"""
    candidates = []
    for cache_dir in CACHE_DIRS:
        pattern = os.path.join(cache_dir, f"{symbol}-YFin-data-*.csv")
        candidates.extend(glob.glob(pattern))
    if not candidates:
        return None
    candidates.sort(key=os.path.getmtime, reverse=True)
    return candidates[0]


def _parse_google_symbol(symbol: str) -> tuple[str, str]:
    """将股票代码转换为 Google Finance 格式 (ticker, exchange)。"""
    symbol = symbol.upper()
    if ".HK" in symbol:
        ticker = symbol.replace(".HK", "").lstrip("0")
        return ticker, "HKG"
    if ".SZ" in symbol:
        return symbol.replace(".SZ", ""), "SHE"
    if ".SS" in symbol:
        return symbol.replace(".SS", ""), "SHA"
    return symbol, "NASDAQ"


def _fetch_google_finance(symbol: str, days: int = 1100) -> pd.DataFrame | None:
    """通过 Google Finance 页面抓取历史数据。"""
    import re
    import json as _json

    ticker, exchange = _parse_google_symbol(symbol)
    url = f"https://www.google.com/finance/quote/{ticker}:{exchange}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        return None

    # Google Finance 不直接给历史 CSV，但我们可以抓取当前价格
    # 使用 Google Finance 的 chart data API
    chart_url = f"https://www.google.com/finance/chart/{ticker}:{exchange}"

    # 尝试用备选方案: stooq.com (免费无需API key的历史数据源)
    return None


def _fetch_stooq(symbol: str, start_date: str, end_date: str) -> pd.DataFrame | None:
    """通过 Stooq 免费 API 获取历史数据。"""
    symbol_map = symbol.upper()
    if ".HK" in symbol_map:
        stooq_sym = symbol_map.replace(".HK", ".HK")
    elif ".SZ" in symbol_map or ".SS" in symbol_map:
        stooq_sym = symbol_map
    else:
        stooq_sym = f"{symbol_map}.US"

    url = f"https://stooq.com/q/d/l/?s={stooq_sym}&d1={start_date.replace('-','')}&d2={end_date.replace('-','')}&i=d"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
    }
    resp = requests.get(url, headers=headers, timeout=30)
    if resp.status_code != 200:
        return None

    from io import StringIO
    df = pd.read_csv(StringIO(resp.text))
    if df.empty or "Date" not in df.columns:
        return None

    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def _fetch_yahoo_chart_api(symbol: str, start_ts: int, end_ts: int) -> pd.DataFrame | None:
    """直接通过 Yahoo Finance Chart API 获取数据。"""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    params = {
        "period1": start_ts,
        "period2": end_ts,
        "interval": "1d",
        "events": "history",
    }
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        ),
    }
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    if resp.status_code != 200:
        return None

    body = resp.json()
    result = body.get("chart", {}).get("result")
    if not result:
        return None

    timestamps = result[0].get("timestamp", [])
    quote = result[0].get("indicators", {}).get("quote", [{}])[0]

    if not timestamps or not quote:
        return None

    df = pd.DataFrame({
        "Date": pd.to_datetime(timestamps, unit="s", utc=True),
        "Open": quote.get("open"),
        "High": quote.get("high"),
        "Low": quote.get("low"),
        "Close": quote.get("close"),
        "Volume": quote.get("volume"),
    })
    df["Date"] = df["Date"].dt.tz_localize(None)
    df = df.dropna(subset=["Close"])
    return df


def fetch_data(symbol: str, curr_date: str, look_back_years: int = 3) -> pd.DataFrame:
    """获取股票历史数据：Stooq → Yahoo Chart API → yfinance → 本地缓存。"""
    end_date = datetime.strptime(curr_date, "%Y-%m-%d") + timedelta(days=1)
    start_date = end_date - pd.DateOffset(years=look_back_years)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    start_ts = int(pd.Timestamp(start_date).timestamp())
    end_ts = int(pd.Timestamp(end_date).timestamp())

    # 方法1: Stooq（免费、无需API key、不限速）
    try:
        print("    尝试 Stooq 数据源...")
        data = _fetch_stooq(symbol, start_str, curr_date)
        if data is not None and len(data) > 0:
            print(f"    Stooq 成功，获取 {len(data)} 条记录")
            _save_cache(data, symbol, start_date, curr_date)
            return data
    except Exception as e:
        print(f"    Stooq 失败: {e}")

    # 方法2: Yahoo Chart API
    try:
        print("    尝试 Yahoo Chart API...")
        data = _fetch_yahoo_chart_api(symbol, start_ts, end_ts)
        if data is not None and len(data) > 0:
            print(f"    Chart API 成功，获取 {len(data)} 条记录")
            _save_cache(data, symbol, start_date, curr_date)
            return data
    except Exception as e:
        print(f"    Chart API 失败: {e}")

    # 方法3: yfinance Ticker.history()
    try:
        print("    尝试 yfinance...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_str, end=end_str, auto_adjust=True)
        if data is not None and len(data) > 0:
            data = data.reset_index()
            data["Date"] = pd.to_datetime(data["Date"]).dt.tz_localize(None)
            print(f"    yfinance 成功，获取 {len(data)} 条记录")
            _save_cache(data, symbol, start_date, curr_date)
            return data
    except Exception as e:
        print(f"    yfinance 失败: {e}")

    # 方法3: 本地缓存回退
    cached = _find_cached_file(symbol)
    if cached:
        print(f"    在线获取均失败，使用本地缓存: {os.path.basename(cached)}")
        data = pd.read_csv(cached)
        if "Date" not in data.columns and "Unnamed: 0" in data.columns:
            data = data.rename(columns={"Unnamed: 0": "Date"})
        data = data.reset_index(drop=True)
        if len(data) > 0:
            return data

    return pd.DataFrame()


def _save_cache(data: pd.DataFrame, symbol: str, start_date, curr_date: str):
    """保存数据到缓存目录。"""
    try:
        cache_dir = CACHE_DIRS[0]
        os.makedirs(cache_dir, exist_ok=True)
        start_str = start_date.strftime("%Y-%m-%d") if hasattr(start_date, "strftime") else str(start_date)[:10]
        cache_file = os.path.join(cache_dir, f"{symbol}-YFin-data-{start_str}-{curr_date}.csv")
        data.to_csv(cache_file, index=False)
    except Exception:
        pass


# ═══════════════════════════ 指标计算 ═══════════════════════════

def compute_indicator_series(
    data: pd.DataFrame, indicator: str, curr_date: str, look_back_days: int
) -> list[dict]:
    """计算指定指标在回看区间内的时间序列。"""
    df = wrap(data.copy())
    df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    df[indicator]  # trigger stockstats calculation

    end = datetime.strptime(curr_date, "%Y-%m-%d")
    start = end - timedelta(days=look_back_days)
    mask = (df["Date"] >= start.strftime("%Y-%m-%d")) & (df["Date"] <= curr_date)
    subset = df.loc[mask, ["Date", indicator]].dropna()

    return [{"date": row["Date"], "value": row[indicator]} for _, row in subset.iterrows()]


def get_recent_prices(data: pd.DataFrame, curr_date: str, days: int = 30) -> pd.DataFrame:
    """截取近期行情数据。"""
    data_copy = data.copy()
    data_copy["DateStr"] = pd.to_datetime(data_copy["Date"]).dt.strftime("%Y-%m-%d")
    end = datetime.strptime(curr_date, "%Y-%m-%d")
    start = end - timedelta(days=days)
    mask = (data_copy["DateStr"] >= start.strftime("%Y-%m-%d")) & (data_copy["DateStr"] <= curr_date)
    subset = data_copy.loc[mask, ["DateStr", "Open", "High", "Low", "Close", "Volume"]]
    return subset.rename(columns={"DateStr": "Date"})


# ═══════════════════════════ 信号判断 ═══════════════════════════

def judge_trend(price, sma50, sma200):
    if sma50 is None or sma200 is None:
        return "数据不足", ""
    if price > sma50 > sma200:
        label = "强势上涨"
        detail = f"多头排列 (价格 {price:.2f} > 50SMA {sma50:.2f} > 200SMA {sma200:.2f})"
    elif price > sma50:
        label = "温和上涨"
        detail = f"中期偏多 (价格 {price:.2f} > 50SMA {sma50:.2f}, 200SMA {sma200:.2f})"
    elif price < sma50 < sma200:
        label = "强势下跌"
        detail = f"空头排列 (价格 {price:.2f} < 50SMA {sma50:.2f} < 200SMA {sma200:.2f})"
    elif price < sma50:
        label = "温和下跌"
        detail = f"中期偏空 (价格 {price:.2f} < 50SMA {sma50:.2f}, 200SMA {sma200:.2f})"
    else:
        label = "震荡整理"
        detail = f"价格 {price:.2f}, 50SMA {sma50:.2f}, 200SMA {sma200:.2f}"
    cross = "金叉 (50SMA > 200SMA)" if sma50 > sma200 else "死叉 (50SMA < 200SMA)"
    return label, f"{detail}\n     {cross}"


def judge_rsi(rsi):
    if rsi is None:
        return "N/A"
    if rsi > 70:
        return "超买区域，注意回调风险"
    if rsi > 60:
        return "偏强，多方占优"
    if rsi > 40:
        return "中性区域"
    if rsi > 30:
        return "偏弱，空方占优"
    return "超卖区域，可能存在反弹机会"


# ═══════════════════════════ 报告输出 ═══════════════════════════

def print_report(symbol: str, curr_date: str, look_back_days: int,
                 data: pd.DataFrame, indicators: list[str]):
    """生成并输出完整的技术分析报告。"""

    print(f"\n{'='*70}")
    print(f"  {symbol} 股票市场技术分析报告")
    print(f"  分析日期: {curr_date}  |  回看周期: {look_back_days} 天")
    print(f"{'='*70}\n")

    # ── 一、近期行情 ──
    print(f"{'─'*70}")
    print("一、近期行情数据（最近 15 个交易日）")
    print(f"{'─'*70}")
    recent = get_recent_prices(data, curr_date, days=25)
    recent_tail = recent.tail(15)

    if recent_tail.empty:
        print("  无法获取近期行情数据。")
        return

    for _, row in recent_tail.iterrows():
        print(f"  {row['Date']}  开:{row['Open']:>10.2f}  高:{row['High']:>10.2f}  "
              f"低:{row['Low']:>10.2f}  收:{row['Close']:>10.2f}  量:{int(row['Volume']):>14,}")

    latest = recent_tail.iloc[-1]
    prev = recent_tail.iloc[-2] if len(recent_tail) >= 2 else latest
    change = latest["Close"] - prev["Close"]
    change_pct = (change / prev["Close"]) * 100
    print(f"\n  最新收盘价: {latest['Close']:.2f}  |  日涨跌: {change:+.2f} ({change_pct:+.2f}%)")

    close_series = recent["Close"]
    print(f"\n  近期统计:")
    print(f"    最高: {close_series.max():.2f}  最低: {close_series.min():.2f}  "
          f"均值: {close_series.mean():.2f}")
    period_change = close_series.iloc[-1] - close_series.iloc[0]
    period_pct = (period_change / close_series.iloc[0]) * 100
    print(f"    区间涨跌: {period_change:+.2f} ({period_pct:+.2f}%)")

    # ── 二、技术指标 ──
    print(f"\n{'─'*70}")
    print("二、技术指标分析")
    print(f"{'─'*70}")

    indicator_latest: dict[str, float | None] = {}

    for ind in indicators:
        print(f"\n  【{ind}】 最近 {look_back_days} 天趋势:")
        try:
            series = compute_indicator_series(data, ind, curr_date, look_back_days)
            if not series:
                print("    无数据")
                indicator_latest[ind] = None
                continue

            if len(series) > 10:
                for item in series[:3]:
                    print(f"  {item['date']}: {item['value']:.4f}")
                print(f"    ... (共 {len(series)} 条，省略中间数据)")
                for item in series[-5:]:
                    print(f"  {item['date']}: {item['value']:.4f}")
            else:
                for item in series:
                    print(f"  {item['date']}: {item['value']:.4f}")

            indicator_latest[ind] = series[-1]["value"]
        except Exception as e:
            print(f"    计算出错: {e}")
            indicator_latest[ind] = None

    # ── 三、综合分析 ──
    print(f"\n{'─'*70}")
    print("三、综合分析")
    print(f"{'─'*70}")

    price = latest["Close"]
    sma50 = indicator_latest.get("close_50_sma")
    sma200 = indicator_latest.get("close_200_sma")
    ema10 = indicator_latest.get("close_10_ema")
    rsi_val = indicator_latest.get("rsi")
    macd_val = indicator_latest.get("macd")
    macds_val = indicator_latest.get("macds")
    macdh_val = indicator_latest.get("macdh")
    atr_val = indicator_latest.get("atr")
    boll_val = indicator_latest.get("boll")
    boll_ub_val = indicator_latest.get("boll_ub")
    boll_lb_val = indicator_latest.get("boll_lb")

    trend_label, trend_detail = judge_trend(price, sma50, sma200)
    rsi_signal = judge_rsi(rsi_val)

    print(f"\n  1. 趋势判断:")
    if trend_detail:
        print(f"     {trend_detail}")

    print(f"\n  2. 动量分析:")
    if rsi_val is not None:
        print(f"     RSI = {rsi_val:.2f} → {rsi_signal}")
    if macd_val is not None and macds_val is not None:
        macd_sig = "MACD 在信号线之上，多头信号" if macd_val > macds_val else "MACD 在信号线之下，空头信号"
        print(f"     MACD = {macd_val:.4f}, 信号线 = {macds_val:.4f} → {macd_sig}")
    if macdh_val is not None:
        direction = "正值（多方动能）" if macdh_val > 0 else "负值（空方动能）"
        print(f"     MACD柱状图 = {macdh_val:.4f} → {direction}")

    print(f"\n  3. 波动率分析:")
    if atr_val is not None:
        atr_pct = (atr_val / price) * 100
        print(f"     ATR = {atr_val:.2f} (占股价 {atr_pct:.2f}%)")
        if atr_pct > 3:
            print("     波动性较高，建议适当控制仓位")
        elif atr_pct > 1.5:
            print("     波动性适中")
        else:
            print("     波动性较低，市场相对平静")
    else:
        atr_pct = None

    if boll_val is not None and boll_ub_val is not None and boll_lb_val is not None:
        print(f"     布林带: 上轨 {boll_ub_val:.2f} | 中轨 {boll_val:.2f} | 下轨 {boll_lb_val:.2f}")
        if price > boll_ub_val:
            print("     价格突破上轨，注意超买回调")
        elif price < boll_lb_val:
            print("     价格跌破下轨，可能超卖反弹")
        else:
            print("     价格在布林带区间内运行")

    if ema10 is not None:
        print(f"\n  4. 短期信号:")
        if price > ema10:
            print(f"     价格在 10EMA ({ema10:.2f}) 之上，短期偏多")
        else:
            print(f"     价格在 10EMA ({ema10:.2f}) 之下，短期偏空")

    # ── 四、汇总表 ──
    print(f"\n{'─'*70}")
    print("四、指标汇总")
    print(f"{'─'*70}")
    print(f"  {'指标':<18} {'当前值':>12} {'信号':>24}")
    print(f"  {'─'*54}")

    def _sig(ind_name):
        v = indicator_latest.get(ind_name)
        match ind_name:
            case "close_50_sma":
                return f"价格{'>' if price > (v or 0) else '<'}均线" if v else "N/A"
            case "close_200_sma":
                return f"价格{'>' if price > (v or 0) else '<'}均线" if v else "N/A"
            case "close_10_ema":
                return f"价格{'>' if price > (v or 0) else '<'}EMA" if v else "N/A"
            case "macd":
                return f"{'多' if (v or 0) > 0 else '空'}头" if v is not None else "N/A"
            case "macds":
                return f"MACD{'>' if (macd_val or 0) > (v or 0) else '<'}信号线" if v is not None else "N/A"
            case "macdh":
                return f"{'正' if (v or 0) > 0 else '负'}值" if v is not None else "N/A"
            case "rsi":
                return rsi_signal
            case "atr":
                return f"波动率{atr_pct:.1f}%" if atr_pct else "N/A"
            case "boll":
                return f"中轨 {v:.2f}" if v else "N/A"
            case "boll_ub":
                return f"价格{'>' if price > (v or 0) else '<'}上轨" if v else "N/A"
            case "boll_lb":
                return f"价格{'>' if price > (v or 0) else '<'}下轨" if v else "N/A"
            case "vwma":
                return f"价格{'>' if price > (v or 0) else '<'}VWMA" if v else "N/A"
            case _:
                return "N/A"

    ind_names = {
        "close_50_sma": "50日均线", "close_200_sma": "200日均线", "close_10_ema": "10日EMA",
        "macd": "MACD", "macds": "信号线", "macdh": "MACD柱",
        "rsi": "RSI", "atr": "ATR",
        "boll": "布林中轨", "boll_ub": "布林上轨", "boll_lb": "布林下轨",
        "vwma": "VWMA",
    }

    for ind in indicators:
        v = indicator_latest.get(ind)
        name = ind_names.get(ind, ind)
        val_str = f"{v:.4f}" if v is not None else "N/A"
        sig = _sig(ind)
        print(f"  {name:<18} {val_str:>12} {sig:>24}")

    print(f"\n{'='*70}")
    print(f"  总体趋势判断: {trend_label}")
    print(f"{'='*70}\n")


# ═══════════════════════════ CLI 入口 ═══════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description="股票技术分析工具 - 基于 market_analyst.py 的分析逻辑",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python analyze_stock.py META
  python analyze_stock.py AAPL --date 2025-02-20
  python analyze_stock.py 0700.HK --days 60
  python analyze_stock.py TSLA --indicators rsi,macd,atr,close_50_sma
  python analyze_stock.py NVDA --indicators all
        """,
    )
    parser.add_argument("symbol", help="股票代码，如 META, AAPL, 0700.HK, TSLA")
    parser.add_argument(
        "--date", "-d",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="分析日期，格式 YYYY-MM-DD（默认: 今天）",
    )
    parser.add_argument(
        "--days", "-n",
        type=int, default=90,
        help="回看天数（默认: 90）",
    )
    parser.add_argument(
        "--indicators", "-i",
        default=None,
        help="逗号分隔的指标列表，或 'all' 使用全部指标（默认: 8个核心指标）",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    symbol = args.symbol.upper()
    curr_date = args.date
    look_back_days = args.days

    if args.indicators:
        if args.indicators.strip().lower() == "all":
            indicators = ALL_SUPPORTED_INDICATORS
        else:
            indicators = [i.strip() for i in args.indicators.split(",")]
            invalid = [i for i in indicators if i not in ALL_SUPPORTED_INDICATORS]
            if invalid:
                print(f"不支持的指标: {', '.join(invalid)}")
                print(f"支持的指标: {', '.join(ALL_SUPPORTED_INDICATORS)}")
                sys.exit(1)
    else:
        indicators = DEFAULT_INDICATORS

    print(f">>> 正在从 Yahoo Finance 获取 {symbol} 数据...")
    data = fetch_data(symbol, curr_date)
    if data.empty:
        print("    未能获取到数据，请检查股票代码或网络后重试。")
        sys.exit(1)
    print(f"    获取到 {len(data)} 条历史记录")

    print_report(symbol, curr_date, look_back_days, data, indicators)


if __name__ == "__main__":
    main()
