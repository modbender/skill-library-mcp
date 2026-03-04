#!/usr/bin/env python3
"""
期权策略分析器 - 计算各种期权策略的盈亏、Breakeven、Max Profit/Loss
用法: python strategy_analyzer.py --strategy iron_condor --spot 180 --legs "175p@2.5,180p@4.0,185c@3.5,190c@1.5" --dte 30
"""

import argparse
import json
import sys
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np


@dataclass
class OptionLeg:
    """期权腿"""
    strike: float
    premium: float
    option_type: str  # 'call' or 'put'
    position: str  # 'long' or 'short'
    quantity: int = 1
    
    def payoff(self, spot_price: float) -> float:
        """计算到期时的盈亏"""
        if self.option_type == 'call':
            intrinsic = max(0, spot_price - self.strike)
        else:  # put
            intrinsic = max(0, self.strike - spot_price)
        
        if self.position == 'long':
            return (intrinsic - self.premium) * self.quantity * 100
        else:  # short
            return (self.premium - intrinsic) * self.quantity * 100


class StrategyAnalyzer:
    """策略分析器"""
    
    STRATEGIES = {
        # 单腿
        'long_call': {'legs': 1, 'desc': '看涨期权多头'},
        'long_put': {'legs': 1, 'desc': '看跌期权多头'},
        'short_call': {'legs': 1, 'desc': '看涨期权空头 (裸卖)'},
        'short_put': {'legs': 1, 'desc': '看跌期权空头 (裸卖)'},
        
        # 垂直价差
        'bull_call_spread': {'legs': 2, 'desc': '牛市看涨价差'},
        'bear_call_spread': {'legs': 2, 'desc': '熊市看涨价差'},
        'bull_put_spread': {'legs': 2, 'desc': '牛市看跌价差'},
        'bear_put_spread': {'legs': 2, 'desc': '熊市看跌价差'},
        
        # 组合策略
        'covered_call': {'legs': 2, 'desc': '备兑看涨 (持有股票+卖Call)'},
        'protective_put': {'legs': 2, 'desc': '保护性看跌 (持有股票+买Put)'},
        'collar': {'legs': 3, 'desc': '领口策略 (持有股票+卖Call+买Put)'},
        
        # 波动率策略
        'straddle': {'legs': 2, 'desc': '跨式 (ATM Call+Put)'},
        'strangle': {'legs': 2, 'desc': '宽跨式 (OTM Call+Put)'},
        
        # 高级策略
        'iron_condor': {'legs': 4, 'desc': '铁鹰 (卖宽跨+买更宽跨)'},
        'butterfly': {'legs': 3, 'desc': '蝶式价差'},
        'iron_butterfly': {'legs': 4, 'desc': '铁蝶式'},
        'calendar_spread': {'legs': 2, 'desc': '日历价差 (不同到期日)'},
    }    
    def __init__(self, spot: float, legs: List[OptionLeg], dte: int = 30):
        self.spot = spot
        self.legs = legs
        self.dte = dte
    
    def total_premium(self) -> float:
        """计算净权利金 (正数=收入，负数=支出)"""
        total = 0
        for leg in self.legs:
            if leg.position == 'long':
                total -= leg.premium * leg.quantity * 100
            else:
                total += leg.premium * leg.quantity * 100
        return total
    
    def payoff_at_price(self, price: float) -> float:
        """计算指定价格的盈亏"""
        return sum(leg.payoff(price) for leg in self.legs)
    
    def payoff_curve(self, price_range: Tuple[float, float] = None, points: int = 100) -> List[dict]:
        """生成盈亏曲线数据"""
        if price_range is None:
            strikes = [leg.strike for leg in self.legs]
            min_strike = min(strikes)
            max_strike = max(strikes)
            margin = (max_strike - min_strike) * 0.5 or self.spot * 0.1
            price_range = (min_strike - margin, max_strike + margin)
        
        prices = np.linspace(price_range[0], price_range[1], points)
        return [{'price': round(p, 2), 'pnl': round(self.payoff_at_price(p), 2)} for p in prices]
    
    def find_breakevens(self) -> List[float]:
        """找到盈亏平衡点"""
        curve = self.payoff_curve(points=1000)
        breakevens = []
        
        for i in range(1, len(curve)):
            if curve[i-1]['pnl'] * curve[i]['pnl'] < 0:  # 符号变化
                # 线性插值找精确点
                p1, pnl1 = curve[i-1]['price'], curve[i-1]['pnl']
                p2, pnl2 = curve[i]['price'], curve[i]['pnl']
                be = p1 - pnl1 * (p2 - p1) / (pnl2 - pnl1)
                breakevens.append(round(be, 2))
        
        return breakevens
    
    def max_profit(self) -> Tuple[float, str]:
        """计算最大盈利"""
        curve = self.payoff_curve(points=1000)
        max_pnl = max(c['pnl'] for c in curve)
        
        # 检查是否无限
        edge_high = self.payoff_at_price(self.spot * 3)
        edge_low = self.payoff_at_price(self.spot * 0.01)
        
        if edge_high > max_pnl * 2 or edge_low > max_pnl * 2:
            return float('inf'), "无限"
        
        return max_pnl, f"${max_pnl:,.2f}"
    
    def max_loss(self) -> Tuple[float, str]:
        """计算最大亏损"""
        curve = self.payoff_curve(points=1000)
        min_pnl = min(c['pnl'] for c in curve)
        
        # 检查是否无限
        edge_high = self.payoff_at_price(self.spot * 3)
        edge_low = self.payoff_at_price(self.spot * 0.01)        
        if edge_high < min_pnl * 2 or edge_low < min_pnl * 2:
            return float('-inf'), "无限"
        
        return min_pnl, f"${min_pnl:,.2f}"
    
    def risk_reward_ratio(self) -> Optional[float]:
        """计算风险收益比"""
        max_profit_val, _ = self.max_profit()
        max_loss_val, _ = self.max_loss()
        
        if max_profit_val == float('inf') or max_loss_val == float('-inf'):
            return None
        
        if max_loss_val == 0:
            return float('inf')
        
        return abs(max_profit_val / max_loss_val)
    
    def analyze(self) -> dict:
        """完整分析"""
        breakevens = self.find_breakevens()
        max_profit_val, max_profit_str = self.max_profit()
        max_loss_val, max_loss_str = self.max_loss()
        rr_ratio = self.risk_reward_ratio()
        
        return {
            'spot': self.spot,
            'dte': self.dte,
            'legs': [
                {
                    'strike': leg.strike,
                    'type': leg.option_type,
                    'position': leg.position,
                    'premium': leg.premium,
                    'quantity': leg.quantity
                }
                for leg in self.legs
            ],
            'net_premium': round(self.total_premium(), 2),
            'max_profit': max_profit_str,
            'max_profit_value': max_profit_val if max_profit_val != float('inf') else None,
            'max_loss': max_loss_str,
            'max_loss_value': max_loss_val if max_loss_val != float('-inf') else None,
            'breakevens': breakevens,
            'risk_reward_ratio': round(rr_ratio, 2) if rr_ratio and rr_ratio != float('inf') else None,
            'payoff_curve': self.payoff_curve(points=50)
        }


def parse_legs(legs_str: str, strategy: str = None) -> List[OptionLeg]:
    """
    解析腿字符串
    格式: "180c@5.0,190c@2.0" 或 "175p@2.5,180p@4.0,185c@3.5,190c@1.5"
    c=call, p=put
    对于价差策略，自动判断 long/short
    """
    legs = []
    parts = legs_str.split(',')
    
    for i, part in enumerate(parts):
        part = part.strip()
        # 解析: 180c@5.0 或 180p@2.5
        if '@' in part:
            spec, premium = part.split('@')
            premium = float(premium)
        else:
            spec = part
            premium = 0
        
        # 提取 strike 和 type
        if spec.endswith('c') or spec.endswith('C'):
            strike = float(spec[:-1])
            opt_type = 'call'
        elif spec.endswith('p') or spec.endswith('P'):
            strike = float(spec[:-1])
            opt_type = 'put'
        else:
            raise ValueError(f"无法解析: {part}, 应为 180c@5.0 或 180p@2.5 格式")
        
        # 根据策略判断 position
        position = determine_position(strategy, i, opt_type, strike, parts)
        
        legs.append(OptionLeg(strike, premium, opt_type, position))
    
    return legs


def determine_position(strategy: str, index: int, opt_type: str, strike: float, all_parts: list) -> str:
    """根据策略和位置判断 long/short"""
    if not strategy:
        # 默认: 第一个long，其他按交替
        return 'long' if index % 2 == 0 else 'short'
    
    strategy = strategy.lower()
    
    # 单腿策略
    if strategy in ['long_call', 'long_put']:
        return 'long'
    if strategy in ['short_call', 'short_put']:
        return 'short'
    
    # 垂直价差
    if strategy == 'bull_call_spread':
        return 'long' if index == 0 else 'short'  # 买低卖高
    if strategy == 'bear_call_spread':
        return 'short' if index == 0 else 'long'  # 卖低买高
    if strategy == 'bull_put_spread':
        return 'short' if index == 0 else 'long'  # 卖高买低
    if strategy == 'bear_put_spread':
        return 'long' if index == 0 else 'short'  # 买高卖低
    
    # 跨式/宽跨式 (都是 long 或都是 short)
    if strategy in ['straddle', 'strangle']:
        return 'long'  # 默认买入
    if strategy in ['short_straddle', 'short_strangle']:
        return 'short'
    
    # Iron Condor: short inner, long outer
    if strategy == 'iron_condor':
        # 顺序: low put(long), mid-low put(short), mid-high call(short), high call(long)
        return 'long' if index in [0, 3] else 'short'
    
    # Butterfly
    if strategy == 'butterfly':
        # 顺序: low(long), mid(short x2), high(long)
        return 'long' if index in [0, 2] else 'short'
    
    # Iron Butterfly
    if strategy == 'iron_butterfly':
        return 'short' if index in [1, 2] else 'long'
    
    return 'long' if index % 2 == 0 else 'short'


def format_markdown(result: dict, strategy_name: str = None) -> str:
    """格式化为 Markdown"""
    lines = []
    
    title = StrategyAnalyzer.STRATEGIES.get(strategy_name, {}).get('desc', '期权策略') if strategy_name else '期权策略'
    lines.append(f"# {title} 分析")
    lines.append(f"\n**标的价格**: ${result['spot']}")
    lines.append(f"**DTE**: {result['dte']}天")
    
    lines.append("\n## 📋 策略腿")
    lines.append("| # | 行权价 | 类型 | 方向 | 权利金 |")
    lines.append("|---|--------|------|------|--------|")
    for i, leg in enumerate(result['legs'], 1):
        direction = "买入" if leg['position'] == 'long' else "卖出"
        opt_type = "Call" if leg['type'] == 'call' else "Put"
        lines.append(f"| {i} | ${leg['strike']} | {opt_type} | {direction} | ${leg['premium']:.2f} |")
    
    lines.append(f"\n**净权利金**: ${result['net_premium']:,.2f}" + (" (收入)" if result['net_premium'] > 0 else " (支出)"))
    
    lines.append("\n## 📊 盈亏分析")
    lines.append(f"- **最大盈利**: {result['max_profit']}")
    lines.append(f"- **最大亏损**: {result['max_loss']}")
    
    if result['breakevens']:
        be_str = ', '.join(f"${be}" for be in result['breakevens'])
        lines.append(f"- **盈亏平衡点**: {be_str}")
    
    if result['risk_reward_ratio']:
        lines.append(f"- **风险收益比**: {result['risk_reward_ratio']:.2f}:1")
    
    # ASCII P&L 图
    lines.append("\n## 📈 盈亏曲线 (到期)")
    lines.append("```")
    curve = result['payoff_curve']
    max_pnl = max(abs(c['pnl']) for c in curve) or 1
    
    for c in curve[::5]:  # 每5个点取一个
        bar_len = int(abs(c['pnl']) / max_pnl * 20)
        if c['pnl'] >= 0:
            bar = ' ' * 20 + '|' + '█' * bar_len
        else:
            bar = ' ' * (20 - bar_len) + '█' * bar_len + '|'
        lines.append(f"${c['price']:>7.1f} {bar} ${c['pnl']:>8.0f}")
    lines.append("```")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='期权策略分析器')
    parser.add_argument('--strategy', '-s', choices=list(StrategyAnalyzer.STRATEGIES.keys()),
                        help='策略类型')
    parser.add_argument('--spot', '-p', type=float, required=True, help='标的当前价格')
    parser.add_argument('--legs', '-l', required=True, 
                        help='期权腿，格式: "180c@5.0,190c@2.0" (c=call, p=put)')
    parser.add_argument('--dte', '-d', type=int, default=30, help='距到期天数')
    parser.add_argument('--format', '-f', choices=['json', 'md'], default='md', help='输出格式')
    parser.add_argument('--list-strategies', action='store_true', help='列出所有策略')
    
    args = parser.parse_args()
    
    if args.list_strategies:
        print("可用策略:")
        for name, info in StrategyAnalyzer.STRATEGIES.items():
            print(f"  {name}: {info['desc']}")
        return
    
    try:
        legs = parse_legs(args.legs, args.strategy)
        analyzer = StrategyAnalyzer(args.spot, legs, args.dte)
        result = analyzer.analyze()
        
        if args.format == 'json':
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_markdown(result, args.strategy))
            
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
