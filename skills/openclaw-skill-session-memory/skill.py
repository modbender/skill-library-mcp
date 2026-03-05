#!/usr/bin/env python3
"""
Session Memory Skill for OpenClaw
自动记录对话并支持快速搜索
"""

import os
import re
import sys
import json
import glob
from datetime import datetime
from pathlib import Path

# 配置
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "conversations"
SESSIONS_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"

# 脱敏正则规则
REDACTION_RULES = [
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]'),
    (r'1[3-9]\d{9}', '[PHONE]'),
    (r'(api[_-]?key|token|secret|password|access[_-]?key)[=:]\s*["\']?[\w-]{20,}["\']?', '[REDACTED]', re.IGNORECASE),
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY]'),
    (r'ghp_[a-zA-Z0-9]{36,}', '[GITHUB_TOKEN]'),
    (r'\d{17}[\dXx]', '[ID_CARD]'),
    (r'\d{16,19}', '[CARD]'),
    (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]'),
    (r'Bearer\s+[a-zA-Z0-9_-]{20,}', '[BEARER_TOKEN]'),
    (r'["\']?[\w-]{30,}["\']?', '[TOKEN]'),
]

def ensure_dir():
    """确保目录存在"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def redact_text(text):
    """对文本进行脱敏处理"""
    for rule in REDACTION_RULES:
        pattern = rule[0]
        replacement = rule[1]
        flags = rule[2] if len(rule) > 2 else 0
        text = re.sub(pattern, replacement, text, flags=flags)
    return text

def get_conversation_files(days=7):
    """获取最近N天的会话文件"""
    ensure_dir()
    files = []
    today = datetime.now()
    
    for i in range(days):
        date = today - timedelta(days=i)
        filename = f"{date.strftime('%Y-%m-%d')}.md"
        filepath = MEMORY_DIR / filename
        if filepath.exists():
            files.append(filepath)
    
    return files

def search_keyword(keyword, days=7):
    """搜索关键字，返回匹配结果"""
    from datetime import timedelta
    files = get_conversation_files(days)
    results = []
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    context_start = max(0, i-1)
                    context_end = min(len(lines), i+2)
                    context = '\n'.join(lines[context_start:context_end])
                    context = redact_text(context)
                    
                    results.append({
                        'file': filepath.name,
                        'line': i + 1,
                        'context': context
                    })
        except Exception as e:
            print(f"读取文件失败 {filepath}: {e}", file=sys.stderr)
    
    return results

def list_conversations(days=7):
    """列出所有会话文件"""
    from datetime import timedelta
    files = get_conversation_files(days)
    
    print(f"\n📋 最近 {days} 天的会话记录:\n")
    for filepath in files:
        stat = filepath.stat()
        size = stat.st_size
        
        title = "无标题"
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('# '):
                    title = first_line[2:]
        except:
            pass
        
        print(f"  📄 {filepath.name} - {title} ({size} bytes)")
    
    if not files:
        print("  (暂无会话记录)")
    print()

def extract_messages_from_jsonl(filepath):
    """从jsonl文件提取对话消息"""
    messages = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        content_list = msg.get('content', [])
                        
                        for content in content_list:
                            if content.get('type') == 'text':
                                text = content.get('text', '')
                                text = re.sub(r'\[message_id:[^\]]+\]', '', text)
                                text = text.strip()
                                
                                if text and len(text) > 2:
                                    ts = msg.get('timestamp', 0)
                                    if ts:
                                        dt = datetime.fromtimestamp(ts/1000)
                                        time_str = dt.strftime('%H:%M')
                                    else:
                                        time_str = ''
                                    
                                    messages.append({
                                        'time': time_str,
                                        'role': msg.get('role', ''),
                                        'text': redact_text(text)
                                    })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"读取文件失败: {e}", file=sys.stderr)
    
    return messages

def get_latest_session_file():
    """获取最新的会话文件"""
    today_str = datetime.now().strftime('%Y-%m-%d')
    patterns = [
        SESSIONS_DIR / f"*{today_str}*.jsonl",
        SESSIONS_DIR / f"*.jsonl.reset.*",
        SESSIONS_DIR / f"*.jsonl",
    ]
    
    latest_file = None
    latest_mtime = 0
    
    for pattern in patterns:
        for filepath in glob.glob(str(pattern)):
            try:
                mtime = os.path.getmtime(filepath)
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = filepath
            except:
                pass
    
    return latest_file

def save_conversation(messages, date_str=None):
    """保存对话到markdown文件"""
    if date_str is None:
        date_str = datetime.now().strftime('%Y-%m-%d')
    
    filepath = MEMORY_DIR / f"{date_str}.md"
    content_lines = [f"# {date_str} 会话记录", ""]
    
    if not messages:
        content_lines.append("*无对话记录*")
        content_lines.append("")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        print(f"📝 已保存: {filepath}")
        return filepath
    
    current_time = ""
    
    for msg in messages:
        time_str = msg.get('time', '')
        role = msg.get('role', '')
        text = msg.get('text', '')
        
        if time_str and time_str != current_time:
            if current_time:
                content_lines.append("")
            content_lines.append(f"## {time_str} {role.upper()}")
            current_time = time_str
        
        if text:
            if len(text) > 500:
                text = text[:500] + "..."
            content_lines.append(f"- {text}")
    
    content_lines.append("")
    content_lines.append(f"*共 {len(messages)} 条消息*")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    print(f"📝 已保存 {len(messages)} 条对话到: {filepath}")
    return filepath

def record():
    """记录当前会话"""
    ensure_dir()
    date_str = datetime.now().strftime('%Y-%m-%d')
    session_file = get_latest_session_file()
    
    if not session_file:
        print("未找到会话文件")
        save_conversation([], date_str)
        return
    
    print(f"📂 读取会话: {session_file}")
    messages = extract_messages_from_jsonl(session_file)
    print(f"📊 提取到 {len(messages)} 条消息")
    save_conversation(messages, date_str)

def search(query, days=7):
    """搜索会话"""
    if query == '--list':
        list_conversations(days)
        return
    
    results = search_keyword(query, days)
    
    if results:
        print(f"\n🔍 搜索 '{query}' (最近{days}天) - 找到 {len(results)} 条结果:\n")
        for r in results[:10]:
            print(f"📄 {r['file']} (第{r['line']}行)")
            print(f"   {r['context']}")
            print()
    else:
        print(f"\n未找到关于 '{query}' 的会话记录\n")

def main():
    ensure_dir()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  skill.py record           # 记录当前会话")
        print("  skill.py search <关键词>  # 搜索关键字")
        print("  skill.py search --list   # 列出所有会话")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'record':
        record()
    elif command == 'search':
        if len(sys.argv) < 3:
            print("请提供搜索关键词")
            sys.exit(1)
        query = sys.argv[2]
        days = 7
        for i, arg in enumerate(sys.argv[3:], 3):
            if arg == '--days' and i < len(sys.argv):
                days = int(sys.argv[i])
        search(query, days)
    else:
        print(f"未知命令: {command}")

if __name__ == '__main__':
    main()
