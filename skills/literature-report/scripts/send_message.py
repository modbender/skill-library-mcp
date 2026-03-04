#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息发送脚本
从配置文件读取用户ID
"""

import sys
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.config_loader import get_feishu_config

def send_message(message, target=None):
    """发送消息"""
    
    # 从配置文件读取飞书配置
    try:
        feishu_config = get_feishu_config()
        if target is None:
            target = feishu_config['target']
    except Exception as e:
        print(f"配置加载失败: {e}")
        return False
    
    print(f"发送消息到: {target}")
    print(f"消息: {message}")
    
    return True

if __name__ == '__main__':
    # 测试
    test_message = "测试消息"
    send_message(test_message)