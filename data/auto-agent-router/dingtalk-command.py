#!/usr/bin/env python3
"""
钉钉群命令处理器 - 解析斜杠命令并路由到子 Agent

用法：
    python3 dingtalk-command.py "@小牛马 /coder 写个脚本"
    python3 dingtalk-command.py --test
"""

import sys
import re
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from router import spawn_agent, route_message

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

# 命令映射
COMMAND_MAP = {
    '/coder': 'coder',
    '/code': 'coder',
    '/writer': 'writer',
    '/write': 'writer',
    '/analyze': 'analyst',
    '/analysis': 'analyst',
    '/research': 'researcher',
    '/review': 'reviewer',
    '/review-code': 'reviewer',
    '/devops': 'devops',
    '/ops': 'devops',
    '/auto': 'auto'  # 自动判断
}

# 命令帮助
COMMAND_HELP = {
    'coder': '🧑‍💻 代码专家 - 写代码、调试、重构',
    'writer': '✍️ 写作专家 - 文档、周报、文章',
    'analyst': '📊 数据专家 - 数据分析、图表、统计',
    'researcher': '🔍 调研专家 - 搜索、调研、竞品分析',
    'reviewer': '👀 审查专家 - 代码审查、优化建议',
    'devops': '🤖 运维专家 - 部署、服务器、日志',
    'auto': '🤖 自动判断 - 根据内容智能路由'
}

def get_bot_names() -> list:
    """获取机器人名字列表"""
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
            return config.get('bot_names', ['小牛马', 'xiaoniuma'])
    return ['小牛马', 'xiaoniuma']

def save_bot_name(new_name: str) -> bool:
    """
    自动保存新发现的机器人名字
    
    Args:
        new_name: 新发现的名字
    
    Returns:
        bool: 是否成功保存
    """
    config_file = Path(__file__).parent / "config.json"
    if not config_file.exists():
        return False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        bot_names = config.get('bot_names', [])
        
        # 如果名字已存在，不重复添加
        if new_name in bot_names:
            return False
        
        # 添加新名字
        bot_names.append(new_name)
        config['bot_names'] = bot_names
        
        # 保存配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 自动保存新名字：{new_name}")
        return True
    
    except Exception as e:
        print(f"❌ 保存名字失败：{e}")
        return False

def extract_bot_name(message: str) -> Optional[str]:
    """
    从消息中提取@的机器人名字
    
    Args:
        message: 原始消息
    
    Returns:
        Optional[str]: 提取到的名字，如果没有@则返回 None
    """
    match = re.search(r'@([^\s,，]+)', message)
    if match:
        return match.group(1)
    return None

def parse_command(message: str, auto_save: bool = True, flexible: bool = False) -> dict:
    """
    解析命令
    
    Args:
        message: 原始消息
        auto_save: 是否自动保存新发现的名字
        flexible: 是否灵活匹配（消息任意位置包含命令）
    
    Returns:
        dict: {
            'is_command': bool,
            'command': str,
            'agent': str,
            'task': str,
            'bot_name': str  # 提取到的机器人名字
        }
    """
    # 先提取@的机器人名字
    extracted_name = extract_bot_name(message)
    
    # 如果提取到名字，自动保存
    if extracted_name and auto_save:
        save_bot_name(extracted_name)
    
    # 获取机器人名字列表（包括刚保存的）
    bot_names = get_bot_names()
    
    # 构建正则表达式匹配所有机器人名字
    name_patterns = '|'.join([re.escape(name) for name in bot_names])
    
    # 去掉@部分（支持所有配置的名字）
    clean_msg = re.sub(rf'@({name_patterns})', '', message, flags=re.IGNORECASE).strip()
    
    # 灵活模式：匹配消息中任意位置的命令
    if flexible:
        # 查找第一个斜杠命令
        match = re.search(r'/(coder|code|writer|write|analyze|analysis|research|review|review-code|devops|ops|auto)\s+(.+?)(?=/|$)', 
                         clean_msg, re.IGNORECASE)
    else:
        # 严格模式：必须开头是命令
        match = re.match(r'^/(coder|code|writer|write|analyze|analysis|research|review|review-code|devops|ops|auto)\s+(.+)$', 
                        clean_msg, re.IGNORECASE)
    
    if not match:
        return {
            'is_command': False,
            'bot_name': extracted_name
        }
    
    cmd = '/' + match.group(1).lower()  # 保留斜杠
    task = match.group(2).strip()
    agent = COMMAND_MAP.get(cmd, None)
    
    if not agent:
        return {
            'is_command': False,
            'bot_name': extracted_name
        }
    
    return {
        'is_command': True,
        'command': cmd,
        'agent': agent,
        'task': task,
        'bot_name': extracted_name
    }

def handle_command(message: str, from_user: str = "", verbose: bool = True) -> dict:
    """
    处理命令
    
    Args:
        message: 消息内容
        from_user: 发送者
        verbose: 是否输出详细信息
    
    Returns:
        dict: 处理结果
    """
    parsed = parse_command(message, auto_save=True)
    
    if not parsed.get('is_command', False):
        bot_name = parsed.get('bot_name', '未知')
        return {
            'action': 'not_command',
            'message': f'未识别到命令（@的名字：{bot_name}）',
            'bot_name': bot_name
        }
    
    if verbose:
        print(f"\n{Colors.CYAN}📋 命令解析:{Colors.NC}")
        print(f"  机器人名字：@{parsed.get('bot_name', '未知')}")
        print(f"  命令：/{parsed['command']}")
        print(f"  目标 Agent: {parsed['agent']}")
        print(f"  任务：{parsed['task']}")
        print(f"  发送者：{from_user or '未知'}")
    
    if parsed['agent'] == 'auto':
        # 自动判断
        if verbose:
            print(f"\n{Colors.BLUE}🤖 自动路由模式{Colors.NC}")
        
        result = route_message(parsed['task'], verbose=verbose)
        
        if result['should_route']:
            agent_name = result['agent']
            spawn_result = spawn_agent(agent_name, parsed['task'], result['model'])
            
            # 构建带 Agent 信息的回复
            agent_display = spawn_result.get('agent_info', {}).get('emoji', '🤖') + ' ' + agent_name
            return {
                'action': 'spawned_agent',
                'agent': agent_name,
                'model': result['model'],
                'spawn_result': spawn_result,
                'message': f"🔄 {spawn_result.get('message', f'已启动 {agent_name}')} 处理您的请求...",
                'handled_by': f"Agent: {agent_display}"
            }
        else:
            return {
                'action': 'handle_directly',
                'agent': None,
                'model': result['model'],
                'message': '简单任务，主 Session 处理',
                'handled_by': '主 Session'
            }
    else:
        # 指定 Agent
        if verbose:
            print(f"\n{Colors.GREEN}🚀 启动 Agent: {parsed['agent']}{Colors.NC}")
        
        spawn_result = spawn_agent(parsed['agent'], parsed['task'])
        
        # 构建带 Agent 信息的回复
        agent_display = spawn_result.get('agent_info', {}).get('emoji', '🤖') + ' ' + parsed['agent']
        return {
            'action': 'spawned_agent',
            'agent': parsed['agent'],
            'spawn_result': spawn_result,
            'message': f"✅ {spawn_result.get('message', f'已启动 {parsed['agent']}')} 处理：{parsed['task']}",
            'handled_by': f"Agent: {agent_display}"
        }

def show_help():
    """显示帮助信息"""
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.BLUE}🤖 钉钉群命令帮助{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
    
    print(f"{Colors.CYAN}用法：{Colors.NC}")
    print(f"  @小牛马 /命令 任务描述\n")
    
    print(f"{Colors.CYAN}可用命令：{Colors.NC}\n")
    
    for cmd, help_text in COMMAND_HELP.items():
        print(f"  /{cmd:<12} {help_text}")
    
    print(f"\n{Colors.CYAN}示例：{Colors.NC}\n")
    print(f"  @小牛马 /coder 写个 Python 脚本打印 hello world")
    print(f"  @小牛马 /writer 写一篇周报总结")
    print(f"  @小牛马 /analyze 分析销售数据趋势")
    print(f"  @小牛马 /auto 帮我处理这个任务...")
    print(f"  @小牛马 今天天气怎么样（简单问题，无需命令）")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")

def main():
    parser = argparse.ArgumentParser(
        description='钉钉群命令处理器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s "@小牛马 /coder 写个脚本"
  %(prog)s --test
  %(prog)s --help
        """
    )
    
    parser.add_argument('message', nargs='?', help='消息内容')
    parser.add_argument('--test', action='store_true', help='运行测试')
    parser.add_argument('--help-commands', action='store_true', help='显示命令帮助')
    parser.add_argument('--user', default='', help='发送者名称')
    parser.add_argument('--json', action='store_true', help='输出 JSON 格式')
    
    args = parser.parse_args()
    
    if args.help_commands:
        show_help()
        return
    
    if args.test:
        # 测试模式
        test_messages = [
            "@小牛马 /coder 写个 hello world",
            "@小牛马 /writer 写周报",
            "@小牛马 /analyze 分析数据",
            "@小牛马 /auto 帮我处理这个",
            "@小牛马 今天天气",  # 无命令
        ]
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}🧪 钉钉命令测试{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
        
        for msg in test_messages:
            print(f"\n{Colors.CYAN}消息：{Colors.NC}{msg}")
            print(f"{Colors.BLUE}{'-'*60}{Colors.NC}")
            
            result = handle_command(msg, "测试用户", verbose=True)
            
            print(f"\n{Colors.GREEN}处理结果：{Colors.NC}")
            print(f"  动作：{result['action']}")
            if result.get('agent'):
                print(f"  Agent: {result['agent']}")
            print(f"  回复：{result['message']}")
        
        return
    
    if not args.message:
        parser.print_help()
        return
    
    # 处理实际消息
    result = handle_command(args.message, args.user, verbose=not args.json)
    
    if args.json:
        # JSON 输出（便于程序调用）
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # 人类可读输出
        print(f"\n{Colors.GREEN}✅ 处理结果：{Colors.NC}")
        print(f"  {result['message']}")

if __name__ == '__main__':
    main()
