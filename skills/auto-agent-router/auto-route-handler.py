#!/usr/bin/env python3
"""
Auto Route Handler - 自动消息路由处理器

集成到 OpenClaw 消息处理流程，实现收到消息时自动判断并分流
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, Optional
import subprocess

# 添加技能路径
SKILL_DIR = Path(__file__).parent
sys.path.insert(0, str(SKILL_DIR))

from router import route_message, spawn_agent, load_agents

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

class AutoRouteHandler:
    """自动路由处理器"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or SKILL_DIR / "config.json"
        self.config = self._load_config()
        self.log_file = Path("/tmp/auto-route-handler.log")
    
    def _load_config(self) -> dict:
        """加载配置"""
        if not self.config_path.exists():
            return {"enabled": False}
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _log(self, message: str):
        """记录日志"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        # 写入日志文件
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # 同时输出到控制台
        print(log_entry.strip())
    
    def should_auto_route(self, message: str, chat_type: str = "group") -> bool:
        """
        判断是否应该自动路由
        
        Args:
            message: 消息内容
            chat_type: 聊天类型 (group/direct)
        
        Returns:
            bool: 是否应该自动路由
        """
        # 检查是否启用
        if not self.config.get('enabled', False):
            return False
        
        # 检查是否启用自动路由
        if not self.config.get('autoRoute', False):
            return False
        
        # 群聊优先自动路由（并发需求高）
        if chat_type == "group":
            return True
        
        # 私聊需要更复杂的任务才路由
        if chat_type == "direct":
            analysis = self._analyze_message(message)
            return analysis['complexity'] in ['medium', 'complex']
        
        return False
    
    def _analyze_message(self, message: str) -> dict:
        """分析消息"""
        from router import analyze_message
        return analyze_message(message)
    
    def handle_message(self, message: str, chat_type: str = "group", 
                      from_user: str = "", verbose: bool = True) -> dict:
        """
        处理消息 - 主入口
        
        Args:
            message: 消息内容
            chat_type: 聊天类型 (group/direct)
            from_user: 发送者
            verbose: 是否输出详细信息
        
        Returns:
            dict: 处理结果
        """
        self._log(f"收到消息：{message[:50]}... (from: {from_user}, type: {chat_type})")
        
        # 路由决策
        result = route_message(message, verbose=verbose)
        
        # 记录决策
        self._log(f"路由决策：{'路由到子 Agent' if result['should_route'] else '主 Session 处理'}")
        self._log(f"  原因：{result['reason']}")
        
        if result['should_route']:
            # 启动子 Agent
            self._log(f"启动子 Agent: {result['agent']} (模型：{result['model']})")
            
            # 构建任务描述
            task_description = f"""
【来自 {chat_type} 的消息】
发送者：{from_user or '未知'}
原始消息：{message}

请以 {result['agent']} 的身份专业地处理这个请求。
"""
            
            # 启动子 Agent
            spawn_result = spawn_agent(
                agent_name=result['agent'],
                task=task_description,
                model=result['model']
            )
            
            self._log(f"Agent 启动结果：{spawn_result}")
            
            return {
                'action': 'spawned_agent',
                'agent': result['agent'],
                'model': result['model'],
                'spawn_result': spawn_result,
                'message': f"已启动 {result['agent']} 处理您的请求..."
            }
        else:
            # 主 Session 处理
            self._log("由主 Session 直接处理")
            
            return {
                'action': 'handle_directly',
                'agent': None,
                'model': result['model'],
                'message': '主 Session 处理'
            }
    
    def handle_with_timeout(self, message: str, chat_type: str = "group",
                           from_user: str = "", timeout_seconds: int = 300) -> dict:
        """
        带超时控制的消息处理
        
        Args:
            message: 消息内容
            chat_type: 聊天类型
            from_user: 发送者
            timeout_seconds: 超时时间（秒）
        
        Returns:
            dict: 处理结果
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Agent 执行超时（{timeout_seconds}秒）")
        
        # 设置超时
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout_seconds)
        
        try:
            result = self.handle_message(message, chat_type, from_user)
            signal.alarm(0)  # 取消超时
            return result
        except TimeoutError as e:
            self._log(f"超时：{e}")
            return {
                'action': 'timeout',
                'error': str(e),
                'message': '任务执行超时，已切换到主 Session 处理'
            }

def main():
    """命令行测试入口"""
    handler = AutoRouteHandler()
    
    # 测试消息
    test_cases = [
        ("写个 Python 脚本处理 Excel", "group", "用户 A"),
        ("今天天气怎么样", "group", "用户 B"),
        ("分析一下销售数据", "group", "用户 C"),
        ("帮我写周报", "direct", "主人"),
    ]
    
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}🧪 Auto Route Handler 测试{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    for message, chat_type, from_user in test_cases:
        print(f"\n{Colors.CYAN}测试用例：{Colors.NC}")
        print(f"  消息：{message}")
        print(f"  类型：{chat_type}")
        print(f"  发送者：{from_user}")
        print(f"{Colors.BLUE}{'-'*60}{Colors.NC}")
        
        result = handler.handle_message(message, chat_type, from_user)
        
        print(f"\n{Colors.GREEN}处理结果：{Colors.NC}")
        print(f"  动作：{result['action']}")
        if result['agent']:
            print(f"  Agent: {result['agent']}")
        print(f"  回复：{result['message']}")
        print()

if __name__ == '__main__':
    main()
