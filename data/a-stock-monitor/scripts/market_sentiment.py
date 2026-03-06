#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场情绪计算模块
基于全市场A股数据，多维度计算市场情绪评分
"""

from stock_cache_db import StockCache
from datetime import datetime
import pandas as pd


def calculate_market_sentiment(use_demo_data=False):
    """
    计算市场情绪评分 (0-100)
    
    维度:
    1. 涨跌家数比 (权重 20%) -> ±10分
    2. 平均涨幅 (权重 20%) -> ±10分
    3. 涨停/跌停比 (权重 15%) -> ±8分
    4. 强势股占比 (涨幅>5%) (权重 15%) -> ±8分
    5. 成交活跃度 (平均换手率) (权重 10%) -> ±5分
    6. 波动率 (ATR均值) (权重 10%) -> ±5分
    7. 趋势 (价格相对MA20) (权重 10%) -> ±4分
    
    返回:
    {
        'score': 50.0,  # 情绪评分 (0-100)
        'level': '中性',  # 情绪等级
        'emoji': '😐',
        'description': '市场平稳运行',
        'stats': {
            'total': 5000,
            'gainers': 2500,
            'losers': 2000,
            'neutral': 500,
            'limit_up': 10,
            'limit_down': 5,
            'strong_stocks': 500,
            'weak_stocks': 400,
            'avg_change': 0.5,
            'avg_turnover': 3.5,
            'avg_volatility': 2.1,
            'trend_score': 55
        }
    }
    """
    
    # 演示模式：生成模拟数据
    if use_demo_data:
        import random
        random.seed(42)
        all_stocks = []
        for i in range(5000):
            # 生成符合A股特征的模拟数据
            change = random.gauss(0, 2.5)  # 平均0%，标准差2.5%
            all_stocks.append({
                'code': f'{i:06d}',
                'name': f'股票{i}',
                'change_pct': round(change, 2),
                'turnover': round(random.uniform(0.5, 8), 2),
                'amplitude': round(abs(change) * random.uniform(1.5, 2.5), 2)
            })
    else:
        cache = StockCache()
        # 先尝试获取30分钟内的数据
        all_stocks = cache.get_all_stocks(max_age_minutes=30)
        
        # 如果没有新数据，获取最近一次的数据（最多保留2天）
        if not all_stocks or len(all_stocks) == 0:
            all_stocks = cache.get_all_stocks(max_age_minutes=2880)  # 2天 = 48小时
        
        cache.close()
    
    if not all_stocks or len(all_stocks) == 0:
        return {
            'score': 50.0,
            'level': '中性',
            'emoji': '😐',
            'description': '暂无数据',
            'stats': {
                'total': 0,
                'gainers': 0,
                'losers': 0,
                'neutral': 0,
                'limit_up': 0,
                'limit_down': 0,
                'strong_stocks': 0,
                'weak_stocks': 0,
                'avg_change': 0.0,
                'avg_turnover': 0.0,
                'avg_volatility': 0.0,
                'trend_score': 50
            }
        }
    
    # === 统计基础数据 ===
    # 过滤掉无效数据
    valid_stocks = [s for s in all_stocks if s.get('change_pct') is not None]
    
    if not valid_stocks:
        return {
            'score': 50.0,
            'level': '中性',
            'emoji': '😐',
            'description': '暂无有效数据',
            'stats': {
                'total': 0,
                'gainers': 0,
                'losers': 0,
                'neutral': 0,
                'limit_up': 0,
                'limit_down': 0,
                'strong_stocks': 0,
                'weak_stocks': 0,
                'avg_change': 0.0,
                'avg_turnover': 0.0,
                'avg_volatility': 0.0,
                'trend_score': 50
            }
        }
    
    total = len(valid_stocks)
    gainers = sum(1 for s in valid_stocks if s['change_pct'] > 0)
    losers = sum(1 for s in valid_stocks if s['change_pct'] < 0)
    neutral = total - gainers - losers
    
    # 涨停/跌停 (A股涨跌停板 ±10%)
    limit_up = sum(1 for s in valid_stocks if s['change_pct'] >= 9.8)
    limit_down = sum(1 for s in valid_stocks if s['change_pct'] <= -9.8)
    
    # 强势/弱势股
    strong_stocks = sum(1 for s in valid_stocks if s['change_pct'] > 5)
    weak_stocks = sum(1 for s in valid_stocks if s['change_pct'] < -5)
    
    # 平均涨幅
    avg_change = sum(s['change_pct'] for s in valid_stocks) / total
    
    # 平均换手率
    avg_turnover = sum(s.get('turnover', 0) or 0 for s in valid_stocks) / total
    
    # 平均波动率 (振幅)
    avg_volatility = sum(s.get('amplitude', 0) or 0 for s in valid_stocks) / total
    
    # 趋势得分 (价格 vs MA20) - 暂时跳过，因为没有MA20数据
    # above_ma20 = sum(1 for s in valid_stocks if (s.get('price') or 0) > (s.get('ma20') or 0))
    # trend_score = (above_ma20 / total) * 100 if total > 0 else 50
    trend_score = 50  # 默认中性
    
    # === 多维度评分系统 ===
    sentiment_score = 50  # 基准分
    
    # 1. 涨跌家数比 (权重 20%) -> ±10分
    up_ratio = gainers / total if total > 0 else 0
    if up_ratio > 0.7:
        sentiment_score += 10  # 普涨
    elif up_ratio > 0.6:
        sentiment_score += 7
    elif up_ratio > 0.5:
        sentiment_score += 4
    elif up_ratio > 0.4:
        sentiment_score += 0  # 中性
    elif up_ratio > 0.3:
        sentiment_score -= 4
    else:
        sentiment_score -= 10  # 普跌
    
    # 2. 平均涨幅 (权重 20%) -> ±10分
    if avg_change > 3:
        sentiment_score += 10
    elif avg_change > 1.5:
        sentiment_score += 7
    elif avg_change > 0.5:
        sentiment_score += 4
    elif avg_change > -0.5:
        sentiment_score += 0
    elif avg_change > -1.5:
        sentiment_score -= 4
    elif avg_change > -3:
        sentiment_score -= 7
    else:
        sentiment_score -= 10
    
    # 3. 涨停/跌停比 (权重 15%) -> ±8分
    limit_ratio = limit_up - limit_down
    if limit_ratio >= 10:
        sentiment_score += 8
    elif limit_ratio >= 5:
        sentiment_score += 5
    elif limit_ratio >= 1:
        sentiment_score += 2
    elif limit_ratio >= -1:
        sentiment_score += 0
    elif limit_ratio >= -5:
        sentiment_score -= 2
    elif limit_ratio >= -10:
        sentiment_score -= 5
    else:
        sentiment_score -= 8
    
    # 4. 强势股占比 (权重 15%) -> ±8分
    strong_ratio = strong_stocks / total if total > 0 else 0
    weak_ratio = weak_stocks / total if total > 0 else 0
    if strong_ratio > 0.3:
        sentiment_score += 8
    elif strong_ratio > 0.2:
        sentiment_score += 5
    elif strong_ratio > 0.1:
        sentiment_score += 2
    elif weak_ratio > 0.3:
        sentiment_score -= 8
    elif weak_ratio > 0.2:
        sentiment_score -= 5
    elif weak_ratio > 0.1:
        sentiment_score -= 2
    
    # 5. 成交活跃度 (权重 10%) -> ±5分
    if avg_turnover > 5:
        sentiment_score += 5  # 极度活跃
    elif avg_turnover > 3:
        sentiment_score += 3
    elif avg_turnover > 2:
        sentiment_score += 1
    elif avg_turnover > 1:
        sentiment_score += 0
    else:
        sentiment_score -= 5  # 成交低迷
    
    # 6. 波动率 (权重 10%) -> ±5分
    if avg_volatility > 8:
        sentiment_score -= 3  # 过度波动，风险
    elif avg_volatility > 5:
        sentiment_score += 2  # 适度活跃
    elif avg_volatility > 3:
        sentiment_score += 5  # 健康波动
    elif avg_volatility > 2:
        sentiment_score += 2
    else:
        sentiment_score -= 3  # 过度平静，死水
    
    # 7. 趋势 (权重 10%) -> ±4分
    if trend_score > 70:
        sentiment_score += 4
    elif trend_score > 60:
        sentiment_score += 2
    elif trend_score > 50:
        sentiment_score += 1
    elif trend_score > 40:
        sentiment_score -= 1
    elif trend_score > 30:
        sentiment_score -= 2
    else:
        sentiment_score -= 4
    
    # 限制在 0-100 范围
    sentiment_score = max(0, min(100, sentiment_score))
    
    # === 情绪等级 ===
    if sentiment_score >= 80:
        level = '极度乐观'
        emoji = '🔥'
        description = '市场情绪极度亢奋，注意追高风险'
    elif sentiment_score >= 65:
        level = '乐观'
        emoji = '📈'
        description = '市场情绪积极，趋势向上'
    elif sentiment_score >= 55:
        level = '偏乐观'
        emoji = '🟢'
        description = '市场偏强，情绪稳定'
    elif sentiment_score >= 45:
        level = '中性'
        emoji = '😐'
        description = '市场平稳，多空平衡'
    elif sentiment_score >= 35:
        level = '偏悲观'
        emoji = '🔻'
        description = '市场偏弱，观望为主'
    elif sentiment_score >= 20:
        level = '悲观'
        emoji = '📉'
        description = '市场情绪低迷，谨慎操作'
    else:
        level = '极度悲观'
        emoji = '❄️'
        description = '市场情绪极度低迷，恐慌情绪蔓延'
    
    # 判断数据是否是历史数据
    is_historical = False
    data_update_time = None
    if valid_stocks and valid_stocks[0].get('update_time'):
        from datetime import timedelta
        try:
            data_update_time = datetime.strptime(valid_stocks[0]['update_time'], '%Y-%m-%d %H:%M:%S.%f')
            if datetime.now() - data_update_time > timedelta(minutes=30):
                is_historical = True
        except:
            pass
    
    return {
        'score': round(sentiment_score, 1),
        'level': level,
        'emoji': emoji,
        'description': description,
        'stats': {
            'total': total,
            'gainers': gainers,
            'losers': losers,
            'neutral': neutral,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'strong_stocks': strong_stocks,
            'weak_stocks': weak_stocks,
            'avg_change': round(avg_change, 2),
            'avg_turnover': round(avg_turnover, 2),
            'avg_volatility': round(avg_volatility, 2),
            'trend_score': round(trend_score, 1),
            'up_ratio': round(up_ratio * 100, 1)
        },
        'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_time': data_update_time.strftime('%Y-%m-%d %H:%M:%S') if data_update_time else None,
        'is_historical': is_historical
    }


if __name__ == '__main__':
    """测试"""
    import json
    result = calculate_market_sentiment()
    print(json.dumps(result, ensure_ascii=False, indent=2))
