#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""早盘报告生成器"""

import akshare as ak
import pandas as pd
from datetime import datetime

def generate_morning_report():
    print("=" * 60)
    print(f" A股早盘报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 获取A股实时行情
    print("\n【正在获取实时行情数据...】")
    df = ak.stock_zh_a_spot_em()

    print(f"✓ 获取到 {len(df)} 只股票数据")

    # 筛选涨幅前10且量比>2的股票
    print("\n" + "=" * 60)
    print("【涨幅前10 且 量比>2 的股票】")
    print("=" * 60)

    df_sorted = df.sort_values('涨跌幅', ascending=False)
    top10 = df_sorted[df_sorted['量比'] > 2].head(10)

    if len(top10) > 0:
        print(top10[['代码', '名称', '最新价', '涨跌幅', '涨跌额', '量比', '所属行业']].to_string(index=False))
    else:
        print("今日暂无符合条件的股票（涨幅前10且量比>2）")

    # 板块平均涨幅分析
    print("\n" + "=" * 60)
    print("【板块平均涨幅 TOP 10】")
    print("=" * 60)

    sector_avg = df.groupby('所属行业')['涨跌幅'].mean().sort_values(ascending=False).head(10)
    for idx, (sector, avg) in enumerate(sector_avg.items(), 1):
        print(f"{idx:2d}. {sector:15s}  {avg:+6.2f}%")

    # 市场整体概况
    print("\n" + "=" * 60)
    print("【市场整体概况】")
    print("=" * 60)

    rising = len(df[df['涨跌幅'] > 0])
    falling = len(df[df['涨跌幅'] < 0])
    flat = len(df[df['涨跌幅'] == 0])

    avg_change = df['涨跌幅'].mean()
    max_change = df['涨跌幅'].max()
    min_change = df['涨跌幅'].min()

    print(f"上涨: {rising:5d} 只  下跌: {falling:5d} 只  平盘: {flat:5d} 只")
    print(f"平均涨跌: {avg_change:+.2f}%  最高: {max_change:+.2f}%  最低: {min_change:+.2f}%")

    # 用户偏好板块关注
    print("\n" + "=" * 60)
    print("【偏好板块表现】")
    print("=" * 60)

    preferred_sectors = ['科技', '白酒', '航天']
    for sector in preferred_sectors:
        sector_stocks = df[df['所属行业'].str.contains(sector, na=False)]
        if len(sector_stocks) > 0:
            sector_avg = sector_stocks['涨跌幅'].mean()
            print(f"{sector:8s}: {len(sector_stocks):3d}只  平均 {sector_avg:+.2f}%")
            # 该板块表现最好的3只
            top3 = sector_stocks.nlargest(3, '涨跌幅')[['代码', '名称', '最新价', '涨跌幅', '量比']]
            print(f"  领涨: ", end="")
            for _, stock in top3.iterrows():
                print(f"{stock['名称']}({stock['涨跌幅']:+.1f}%) ", end="")
            print()

    print("\n" + "=" * 60)
    print("报告生成完毕")
    print("=" * 60)

if __name__ == "__main__":
    generate_morning_report()
