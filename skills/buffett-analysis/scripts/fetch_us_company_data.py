#!/usr/bin/env python3
"""
美股公司基本面数据采集脚本
==========================
调用 us-market skill 统一入口，批量采集美股公司数据用于巴菲特分析。

用法：
    python3 fetch_us_company_data.py AAPL
    python3 fetch_us_company_data.py NVDA
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
US_MARKET_SCRIPT = os.path.join(SCRIPT_DIR, '..', '..', 'us-market', 'scripts', 'us_market_query.py')


def run_query(query_type, symbol, **extra_args):
    """调用 us_market_query.py 并读取输出"""
    cmd = [sys.executable, US_MARKET_SCRIPT, '--type', query_type, '--symbol', symbol]
    for k, v in extra_args.items():
        cmd.extend([f'--{k}', str(v)])
    
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return None
    
    # 读取输出文件
    safe_sym = symbol.upper().replace('^', 'IDX_').replace('/', '_')
    out_path = f"/tmp/us_market_{query_type}_{safe_sym}.json"
    if os.path.exists(out_path):
        with open(out_path, encoding='utf-8') as f:
            data = json.load(f)
            if 'error' not in data:
                return data
    return None


def fetch_us_company(ticker):
    """采集美股公司全面数据"""
    ticker = ticker.upper()
    result = {
        'symbol': ticker,
        'market': 'US',
        'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'errors': []
    }

    # ━━━ 1. 公司概况 ━━━
    print(f"[1/7] 公司概况...", flush=True)
    profile = run_query('profile', ticker)
    if profile:
        result['company_info'] = profile
        result['name'] = profile.get('name', ticker)
    else:
        result['company_info'] = {}
        result['name'] = ticker
        result['errors'].append('公司概况获取失败')

    # ━━━ 2. 实时行情 ━━━
    print(f"[2/7] 实时行情...", flush=True)
    quote = run_query('quote', ticker)
    if quote:
        result['snapshot'] = quote
    else:
        result['snapshot'] = {}
        result['errors'].append('行情获取失败')
    time.sleep(0.3)

    # ━━━ 3. 利润表 ━━━
    print(f"[3/7] 利润表...", flush=True)
    income = run_query('financials', ticker, statement='income')
    if income:
        result['income_statements'] = income.get('data', {})
        result['income_periods'] = income.get('periods', [])
    else:
        result['income_statements'] = {}
        result['income_periods'] = []
        result['errors'].append('利润表获取失败')
    time.sleep(0.3)

    # ━━━ 4. 资产负债表 ━━━
    print(f"[4/7] 资产负债表...", flush=True)
    balance = run_query('financials', ticker, statement='balance')
    if balance:
        result['balance_sheets'] = balance.get('data', {})
        result['balance_periods'] = balance.get('periods', [])
    else:
        result['balance_sheets'] = {}
        result['balance_periods'] = []
        result['errors'].append('资产负债表获取失败')
    time.sleep(0.3)

    # ━━━ 5. 现金流量表 ━━━
    print(f"[5/7] 现金流量表...", flush=True)
    cashflow = run_query('financials', ticker, statement='cashflow')
    if cashflow:
        result['cash_flows'] = cashflow.get('data', {})
        result['cashflow_periods'] = cashflow.get('periods', [])
    else:
        result['cash_flows'] = {}
        result['cashflow_periods'] = []
        result['errors'].append('现金流量表获取失败')
    time.sleep(0.3)

    # ━━━ 6. 分析师评级 ━━━
    print(f"[6/7] 分析师评级...", flush=True)
    analyst = run_query('analyst', ticker)
    if analyst:
        result['analyst'] = analyst
    else:
        result['analyst'] = {}

    # ━━━ 7. 分红记录 ━━━
    print(f"[7/7] 分红记录...", flush=True)
    dividends = run_query('dividends', ticker)
    if dividends:
        result['dividends'] = dividends.get('dividends', [])
    else:
        result['dividends'] = []

    return result


def main():
    if len(sys.argv) < 2:
        print("用法: python3 fetch_us_company_data.py <美股ticker>")
        print("示例: python3 fetch_us_company_data.py AAPL")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    print(f"━━━ 采集 {ticker} 基本面数据（美股）━━━", flush=True)

    data = fetch_us_company(ticker)

    out_path = f"/tmp/buffett_analysis_{ticker}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n━━━ 完成 ━━━")
    print(f"公司: {data['name']} ({ticker})")
    print(f"利润表: {len(data.get('income_periods', []))} 期")
    print(f"资产负债表: {len(data.get('balance_periods', []))} 期")
    print(f"现金流量表: {len(data.get('cashflow_periods', []))} 期")
    if data['errors']:
        print(f"⚠️ 错误: {data['errors']}")
    print(f"输出: {out_path}")


if __name__ == '__main__':
    main()
