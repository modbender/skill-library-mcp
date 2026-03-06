#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A股数据分析 - Cron任务专用脚本"""

import akshare as ak
import pandas as pd
from datetime import datetime

def analyze_stocks():
    try:
        # 获取实时数据
        df = ak.stock_zh_a_spot_em()

        # 筛选用户关注的板块
        keywords = ['科技', '白酒', '航天', '半导体', '芯片', '航空']
        preferred_stocks = df[df['名称'].str.contains('|'.join(keywords), na=False)]

        # 按条件筛选：量比 > 1.5, 涨幅 0-7%
        filtered = preferred_stocks[
            (preferred_stocks['量比'] > 1.5) &
            (preferred_stocks['涨跌幅'] > 0) &
            (preferred_stocks['涨跌幅'] < 7)
        ].sort_values('量比', ascending=False)

        # 输出报告
        print("=" * 60)
        print(f" A股数据分析报告 - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)

        # 板块平均涨幅
        print("\n【板块热点】")
        for kw in keywords:
            sector = preferred_stocks[preferred_stocks['名称'].str.contains(kw, na=False)]
            if len(sector) > 0:
                avg_change = sector['涨跌幅'].mean()
                print(f"{kw}: {avg_change:+.2f}% ({len(sector)}只)")

        # 推荐标的
        print("\n【推荐标的】")
        if len(filtered) > 0:
            for idx, (_, row) in enumerate(filtered.head(5).iterrows(), 1):
                print(f"{idx}. {row['名称']}({row['代码']}) - {row['最新价']:.2f} - {row['涨跌幅']:+.2f}% - 量比:{row['量比']:.2f}")
        else:
            print("暂无符合条件股票（量比>1.5，涨幅0-7%）")

        # 操作建议
        print("\n【操作建议】")
        if len(filtered) > 0:
            print("建议：关注量比放大个股，分批建仓，设置止损-7%")
        else:
            print("当前市场条件下，建议观望等待更好的入场时机")

        print("=" * 60)

    except Exception as e:
        print(f"分析失败: {e}")

if __name__ == "__main__":
    analyze_stocks()
