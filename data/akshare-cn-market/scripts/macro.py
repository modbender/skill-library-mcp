#!/usr/bin/env python3
"""中国宏观经济数据 - 基于 AKShare"""
import sys
import json
import argparse
import akshare as ak


def get_gdp(n: int = 8):
    """中国GDP季度数据（最新在前）"""
    df = ak.macro_china_gdp()
    return df.head(n).to_dict(orient="records")


def get_cpi(n: int = 12):
    """中国CPI月度数据（最新在前）"""
    df = ak.macro_china_cpi()
    cols = ["月份", "全国-当月", "全国-同比增长", "全国-环比增长"]
    return df[cols].head(n).to_dict(orient="records")


def get_pmi(n: int = 12):
    """制造业/非制造业PMI月度数据（最新在前）"""
    df = ak.macro_china_pmi()
    return df.head(n).to_dict(orient="records")


def get_money_supply(n: int = 12):
    """货币供应量 M0/M1/M2 月度数据（最新在前）"""
    df = ak.macro_china_money_supply()
    cols = [
        "月份",
        "货币和准货币(M2)-数量(亿元)", "货币和准货币(M2)-同比增长",
        "货币(M1)-数量(亿元)", "货币(M1)-同比增长",
        "流通中的现金(M0)-数量(亿元)", "流通中的现金(M0)-同比增长",
    ]
    return df[cols].head(n).to_dict(orient="records")


def get_bond_rate(n: int = 10):
    """中美国债收益率对比（历史数据）"""
    df = ak.bond_zh_us_rate()
    cols = [
        "日期",
        "中国国债收益率2年", "中国国债收益率10年", "中国国债收益率30年",
        "美国国债收益率2年", "美国国债收益率10年",
    ]
    df = df[cols].dropna()
    df["日期"] = df["日期"].astype(str)
    return df.tail(n).to_dict(orient="records")


def main():
    parser = argparse.ArgumentParser(description="中国宏观经济数据工具")
    sub = parser.add_subparsers(dest="cmd")

    p1 = sub.add_parser("gdp", help="中国GDP季度数据")
    p1.add_argument("--n", type=int, default=8, help="返回最近N条（季度）")

    p2 = sub.add_parser("cpi", help="中国CPI月度数据")
    p2.add_argument("--n", type=int, default=12, help="返回最近N条（月）")

    p3 = sub.add_parser("pmi", help="制造业/非制造业PMI")
    p3.add_argument("--n", type=int, default=12, help="返回最近N条（月）")

    p4 = sub.add_parser("money", help="货币供应量 M0/M1/M2")
    p4.add_argument("--n", type=int, default=12, help="返回最近N条（月）")

    p5 = sub.add_parser("bond", help="中美国债收益率")
    p5.add_argument("--n", type=int, default=10, help="返回最近N条（交易日）")

    args = parser.parse_args()

    try:
        if args.cmd == "gdp":
            result = get_gdp(args.n)
        elif args.cmd == "cpi":
            result = get_cpi(args.n)
        elif args.cmd == "pmi":
            result = get_pmi(args.n)
        elif args.cmd == "money":
            result = get_money_supply(args.n)
        elif args.cmd == "bond":
            result = get_bond_rate(args.n)
        else:
            parser.print_help()
            sys.exit(1)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
