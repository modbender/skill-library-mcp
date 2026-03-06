#!/usr/bin/env python3
"""
使用真实API密钥运行完整的InvestmentTracker技能
"""

import json
import os
import sys
import tempfile
import subprocess

# 创建临时配置文件
temp_config = {
    "mcpServers": {
        "investmenttracker": {
            "url": "https://claw.investtracker.ai/mcp",
            "headers": {
                "Authorization": "Bearer it_live_IGWL2ZjlCHmxHCHMV_AFU87xz0CszLrJTCvfzs5gAjo",
                "Accept": "application/json, text/event-stream",
                "Content-Type": "application/json"
            },
            "timeout": 30,
            "retry_attempts": 3,
            "cache_enabled": True,
            "cache_ttl": 300
        }
    },
    "features": {
        "portfolio_management": True,
        "transaction_history": True,
        "performance_analytics": True,
        "market_data": True,
        "price_alerts": False,
        "tax_reporting": False
    },
    "display": {
        "currency": "USD",
        "date_format": "YYYY-MM-DD",
        "number_format": "en-US",
        "theme": "light"
    },
    "notifications": {
        "daily_summary": False,
        "price_change_alerts": False,
        "portfolio_rebalancing": False,
        "market_news": False
    },
    "integrations": {
        "feishu": {
            "enabled": False,
            "webhook_url": ""
        },
        "telegram": {
            "enabled": False,
            "bot_token": "",
            "chat_id": ""
        }
    }
}

# 创建临时文件
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(temp_config, f, indent=2)
    temp_config_path = f.name

print(f"🔧 使用临时配置文件: {temp_config_path}")
print(f"🔑 API密钥: it_live_IGWL2ZjlCHmxHCHMV_AFU87xz0CszLrJTCvfzs5gAjo")
print(f"🌐 MCP URL: https://claw.investtracker.ai/mcp")
print("=" * 60)

try:
    # 备份原始配置
    original_config_path = os.path.join(os.path.dirname(__file__), "config.json")
    backup_config_path = os.path.join(os.path.dirname(__file__), "config.json.backup")
    
    if os.path.exists(original_config_path):
        with open(original_config_path, 'r') as f:
            original_config = f.read()
        with open(backup_config_path, 'w') as f:
            f.write(original_config)
        print("✅ 已备份原始配置文件")
    
    # 使用临时配置替换原始配置
    with open(original_config_path, 'w') as f:
        json.dump(temp_config, f, indent=2)
    print("✅ 已更新配置文件使用真实API密钥")
    
    print()
    print("=" * 60)
    print("运行InvestmentTracker技能...")
    print("=" * 60)
    
    # 运行技能
    result = subprocess.run(
        [sys.executable, "InvestmentTracker_skill.py", "all", "--mode", "api"],
        capture_output=True,
        text=True,
        timeout=45
    )
    
    print(result.stdout)
    
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    print("=" * 60)
    print("技能运行完成")
    
finally:
    # 恢复原始配置
    if os.path.exists(backup_config_path):
        with open(backup_config_path, 'r') as f:
            backup_config = f.read()
        with open(original_config_path, 'w') as f:
            f.write(backup_config)
        os.remove(backup_config_path)
        print("✅ 已恢复原始配置文件")
    
    # 清理临时文件
    if os.path.exists(temp_config_path):
        os.remove(temp_config_path)
        print("✅ 已清理临时配置文件")