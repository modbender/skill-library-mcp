#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版资金日报数据提取器 - 提取完整信息
"""

import pandas as pd
import json
from pathlib import Path
from datetime import datetime

def extract_enhanced_fund_data(excel_path):
    """提取Excel文件中的完整资金信息"""
    result = {
        'file_info': {
            'filename': Path(excel_path).name,
            'extracted_at': datetime.now().isoformat()
        },
        'summary': {},
        'bank_accounts': {},
        'transaction_details': [],
        'income_breakdown': {},
        'expense_breakdown': {}
    }
    
    try:
        # 1. 提取日报表汇总信息
        df_summary = pd.read_excel(excel_path, sheet_name='日报表')
        
        # 提取基础4字段
        for idx, row in df_summary.iterrows():
            if '昨日结余' in str(row.iloc[2]):
                result['summary']['yesterday_balance'] = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            elif '本日结余' in str(row.iloc[2]):
                result['summary']['today_balance'] = float(row.iloc[4]) if pd.notna(row.iloc[4]) else 0
            elif '资金流入合计' in str(row.iloc[1]):
                result['summary']['total_inflow'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            elif '资金流出合计' in str(row.iloc[1]):
                result['summary']['total_outflow'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            
            # 提取收入分类
            if '大金额客户收入' in str(row.iloc[2]):
                result['income_breakdown']['large_customer'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            elif '其他客户收入' in str(row.iloc[2]):
                result['income_breakdown']['other_income'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            
            # 提取支出分类
            if '大金额支出' in str(row.iloc[2]):
                result['expense_breakdown']['large_expense'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
            elif '其他供应商' in str(row.iloc[2]):
                result['expense_breakdown']['other_expense'] = float(row.iloc[5]) if pd.notna(row.iloc[5]) else 0
        
        # 2. 提取银行账户汇总
        df_banks = pd.read_excel(excel_path, sheet_name='日汇总')
        
        # 清理数据，只保留有意义的银行账户行
        df_banks_clean = df_banks[
            (df_banks['公司名称'].notna()) & 
            (df_banks['公司名称'] != '金额总计') &
            (df_banks['期末余额'].notna()) &
            (df_banks['期末余额'] != 0)
        ].copy()
        
        for idx, row in df_banks_clean.iterrows():
            bank_name = str(row['公司名称'])
            if bank_name and bank_name != 'nan':
                result['bank_accounts'][bank_name] = {
                    'opening_balance': float(row['期初余额']) if pd.notna(row['期初余额']) else 0,
                    'income': float(row['收入']) if pd.notna(row['收入']) else 0,
                    'expense': float(row['支出']) if pd.notna(row['支出']) else 0,
                    'net_income': float(row['净收入']) if pd.notna(row['净收入']) else 0,
                    'closing_balance': float(row['期末余额']) if pd.notna(row['期末余额']) else 0
                }
        
        # 3. 提取交易明细
        df_details = pd.read_excel(excel_path, sheet_name='日明细')
        
        for idx, row in df_details.iterrows():
            if pd.notna(row['公司名称']) and str(row['公司名称']) != 'nan':
                detail = {
                    'bank_account': str(row['所属公司']) if pd.notna(row['所属公司']) else '',
                    'date': str(row['日期']) if pd.notna(row['日期']) else '',
                    'counterparty': str(row['公司名称']),
                    'income_amount': float(row['收款金额']) if pd.notna(row['收款金额']) else 0,
                    'expense_amount': float(row['支出金额']) if pd.notna(row['支出金额']) else 0
                }
                result['transaction_details'].append(detail)
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result

def save_enhanced_data(data, output_file='fund_enhanced_data.json'):
    """保存增强数据到JSON文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✅ 增强数据已保存到: {output_file}")

def print_summary(data):
    """打印数据摘要"""
    print("📊 资金日报增强分析结果")
    print("=" * 50)
    
    if 'error' in data:
        print(f"❌ 错误: {data['error']}")
        return
    
    print(f"📁 文件: {data['file_info']['filename']}")
    print(f"⏰ 提取时间: {data['file_info']['extracted_at']}")
    print()
    
    # 基础汇总
    summary = data['summary']
    print("💰 资金汇总:")
    print(f"   昨日结余: {summary.get('yesterday_balance', 0):,.2f} 元")
    print(f"   本日结余: {summary.get('today_balance', 0):,.2f} 元")
    print(f"   资金流入: {summary.get('total_inflow', 0):,.2f} 元")
    print(f"   资金流出: {summary.get('total_outflow', 0):,.2f} 元")
    print()
    
    # 收支分类
    if data['income_breakdown']:
        print("📈 收入分类:")
        for category, amount in data['income_breakdown'].items():
            print(f"   {category}: {amount:,.2f} 元")
        print()
    
    if data['expense_breakdown']:
        print("📉 支出分类:")
        for category, amount in data['expense_breakdown'].items():
            print(f"   {category}: {amount:,.2f} 元")
        print()
    
    # 银行账户
    print("🏦 银行账户分布:")
    for bank, info in data['bank_accounts'].items():
        print(f"   {bank}: {info['closing_balance']:,.2f} 元")
        if info['income'] > 0 or info['expense'] > 0:
            print(f"      (收入: {info['income']:,.2f}, 支出: {info['expense']:,.2f})")
    print()
    
    # 交易明细统计
    details = data['transaction_details']
    print(f"🔍 交易明细: 共{len(details)}笔")
    
    # 按交易对手方汇总
    counterparty_summary = {}
    for detail in details:
        cp = detail['counterparty']
        if cp not in counterparty_summary:
            counterparty_summary[cp] = {'income': 0, 'expense': 0}
        counterparty_summary[cp]['income'] += detail['income_amount']
        counterparty_summary[cp]['expense'] += detail['expense_amount']
    
    print("   主要交易对手方:")
    for cp, amounts in sorted(counterparty_summary.items(), 
                            key=lambda x: x[1]['income'] + x[1]['expense'], reverse=True)[:5]:
        total = amounts['income'] + amounts['expense']
        print(f"     {cp}: {total:,.2f} 元")

def main():
    # 选择最新的Excel文件
    excel_files = list(Path("fund_attachments").glob("*.xlsx"))
    
    if not excel_files:
        print("❌ 未找到Excel文件")
        return
    
    # 选择最新文件
    latest_file = max(excel_files, key=lambda x: x.stat().st_mtime)
    
    print(f"🎯 分析文件: {latest_file.name}")
    print()
    
    # 提取增强数据
    enhanced_data = extract_enhanced_fund_data(latest_file)
    
    # 显示摘要
    print_summary(enhanced_data)
    
    # 保存到JSON文件
    save_enhanced_data(enhanced_data)
    
    print(f"\n🎉 分析完成！发现了比原有4字段更丰富的信息：")
    print(f"   • {len(enhanced_data.get('bank_accounts', {}))} 个银行账户")
    print(f"   • {len(enhanced_data.get('transaction_details', []))} 笔交易明细")
    print(f"   • {len(enhanced_data.get('income_breakdown', {}))} 类收入分类")
    print(f"   • {len(enhanced_data.get('expense_breakdown', {}))} 类支出分类")

if __name__ == "__main__":
    main()