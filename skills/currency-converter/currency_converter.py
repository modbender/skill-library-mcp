#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
汇率转换器脚本
"""

import requests
import json
import sys
import argparse
from datetime import datetime

# 支持的货币列表及其中文名称
SUPPORTED_CURRENCIES = {
    'CNY': '人民币',
    'USD': '美元',
    'EUR': '欧元',
    'GBP': '英镑',
    'JPY': '日元',
    'AUD': '澳元',
    'CAD': '加元',
    'CHF': '瑞士法郎',
    'HKD': '港币',
    'NZD': '纽元',
    'SGD': '新加坡元',
    'KRW': '韩元',
    'INR': '印度卢比',
    'RUB': '俄罗斯卢布',
    'BRL': '巴西雷亚尔',
    'ZAR': '南非兰特'
}

# 货币代码映射（中英文转标准代码）
CURRENCY_NAME_MAP = {
    # 中文映射
    '人民币': 'CNY', '元': 'CNY', '块': 'CNY',
    '美元': 'USD', '美金': 'USD',
    '欧元': 'EUR',
    '英镑': 'GBP',
    '日元': 'JPY', '日圆': 'JPY',
    '澳元': 'AUD', '澳大利亚元': 'AUD',
    '加元': 'CAD', '加拿大元': 'CAD',
    '瑞士法郎': 'CHF',
    '港币': 'HKD', '港元': 'HKD',
    '纽元': 'NZD', '新西兰元': 'NZD',
    '新加坡元': 'SGD',
    '韩元': 'KRW', '韩币': 'KRW',
    '印度卢比': 'INR',
    '俄罗斯卢布': 'RUB',
    '巴西雷亚尔': 'BRL',
    '南非兰特': 'ZAR',
    
    # 英文映射（常见写法）
    'cny': 'CNY', 'rmb': 'CNY', 'yuan': 'CNY',
    'usd': 'USD', 'dollar': 'USD', 'us dollar': 'USD',
    'eur': 'EUR', 'euro': 'EUR',
    'gbp': 'GBP', 'pound': 'GBP',
    'jpy': 'JPY', 'yen': 'JPY',
    'aud': 'AUD', 'australian dollar': 'AUD',
    'cad': 'CAD', 'canadian dollar': 'CAD',
    'chf': 'CHF', 'swiss franc': 'CHF',
    'hkd': 'HKD', 'hong kong dollar': 'HKD',
    'nzd': 'NZD', 'new zealand dollar': 'NZD',
    'sgd': 'SGD', 'singapore dollar': 'SGD',
    'krw': 'KRW', 'won': 'KRW',
    'inr': 'INR', 'indian rupee': 'INR',
    'rub': 'RUB', 'russian ruble': 'RUB',
    'brl': 'BRL', 'brazilian real': 'BRL',
    'zar': 'ZAR', 'south african rand': 'ZAR'
}

def normalize_currency_code(currency_input):
    """
    将用户输入的货币名称标准化为三位代码
    """
    # 去除首尾空格并转为小写（用于查找）
    currency_lower = currency_input.strip().lower()
    
    # 直接检查是否是有效的三位代码
    if currency_lower.upper() in SUPPORTED_CURRENCIES:
        return currency_lower.upper()
    
    # 在映射表中查找
    if currency_lower in CURRENCY_NAME_MAP:
        return CURRENCY_NAME_MAP[currency_lower]
    
    # 检查是否包含在映射键中（处理多词输入）
    for key, code in CURRENCY_NAME_MAP.items():
        if key in currency_lower:
            return code
    
    return None

def get_exchange_rate(from_currency, to_currency):
    """
    从API获取实时汇率
    使用免费的 exchangerate-api.com
    """
    try:
        # 使用免费API（不需要API密钥）
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'rates' in data and to_currency in data['rates']:
            rate = data['rates'][to_currency]
            update_time = datetime.fromtimestamp(data.get('date', 0))
            return {
                'success': True,
                'rate': rate,
                'from_currency': from_currency,
                'to_currency': to_currency,
                'update_time': update_time.strftime('%Y-%m-%d %H:%M:%S'),
                'base': data.get('base', from_currency)
            }
        else:
            return {
                'success': False,
                'error': f'无法获取 {to_currency} 的汇率'
            }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'error': '连接超时，请稍后重试'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'error': '网络连接失败，请检查网络'
        }
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f'API请求失败: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'发生未知错误: {str(e)}'
        }

def format_currency_amount(amount, currency_code):
    """
    格式化货币金额显示
    """
    if currency_code in ['JPY', 'KRW']:  # 日元、韩元不需要小数
        return f"{amount:,.0f}"
    else:
        return f"{amount:,.2f}"

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='汇率转换工具')
    parser.add_argument('--amount', type=float, required=True, help='要转换的金额')
    parser.add_argument('--from', dest='from_currency', required=True, help='原始货币')
    parser.add_argument('--to', dest='to_currency', required=True, help='目标货币')
    
    args = parser.parse_args()
    
    # 验证金额
    if args.amount <= 0:
        result = {
            'success': False,
            'error': '金额必须大于0'
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    
    # 标准化货币代码
    from_code = normalize_currency_code(args.from_currency)
    to_code = normalize_currency_code(args.to_currency)
    
    # 验证货币是否支持
    if not from_code:
        result = {
            'success': False,
            'error': f'不支持原始货币: {args.from_currency}',
            'supported_currencies': list(SUPPORTED_CURRENCIES.keys())
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    
    if not to_code:
        result = {
            'success': False,
            'error': f'不支持目标货币: {args.to_currency}',
            'supported_currencies': list(SUPPORTED_CURRENCIES.keys())
        }
        print(json.dumps(result, ensure_ascii=False))
        return
    
    # 获取汇率
    exchange_data = get_exchange_rate(from_code, to_code)
    
    if exchange_data['success']:
        # 计算转换后的金额
        rate = exchange_data['rate']
        converted_amount = args.amount * rate
        
        # 准备返回结果
        result = {
            'success': True,
            'original_amount': args.amount,
            'original_currency': from_code,
            'original_currency_name': SUPPORTED_CURRENCIES.get(from_code, from_code),
            'converted_amount': converted_amount,
            'target_currency': to_code,
            'target_currency_name': SUPPORTED_CURRENCIES.get(to_code, to_code),
            'exchange_rate': rate,
            'update_time': exchange_data['update_time'],
            'formatted_original': format_currency_amount(args.amount, from_code),
            'formatted_converted': format_currency_amount(converted_amount, to_code)
        }
    else:
        result = exchange_data
    
    # 输出JSON结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()