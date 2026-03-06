#!/usr/bin/env python3
"""
Kimi CLI Runner v2 - PTY 模式支持

支持两种模式：
1. 单次模式 (quick): kimi "task" → 执行完成返回
2. 交互模式 (interactive): kimi → 保持会话，支持多轮

用法:
    python3 kimi_runner.py --mode quick "任务描述"
    python3 kimi_runner.py --mode interactive --session-name "my-task"
"""

import argparse
import json
import sys
from pathlib import Path


def run_quick_mode(task: str, cwd: str = None, timeout: int = 300):
    """
    快速模式：单次执行，返回结果
    生成可直接使用的 exec 命令
    """
    workdir = cwd or "${PWD}"
    
    cmd = f'''bash pty:true workdir:{workdir} timeout:{timeout} command:"kimi '{task}'"'''
    
    result = {
        "mode": "quick",
        "tool": "exec",
        "command": cmd,
        "note": "将此命令粘贴到 OpenClaw 中执行"
    }
    
    return result


def run_interactive_mode(session_name: str, cwd: str = None):
    """
    交互模式：后台启动，保持会话
    生成 background 模式的 exec 命令
    """
    workdir = cwd or "${PWD}"
    
    cmd = f'''bash pty:true workdir:{workdir} background:true command:"kimi"'''
    
    result = {
        "mode": "interactive",
        "tool": "exec",
        "command": cmd,
        "session_name": session_name,
        "next_steps": [
            "1. 执行上述命令获取 sessionId",
            "2. 使用 process action:log sessionId:XXX 查看输出",
            "3. 使用 process action:submit sessionId:XXX data:'你的输入' 发送消息",
            "4. 使用 process action:kill sessionId:XXX 结束会话"
        ]
    }
    
    return result


def generate_wake_on_complete(task_desc: str):
    """
    生成任务完成时自动唤醒的命令
    用于长时间运行的任务
    """
    wake_cmd = f'openclaw gateway wake --text "Kimi完成: {task_desc}" --mode now'
    
    return {
        "usage": f"在任务描述末尾添加: 完成后执行 {wake_cmd}",
        "command": wake_cmd
    }


def main():
    parser = argparse.ArgumentParser(
        description="Kimi CLI Runner - OpenClaw 桥接工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 快速模式 - 单次执行
  python3 kimi_runner.py --mode quick "创建一个 Flask API"

  # 交互模式 - 保持会话
  python3 kimi_runner.py --mode interactive --session-name "debug-session"

  # 带工作目录
  python3 kimi_runner.py --mode quick "重构代码" --cwd ./src --timeout 600
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["quick", "interactive"],
        default="quick",
        help="执行模式: quick=单次执行, interactive=保持会话"
    )
    
    parser.add_argument(
        "task",
        nargs="?",
        help="任务描述 (quick 模式必需)"
    )
    
    parser.add_argument(
        "--cwd",
        default=None,
        help="工作目录"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="超时时间(秒)，默认 300"
    )
    
    parser.add_argument(
        "--session-name",
        default="kimi-session",
        help="交互模式的会话名称"
    )
    
    parser.add_argument(
        "--wake",
        action="store_true",
        help="任务完成时自动唤醒"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if args.mode == "quick" and not args.task:
        parser.error("quick 模式需要提供 task 参数")
    
    # 生成结果
    if args.mode == "quick":
        result = run_quick_mode(args.task, args.cwd, args.timeout)
        
        if args.wake:
            wake_info = generate_wake_on_complete(args.task[:50])
            result["wake_command"] = wake_info
            # 修改命令，添加唤醒
            result["command_with_wake"] = result["command"].rstrip('"') + f" && {wake_info['command']}\""
    else:
        result = run_interactive_mode(args.session_name, args.cwd)
    
    # 输出 JSON
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
