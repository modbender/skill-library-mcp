#!/usr/bin/env python3
"""
钉钉消息自动触发器

集成到主 Session 消息处理流程，实现收到钉钉群@消息时自动路由到子 Agent
"""

import sys
import re
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from dingtalk_command import handle_command

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def check_command(message: str, chat_type: str = "", from_user: str = "") -> dict:
    """
    检查消息是否以命令开头，如果是则返回路由信息
    触发条件（严格模式）：
    1. 消息开头必须是 /coder 等命令
    2. 或 @名字 + 命令开头
    
    Args:
        message: 消息内容
        chat_type: 聊天类型 (dingtalk-group/dingtalk-direct/tui/other)
        from_user: 发送者
    
    Returns:
        dict: {
            'is_command': bool,
            'should_route': bool,
            'agent': str,
            'task': str,
            'message': str  # 回复消息
        }
    """
    # 可用命令列表
    COMMANDS = ['/coder', '/code', '/writer', '/write', '/analyze', '/analysis', 
                '/research', '/review', '/devops', '/ops', '/auto']
    
    # 清理消息：去掉开头的@名字
    clean_message = re.sub(r'@[^\s]+', '', message).strip()
    
    # 严格匹配：必须开头是命令
    has_command = any(clean_message.lower().startswith(cmd) for cmd in COMMANDS)
    
    if not has_command:
        return {
            'is_command': False,
            'should_route': False
        }
    
    # 调用命令处理器
    result = handle_command(message, from_user, verbose=False)
    
    if result.get('action') == 'spawned_agent':
        return {
            'is_command': True,
            'should_route': True,
            'agent': result.get('agent'),
            'task': result.get('message', ''),
            'handled_by': result.get('handled_by', ''),
            'message': f"{result.get('message', '')}\n\n─────────────────────\n🤖 处理者：{result.get('handled_by', '未知')}"
        }
    elif result.get('action') == 'handle_directly':
        return {
            'is_command': True,
            'should_route': False,
            'agent': None,
            'message': '简单任务，主 Session 处理'
        }
    else:
        return {
            'is_command': False,
            'should_route': False
        }

def main():
    """命令行测试"""
    if len(sys.argv) < 2:
        print("用法：python3 auto-trigger.py '<消息内容>' [聊天类型] [发送者]")
        print("\n示例：")
        print("  python3 auto-trigger.py '/coder 写代码'")
        print("  python3 auto-trigger.py '@小牛马 /coder 写代码'")
        print("  python3 auto-trigger.py '请帮我 /coder 写个脚本'")
        print("  python3 auto-trigger.py '/writer 写周报'")
        sys.exit(1)
    
    message = sys.argv[1]
    chat_type = sys.argv[2] if len(sys.argv) > 2 else "any"
    from_user = sys.argv[3] if len(sys.argv) > 3 else "未知用户"
    
    result = check_command(message, chat_type, from_user)
    
    print(f"\n{Colors.CYAN}检测结果：{Colors.NC}")
    print(f"  是否命令：{result['is_command']}")
    print(f"  是否路由：{result['should_route']}")
    if result.get('agent'):
        print(f"  Agent: {result['agent']}")
    if result.get('handled_by'):
        print(f"  处理者：{result['handled_by']}")
    print(f"  回复：{result.get('message', '')}")

if __name__ == '__main__':
    main()
