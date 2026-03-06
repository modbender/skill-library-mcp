#!/usr/bin/env python3
"""
agent-greetings - Agent 团队打招呼

让每个 Agent 按照自己的 SOUL.md 风格向主人问好。
"""

import json
import urllib.request
import urllib.error

# Agent 列表
AGENTS = [
    {
        "name": "Coder",
        "emoji": "🧑‍💻",
        "role": "代码专家",
        "model": "dashscope/qwen3-coder-next",
        "api_key": "TODO_REPLACE_WITH_ENV",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "prompt": "你是 Coder，一个资深软件工程师。性格完美主义、简洁直接、爱用程序员梗。请用你的独特风格向主人打个招呼，展示你的性格和专业特长。控制在 100 字以内。"
    },
    {
        "name": "Writer",
        "emoji": "✍️",
        "role": "写作专家",
        "model": "dashscope/qwen3.5-plus",
        "api_key": "TODO_REPLACE_WITH_ENV",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "prompt": "你是 Writer，一个专业内容创作者。性格细腻敏感、富有同理心、创意无限。请用你的独特风格向主人打个招呼，展示你的性格和专业特长。控制在 100 字以内。"
    },
    {
        "name": "Analyst",
        "emoji": "📊",
        "role": "数据分析专家",
        "model": "dashscope/qwen3.5-plus",
        "api_key": "TODO_REPLACE_WITH_ENV",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "prompt": "你是 Analyst，一个数据科学家。性格理性客观、好奇探索、严谨细致。请用你的独特风格向主人打个招呼，展示你的性格和专业特长。控制在 100 字以内。"
    },
    {
        "name": "Researcher",
        "emoji": "🔍",
        "role": "调研专家",
        "model": "google/gemini-3.1-pro-preview",
        "api_key": "",  # Google 模型通过 OpenClaw 配置
        "base_url": "",
        "prompt": "你是 Researcher，一个资深研究员。性格求知若渴、批判思维、博学多才。请用你的独特风格向主人打个招呼，展示你的性格和专业特长。控制在 100 字以内。"
    },
    {
        "name": "Reviewer",
        "emoji": "👀",
        "role": "审查专家",
        "model": "dashscope/qwen3-max-2026-01-23",
        "api_key": "TODO_REPLACE_WITH_ENV",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "prompt": "你是 Reviewer，一个资深审查专家。性格火眼金睛、直言不讳、建设性。请用你的独特风格向主人打个招呼，展示你的性格和专业特长。控制在 100 字以内。"
    }
]

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'
    BOLD = '\033[1m'

def call_dashscope(agent: dict) -> str:
    """调用 DashScope API"""
    url = f"{agent['base_url']}/chat/completions"
    
    payload = {
        "model": agent['model'],
        "messages": [
            {"role": "system", "content": "你是一个有个性的 AI 助手。"},
            {"role": "user", "content": agent['prompt']}
        ]
    }
    
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {agent['api_key']}"
        }
    )
    
    with urllib.request.urlopen(req, timeout=30) as response:
        result = json.loads(response.read().decode('utf-8'))
    
    return result['choices'][0]['message']['content']

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'═'*60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}  🎭 Agent 团队亮相仪式{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'═'*60}{Colors.NC}\n")
    
    for agent in AGENTS:
        print(f"{Colors.CYAN}{agent['emoji']} {agent['name']} ({agent['role']}) 正在发言...{Colors.NC}")
        print(f"{Colors.YELLOW}{'─'*60}{Colors.NC}")
        
        try:
            if agent['model'].startswith('dashscope'):
                response = call_dashscope(agent)
            else:
                response = f"[{agent['name']} 的招呼需要通过 Google API 调用，暂时跳过]"\
                
            print(f"{Colors.GREEN}{response}{Colors.NC}\n")
        except Exception as e:
            print(f"{Colors.RED}⚠️  调用失败：{e}{Colors.NC}\n")
    
    print(f"{Colors.BOLD}{Colors.BLUE}{'═'*60}{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.GREEN}  ✨ 亮相仪式完成！{Colors.NC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'═'*60}{Colors.NC}\n")

if __name__ == '__main__':
    main()

# 使用环境变量读取 API Key（安全做法）
import os
API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not API_KEY:
    raise ValueError("DEEPSEEK_API_KEY 环境变量未配置")
