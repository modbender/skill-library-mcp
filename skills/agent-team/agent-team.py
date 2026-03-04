#!/usr/bin/env python3
"""
agent-team - 多 Agent 团队管理系统

管理和调用具有不同"灵魂"的子 Agent 团队。

用法:
    agent-team list                      # 列出所有 Agent
    agent-team show <name>              # 查看 Agent 详情
    agent-team spawn <name> [task]      # 启动 Agent 执行任务
    agent-team chat <name>              # 与 Agent 交互对话
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# 配置
AGENTS_DIR = Path.home() / ".openclaw" / "workspace" / "agents"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

# ANSI 颜色
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def load_agents() -> Dict[str, dict]:
    """加载所有 Agent 配置"""
    agents = {}
    
    if not AGENTS_DIR.exists():
        return agents
    
    for agent_dir in AGENTS_DIR.iterdir():
        if agent_dir.is_dir():
            config_file = agent_dir / "config.json"
            soul_file = agent_dir / "SOUL.md"
            
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config['_path'] = str(agent_dir)
                    config['_has_soul'] = soul_file.exists()
                    agents[agent_dir.name] = config
    
    return agents

def list_agents():
    """列出所有 Agent"""
    agents = load_agents()
    
    if not agents:
        print(f"{Colors.YELLOW}⚠️  未找到任何 Agent{Colors.NC}")
        print(f"提示：在 {AGENTS_DIR} 目录下创建 Agent")
        return
    
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}🤖 Agent 团队 ({len(agents)} 个成员){Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    for name, config in sorted(agents.items()):
        emoji = config.get('emoji', '🤖')
        role = config.get('role', '未知角色')
        model = config.get('model', {}).get('primary', 'N/A')
        desc = config.get('description', '')
        
        print(f"{emoji} **{name}** - {role}")
        print(f"   {desc}")
        print(f"   模型：{model}")
        print()

def show_agent(name: str):
    """显示 Agent 详情"""
    agents = load_agents()
    
    if name not in agents:
        print(f"{Colors.RED}❌ 未找到 Agent: {name}{Colors.NC}")
        print(f"可用的 Agent: {', '.join(agents.keys())}")
        return
    
    config = agents[name]
    
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}{config.get('emoji', '🤖')} {name} - {config.get('role', '未知角色')}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    # 基本信息
    print(f"{Colors.CYAN}📋 基本信息{Colors.NC}")
    print(f"  描述：{config.get('description', 'N/A')}")
    print(f"  模型：{config.get('model', {}).get('primary', 'N/A')}")
    print(f"  备选：{config.get('model', {}).get('fallback', 'N/A')}")
    print()
    
    # 能力
    capabilities = config.get('capabilities', [])
    if capabilities:
        print(f"{Colors.CYAN}🛠️  能力{Colors.NC}")
        for cap in capabilities:
            print(f"  • {cap}")
        print()
    
    # 性格
    personality = config.get('personality', {})
    if personality:
        print(f"{Colors.CYAN}🎭 性格特质{Colors.NC}")
        for trait, value in personality.items():
            print(f"  • {trait}: {value}")
        print()
    
    # SOUL.md 预览
    soul_file = Path(config['_path']) / "SOUL.md"
    if soul_file.exists():
        print(f"{Colors.CYAN}📜 SOUL.md 预览{Colors.NC}")
        with open(soul_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:15]
            for line in lines:
                if line.strip() and not line.startswith('#'):
                    print(f"  {line.rstrip()}")
        print()

def spawn_agent(name: str, task: Optional[str] = None):
    """启动 Agent 执行任务"""
    agents = load_agents()
    
    if name not in agents:
        print(f"{Colors.RED}❌ 未找到 Agent: {name}{Colors.NC}")
        return
    
    config = agents[name]
    model = config.get('model', {}).get('primary', 'dashscope/qwen3.5-plus')
    
    # 读取 SOUL.md
    soul_file = Path(config['_path']) / "SOUL.md"
    soul_content = ""
    if soul_file.exists():
        with open(soul_file, 'r', encoding='utf-8') as f:
            soul_content = f.read()
    
    print(f"{Colors.GREEN}🚀 启动 {config.get('emoji', '🤖')} {name}...{Colors.NC}")
    print(f"   模型：{model}")
    print(f"   任务：{task or '交互式对话'}")
    print()
    
    # 构建系统提示
    system_prompt = f"""你现在的身份是 {name} ({config.get('role', '未知角色')})。

{soul_content}

请完全代入这个角色，按照 SOUL.md 中定义的性格、价值观和沟通风格与用户交流。
"""
    
    if task:
        # 有任务：直接执行
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}任务执行中...{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
        
        # 使用 sessions_spawn 创建子代理
        cmd = [
            'openclaw', 'sessions', 'spawn',
            '--task', f"{system_prompt}\n\n任务：{task}",
            '--model', model,
            '--label', f"agent-{name}"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Agent 已启动{Colors.NC}")
                print(result.stdout)
            else:
                print(f"{Colors.RED}❌ 启动失败{Colors.NC}")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print(f"{Colors.YELLOW}⚠️  超时，但 Agent 可能已在后台运行{Colors.NC}")
        except Exception as e:
            print(f"{Colors.RED}❌ 错误：{e}{Colors.NC}")
    else:
        # 无任务：进入交互模式
        print(f"{Colors.YELLOW}💬 进入交互模式 (输入 'quit' 退出){Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
        
        while True:
            try:
                user_input = input(f"{Colors.CYAN}你：{Colors.NC}").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not user_input:
                    continue
                
                # 调用模型
                print(f"{Colors.GREEN}{name}：{Colors.NC}", end='', flush=True)
                
                # 简单实现：调用 curl 到模型 API
                # 这里可以使用 openclaw agent 命令
                cmd = [
                    'openclaw', 'agent',
                    '--model', model,
                    '--message', f"{system_prompt}\n\n用户：{user_input}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                print(result.stdout)
                print()
                
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print(f"{Colors.RED}错误：{e}{Colors.NC}")

def chat_with_agent(name: str):
    """与 Agent 交互对话"""
    spawn_agent(name, task=None)

def main():
    parser = argparse.ArgumentParser(
        description='多 Agent 团队管理系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s list                     列出所有 Agent
  %(prog)s show coder              查看 Coder 详情
  %(prog)s spawn writer "写篇文章"  启动 Writer 写文章
  %(prog)s chat analyst            与 Analyst 对话
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有 Agent')
    
    # show 命令
    show_parser = subparsers.add_parser('show', help='查看 Agent 详情')
    show_parser.add_argument('name', help='Agent 名称')
    
    # spawn 命令
    spawn_parser = subparsers.add_parser('spawn', help='启动 Agent 执行任务')
    spawn_parser.add_argument('name', help='Agent 名称')
    spawn_parser.add_argument('task', nargs='?', help='任务描述')
    
    # chat 命令
    chat_parser = subparsers.add_parser('chat', help='与 Agent 对话')
    chat_parser.add_argument('name', help='Agent 名称')
    
    args = parser.parse_args()
    
    if args.command == 'list':
        list_agents()
    elif args.command == 'show':
        show_agent(args.name)
    elif args.command == 'spawn':
        spawn_agent(args.name, args.task)
    elif args.command == 'chat':
        chat_with_agent(args.name)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
