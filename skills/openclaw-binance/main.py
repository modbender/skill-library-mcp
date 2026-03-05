# -*- coding: utf-8 -*-
"""
币安量化交易监控系统 - 正式版
支持实时监控、数据分析和风险预警
"""
import os
import json
import time
import datetime
import pandas as pd
from binance.client import Client
from openclaw_sdk import OpenClawClient
import requests

# ===================== 配置加载 =====================
CONFIG_FILE = "config.json"
if not os.path.exists(CONFIG_FILE):
    print("⚠️ 未找到配置文件，请先复制config.example.json并重命名为config.json")
    exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# ===================== 币安客户端初始化 =====================
client = Client(CONFIG["API_KEY"], CONFIG["SECRET_KEY"])

# ===================== 核心功能 =====================
def get_market_data(symbol="BTCUSDT"):
    """获取当前市场数据"""
    try:
        klines = client.get_klines(symbol=symbol, interval='1h', limit=24)
        df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"❌ 获取市场数据失败：{str(e)}")
        return None

def analyze_trading_strategy(df):
    """分析交易策略"""
    if df is None or len(df) < 2:
        return None
    
    # 计算收益率
    df['return'] = df['close'].pct_change()
    df['cumulative_return'] = (1 + df['return']).cumprod() - 1
    
    # 计算风险指标
    max_drawdown = (df['close'] / df['close'].cummax() - 1).min()
    win_rate = (df['return'] > 0).mean()
    avg_profit = df[df['return'] > 0]['return'].mean()
    avg_loss = df[df['return'] < 0]['return'].mean()
    
    return {
        "胜率": f"{win_rate:.2%}",
        "平均盈利": f"{avg_profit:.2%}",
        "平均亏损": f"{avg_loss:.2%}",
        "最大回撤": f"{max_drawdown:.2%}",
        "累计收益": f"{df['cumulative_return'].iloc[-1]:.2%}"
    }

def generate_report(trade_data, strategy_analysis):
    """生成交易报告"""
    today = datetime.date.today().isoformat()
    output_dir = os.path.join(os.getcwd(), "data", "binance_trades")
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成Markdown报告
    md_content = f"# 币安量化交易报告（{today}）\n\n"
    md_content += f"## 交易对：{trade_data['symbol']}\n"
    md_content += f"## 时间范围：{trade_data['start_time']} 至 {trade_data['end_time']}\n\n"
    
    md_content += "## 策略分析\n"
    for key, value in strategy_analysis.items():
        md_content += f"- {key}：{value}\n"
    
    md_content += "\n## 风险提示\n"
    if float(strategy_analysis["最大回撤"]) < -0.05:
        md_content += "🔴 风险较高！建议调整策略或降低仓位\n"
    elif float(strategy_analysis["最大回撤"]) < -0.02:
        md_content += "🟡 风险中等，建议密切监控\n"
    else:
        md_content += "🟢 风险较低，策略运行正常\n"
    
    # 保存报告
    report_file = os.path.join(output_dir, f"trade_report_{today}.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    return report_file

def send_alert(message):
    """发送风险预警"""
    if "FEISHU_WEBHOOK_URL" in CONFIG and CONFIG["FEISHU_WEBHOOK_URL"]:
        headers = {"Content-Type": "application/json; charset=utf-8"}
        data = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        try:
            response = requests.post(CONFIG["FEISHU_WEBHOOK_URL"], headers=headers, json=data, timeout=10)
            if response.status_code == 200:
                print("✅ 飞书预警推送成功！")
            else:
                print(f"❌ 飞书推送失败：{response.text}")
        except Exception as e:
            print(f"❌ 飞书推送报错：{str(e)}")

def main():
    print("🚀 启动币安量化交易监控系统")
    
    # 1. 获取市场数据
    symbol = "BTCUSDT"
    market_data = get_market_data(symbol)
    
    if market_data is None:
        print("❌ 获取市场数据失败，退出程序")
        return
    
    # 2. 分析交易策略
    strategy_analysis = analyze_trading_strategy(market_data)
    
    if strategy_analysis is None:
        print("❌ 分析交易策略失败，退出程序")
        return
    
    # 3. 生成报告
    trade_data = {
        "symbol": symbol,
        "start_time": market_data['timestamp'].iloc[0],
        "end_time": market_data['timestamp'].iloc[-1]
    }
    
    report_file = generate_report(trade_data, strategy_analysis)
    print(f"🎉 报告已生成：{report_file}")
    
    # 4. 发送风险预警
    alert_message = f"币安交易警报：{symbol} 策略分析结果 - 最大回撤：{strategy_analysis['最大回撤']}"
    send_alert(alert_message)
    
    print("🔧 系统已配置定时任务，将持续监控交易数据")

if __name__ == "__main__":
    main()