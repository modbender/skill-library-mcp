#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版中长线选股引擎
集成基本面分析+高级指标
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from typing import List, Dict
from smart_data_source import SmartDataSource
from stock_cache_db import StockCache
from advanced_indicators import AdvancedIndicators
from advanced_long_term_indicators import AdvancedLongTermIndicators
from fundamental_data import FundamentalData


class EnhancedLongTermSelector:
    """增强版中长线选股引擎"""
    
    def __init__(self):
        self.ds = SmartDataSource()
        self.cache = StockCache()
        self.indicators = AdvancedIndicators()
        self.advanced_indicators = AdvancedLongTermIndicators()
        self.fundamental = FundamentalData()
        
    def load_watchlist(self) -> List[str]:
        """加载监控列表，过滤创业板和科创板"""
        try:
            with open('watchlist.json', 'r') as f:
                all_stocks = json.load(f)
            
            # 过滤: 排除3开头(创业板)和688开头(科创板)
            filtered = [
                code for code in all_stocks 
                if not code.startswith('3') and not code.startswith('688')
            ]
            
            return filtered
        except:
            return []
    
    def analyze_single_stock(self, code: str) -> Dict:
        """
        增强版单股分析
        包含技术面+基本面+高级指标
        """
        try:
            # 获取历史数据
            df = self.ds.get_history_data(code, days=120)
            if df is None or df.empty or len(df) < 60:
                return None
            
            # 获取基础信息
            stock_info = self.cache.get_stock(code)
            if not stock_info:
                return None
            
            score = 0
            max_score = 130  # 扩展总分
            details = {}
            
            # ====== 1. 技术面评分 (30分) ======
            trend = self.indicators.score_trend(df)
            trend_score = trend['score'] * 0.30
            score += trend_score
            
            details['trend'] = {
                'score': trend_score,
                'rating': trend['rating'],
                'reasons': trend['reasons']
            }
            
            # ====== 2. 基本面评分 (30分) ✨新增 ======
            fundamental_data = self.fundamental.get_stock_fundamental(code)
            fundamental_score = self._calc_fundamental_score(fundamental_data)
            score += fundamental_score['score']
            
            details['fundamental'] = fundamental_score
            
            # ====== 3. 估值评分 (15分) ✨新增 ======
            valuation_score = self._calc_valuation_score(
                fundamental_data.get('pe', 0),
                fundamental_data.get('profit_growth', 0)
            )
            score += valuation_score['score']
            
            details['valuation'] = valuation_score
            
            # ====== 4. 动量评分 (15分) ======
            returns_20d = (df['close'].iloc[-1] - df['close'].iloc[-21]) / df['close'].iloc[-21] * 100
            momentum_score = 15 if returns_20d > 0 else 0
            score += momentum_score
            
            details['momentum'] = {
                'score': momentum_score,
                'returns_20d': returns_20d
            }
            
            # ====== 5. 量价评分 (15分) ======
            obv = self.indicators.calc_obv(df)
            volume_score = 15 if obv.iloc[-1] > obv.iloc[-20] else 5
            score += volume_score
            
            details['volume'] = {
                'score': volume_score,
                'obv_trend': 'up' if obv.iloc[-1] > obv.iloc[-20] else 'down'
            }
            
            # ====== 6. DMI评分 (15分) ✨新增 ======
            plus_di, minus_di, adx = self.advanced_indicators.calc_dmi(df)
            dmi_analysis = self.advanced_indicators.analyze_dmi_signal(
                plus_di.iloc[-1], minus_di.iloc[-1], adx.iloc[-1]
            )
            dmi_score = 15 if dmi_analysis['signal'] in ['buy', 'strong_buy'] else 0
            score += dmi_score
            
            details['dmi'] = {
                'score': dmi_score,
                **dmi_analysis
            }
            
            # ====== 7. 资金流评分 (10分) ======
            fund_flow = self.cache.get_fund_flow(code)
            fund_score = 10 if fund_flow and fund_flow.get('main_in', 0) > 0 else 0
            score += fund_score
            
            details['fund_flow'] = {
                'score': fund_score,
                'main_in': fund_flow.get('main_in', 0) / 10000 if fund_flow else 0
            }
            
            # ====== 综合信号评分 ✨新增 ======
            signals = {
                'trend': trend,
                'momentum': {'signal': 'buy' if returns_20d > 0 else 'sell'},
                'volume': {'signal': 'buy' if obv.iloc[-1] > obv.iloc[-20] else 'sell'},
                'dmi': dmi_analysis,
                'valuation': {'signal': 'buy' if valuation_score['level'] in ['低估', '合理'] else 'sell'}
            }
            
            optimized_signal = self.advanced_indicators.optimize_signal_trigger(signals)
            
            # ====== 汇总结果 ======
            final_score = (score / max_score) * 100  # 归一化到100分
            
            # 生成买入信号列表
            buy_signals = []
            if optimized_signal['decision'] in ['强烈买入', '买入']:
                for reason in optimized_signal['reasons']:
                    buy_signals.append(reason)
            
            # 添加基本面信号
            if fundamental_score['score'] >= 24:
                buy_signals.append(f"基本面优秀(ROE {fundamental_data.get('roe', 0):.1f}%)")
            if valuation_score['level'] == '低估':
                buy_signals.append(f"PEG低估({valuation_score['peg']:.2f})")
            if fundamental_data.get('dividend_yield', 0) >= 3:
                buy_signals.append(f"高股息({fundamental_data.get('dividend_yield', 0):.1f}%)")
            
            # DMI信号
            if dmi_analysis['signal'] in ['buy', 'strong_buy']:
                buy_signals.append(f"DMI多头({dmi_analysis['strength']})")
            
            # 计算买卖点（中长线：-8%止损，+20%止盈）
            current_price = float(stock_info.get('price', 0))
            buy_price = current_price
            stop_loss = current_price * 0.92  # -8%
            take_profit = current_price * 1.20  # +20%
            stop_loss_pct = -8.0
            take_profit_pct = 20.0
            risk_reward_ratio = 20.0 / 8.0  # 2.5:1
            
            result = {
                'code': code,
                'name': stock_info.get('name', 'Unknown'),
                'price': float(stock_info.get('price', 0)),
                'change_pct': float(stock_info.get('change_pct', 0)),
                'score': round(final_score, 2),
                'rating': self._get_rating(final_score),
                'details': self._convert_to_json_safe(details),
                'signal': optimized_signal,
                'recommend': final_score >= 65,  # 65分以上推荐
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                # 新增字段
                'buy_signals': buy_signals,
                'buy_signal_count': len(buy_signals),
                'buy_price': buy_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'stop_loss_pct': stop_loss_pct,
                'take_profit_pct': take_profit_pct,
                'risk_reward_ratio': risk_reward_ratio
            }
            
            return result
            
        except Exception as e:
            print(f"分析{code}失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _calc_fundamental_score(self, data: Dict) -> Dict:
        """计算基本面评分 (30分)"""
        score = 0
        
        # ROE (10分)
        roe = data.get('roe', 0)
        if roe >= 20:
            score += 10
        elif roe >= 15:
            score += 8
        elif roe >= 10:
            score += 5
        
        # 利润增长 (10分)
        profit_growth = data.get('profit_growth', 0)
        if profit_growth >= 25:
            score += 10
        elif profit_growth >= 15:
            score += 7
        elif profit_growth >= 10:
            score += 5
        
        # 股息率 (10分)
        dividend = data.get('dividend_yield', 0)
        if dividend >= 4:
            score += 10
        elif dividend >= 2:
            score += 6
        elif dividend >= 1:
            score += 3
        
        level = 'A' if score >= 24 else 'B' if score >= 18 else 'C' if score >= 12 else 'D'
        
        return {
            'score': score,
            'level': level,
            'roe': data.get('roe', 0),
            'profit_growth': data.get('profit_growth', 0),
            'dividend_yield': data.get('dividend_yield', 0),
            'revenue_growth': data.get('revenue_growth', 0)
        }
    
    def _calc_valuation_score(self, pe: float, growth: float) -> Dict:
        """计算估值评分 (15分)"""
        score = 0
        
        if pe <= 0 or growth <= 0:
            return {
                'score': 0,
                'level': '无效',
                'pe': pe,
                'peg': None
            }
        
        # 计算PEG
        peg_data = self.advanced_indicators.calc_peg_ratio(pe, growth)
        peg = peg_data['peg']
        
        if peg and peg < 0.8:
            score = 15
            level = '低估'
        elif peg and peg < 1.2:
            score = 10
            level = '合理'
        elif peg and peg < 2.0:
            score = 5
            level = '偏高'
        else:
            score = 0
            level = '高估'
        
        return {
            'score': score,
            'level': level,
            'pe': pe,
            'peg': peg,
            'growth': growth
        }
    
    def _get_rating(self, score: float) -> str:
        """评级"""
        if score >= 80:
            return 'A+'
        elif score >= 70:
            return 'A'
        elif score >= 60:
            return 'B+'
        elif score >= 50:
            return 'B'
        elif score >= 40:
            return 'C'
        else:
            return 'D'
    
    def _convert_to_json_safe(self, obj):
        """转换为JSON安全的数据类型"""
        import numpy as np
        import math
        
        if isinstance(obj, dict):
            return {k: self._convert_to_json_safe(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_safe(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            val = float(obj)
            if math.isnan(val) or math.isinf(val):
                return None
            return val
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, bool):
            return bool(obj)
        elif obj is None:
            return None
        else:
            return obj
    
    def select_top_stocks(self, top_n: int = 5) -> List[Dict]:
        """选择TOP N股票"""
        print("=" * 60)
        print(f"🎯 增强版中长线选股 - TOP {top_n}")
        print("=" * 60)
        print()
        
        watchlist = self.load_watchlist()
        if not watchlist:
            print("❌ 监控列表为空")
            return []
        
        print(f"📊 分析 {len(watchlist)} 只股票（含基本面分析）...")
        print()
        
        results = []
        for i, code in enumerate(watchlist, 1):
            print(f"[{i}/{len(watchlist)}] {code}...", end=" ")
            
            result = self.analyze_single_stock(code)
            if result:
                print(f"✅ {result['score']:.1f}分 ({result['rating']})")
                results.append(result)
            else:
                print("❌ 分析失败")
        
        # 按评分排序
        results.sort(key=lambda x: x['score'], reverse=True)
        
        # 取TOP N
        top_stocks = results[:top_n]
        
        print()
        print("=" * 60)
        print(f"📈 推荐结果 (TOP {len(top_stocks)})")
        print("=" * 60)
        print()
        
        for i, stock in enumerate(top_stocks, 1):
            print(f"{i}. {stock['name']} ({stock['code']})")
            print(f"   评分: {stock['score']:.1f} ({stock['rating']})")
            print(f"   价格: ¥{stock['price']:.2f} ({stock['change_pct']:+.2f}%)")
            
            # 基本面
            fund = stock['details']['fundamental']
            print(f"   基本面: ROE={fund['roe']:.1f}% | 利润增长={fund['profit_growth']:+.1f}% | 股息率={fund['dividend_yield']:.2f}%")
            
            # 估值
            val = stock['details']['valuation']
            if val['peg']:
                print(f"   估值: PE={val['pe']:.1f} | PEG={val['peg']:.2f} ({val['level']})")
            
            # 信号
            sig = stock['signal']
            print(f"   信号: {sig['decision']} (评分{sig['score']:.1f}, {sig['signal_count']}个买点)")
            print()
        
        return top_stocks
    
    def close(self):
        self.ds.close()
        self.cache.close()
        self.fundamental.close()


if __name__ == '__main__':
    selector = EnhancedLongTermSelector()
    
    # 选择TOP 5
    top_stocks = selector.select_top_stocks(top_n=5)
    
    selector.close()
