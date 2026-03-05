#!/usr/bin/env python3
"""
Hello World 技能 - Python版本
从环境变量 HELLO_USERNAME 读取用户名并输出问候语
"""

import os
import sys
from datetime import datetime

def get_greeting_by_time():
    """根据当前时间返回相应的问候语"""
    current_hour = datetime.now().hour
    
    if current_hour < 12:
        return "Good morning!"
    elif current_hour < 18:
        return "Good afternoon!"
    else:
        return "Good evening!"

def main():
    """主函数"""
    # 检查环境变量 - 首先尝试HELLO_USERNAME，然后尝试apiKey
    username = os.getenv("HELLO_USERNAME")
    
    # 如果HELLO_USERNAME不存在，尝试从apiKey环境变量读取
    if not username:
        username = os.getenv("apiKey")
    
    if not username:
        print("错误: 请配置用户名")
        print("在OpenClaw技能配置界面中设置apiKey字段作为用户名")
        sys.exit(1)
    
    # 输出基本问候
    print(f"Hello, {username}!")
    
    # 输出时间相关的问候
    time_greeting = get_greeting_by_time()
    print(time_greeting)
    
    # 可选：输出调试信息（仅在调试模式下）
    if os.getenv("HELLO_DEBUG", "false").lower() == "true":
        print(f"\n[调试信息]")
        print(f"用户名: {username}")
        print(f"环境变量 HELLO_USERNAME: {os.getenv('HELLO_USERNAME')}")
        print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()