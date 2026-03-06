#!/usr/bin/env python3
"""A股行情数据 - 基于 AKShare"""
import sys
import json
import argparse
import akshare as ak


def get_stock_hist(symbol: str, adjust: str = "qfq", n: int = 10):
    """获取个股历史K线（新浪源，不依赖东方财富）
    symbol 格式: sz000001 / sh600519（需加交易所前缀）
    若只传纯数字，自动判断：6开头=sh，其余=sz
    """
    if not symbol.startswith(("sh", "sz")):
        prefix = "sh" if symbol.startswith("6") else "sz"
        symbol = prefix + symbol
    df = ak.stock_zh_a_daily(symbol=symbol, adjust=adjust)
    df["date"] = df["date"].astype(str)
    df = df.tail(n)
    return df.to_dict(orient="records")


def get_index_daily(symbol: str = "sh000001", n: int = 10):
    """获取大盘指数K线（新浪源，不依赖东方财富）
    常用代码: sh000001=上证, sz399001=深证, sh000300=沪深300, sh000016=上证50
    """
    df = ak.stock_zh_index_daily(symbol=symbol)
    df["date"] = df["date"].astype(str)
    df = df.tail(n)
    return df.to_dict(orient="records")


def get_stock_financial(symbol: str):
    """获取个股财务摘要（同花顺，按年度）"""
    df = ak.stock_financial_abstract_ths(symbol=symbol, indicator="按年度")
    return df.head(5).to_dict(orient="records")


def main():
    parser = argparse.ArgumentParser(description="A股行情工具")
    sub = parser.add_subparsers(dest="cmd")

    # hist: 个股K线
    p1 = sub.add_parser("hist", help="个股历史K线（新浪源）")
    p1.add_argument("symbol", help="股票代码，如 000001 或 sz000001")
    p1.add_argument("--adjust", default="qfq", choices=["qfq", "hfq", ""], help="复权方式")
    p1.add_argument("--n", type=int, default=10, help="返回最近N条")

    # index: 大盘指数
    p2 = sub.add_parser("index", help="大盘指数K线")
    p2.add_argument("symbol", nargs="?", default="sh000001",
                    help="指数代码: sh000001=上证, sz399001=深证, sh000300=沪深300, sh000016=上证50")
    p2.add_argument("--n", type=int, default=10, help="返回最近N条")

    # financial: 财务摘要
    p3 = sub.add_parser("financial", help="个股财务摘要（近5年）")
    p3.add_argument("symbol", help="股票代码，如 000001")

    args = parser.parse_args()

    try:
        if args.cmd == "hist":
            result = get_stock_hist(args.symbol, args.adjust, args.n)
        elif args.cmd == "index":
            result = get_index_daily(args.symbol, args.n)
        elif args.cmd == "financial":
            result = get_stock_financial(args.symbol)
        else:
            parser.print_help()
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
