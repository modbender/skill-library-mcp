#!/usr/bin/env python3
"""
InvestmentTracker 详细持仓分析报告
包含持仓详情、市场信息和投资分析
"""

import json
import time
import subprocess
from datetime import datetime

# MCP API配置
BASE_URL = 'https://investmenttracker-ingest-production.up.railway.app/mcp'
AUTH_TOKEN = 'it_live_E8MnP28kdPmgpxdjfRG1wzUB9Nr7mCiBU34NjFkAPes'

def call_mcp_tool(tool_name, arguments=None):
    """调用MCP工具"""
    request_data = {
        'jsonrpc': '2.0',
        'method': 'tools/call',
        'params': {
            'name': tool_name,
            'arguments': arguments or {}
        },
        'id': int(time.time() * 1000)
    }
    
    json_data = json.dumps(request_data)
    curl_cmd = [
        'curl', '-s', '-X', 'POST', BASE_URL,
        '-H', 'Authorization: Bearer ' + AUTH_TOKEN,
        '-H', 'Accept: application/json, text/event-stream',
        '-H', 'Content-Type: application/json',
        '-d', json_data
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('data: '):
                    try:
                        event_data = json.loads(line[6:])
                        if 'result' in event_data and 'content' in event_data['result']:
                            for content in event_data['result']['content']:
                                if content['type'] == 'text':
                                    return json.loads(content['text'])
                    except json.JSONDecodeError:
                        continue
        return None
    except Exception as e:
        print(f'调用{tool_name}失败: {e}')
        return None

def analyze_position(position):
    """分析单个持仓"""
    analysis = []
    
    # 持仓时间分析
    buy_date = datetime.strptime(position['buy_date'], '%Y-%m-%d')
    days_held = (datetime.now() - buy_date).days
    
    if days_held < 7:
        analysis.append(f"🆕 新持仓（持有{days_held}天）")
    elif days_held < 30:
        analysis.append(f"📅 短期持仓（持有{days_held}天）")
    elif days_held < 180:
        analysis.append(f"📊 中期持仓（持有{days_held}天）")
    else:
        analysis.append(f"🏆 长期持仓（持有{days_held}天）")
    
    # 持仓数量分析
    quantity = position['quantity']
    if quantity < 100:
        analysis.append(f"📦 小量持仓（{quantity:,}股）")
    elif quantity < 1000:
        analysis.append(f"📦 中等持仓（{quantity:,}股）")
    else:
        analysis.append(f"📦 大量持仓（{quantity:,}股）")
    
    # 代码分析
    code = position['code']
    if code.startswith('6'):
        analysis.append("🇭🇰 港股主板")
    elif code.startswith('0'):
        analysis.append("🇭🇰 港股创业板")
    else:
        analysis.append("📊 其他市场")
    
    return analysis

def main():
    print('📊 InvestmentTracker 详细持仓分析报告')
    print('=' * 70)
    
    # 获取持仓数据
    print('📈 当前持仓详情')
    print('-' * 70)
    positions = call_mcp_tool('positions_list_v1', {'status': 'POSITION', 'limit': 20})
    
    if positions and 'items' in positions:
        positions_list = positions['items']
        print(f'📊 总持仓数量: {len(positions_list)}个')
        print()
        
        # 按买入日期排序
        positions_list.sort(key=lambda x: x['buy_date'], reverse=True)
        
        total_quantity = 0
        hkd_positions = 0
        
        for i, position in enumerate(positions_list, 1):
            print(f'{i}. {position["code"]} - {position["name"]}')
            print(f'   📊 基本信息')
            print(f'      持仓状态: {position["status"]}')
            print(f'      货币: {position["currency"]}')
            print(f'      数量: {position["quantity"]:,}')
            print(f'      买入日期: {position["buy_date"]}')
            print(f'      投资组合: {position["portfolio"]}')
            print(f'      最后更新: {position["source_updated_at"][:19]}')
            
            # 持仓分析
            analysis = analyze_position(position)
            print(f'   📈 持仓分析')
            for item in analysis:
                print(f'      {item}')
            
            print()
            
            total_quantity += position['quantity']
            if position['currency'] == 'HKD':
                hkd_positions += 1
        
        print('📊 持仓汇总')
        print('-' * 30)
        print(f'总持仓数量: {total_quantity:,}')
        print(f'HKD持仓: {hkd_positions}个')
        print(f'其他货币持仓: {len(positions_list) - hkd_positions}个')
        
        # 投资组合分析
        print()
        print('📈 投资组合分析')
        print('-' * 30)
        
        # 按投资组合分组
        portfolio_groups = {}
        for position in positions_list:
            portfolio = position['portfolio']
            if portfolio not in portfolio_groups:
                portfolio_groups[portfolio] = []
            portfolio_groups[portfolio].append(position)
        
        for portfolio, positions in portfolio_groups.items():
            total_qty = sum(p['quantity'] for p in positions)
            print(f'{portfolio}: {len(positions)}个持仓，总数量: {total_qty:,}')
        
        # 持仓时间分布
        print()
        print('📅 持仓时间分布')
        print('-' * 30)
        
        now = datetime.now()
        time_groups = {'<7天': 0, '7-30天': 0, '30-180天': 0, '>180天': 0}
        
        for position in positions_list:
            buy_date = datetime.strptime(position['buy_date'], '%Y-%m-%d')
            days_held = (now - buy_date).days
            
            if days_held < 7:
                time_groups['<7天'] += 1
            elif days_held < 30:
                time_groups['7-30天'] += 1
            elif days_held < 180:
                time_groups['30-180天'] += 1
            else:
                time_groups['>180天'] += 1
        
        for period, count in time_groups.items():
            if count > 0:
                print(f'{period}: {count}个持仓')
        
    else:
        print('❌ 持仓数据获取失败')
    
    print()
    print('=' * 70)
    print('📋 报告说明')
    print('-' * 30)
    print('1. 数据来源: InvestmentTracker MCP API')
    print('2. 报告时间: 2026-02-17 04:00 UTC')
    print('3. 持仓状态: POSITION (活跃持仓)')
    print('4. 货币单位: HKD (港币)')
    print('5. 数据更新: 实时获取')
    print()
    print('💡 投资建议')
    print('-' * 30)
    print('• 定期检查持仓表现')
    print('• 关注市场动态和新闻')
    print('• 根据投资目标调整持仓')
    print('• 保持适当的风险分散')
    print('=' * 70)

if __name__ == '__main__':
    main()