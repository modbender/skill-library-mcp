#!/usr/bin/env python3
"""
钉钉群消息自动处理器

集成到 OpenClaw 消息处理流程，实现收到@消息时自动路由到子 Agent
"""

import sys
import json
import re
import subprocess
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from dingtalk_command import parse_command, handle_command

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

LOG_FILE = Path("/tmp/auto-route-handler.log")

def log(message: str):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"
    
    # 写入日志
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # 输出到控制台
    print(log_entry.strip())

def handle_dingtalk_message(message: str, chat_type: str = "group", 
                           from_user: str = "", conversation_id: str = "") -> dict:
    """
    处理钉钉群消息
    
    Args:
        message: 消息内容
        chat_type: 聊天类型 (group/direct)
        from_user: 发送者
        conversation_id: 会话 ID
    
    Returns:
        dict: 处理结果
    """
    log(f"收到钉钉消息：{message[:50]}... (from: {from_user}, conv: {conversation_id})")
    
    # 检查是否包含@和命令
    if '@' not in message or '/' not in message:
        log("不是命令消息，跳过")
        return {'action': 'skip', 'reason': 'not_a_command'}
    
    # 解析命令
    result = handle_command(message, from_user, verbose=False)
    
    log(f"处理结果：{result.get('action', 'unknown')}")
    
    if result.get('action') == 'spawned_agent':
        log(f"✅ 已启动 Agent: {result.get('agent')}")
        return {
            'action': 'agent_spawned',
            'agent': result.get('agent'),
            'message': result.get('message', '')
        }
    elif result.get('action') == 'handle_directly':
        log("ℹ️  主 Session 处理")
        return {
            'action': 'handle_directly',
            'message': '简单任务，主 Session 处理'
        }
    else:
        log("❌ 未识别到命令")
        return {
            'action': 'not_command',
            'message': result.get('message', '未识别到命令')
        }

def main():
    """命令行入口 - 用于测试"""
    if len(sys.argv) < 2:
        print("用法：python3 message-handler.py '<消息内容>' [发送者] [会话 ID]")
        sys.exit(1)
    
    message = sys.argv[1]
    from_user = sys.argv[2] if len(sys.argv) > 2 else "未知用户"
    conversation_id = sys.argv[3] if len(sys.argv) > 3 else ""
    
    result = handle_dingtalk_message(message, "group", from_user, conversation_id)
    
    print(f"\n{Colors.GREEN}处理结果：{Colors.NC}")
    print(f"  动作：{result['action']}")
    if result.get('agent'):
        print(f"  Agent: {result['agent']}")
    print(f"  回复：{result.get('message', '')}")

if __name__ == '__main__':
    main()
