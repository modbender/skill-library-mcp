#!/usr/bin/env python3
"""
Auto Agent Router - 自动子 Agent 分流

根据消息内容自动判断并分发给合适的子 Agent
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# 配置
CONFIG_FILE = Path(__file__).parent / "config.json"
WORKSPACE_DIR = Path.home() / ".openclaw" / "workspace"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'

def load_config() -> dict:
    """加载路由配置"""
    if not CONFIG_FILE.exists():
        return {"enabled": False, "rules": []}
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_agents() -> Dict[str, dict]:
    """加载所有可用 Agent"""
    agents = {}
    agents_dir = WORKSPACE_DIR / "agents"
    
    if not agents_dir.exists():
        return agents
    
    for agent_dir in agents_dir.iterdir():
        if agent_dir.is_dir():
            config_file = agent_dir / "config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    config['_path'] = str(agent_dir)
                    agents[agent_dir.name] = config
    
    return agents

def analyze_message(message: str) -> dict:
    """
    分析消息内容，返回分析结果
    
    Returns:
        dict: {
            'length': int,          # 消息长度
            'steps': int,           # 步骤数量
            'is_question': bool,    # 是否是问题
            'has_attachment': bool, # 是否有附件
            'complexity': str       # 复杂度：simple/medium/complex
        }
    """
    # 计算长度
    length = len(message)
    
    # 检测步骤数量（通过序号或连接词）
    steps = len(re.findall(r'(?:(?:首先 | 然后 | 接着 | 最后)|\d+[,.]\s*\n)', message))
    
    # 检测是否是问题
    is_question = bool(re.search(r'[?？]$', message.strip()))
    
    # 检测是否有附件引用
    has_attachment = bool(re.search(r'(文件 | 图片 | 截图 | 附件|upload|file)', message, re.IGNORECASE))
    
    # 综合复杂度判断
    if length > 500 or steps >= 3 or has_attachment:
        complexity = "complex"
    elif length > 200 or steps >= 1:
        complexity = "medium"
    else:
        complexity = "simple"
    
    return {
        'length': length,
        'steps': steps,
        'is_question': is_question,
        'has_attachment': has_attachment,
        'complexity': complexity
    }

def match_keywords(message: str, keywords: List[str]) -> Tuple[bool, List[str]]:
    """
    匹配关键词
    
    Returns:
        Tuple[bool, List[str]]: (是否匹配，匹配到的关键词列表)
    """
    message_lower = message.lower()
    matched = [kw for kw in keywords if kw.lower() in message_lower]
    return len(matched) > 0, matched

def route_message(message: str, verbose: bool = True) -> dict:
    """
    路由决策主函数
    
    Args:
        message: 消息内容
        verbose: 是否输出详细信息
    
    Returns:
        dict: {
            'should_route': bool,       # 是否应该路由到子 Agent
            'agent': Optional[str],     # 目标 Agent 名称
            'model': str,               # 使用的模型
            'reason': str,              # 路由原因
            'matched_keywords': list,   # 匹配到的关键词
            'analysis': dict            # 消息分析结果
        }
    """
    config = load_config()
    
    # 检查是否启用自动路由
    if not config.get('enabled', False):
        return {
            'should_route': False,
            'agent': None,
            'model': config.get('fallback', {}).get('model', 'dashscope/qwen3.5-plus'),
            'reason': '自动路由未启用',
            'matched_keywords': [],
            'analysis': analyze_message(message)
        }
    
    # 分析消息
    analysis = analyze_message(message)
    
    if verbose:
        print(f"\n{Colors.CYAN}📊 消息分析:{Colors.NC}")
        print(f"  长度：{analysis['length']} 字")
        print(f"  步骤数：{analysis['steps']}")
        print(f"  复杂度：{analysis['complexity']}")
        print(f"  是问题：{analysis['is_question']}")
    
    # 规则匹配
    rules = config.get('rules', [])
    for rule in rules:
        matched, keywords = match_keywords(message, rule.get('keywords', []))
        if matched:
            agent_name = rule.get('agent')
            model = rule.get('model', 'dashscope/qwen3.5-plus')
            
            # 检查 Agent 是否存在
            agents = load_agents()
            agent_exists = agent_name in agents
            
            if verbose:
                print(f"\n{Colors.GREEN}✅ 匹配到规则:{Colors.NC}")
                print(f"  类型：{rule.get('type', 'unknown')}")
                print(f"  关键词：{', '.join(keywords)}")
                print(f"  目标 Agent: {agent_name} {'✅' if agent_exists else '⚠️ 未找到'}")
                print(f"  模型：{model}")
            
            return {
                'should_route': agent_exists,  # 只有 Agent 存在时才路由
                'agent': agent_name if agent_exists else None,
                'model': model,
                'reason': f"匹配到 {rule.get('type', 'unknown')} 类型任务",
                'matched_keywords': keywords,
                'analysis': analysis
            }
    
    # 复杂度判断 - 长消息可能需要研究专家
    thresholds = config.get('thresholds', {})
    if analysis['length'] > thresholds.get('maxLength', 500):
        if verbose:
            print(f"\n{Colors.YELLOW}⚠️  消息较长，建议由 researcher 处理{Colors.NC}")
        return {
            'should_route': True,
            'agent': 'researcher',
            'model': 'google/gemini-3.1-pro-preview',
            'reason': '消息过长，需要深度分析',
            'matched_keywords': [],
            'analysis': analysis
        }
    
    # 默认由主 Session 处理
    if verbose:
        print(f"\n{Colors.BLUE}ℹ️  简单消息，主 Session 处理{Colors.NC}")
    
    return {
        'should_route': False,
        'agent': None,
        'model': config.get('fallback', {}).get('model', 'dashscope/qwen3.5-plus'),
        'reason': '简单消息，主 Session 处理',
        'matched_keywords': [],
        'analysis': analysis
    }

def spawn_agent(agent_name: str, task: str, model: str = None) -> dict:
    """
    启动子 Agent 执行任务
    
    Args:
        agent_name: Agent 名称
        task: 任务描述
        model: 模型名称（可选）
    
    Returns:
        dict: {
            'success': bool,
            'agent': str,
            'agent_info': dict,
            'session_key': str,
            'message': str
        }
    """
    agents = load_agents()
    if agent_name not in agents:
        return {
            'success': False,
            'agent': agent_name,
            'message': f"❌ Agent 不存在：{agent_name}"
        }
    
    agent_config = agents[agent_name]
    model = model or agent_config.get('model', {}).get('primary', 'dashscope/qwen3.5-plus')
    emoji = agent_config.get('emoji', '🤖')
    role = agent_config.get('role', '专家')
    
    # 读取 SOUL.md
    soul_file = Path(agent_config['_path']) / "SOUL.md"
    soul_content = ""
    if soul_file.exists():
        with open(soul_file, 'r', encoding='utf-8') as f:
            soul_content = f.read()
    
    # 构建系统提示
    system_prompt = f"""你现在的身份是 {agent_name} ({role})。

{soul_content}

请完全代入这个角色，按照 SOUL.md 中定义的性格、价值观和沟通风格与用户交流。
"""
    
    # 返回启动信息（实际启动由主 Session 调用 sessions_spawn 工具）
    return {
        'success': True,
        'agent': agent_name,
        'agent_info': {
            'name': agent_name,
            'role': role,
            'emoji': emoji,
            'model': model
        },
        'system_prompt': system_prompt,
        'task': task,
        'model': model,
        'message': f"{emoji} 已启动 **{agent_name}** ({role}) 处理您的任务"
    }
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return f"✅ Agent 已启动：{agent_name}"
        else:
            return f"❌ 启动失败：{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"⚠️  超时，但 Agent 可能已在后台运行"
    except Exception as e:
        return f"❌ 错误：{e}"

def main():
    """命令行入口"""
    import sys
    
    if len(sys.argv) < 2:
        print("用法：python router.py <消息内容>")
        print("   或：python router.py --test")
        sys.exit(1)
    
    if sys.argv[1] == '--test':
        # 测试模式
        test_messages = [
            "写个 Python 脚本处理 Excel 文件",
            "分析一下销售数据趋势",
            "今天天气怎么样",
            "帮我写一篇周报总结",
            "调研一下竞品情况",
            "审查这段代码有什么问题"
        ]
        
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}")
        print(f"{Colors.BLUE}🧪 路由测试{Colors.NC}")
        print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")
        
        for msg in test_messages:
            print(f"\n{Colors.CYAN}消息：{Colors.NC}{msg}")
            print(f"{Colors.BLUE}{'-'*60}{Colors.NC}")
            result = route_message(msg, verbose=True)
            print(f"\n{Colors.GREEN}决策：{Colors.NC}")
            print(f"  路由：{'是' if result['should_route'] else '否'}")
            print(f"  Agent: {result['agent'] or '主 Session'}")
            print(f"  模型：{result['model']}")
            print(f"  原因：{result['reason']}")
    else:
        # 实际路由
        message = ' '.join(sys.argv[1:])
        result = route_message(message, verbose=True)
        
        print(f"\n{Colors.GREEN}最终决策：{Colors.NC}")
        print(f"  路由：{'是' if result['should_route'] else '否'}")
        if result['should_route']:
            print(f"  目标 Agent: {result['agent']}")
            print(f"  模型：{result['model']}")
        print(f"  原因：{result['reason']}")

if __name__ == '__main__':
    main()
