#!/usr/bin/env python3
"""A股交易日历工具 - 基于 AKShare（新浪财经数据，覆盖至2026年底）"""
import sys
import json
import argparse
from datetime import date, datetime, timedelta
import akshare as ak

_CACHE: set = None


def _load_calendar() -> set:
    global _CACHE
    if _CACHE is None:
        df = ak.tool_trade_date_hist_sina()
        # trade_date 是 datetime.date 对象，统一转为 YYYY-MM-DD 字符串
        _CACHE = set(str(d) for d in df["trade_date"].tolist())
    return _CACHE


def is_trade_day(d: str) -> bool:
    """判断某天是否为A股交易日，d 格式：YYYY-MM-DD"""
    cal = _load_calendar()
    return d in cal


def next_trade_day(d: str) -> str:
    """返回 d 当天或之后最近的交易日"""
    cal = _load_calendar()
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    for _ in range(30):
        if dt.strftime("%Y-%m-%d") in cal:
            return dt.strftime("%Y-%m-%d")
        dt += timedelta(days=1)
    raise ValueError("找不到下一个交易日（超过30天）")


def prev_trade_day(d: str) -> str:
    """返回 d 当天或之前最近的交易日"""
    cal = _load_calendar()
    dt = datetime.strptime(d, "%Y-%m-%d").date()
    for _ in range(30):
        if dt.strftime("%Y-%m-%d") in cal:
            return dt.strftime("%Y-%m-%d")
        dt -= timedelta(days=1)
    raise ValueError("找不到上一个交易日（超过30天）")


def trade_days_in_range(start: str, end: str) -> list:
    """返回 [start, end] 范围内所有交易日列表"""
    cal = _load_calendar()
    s = datetime.strptime(start, "%Y-%m-%d").date()
    e = datetime.strptime(end, "%Y-%m-%d").date()
    result = []
    cur = s
    while cur <= e:
        ds = cur.strftime("%Y-%m-%d")
        if ds in cal:
            result.append(ds)
        cur += timedelta(days=1)
    return result


def main():
    parser = argparse.ArgumentParser(description="A股交易日历工具")
    sub = parser.add_subparsers(dest="cmd")

    # check: 判断某天是否交易日
    p1 = sub.add_parser("check", help="判断某天是否为交易日")
    p1.add_argument("date", help="日期，格式 YYYY-MM-DD，或 today")

    # next: 下一个交易日
    p2 = sub.add_parser("next", help="当天或之后最近的交易日")
    p2.add_argument("date", nargs="?", default="today", help="日期，格式 YYYY-MM-DD，或 today（默认）")

    # prev: 上一个交易日
    p3 = sub.add_parser("prev", help="当天或之前最近的交易日")
    p3.add_argument("date", nargs="?", default="today", help="日期，格式 YYYY-MM-DD，或 today（默认）")

    # range: 某段时间内的交易日列表
    p4 = sub.add_parser("range", help="列出某区间内所有交易日")
    p4.add_argument("start", help="开始日期 YYYY-MM-DD")
    p4.add_argument("end", help="结束日期 YYYY-MM-DD")

    args = parser.parse_args()

    def resolve_date(d: str) -> str:
        if d == "today":
            return date.today().strftime("%Y-%m-%d")
        return d

    try:
        if args.cmd == "check":
            d = resolve_date(args.date)
            result = {"date": d, "is_trade_day": is_trade_day(d)}
        elif args.cmd == "next":
            d = resolve_date(args.date)
            result = {"input": d, "next_trade_day": next_trade_day(d)}
        elif args.cmd == "prev":
            d = resolve_date(args.date)
            result = {"input": d, "prev_trade_day": prev_trade_day(d)}
        elif args.cmd == "range":
            days = trade_days_in_range(args.start, args.end)
            result = {"start": args.start, "end": args.end, "count": len(days), "trade_days": days}
        else:
            parser.print_help()
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
