#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书推送脚本
从配置文件读取用户ID
"""

import requests
import json
from pathlib import Path
import sys

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_loader import get_feishu_config

def send_to_feishu(message, target=None):
    """发送消息到飞书"""
    
    # 从配置文件读取飞书配置
    try:
        feishu_config = get_feishu_config()
        if not feishu_config['enabled']:
            print("飞书推送未启用")
            return False
        
        if target is None:
            target = feishu_config['target']
    except Exception as e:
        print(f"飞书配置加载失败: {e}")
        return False
    
    # 检查用户ID是否已配置
    if target == "YOUR_USER_ID_HERE":
        print("请先在config.yaml中配置飞书用户ID")
        return False
    
    # 发送消息
    # 注意：这里需要替换为实际的飞书API调用
    print(f"发送消息到飞书: {target}")
    print(f"消息内容: {message[:100]}...")
    
    return True

if __name__ == '__main__':
    # 测试
    test_message = "这是一条测试消息"
    send_to_feishu(test_message)