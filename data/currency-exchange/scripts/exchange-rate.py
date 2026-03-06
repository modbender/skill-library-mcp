#!/usr/bin/env python3
"""
Exchange Rate Tool
货币汇率查询和转换
使用 exchangerate-api.com 免费 API（无需 API Key）
"""

import sys
import json
import urllib.request
import urllib.error
from urllib.parse import quote

API_BASE = "https://api.exchangerate-api.com/v4/latest"

def fetch_json(url, timeout=15):
    """获取 JSON 数据"""
    try:
        req = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (OpenClaw exchange-rate skill)"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        if e.code == 429:
            return {"error": "API 请求过于频繁，请稍后再试"}
        return {"error": f"HTTP 错误: {e.code}"}
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}

def get_rates(base_currency="USD"):
    """获取汇率数据"""
    url = f"{API_BASE}/{base_currency.upper()}"
    return fetch_json(url)

def convert_currency(amount, from_currency, to_currency):
    """转换货币"""
    data = get_rates(from_currency)
    
    if "error" in data:
        return data
    
    rates = data.get("rates", {})
    to_currency = to_currency.upper()
    
    if to_currency not in rates:
        return {"error": f"不支持的货币代码: {to_currency}"}
    
    rate = rates[to_currency]
    result = amount * rate
    
    return {
        "amount": amount,
        "from": from_currency.upper(),
        "to": to_currency,
        "rate": rate,
        "result": result,
        "date": data.get("date", "N/A")
    }

def get_supported_currencies():
    """获取支持的货币列表"""
    data = get_rates("USD")
    if "error" in data:
        return []
    return sorted(data.get("rates", {}).keys())

def format_currency(amount, currency):
    """格式化货币金额"""
    symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥",
        "CNY": "¥", "KRW": "₩", "INR": "₹", "RUB": "₽",
        "BTC": "₿", "ETH": "Ξ"
    }
    symbol = symbols.get(currency, currency)
    
    if amount >= 1000000:
        return f"{symbol}{amount:,.2f}"
    elif amount >= 1:
        return f"{symbol}{amount:,.4f}"
    else:
        return f"{symbol}{amount:.8f}"

def main():
    if len(sys.argv) < 2:
        print("用法: exchange-rate <command> [args]")
        print("")
        print("命令:")
        print("  exchange-rate convert <金额> <从货币> <到货币>  货币转换")
        print("  exchange-rate rate <基准货币>                  查看汇率表")
        print("  exchange-rate list                             列出支持的货币")
        print("")
        print("示例:")
        print("  exchange-rate convert 100 USD CNY     100美元转人民币")
        print("  exchange-rate convert 50 EUR USD      50欧元转美元")
        print("  exchange-rate rate USD                以美元为基准的汇率")
        print("  exchange-rate rate CNY                以人民币为基准的汇率")
        print("")
        print("常见货币代码:")
        print("  USD 美元 | CNY 人民币 | EUR 欧元 | GBP 英镑")
        print("  JPY 日元 | KRW 韩元 | HKD 港币 | TWD 新台币")
        print("  AUD 澳元 | CAD 加元 | CHF 瑞士法郎 | SGD 新加坡元")
        return 1

    command = sys.argv[1]

    if command == "convert":
        if len(sys.argv) < 5:
            print("错误: 请提供金额、源货币和目标货币")
            print("用法: exchange-rate convert <金额> <从货币> <到货币>")
            return 1
        
        try:
            amount = float(sys.argv[2])
        except ValueError:
            print("错误: 金额必须是数字")
            return 1
        
        from_currency = sys.argv[3].upper()
        to_currency = sys.argv[4].upper()
        
        result = convert_currency(amount, from_currency, to_currency)
        
        if "error" in result:
            print(f"错误: {result['error']}")
            return 1
        
        print(f"\n💱 汇率转换")
        print(f"{format_currency(result['amount'], result['from'])} = {format_currency(result['result'], result['to'])}")
        print(f"汇率: 1 {result['from']} = {result['rate']:.6f} {result['to']}")
        print(f"日期: {result['date']}")
        print()

    elif command == "rate":
        base = sys.argv[2].upper() if len(sys.argv) > 2 else "USD"
        
        data = get_rates(base)
        
        if "error" in data:
            print(f"错误: {data['error']}")
            return 1
        
        rates = data.get("rates", {})
        date = data.get("date", "N/A")
        
        # 显示主要货币
        main_currencies = ["USD", "EUR", "GBP", "JPY", "CNY", "KRW", "HKD", "AUD", "CAD", "CHF", "SGD", "INR", "RUB", "BRL", "MXN"]
        
        print(f"\n📊 汇率表 (基准: {base})")
        print(f"日期: {date}\n")
        print(f"{'货币':<8} {'汇率':<15} {'货币':<8} {'汇率':<15}")
        print("-" * 50)
        
        # 两列显示
        for i in range(0, len(main_currencies), 2):
            curr1 = main_currencies[i]
            rate1 = rates.get(curr1, 0)
            
            curr2 = main_currencies[i+1] if i+1 < len(main_currencies) else ""
            rate2 = rates.get(curr2, 0) if curr2 else 0
            
            if curr1 == base:
                line1 = f"{curr1:<8} {'1.000000':<15}"
            else:
                line1 = f"{curr1:<8} {rate1:<15.6f}"
            
            if curr2:
                if curr2 == base:
                    line2 = f"{curr2:<8} {'1.000000':<15}"
                else:
                    line2 = f"{curr2:<8} {rate2:<15.6f}"
            else:
                line2 = ""
            
            print(f"{line1} {line2}")
        print()

    elif command == "list":
        currencies = get_supported_currencies()
        
        if not currencies:
            print("错误: 无法获取货币列表")
            return 1
        
        print(f"\n🌍 支持的货币 ({len(currencies)} 种)\n")
        
        # 每行显示6个
        for i in range(0, len(currencies), 6):
            row = currencies[i:i+6]
            print("  ".join(f"{c:<6}" for c in row))
        print()

    else:
        print(f"未知命令: {command}")
        print("使用 'exchange-rate' 查看帮助")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
