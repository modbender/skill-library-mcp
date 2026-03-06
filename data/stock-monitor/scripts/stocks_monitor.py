#!/usr/bin/env python3
"""
多股票股价监控脚本
使用 Yahoo Finance
用法：python3 stocks_monitor.py [config_file]
默认读取 ~/.openclaw/workspace/memory/stocks_config.json
"""

import json
import os
import sys
from datetime import datetime
import urllib.request

ALERT_THRESHOLD_2PCT = 0.02  # 2% 首次预警
ALERT_THRESHOLD_1PCT = 0.01  # 1% 续警波动

def get_config_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.expanduser("~/.openclaw/workspace/memory/stocks_config.json")

def get_state_path():
    return os.path.expanduser("~/.openclaw/workspace/memory/stocks_alert.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {
        "stocks": {
            "贵州茅台": {"symbol": "600519.SS", "base_price": 1600.0, "currency": "¥"},
            "腾讯控股": {"symbol": "0700.HK", "base_price": 512.0, "currency": "HK$"},
            "拼多多": {"symbol": "PDD", "base_price": 120.0, "currency": "$"}
        }
    }

def get_price(symbol):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=5m&range=1d"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
        if "chart" in data and "result" in data["chart"] and data["chart"]["result"]:
            result = data["chart"]["result"][0]
            meta = result.get("meta", {})
            price = meta.get("regularMarketPrice")
            if price:
                return float(price)
        return None
    except Exception as e:
        print(f"获取 {symbol} 股价失败：{e}")
        return None

def load_state():
    state_path = get_state_path()
    if os.path.exists(state_path):
        with open(state_path, 'r') as f:
            return json.load(f)
    return {}

def save_state(state):
    state_path = get_state_path()
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w') as f:
        json.dump(state, f, indent=2)

def is_cn_stock(symbol):
    """判断是否是 A 股（.SS 或 .SZ 后缀）"""
    return symbol.endswith(".SS") or symbol.endswith(".SZ")

def is_hk_stock(symbol):
    """判断是否是港股（.HK 后缀）"""
    return symbol.endswith(".HK")

def is_cn_hk_market_open():
    """判断 A 股/港股是否已开盘（9:30 后）"""
    now = datetime.now()
    # A 股/港股开盘时间：9:30 AM (北京时间)
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    return now >= market_open_time

def check_stock(name, config):
    symbol = config["symbol"]
    base = config["base_price"]
    currency = config["currency"]
    
    # A 股/港股 9:30 前跳过（竞价阶段波动大）
    if (is_cn_stock(symbol) or is_hk_stock(symbol)) and not is_cn_hk_market_open():
        return None
    
    price = get_price(symbol)
    if not price:
        return None
    
    state = load_state()
    if name not in state:
        state[name] = {
            "alerted": False,
            "alert_date": None,
            "base_price": base,
            "last_alert_price": None
        }
    
    stock_state = state[name]
    alerted = stock_state.get("alerted", False)
    alert_date = stock_state.get("alert_date")
    base_price = stock_state.get("base_price", base)
    last_alert_price = stock_state.get("last_alert_price")
    
    today = datetime.now().strftime("%Y-%m-%d")
    change_pct = (price - base_price) / base_price * 100
    
    message = None
    
    # 新的一天，重置
    if alert_date != today:
        stock_state["alerted"] = False
        stock_state["alert_date"] = None
        stock_state["last_alert_price"] = None
        stock_state["base_price"] = price
    
    # 首次预警：涨跌超 2%
    if not stock_state["alerted"]:
        alert_2pct_up = base_price * (1 + ALERT_THRESHOLD_2PCT)
        alert_2pct_down = base_price * (1 - ALERT_THRESHOLD_2PCT)
        
        if price >= alert_2pct_up:
            message = f"🚀 {name}预警：现价 {currency}{price:.2f}，涨{change_pct:.2f}% 首次超 2%"
            stock_state["alerted"] = True
            stock_state["alert_date"] = today
            stock_state["last_alert_price"] = price
        elif price <= alert_2pct_down:
            message = f"📉 {name}预警：现价 {currency}{price:.2f}，跌{abs(change_pct):.2f}% 首次超 2%"
            stock_state["alerted"] = True
            stock_state["alert_date"] = today
            stock_state["last_alert_price"] = price
    else:
        # 续警：相对上次 alert 价格再波动超 1%
        if last_alert_price:
            change_from_last = (price - last_alert_price) / last_alert_price * 100
            
            if abs(change_from_last) >= ALERT_THRESHOLD_1PCT * 100:
                if change_from_last > 0:
                    message = f"📈 {name}续警：现价 {currency}{price:.2f}，较上次涨{change_from_last:.2f}%"
                else:
                    message = f"📉 {name}续警：现价 {currency}{price:.2f}，较上次跌{abs(change_from_last):.2f}%"
                stock_state["last_alert_price"] = price
    
    stock_state["current_price"] = price
    stock_state["last_check"] = today
    save_state(state)
    
    return message

def main():
    config = load_config()
    stocks = config.get("stocks", {})
    
    if not stocks:
        print("请先配置股票列表")
        return
    
    results = []
    for name, cfg in stocks.items():
        result = check_stock(name, cfg)
        if result:
            results.append(result)
    
    if not results:
        return
    
    for r in results:
        print(r)

if __name__ == "__main__":
    main()
