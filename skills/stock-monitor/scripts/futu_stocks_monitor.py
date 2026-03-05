#!/usr/bin/env python3
"""
富途 OpenD 股票监控脚本
使用富途开放 API 获取实时行情
用法：python3 futu_stocks_monitor.py [config_file]
"""

import json
import os
import sys
from datetime import datetime
from futu import *

ALERT_THRESHOLD_2PCT = 0.02  # 2% 首次预警
ALERT_THRESHOLD_1PCT = 0.01  # 1% 续警波动

def get_config_path():
    if len(sys.argv) > 1:
        return sys.argv[1]
    return os.path.expanduser("~/.openclaw/workspace/memory/futu_stocks_config.json")

def get_state_path():
    return os.path.expanduser("~/.openclaw/workspace/memory/futu_stocks_alert.json")

def load_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    print(f"配置文件不存在：{config_path}")
    sys.exit(1)

def load_state():
    state_path = get_state_path()
    if os.path.exists(state_path):
        with open(state_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_state(state):
    state_path = get_state_path()
    os.makedirs(os.path.dirname(state_path), exist_ok=True)
    with open(state_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def get_realtime_quotes(quote_ctx, code_list):
    """获取实时行情"""
    ret_code, ret_data = quote_ctx.get_market_snapshot(code_list)
    if ret_code != RET_OK:
        print(f"获取行情失败：{ret_data}")
        return None
    return ret_data

def check_stock(name, stock_info, quote_ctx):
    """检查单只股票"""
    code = stock_info["code"]
    base = stock_info["base_price"]
    currency = stock_info["currency"]
    
    # 获取实时行情
    ret_code, ret_data = quote_ctx.get_market_snapshot([code])
    if ret_code != RET_OK:
        print(f"获取 {name} 行情失败：{ret_data}")
        return None
    
    if ret_data is None or ret_data.empty:
        print(f"{name} 无数据")
        return None
    
    row = ret_data.iloc[0]
    price = row['last_price']
    
    # 加载状态
    state = load_state()
    if name not in state:
        state[name] = {
            "alerted": False,
            "alert_date": None,
            "base_price": base,
            "last_alert_price": None
        }
    
    stock_state = state[name]
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 新的一天，重置基准价
    if stock_state.get("alert_date") != today:
        stock_state["alerted"] = False
        stock_state["alert_date"] = None
        stock_state["last_alert_price"] = None
        stock_state["base_price"] = price
    
    base_price = stock_state.get("base_price", base)
    change_pct = (price - base_price) / base_price * 100
    
    message = None
    
    # 首次预警：涨跌超 2%
    if not stock_state["alerted"]:
        if abs(change_pct) >= ALERT_THRESHOLD_2PCT * 100:
            if change_pct > 0:
                message = f"🚀 {name}预警：现价 {currency}{price:.2f}，涨{change_pct:.2f}% 首次超 2%"
            else:
                message = f"📉 {name}预警：现价 {currency}{price:.2f}，跌{abs(change_pct):.2f}% 首次超 2%"
            stock_state["alerted"] = True
            stock_state["alert_date"] = today
            stock_state["last_alert_price"] = price
    else:
        # 续警：相对上次 alert 价格再波动超 1%
        last_alert_price = stock_state.get("last_alert_price")
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
    futu_config = config.get("futu_config", {})
    stocks = config.get("stocks", {})
    
    if not stocks:
        print("请先配置股票列表")
        return
    
    # 连接富途 OpenD
    host = futu_config.get("host", "127.0.0.1")
    port = futu_config.get("port", 11111)
    
    quote_ctx = OpenQuoteContext(host=host, port=port)
    
    # 设置连接（如果需要解锁）
    unlock_password = futu_config.get("unlock_password", "")
    if unlock_password:
        ret = quote_ctx.unlock_market(password=unlock_password, unlock=True)
        if ret[0] != RET_OK:
            print(f"解锁失败：{ret[1]}")
            quote_ctx.close()
            return
    
    try:
        # 检查每只股票
        results = []
        for name, stock_info in stocks.items():
            result = check_stock(name, stock_info, quote_ctx)
            if result:
                results.append(result)
        
        if results:
            for r in results:
                print(r)
        else:
            print("无预警信息")
    
    finally:
        quote_ctx.close()

if __name__ == "__main__":
    main()
