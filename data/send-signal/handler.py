import json
import requests

# 【重要】把这里改成你自己编的暗号，比如 "my_robot_888"
MY_UUID = "530032201"

def handler(action: str, symbol: str, price: float, reason: str):
    """
    向 FMZ 发送交易信号。
    
    Args:
        action (str): 动作，例如 'buy', 'sell'
        symbol (str): 交易对，例如 'BTC_USDT'
        price (float): 价格
        reason (str): 原因
    """
    # FMZ 的频道 API 地址
    url = "https://www.fmz.com/api/v1/channel"
    
    # 构造信号内容
    signal_data = {
        "uuid": MY_UUID,
        "action": action,
        "symbol": symbol,
        "price": price,
        "reason": reason
    }
    
    # 包装成 FMZ 需要的格式 (cmd字段)
    payload = {
        "node_id": 0,  # 0代表广播给所有机器人
        "cmd": json.dumps(signal_data) 
    }

    try:
        # 发送请求
        # 注意：如果你的 OpenClaw 环境没有 requests 库，可能需要其他方式
        # 但标准 Python 环境通常支持
        resp = requests.post(url, json=payload, timeout=5)
        return f"信号发送成功: {action} {symbol}, 状态码: {resp.status_code}"
    except Exception as e:
        return f"信号发送失败: {str(e)}"
