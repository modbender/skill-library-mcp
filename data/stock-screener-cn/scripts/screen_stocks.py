#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股技术形态筛选器
支持多种技术分析策略筛选股票

依赖: pip install akshare pandas numpy
"""

import json
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import argparse

try:
    import akshare as ak
    import pandas as pd
    import numpy as np
except ImportError as e:
    print(json.dumps({"error": f"缺少依赖库: {e}. 请运行: pip install akshare pandas numpy"}))
    sys.exit(1)


class StockScreener:
    """A股技术形态筛选器"""
    
    def __init__(self):
        self.strategies = {
            "均线多头排列": self._check_ma_bullish_alignment,
            "均线向上": self._check_ma_rising,
            "缩量回踩": self._check_volume_shrinkage_pullback,
            "放量突破": self._check_volume_breakout,
            "金叉": self._check_golden_cross,
            "大帅逼策略": self._check_dashuaibi_strategy,
            "龙回头": self._check_dragon_turnback,
        }
    
    def get_stock_list(self, market: str = "A股") -> pd.DataFrame:
        """获取股票列表"""
        try:
            if market in ["A股", "深A", "沪A"]:
                # 获取A股列表
                stock_info = ak.stock_zh_a_spot_em()
                if market == "深A":
                    stock_info = stock_info[stock_info['代码'].str.startswith(('00', '30'))]
                elif market == "沪A":
                    stock_info = stock_info[stock_info['代码'].str.startswith(('60', '68'))]
                return stock_info
            elif market == "港股":
                return ak.stock_hk_spot_em()
            else:
                return ak.stock_zh_a_spot_em()
        except Exception as e:
            print(json.dumps({"error": f"获取股票列表失败: {e}"}))
            return pd.DataFrame()
    
    def get_stock_history(self, code: str, days: int = 60) -> pd.DataFrame:
        """获取股票历史数据"""
        try:
            df = ak.stock_zh_a_hist(symbol=code, period="daily", 
                                    adjust="qfq", 
                                    end_date=datetime.now().strftime("%Y%m%d"))
            if df is not None and len(df) > 0:
                return df.tail(days)
            return pd.DataFrame()
        except Exception:
            return pd.DataFrame()
    
    def _calculate_ma(self, df: pd.DataFrame, periods: List[int]) -> Dict[str, pd.Series]:
        """计算均线"""
        result = {}
        for period in periods:
            result[f"MA{period}"] = df['收盘'].rolling(window=period).mean()
        return result
    
    def _check_ma_bullish_alignment(self, df: pd.DataFrame) -> Dict[str, Any]:
        """均线多头排列"""
        if len(df) < 60:
            return {"match": False, "reason": "数据不足"}
        
        ma = self._calculate_ma(df, [5, 10, 20, 60])
        last = df.iloc[-1]
        
        # 检查多头排列
        is_bullish = (
            ma['MA5'].iloc[-1] > ma['MA10'].iloc[-1] > 
            ma['MA20'].iloc[-1] > ma['MA60'].iloc[-1]
        )
        
        if is_bullish:
            return {
                "match": True,
                "score": 85,
                "reason": f"MA5={ma['MA5'].iloc[-1]:.2f} > MA10={ma['MA10'].iloc[-1]:.2f} > MA20={ma['MA20'].iloc[-1]:.2f} > MA60={ma['MA60'].iloc[-1]:.2f}"
            }
        return {"match": False, "reason": "均线未形成多头排列"}
    
    def _check_ma_rising(self, df: pd.DataFrame, period: int = 5, days: int = 3) -> Dict[str, Any]:
        """均线向上"""
        if len(df) < period + days:
            return {"match": False, "reason": "数据不足"}
        
        ma = df['收盘'].rolling(window=period).mean()
        
        # 检查连续N日均线向上
        rising_count = 0
        for i in range(-days, 0):
            if ma.iloc[i] > ma.iloc[i-1]:
                rising_count += 1
        
        if rising_count == days:
            return {
                "match": True,
                "score": 70 + days * 5,
                "reason": f"MA{period}连续{days}日向上"
            }
        return {"match": False, "reason": f"MA{period}未连续向上"}
    
    def _check_volume_shrinkage_pullback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """缩量回踩"""
        if len(df) < 10:
            return {"match": False, "reason": "数据不足"}
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 计算MA5
        ma5 = df['收盘'].rolling(window=5).mean()
        
        # 检查条件
        # 1. 昨日缩量
        volume_shrink = prev['成交量'] < df['成交量'].iloc[-6:-1].mean()
        
        # 2. 回踩不破MA5
        low_above_ma5 = prev['最低'] > ma5.iloc[-2] * 0.98  # 允许2%误差
        
        # 3. 收盘站稳MA5
        close_above_ma5 = prev['收盘'] > ma5.iloc[-2]
        
        if volume_shrink and low_above_ma5 and close_above_ma5:
            return {
                "match": True,
                "score": 80,
                "reason": f"缩量{(1-prev['成交量']/df['成交量'].iloc[-6:-1].mean())*100:.1f}%回踩，未破MA5"
            }
        return {"match": False, "reason": "不满足缩量回踩条件"}
    
    def _check_volume_breakout(self, df: pd.DataFrame) -> Dict[str, Any]:
        """放量突破"""
        if len(df) < 30:
            return {"match": False, "reason": "数据不足"}
        
        last = df.iloc[-1]
        
        # 1. 突破20日高点
        high_20 = df['最高'].iloc[-21:-1].max()
        breakout = last['收盘'] > high_20
        
        # 2. 放量
        vol_avg = df['成交量'].iloc[-6:-1].mean()
        volume_up = last['成交量'] > vol_avg * 1.5
        
        # 3. MA5向上
        ma5 = df['收盘'].rolling(window=5).mean()
        ma_rising = ma5.iloc[-1] > ma5.iloc[-2]
        
        if breakout and volume_up and ma_rising:
            return {
                "match": True,
                "score": 85,
                "reason": f"突破20日高点{high_20:.2f}，放量{(last['成交量']/vol_avg-1)*100:.1f}%"
            }
        return {"match": False, "reason": "不满足放量突破条件"}
    
    def _check_golden_cross(self, df: pd.DataFrame, short: int = 5, long: int = 10) -> Dict[str, Any]:
        """金叉"""
        if len(df) < long + 2:
            return {"match": False, "reason": "数据不足"}
        
        ma_short = df['收盘'].rolling(window=short).mean()
        ma_long = df['收盘'].rolling(window=long).mean()
        
        # 今日金叉：短期均线上穿长期均线
        cross_today = ma_short.iloc[-1] > ma_long.iloc[-1] and ma_short.iloc[-2] <= ma_long.iloc[-2]
        
        if cross_today:
            return {
                "match": True,
                "score": 75,
                "reason": f"MA{short}上穿MA{long}形成金叉"
            }
        return {"match": False, "reason": "未形成金叉"}
    
    def _check_dashuaibi_strategy(self, df: pd.DataFrame) -> Dict[str, Any]:
        """大帅逼策略：五日线十三日线均向上，昨日缩量回踩但未破五日线"""
        if len(df) < 20:
            return {"match": False, "reason": "数据不足"}
        
        # 计算均线
        ma5 = df['收盘'].rolling(window=5).mean()
        ma13 = df['收盘'].rolling(window=13).mean()
        
        last = df.iloc[-1]
        prev = df.iloc[-2]
        
        # 条件1：MA5向上
        ma5_rising = ma5.iloc[-1] > ma5.iloc[-2]
        
        # 条件2：MA13向上
        ma13_rising = ma13.iloc[-1] > ma13.iloc[-2]
        
        # 条件3：昨日缩量
        vol_avg = df['成交量'].iloc[-6:-1].mean()
        volume_shrink = prev['成交量'] < vol_avg
        
        # 条件4：回踩未破MA5
        pullback_ok = prev['最低'] > ma5.iloc[-2] * 0.98 and prev['收盘'] > ma5.iloc[-2]
        
        # 综合判断
        if ma5_rising and ma13_rising and volume_shrink and pullback_ok:
            shrink_pct = (1 - prev['成交量'] / vol_avg) * 100
            return {
                "match": True,
                "score": 88,
                "reason": f"MA5↑ MA13↑ 缩量{shrink_pct:.1f}%回踩未破MA5"
            }
        
        reasons = []
        if not ma5_rising:
            reasons.append("MA5未向上")
        if not ma13_rising:
            reasons.append("MA13未向上")
        if not volume_shrink:
            reasons.append("未缩量")
        if not pullback_ok:
            reasons.append("破MA5")
        
        return {"match": False, "reason": "，".join(reasons)}
    
    def _check_dragon_turnback(self, df: pd.DataFrame) -> Dict[str, Any]:
        """龙回头：强势上涨后回调至关键均线"""
        if len(df) < 30:
            return {"match": False, "reason": "数据不足"}
        
        # 1. 近10日有强势上涨（涨幅>15%）
        gain_10 = (df['收盘'].iloc[-1] - df['收盘'].iloc[-11]) / df['收盘'].iloc[-11]
        
        # 2. 近3日回调
        pullback = df['收盘'].iloc[-1] < df['收盘'].iloc[-4]
        
        # 3. 缩量
        vol_shrink = df['成交量'].iloc[-1] < df['成交量'].iloc[-5:-1].mean()
        
        # 4. 站稳MA10
        ma10 = df['收盘'].rolling(window=10).mean()
        above_ma10 = df['收盘'].iloc[-1] > ma10.iloc[-1]
        
        if gain_10 > 0.15 and pullback and vol_shrink and above_ma10:
            return {
                "match": True,
                "score": 82,
                "reason": f"10日涨{gain_10*100:.1f}%后缩量回调至MA10上方"
            }
        return {"match": False, "reason": "不满足龙回头形态"}
    
    def screen(self, strategies: List[str], market: str = "A股", 
               limit: int = 50, min_price: float = 3.0, 
               max_price: float = 300.0) -> List[Dict[str, Any]]:
        """
        执行股票筛选
        
        Args:
            strategies: 策略名称列表
            market: 市场（A股/深A/沪A/港股）
            limit: 最大返回数量
            min_price: 最低价格
            max_price: 最高价格
        """
        results = []
        
        # 获取股票列表
        print(json.dumps({"status": "正在获取股票列表..."}), file=sys.stderr)
        stock_list = self.get_stock_list(market)
        
        if stock_list.empty:
            return [{"error": "无法获取股票列表"}]
        
        # 过滤价格
        if '最新价' in stock_list.columns:
            stock_list = stock_list[
                (stock_list['最新价'] >= min_price) & 
                (stock_list['最新价'] <= max_price)
            ]
        
        # 过滤ST股票
        stock_list = stock_list[~stock_list['名称'].str.contains('ST|退市', na=False)]
        
        total = len(stock_list)
        print(json.dumps({"status": f"共{total}只股票待筛选..."}), file=sys.stderr)
        
        # 遍历股票
        for idx, row in stock_list.head(500).iterrows():  # 限制数量避免超时
            code = row['代码']
            name = row['名称']
            
            if idx % 50 == 0:
                print(json.dumps({"progress": f"已筛选 {idx}/{min(total, 500)}"}), file=sys.stderr)
            
            # 获取历史数据
            hist = self.get_stock_history(code)
            if hist.empty or len(hist) < 30:
                continue
            
            # 检查每个策略
            for strategy in strategies:
                if strategy in self.strategies:
                    result = self.strategies[strategy](hist)
                    if result.get("match"):
                        results.append({
                            "code": code,
                            "name": name,
                            "price": float(row.get('最新价', 0)),
                            "strategy": strategy,
                            "score": result.get("score", 0),
                            "reason": result.get("reason", ""),
                            "change_pct": float(row.get('涨跌幅', 0)) if '涨跌幅' in row else 0
                        })
        
        # 按评分排序
        results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return results[:limit]


def main():
    parser = argparse.ArgumentParser(description='A股技术形态筛选器')
    parser.add_argument('--strategy', '-s', nargs='+', 
                        default=['大帅逼策略'],
                        help='筛选策略，可多选：均线多头排列、均线向上、缩量回踩、放量突破、金叉、大帅逼策略、龙回头')
    parser.add_argument('--market', '-m', default='A股',
                        help='市场：A股、深A、沪A、港股')
    parser.add_argument('--limit', '-l', type=int, default=30,
                        help='最大返回数量')
    parser.add_argument('--min-price', type=float, default=3.0,
                        help='最低价格')
    parser.add_argument('--max-price', type=float, default=300.0,
                        help='最高价格')
    
    args = parser.parse_args()
    
    screener = StockScreener()
    results = screener.screen(
        strategies=args.strategy,
        market=args.market,
        limit=args.limit,
        min_price=args.min_price,
        max_price=args.max_price
    )
    
    # 输出JSON结果
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
