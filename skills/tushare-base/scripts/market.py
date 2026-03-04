#!/usr/bin/env python3
"""
Tushare 金融数据接口
支持：股票行情、期货数据、基本面数据、宏观经济
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
from typing import Optional, Dict, List

# 尝试导入 tushare
try:
    import tushare as ts
    TUSHARE_AVAILABLE = True
except ImportError:
    TUSHARE_AVAILABLE = False
    print("⚠️  tushare 库未安装，请先运行: pip3 install tushare --user")

def get_pro_api():
    """获取 Tushare Pro API 实例"""
    if not TUSHARE_AVAILABLE:
        return None
    
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("❌ 错误: 请设置 TUSHARE_TOKEN 环境变量")
        print("获取方式: https://tushare.pro/register")
        return None
    
    ts.set_token(token)
    return ts.pro_api()

# ==================== 股票数据 ====================

def get_stock_basic(exchange: str = '', list_status: str = 'L') -> List[Dict]:
    """获取股票基础信息"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.stock_basic(exchange=exchange, list_status=list_status)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取股票基础信息失败: {e}")
        return []

def get_daily(ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> List[Dict]:
    """获取日线行情"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.daily(ts_code=ts_code, trade_date=trade_date, 
                      start_date=start_date, end_date=end_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取日线行情失败: {e}")
        return []

def get_weekly(ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> List[Dict]:
    """获取周线行情"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.weekly(ts_code=ts_code, trade_date=trade_date, 
                       start_date=start_date, end_date=end_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取周线行情失败: {e}")
        return []

def get_monthly(ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> List[Dict]:
    """获取月线行情"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.monthly(ts_code=ts_code, trade_date=trade_date, 
                        start_date=start_date, end_date=end_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取月线行情失败: {e}")
        return []

def get_realtime_quote(ts_code: str) -> Optional[Dict]:
    """获取实时行情（使用旧版接口）"""
    if not TUSHARE_AVAILABLE:
        return None
    
    try:
        df = ts.get_realtime_quotes(ts_code)
        if df is not None and not df.empty:
            return df.iloc[0].to_dict()
        return None
    except Exception as e:
        print(f"❌ 获取实时行情失败: {e}")
        return None

def get_stock_company(ts_code: str = '') -> List[Dict]:
    """获取上市公司基本信息"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.stock_company(ts_code=ts_code)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取公司信息失败: {e}")
        return []

def get_top10_holders(ts_code: str, start_date: str = '', end_date: str = '') -> List[Dict]:
    """获取前十大股东"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.top10_holders(ts_code=ts_code, start_date=start_date, end_date=end_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取股东信息失败: {e}")
        return []

def get_moneyflow(ts_code: str = '', trade_date: str = '') -> List[Dict]:
    """获取个股资金流向"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.moneyflow(ts_code=ts_code, trade_date=trade_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取资金流向失败: {e}")
        return []

# ==================== 期货数据 ====================

def get_fut_basic(exchange: str = '', fut_type: str = '2') -> List[Dict]:
    """获取期货合约基础信息"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.fut_basic(exchange=exchange, fut_type=fut_type)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取期货基础信息失败: {e}")
        return []

def get_fut_daily(ts_code: str = '', trade_date: str = '', start_date: str = '', end_date: str = '') -> List[Dict]:
    """获取期货日线行情"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.fut_daily(ts_code=ts_code, trade_date=trade_date,
                          start_date=start_date, end_date=end_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取期货日线失败: {e}")
        return []

def get_fut_holding(trade_date: str = '', symbol: str = '') -> List[Dict]:
    """获取每日持仓排名"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.fut_holding(trade_date=trade_date, symbol=symbol)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取持仓排名失败: {e}")
        return []

def get_fut_wsr(trade_date: str = '') -> List[Dict]:
    """获取仓单日报"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.fut_wsr(trade_date=trade_date)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取仓单数据失败: {e}")
        return []

def get_fut_settle(trade_date: str = '', exchange: str = '') -> List[Dict]:
    """获取期货结算参数"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.fut_settle(trade_date=trade_date, exchange=exchange)
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取结算参数失败: {e}")
        return []

# ==================== 宏观经济 ====================

def get_gdp() -> List[Dict]:
    """获取GDP数据"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.cn_gdp()
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取GDP数据失败: {e}")
        return []

def get_cpi() -> List[Dict]:
    """获取CPI数据"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.cn_cpi()
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取CPI数据失败: {e}")
        return []

def get_ppi() -> List[Dict]:
    """获取PPI数据"""
    pro = get_pro_api()
    if not pro:
        return []
    
    try:
        df = pro.cn_ppi()
        return df.to_dict('records')
    except Exception as e:
        print(f"❌ 获取PPI数据失败: {e}")
        return []

# ==================== 输出格式化 ====================

def print_stock_basic(data: List[Dict]):
    """打印股票基础信息"""
    if not data:
        print("📭 没有数据")
        return
    
    print(f"\n📈 股票列表 ({len(data)} 只):\n")
    print(f"{'代码':<12} {'名称':<15} {'行业':<15} {'上市日期':<12}")
    print("-" * 60)
    
    for item in data[:50]:  # 限制显示数量
        ts_code = item.get('ts_code', 'N/A')
        name = item.get('name', 'Unknown')[:14]
        industry = item.get('industry', '-')[:14]
        list_date = item.get('list_date', '-')
        print(f"{ts_code:<12} {name:<15} {industry:<15} {list_date:<12}")

def print_daily(data: List[Dict]):
    """打印日线行情"""
    if not data:
        print("📭 没有数据")
        return
    
    print(f"\n📊 日线行情 ({len(data)} 条):\n")
    print(f"{'日期':<12} {'开盘':<10} {'收盘':<10} {'最高':<10} {'最低':<10} {'成交量':<12}")
    print("-" * 70)
    
    for item in data[:20]:
        trade_date = item.get('trade_date', '-')
        open_price = item.get('open', 0)
        close = item.get('close', 0)
        high = item.get('high', 0)
        low = item.get('low', 0)
        vol = item.get('vol', 0)
        
        change = item.get('change', 0)
        pct_chg = item.get('pct_chg', 0)
        
        emoji = "🟢" if pct_chg > 0 else "🔴" if pct_chg < 0 else "⚪"
        
        print(f"{trade_date:<12} {open_price:<10.2f} {close:<10.2f} {high:<10.2f} {low:<10.2f} {vol:<12}")
        print(f"    {emoji} 涨跌: {change:+.2f} ({pct_chg:+.2f}%)")
        print()

def print_fut_basic(data: List[Dict]):
    """打印期货基础信息"""
    if not data:
        print("📭 没有数据")
        return
    
    print(f"\n📦 期货合约 ({len(data)} 个):\n")
    print(f"{'代码':<15} {'名称':<20} {'交易所':<10} {'合约类型':<10}")
    print("-" * 60)
    
    for item in data[:50]:
        ts_code = item.get('ts_code', 'N/A')
        name = item.get('name', 'Unknown')[:18]
        exchange = item.get('exchange', '-')
        fut_type = item.get('fut_type', '-')
        print(f"{ts_code:<15} {name:<20} {exchange:<10} {fut_type:<10}")

def print_fut_daily(data: List[Dict]):
    """打印期货日线"""
    if not data:
        print("📭 没有数据")
        return
    
    print(f"\n📊 期货日线 ({len(data)} 条):\n")
    print(f"{'日期':<12} {'开盘':<10} {'收盘':<10} {'最高':<10} {'最低':<10} {'持仓':<10}")
    print("-" * 70)
    
    for item in data[:20]:
        trade_date = item.get('trade_date', '-')
        open_price = item.get('open', 0)
        close = item.get('close', 0)
        high = item.get('high', 0)
        low = item.get('low', 0)
        oi = item.get('oi', 0)  # 持仓量
        
        change = close - open_price
        
        emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
        
        print(f"{trade_date:<12} {open_price:<10.2f} {close:<10.2f} {high:<10.2f} {low:<10.2f} {oi:<10.0f}")

def print_moneyflow(data: List[Dict]):
    """打印资金流向"""
    if not data:
        print("📭 没有数据")
        return
    
    print(f"\n💰 资金流向 ({len(data)} 条):\n")
    print(f"{'代码':<12} {'日期':<12} {'净流入':<12} {'主力净流入':<12}")
    print("-" * 55)
    
    for item in data[:20]:
        ts_code = item.get('ts_code', '-')
        trade_date = item.get('trade_date', '-')
        net_mf = item.get('net_mf', 0) / 10000  # 万元
        net_mf_amount = item.get('net_mf_amount', 0) / 10000
        
        emoji = "🟢" if net_mf > 0 else "🔴"
        
        print(f"{ts_code:<12} {trade_date:<12} {emoji} {net_mf:<10.1f}万 {net_mf_amount:<10.1f}万")

# ==================== 主程序 ====================

def main():
    parser = argparse.ArgumentParser(description='Tushare 金融数据接口')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 股票基础信息
    stock_basic = subparsers.add_parser('stock_basic', help='获取股票基础信息')
    stock_basic.add_argument('--exchange', default='', help='交易所 (SSE/SZSE)')
    
    # 日线行情
    daily = subparsers.add_parser('daily', help='获取日线行情')
    daily.add_argument('--ts_code', required=True, help='股票代码 (如: 000001.SZ)')
    daily.add_argument('--start_date', help='开始日期 (YYYYMMDD)')
    daily.add_argument('--end_date', help='结束日期 (YYYYMMDD)')
    daily.add_argument('--trade_date', help='交易日期 (YYYYMMDD)')
    
    # 周线行情
    weekly = subparsers.add_parser('weekly', help='获取周线行情')
    weekly.add_argument('--ts_code', required=True, help='股票代码 (如: 000001.SZ)')
    weekly.add_argument('--start_date', help='开始日期 (YYYYMMDD)')
    weekly.add_argument('--end_date', help='结束日期 (YYYYMMDD)')
    weekly.add_argument('--trade_date', help='交易日期 (YYYYMMDD)')
    
    # 月线行情
    monthly = subparsers.add_parser('monthly', help='获取月线行情')
    monthly.add_argument('--ts_code', required=True, help='股票代码 (如: 000001.SZ)')
    monthly.add_argument('--start_date', help='开始日期 (YYYYMMDD)')
    monthly.add_argument('--end_date', help='结束日期 (YYYYMMDD)')
    monthly.add_argument('--trade_date', help='交易日期 (YYYYMMDD)')
    
    # 实时行情
    realtime = subparsers.add_parser('realtime', help='获取实时行情')
    realtime.add_argument('ts_code', help='股票代码')
    
    # 公司信息
    subparsers.add_parser('company', help='获取上市公司信息')
    
    # 资金流向
    moneyflow = subparsers.add_parser('moneyflow', help='获取资金流向')
    moneyflow.add_argument('--ts_code', help='股票代码')
    moneyflow.add_argument('--trade_date', help='交易日期')
    
    # 期货基础
    fut_basic = subparsers.add_parser('fut_basic', help='获取期货基础信息')
    fut_basic.add_argument('--exchange', default='', help='交易所')
    
    # 期货日线
    fut_daily = subparsers.add_parser('fut_daily', help='获取期货日线')
    fut_daily.add_argument('--ts_code', required=True, help='期货代码 (如: CU.SHF)')
    fut_daily.add_argument('--start_date', help='开始日期')
    fut_daily.add_argument('--end_date', help='结束日期')
    
    # 期货持仓
    fut_holding = subparsers.add_parser('fut_holding', help='获取期货持仓排名')
    fut_holding.add_argument('--trade_date', help='交易日期')
    fut_holding.add_argument('--symbol', help='合约代码')
    
    # 宏观经济
    subparsers.add_parser('gdp', help='获取GDP数据')
    subparsers.add_parser('cpi', help='获取CPI数据')
    subparsers.add_parser('ppi', help='获取PPI数据')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if not TUSHARE_AVAILABLE:
        print("\n❌ 请先安装 tushare:")
        print("   pip3 install tushare --user")
        return
    
    # 执行命令
    if args.command == 'stock_basic':
        data = get_stock_basic(exchange=args.exchange)
        print_stock_basic(data)
    
    elif args.command == 'daily':
        data = get_daily(ts_code=args.ts_code, trade_date=args.trade_date,
                        start_date=args.start_date, end_date=args.end_date)
        print_daily(data)
    
    elif args.command == 'weekly':
        data = get_weekly(ts_code=args.ts_code, trade_date=args.trade_date,
                         start_date=args.start_date, end_date=args.end_date)
        print(f"\n📊 周线行情 ({len(data)} 条):\n")
        print(f"{'日期':<12} {'开盘':<10} {'收盘':<10} {'最高':<10} {'最低':<10} {'成交量':<12}")
        print("-" * 70)
        for item in data[:20]:
            trade_date = item.get('trade_date', '-')
            open_price = item.get('open', 0)
            close = item.get('close', 0)
            high = item.get('high', 0)
            low = item.get('low', 0)
            vol = item.get('vol', 0)
            print(f"{trade_date:<12} {open_price:<10.2f} {close:<10.2f} {high:<10.2f} {low:<10.2f} {vol:<12}")
    
    elif args.command == 'monthly':
        data = get_monthly(ts_code=args.ts_code, trade_date=args.trade_date,
                          start_date=args.start_date, end_date=args.end_date)
        print(f"\n📊 月线行情 ({len(data)} 条):\n")
        print(f"{'日期':<12} {'开盘':<10} {'收盘':<10} {'最高':<10} {'最低':<10} {'成交量':<12}")
        print("-" * 70)
        for item in data[:20]:
            trade_date = item.get('trade_date', '-')
            open_price = item.get('open', 0)
            close = item.get('close', 0)
            high = item.get('high', 0)
            low = item.get('low', 0)
            vol = item.get('vol', 0)
            print(f"{trade_date:<12} {open_price:<10.2f} {close:<10.2f} {high:<10.2f} {low:<10.2f} {vol:<12}")
    
    elif args.command == 'realtime':
        data = get_realtime_quote(args.ts_code)
        if data:
            print(json.dumps(data, indent=2, ensure_ascii=False))
    
    elif args.command == 'company':
        data = get_stock_company()
        print(f"\n🏢 上市公司信息 ({len(data)} 家):\n")
        for item in data[:20]:
            print(f"{item.get('ts_code')}: {item.get('chairman', '-')} - {item.get('main_business', '-')[:30]}...")
    
    elif args.command == 'moneyflow':
        data = get_moneyflow(ts_code=args.ts_code, trade_date=args.trade_date)
        print_moneyflow(data)
    
    elif args.command == 'fut_basic':
        data = get_fut_basic(exchange=args.exchange)
        print_fut_basic(data)
    
    elif args.command == 'fut_daily':
        data = get_fut_daily(ts_code=args.ts_code, start_date=args.start_date, end_date=args.end_date)
        print_fut_daily(data)
    
    elif args.command == 'fut_holding':
        data = get_fut_holding(trade_date=args.trade_date, symbol=args.symbol)
        print(f"\n📊 期货持仓排名 ({len(data)} 条):\n")
        for item in data[:20]:
            print(f"{item.get('trade_date')} {item.get('symbol')} {item.get('broker')}: {item.get('vol')} 手")
    
    elif args.command == 'gdp':
        data = get_gdp()
        print(f"\n📈 GDP数据 ({len(data)} 条):\n")
        for item in data[:10]:
            print(f"{item.get('year')}年{item.get('quarter')}季度: GDP {item.get('gdp')}亿元, 增速 {item.get('gdp_yoy')}%")
    
    elif args.command == 'cpi':
        data = get_cpi()
        print(f"\n📊 CPI数据 ({len(data)} 条):\n")
        for item in data[:10]:
            print(f"{item.get('month')}: 全国 {item.get('nt_val')}%, 城市 {item.get('town_val')}%, 农村 {item.get('cnt_val')}%")
    
    elif args.command == 'ppi':
        data = get_ppi()
        print(f"\n🏭 PPI数据 ({len(data)} 条):\n")
        for item in data[:10]:
            print(f"{item.get('month')}: PPI {item.get('ppi')}%, 环比 {item.get('ppi_mp')}%")

if __name__ == '__main__':
    main()
