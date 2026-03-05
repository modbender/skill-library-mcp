#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""股票推荐分析工具"""

import akshare as ak
import pandas as pd
from datetime import datetime

def get_stock_recommendations():
    print("=" * 70)
    print(f" 股票推荐分析 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # 用户偏好
    preferences = {
        'sectors': ['科技', '白酒', '航天', '半导体', '芯片', '航空'],
        'risk': '中等',
        'style': '事件驱动、中短线'
    }

    print(f"\n【用户偏好】")
    print(f"关注板块: {', '.join(preferences['sectors'])}")
    print(f"风险偏好: {preferences['risk']}")
    print(f"投资风格: {preferences['style']}")

    # 获取实时行情
    print(f"\n【正在获取A股实时数据...】")
    df = ak.stock_zh_a_spot_em()
    print(f"获取到 {len(df)} 只股票数据")

    # 获取新闻（akshare的新闻接口）
    print(f"\n【正在获取财经新闻...】")
    try:
        news_df = ak.stock_news_em()
        print(f"获取到 {len(news_df)} 条新闻")
        # 显示最新的5条
        print("\n--- 最新新闻标题 ---")
        for idx, row in news_df.head(5).iterrows():
            print(f"{idx+1}. {row['新闻标题']}")
    except Exception as e:
        print(f"获取新闻失败: {e}")
        news_df = None

    # 筛选用户关注的板块
    print("\n" + "=" * 70)
    print("【偏好板块筛选】")
    print("=" * 70)

    target_stocks = df[df['所属行业'].str.contains('|'.join(preferences['sectors']), na=False)]
    print(f"匹配到 {len(target_stocks)} 只股票")

    # 筛选条件：量比>1.5, 涨幅0-7%（避免追高）
    print("\n【筛选条件：量比>1.5, 涨幅0-7%】")
    filtered = target_stocks[
        (target_stocks['量比'] > 1.5) &
        (target_stocks['涨跌幅'] > 0) &
        (target_stocks['涨跌幅'] < 7)
    ].sort_values('量比', ascending=False)

    print(f"\n符合条件: {len(filtered)} 只")
    if len(filtered) == 0:
        print("暂无符合条件股票，扩大筛选范围...")
        # 放宽条件：量比>1.2, 涨幅<10%
        filtered = target_stocks[
            (target_stocks['量比'] > 1.2) &
            (target_stocks['涨跌幅'] > 0) &
            (target_stocks['涨跌幅'] < 10)
        ].sort_values('量比', ascending=False)
        print(f"放宽后符合条件: {len(filtered)} 只")

    # 推荐前3名
    print("\n" + "=" * 70)
    print("【推荐关注 TOP 3】")
    print("=" * 70)

    if len(filtered) > 0:
        for idx, (_, stock) in enumerate(filtered.head(3).iterrows(), 1):
            print(f"\n推荐 #{idx}: {stock['名称']} ({stock['代码']})")
            print(f"  板块: {stock['所属行业']}")
            print(f"  现价: {stock['最新价']}  涨跌幅: {stock['涨跌幅']:+.2f}%")
            print(f"  量比: {stock['量比']:.2f}  成交额: {stock['成交额']:.0f}万")
            print(f"  评级: {'强' if stock['量比'] > 2 else '中'}")

            # 风险提示
            print(f"  风险提示: 建议分批建仓，设置止损")
    else:
        print("\n当前市场条件下，暂无推荐标的。")
        print("建议观望等待更好的入场时机。")

    # 市场热点板块（按涨幅和成交额综合）
    print("\n" + "=" * 70)
    print("【市场热点板块】")
    print("=" * 70)

    # 计算每个板块的平均涨跌幅和总成交额
    sector_stats = df.groupby('所属行业').agg({
        '涨跌幅': 'mean',
        '成交额': 'sum',
        '代码': 'count'
    }).sort_values('涨跌幅', ascending=False)

    sector_stats.columns = ['平均涨幅', '总成交额', '股票数量']
    print(sector_stats.head(10).to_string())

    print("\n" + "=" * 70)

if __name__ == "__main__":
    get_stock_recommendations()
