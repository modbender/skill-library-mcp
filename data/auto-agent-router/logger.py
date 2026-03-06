#!/usr/bin/env python3
"""
Auto Agent Router 日志记录器
"""

from datetime import datetime
from pathlib import Path

LOG_FILE = Path("/tmp/auto-route-handler.log")

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def log(message: str, level: str = "INFO"):
    """
    记录日志
    
    Args:
        message: 日志内容
        level: 日志级别 (INFO/DEBUG/ERROR/SUCCESS)
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # 写入日志文件
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        pass  # 忽略写入错误
    
    # 输出到控制台（带颜色）
    color_map = {
        "INFO": Colors.BLUE,
        "DEBUG": Colors.CYAN,
        "ERROR": Colors.RED,
        "SUCCESS": Colors.GREEN,
        "WARNING": Colors.YELLOW
    }
    color = color_map.get(level, Colors.NC)
    
    print(f"{color}[{timestamp}] [{level}] {message}{Colors.NC}")

def log_command(message: str, command: str, agent: str, chat_type: str = ""):
    """记录命令检测"""
    log(f"收到消息：{message[:50]}... (类型：{chat_type or '未知'})")
    log(f"检测到命令：{command} → 路由到：{agent}", "SUCCESS")

def log_agent_start(agent: str, model: str, task: str):
    """记录 Agent 启动"""
    log(f"启动 Agent: {agent} (模型：{model})", "SUCCESS")
    log(f"任务：{task[:100]}...")

def log_agent_complete(agent: str, result: str):
    """记录 Agent 完成"""
    log(f"Agent {agent} 完成：{result[:100]}...", "SUCCESS")

def log_error(message: str):
    """记录错误"""
    log(f"错误：{message}", "ERROR")

def get_recent_logs(count: int = 20):
    """获取最近的日志"""
    if not LOG_FILE.exists():
        return ["日志文件不存在"]
    
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return lines[-count:]

def clear_logs():
    """清空日志"""
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        log("日志已清空", "SUCCESS")
    else:
        log("日志文件不存在", "WARNING")

if __name__ == '__main__':
    # 测试
    print("测试日志记录器：\n")
    log("系统启动", "INFO")
    log_command("/coder 写代码", "/coder", "coder", "test")
    log_agent_start("coder", "qwen3-coder-next", "写个 Hello World")
    log_agent_complete("coder", "代码已生成")
    log_error("测试错误")
    
    print(f"\n日志文件位置：{LOG_FILE}")
    print(f"\n最近日志：")
    for line in get_recent_logs(10):
        print(line.strip())
