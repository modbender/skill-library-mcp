#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sina Stock - A 股实时行情获取脚本
数据来源：新浪财经 API (https://finance.sina.com.cn/)
无需 API Key，免费使用

使用方法:
    python get_stock.py sh000001,sz399001,sz399006
    python get_stock.py sh600519 sz000858 --json
    python get_stock.py sh000001 --simple
"""

import urllib.request
import re
import json
import sys
from datetime import datetime

# A 股常用指数代码
DEFAULT_INDICES = {
    'sh000001': '上证指数',
    'sz399001': '深证成指',
    'sz399006': '创业板指',
    'sh000300': '沪深 300',
    'sh000016': '上证 50',
    'sh000905': '中证 500',
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://finance.sina.com.cn/',
}


def fetch_stock_data(codes):
    """
    从新浪财经 API 获取股票数据

    Args:
        codes: 股票代码列表 (如 ['sh000001', 'sz399001'])

    Returns:
        list: 股票数据字典列表
    """
    results = []
    url = f"https://hq.sinajs.cn/list={','.join(codes)}"

    try:
        req = urllib.request.Request(url, headers=HEADERS)
        response = urllib.request.urlopen(req, timeout=10)
        content = response.read().decode('gbk')

        # 解析每条股票数据
        lines = content.strip().split('\n')
        for line in lines:
            if not line.strip():
                continue

            # 提取股票代码
            code_match = re.search(r'hq_str_(\w+)=', line)
            if not code_match:
                continue
            code = code_match.group(1)

            # 提取数据内容
            data_match = re.search(r'"([^"]+)"', line)
            if not data_match:
                continue

            fields = data_match.group(1).split(',')
            if len(fields) < 10:
                continue

            # 解析数据字段
            try:
                name = fields[0]
                current = float(fields[1]) if fields[1] else 0
                open_p = float(fields[2]) if fields[2] else 0
                prev_close = float(fields[3]) if fields[3] else 0
                high = float(fields[4]) if fields[4] else 0
                low = float(fields[5]) if fields[5] else 0

                # 计算涨跌额和涨跌幅
                change = current - prev_close
                change_pct = (change / prev_close * 100) if prev_close > 0 else 0

                # 成交量和成交额
                volume = int(float(fields[8])) if fields[8] else 0
                turnover = float(fields[9]) if fields[9] else 0

                # 计算振幅
                amplitude = ((high - low) / prev_close * 100) if prev_close > 0 else 0

                # 获取时间戳
                timestamp = ''
                if len(fields) > 31 and fields[31]:
                    timestamp = fields[31]
                if len(fields) > 32 and fields[32]:
                    timestamp += ' ' + fields[32]

                results.append({
                    'code': code,
                    'name': name,
                    'current': current,
                    'change': change,
                    'change_pct': change_pct,
                    'open': open_p,
                    'prev_close': prev_close,
                    'high': high,
                    'low': low,
                    'amplitude': amplitude,
                    'volume': volume,
                    'turnover': turnover,
                    'timestamp': timestamp,
                })
            except (ValueError, IndexError) as e:
                print(f"解析 {code} 数据失败：{e}", file=sys.stderr)
                continue

    except Exception as e:
        print(f"获取数据失败：{e}", file=sys.stderr)

    return results


def format_text(data_list, simple=False):
    """
    格式化输出为文本

    Args:
        data_list: 股票数据列表
        simple: 是否简化输出
    """
    if not data_list:
        print("未获取到数据")
        return

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # 判断是否是大盘指数
    is_indices = all(d['code'] in DEFAULT_INDICES for d in data_list)

    if is_indices:
        print("=" * 60)
        print("           A 股股市大盘实时数据")
        print(f"           更新时间：{now}")
        print("=" * 60)

    for d in data_list:
        sign = '+' if d['change'] >= 0 else ''

        if simple:
            # 简化格式
            print(f"{d['name']}({d['code']}): {d['current']:.2f} "
                  f"({sign}{d['change']:.2f}, {sign}{d['change_pct']:.2f}%)")
        else:
            # 详细格式
            print(f"\n【{d['name']} ({d['code']})】")
            print(f"  当前价：   {d['current']:.2f}")
            print(f"  涨跌幅：   {sign}{d['change']:.2f} ({sign}{d['change_pct']:.2f}%)")

            if not simple:
                print(f"  开盘价：   {d['open']:.2f}")
                print(f"  昨收价：   {d['prev_close']:.2f}")
                print(f"  最高价：   {d['high']:.2f}")
                print(f"  最低价：   {d['low']:.2f}")
                print(f"  振幅：     {d['amplitude']:.2f}%")
                print(f"  成交量：   {d['volume']:,} 手")
                print(f"  成交额：   {d['turnover']:,.0f} 元")

    if not simple:
        print("\n" + "=" * 60)
        print("数据来源：新浪财经 API (https://finance.sina.com.cn/)")
        print("=" * 60)


def format_json(data_list):
    """
    格式化输出为 JSON

    Args:
        data_list: 股票数据列表
    """
    output = {
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'source': '新浪财经 API',
        'count': len(data_list),
        'data': data_list,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description='获取 A 股实时行情数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python get_stock.py sh000001,sz399001,sz399006    获取大盘指数
  python get_stock.py sh600519 sz000858             获取个股行情
  python get_stock.py sh000001 --json               JSON 格式输出
  python get_stock.py sh000001 --simple             简化输出
        """
    )

    parser.add_argument(
        'codes',
        nargs='+',
        help='股票代码（逗号分隔或多个参数）'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='输出 JSON 格式'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='简化输出'
    )

    args = parser.parse_args()

    # 解析股票代码（支持逗号分隔和空格分隔）
    all_codes = []
    for code_arg in args.codes:
        all_codes.extend(code_arg.split(','))

    # 去除空白和重复
    all_codes = [c.strip().lower() for c in all_codes if c.strip()]

    if not all_codes:
        print("错误：请提供股票代码", file=sys.stderr)
        print("示例：python get_stock.py sh000001,sz399001", file=sys.stderr)
        sys.exit(1)

    # 获取数据
    data_list = fetch_stock_data(all_codes)

    if not data_list:
        print("未获取到数据，请检查股票代码是否正确", file=sys.stderr)
        sys.exit(1)

    # 输出结果
    if args.json:
        format_json(data_list)
    else:
        format_text(data_list, simple=args.simple)


if __name__ == '__main__':
    main()
