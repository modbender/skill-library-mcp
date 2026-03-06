#!/usr/bin/env python3
"""
会话记录工具
自动从会话日志中提取对话内容并保存为markdown
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
    (r'["\']?[\w-]{30,}["\']?', '[TOKEN]'),  # 通用长字符串
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
                        role = msg.get('role', '')
                        content_list = msg.get('content', [])
                        
                        for content in content_list:
                            if content.get('type') == 'text':
                                text = content.get('text', '')
                                # 移除message_id引用
                                text = re.sub(r'\[message_id:[^\]]+\]', '', text)
                                text = text.strip()
                                
                                if text and len(text) > 2:
                                    # 获取时间戳
                                    ts = msg.get('timestamp', 0)
                                    if ts:
                                        dt = datetime.fromtimestamp(ts/1000)
                                        time_str = dt.strftime('%H:%M')
                                    else:
                                        time_str = ''
                                    
                                    messages.append({
                                        'time': time_str,
                                        'role': role,
                                        'text': redact_text(text)
                                    })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"读取文件失败: {e}", file=sys.stderr)
    
    return messages

def get_latest_session_file():
    """获取最新的会话文件"""
    # 查找今天的会话文件
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
    
    # 构建内容
    content_lines = [f"# {date_str} 会话记录", ""]
    
    if not messages:
        content_lines.append("*无对话记录*")
        content_lines.append("")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_lines))
        print(f"📝 已保存: {filepath}")
        return
    
    # 按时间分组
    current_time = ""
    session_count = 0
    
    for msg in messages:
        time_str = msg.get('time', '')
        role = msg.get('role', '')
        text = msg.get('text', '')
        
        if time_str and time_str != current_time:
            # 新的时间段
            if session_count > 0:
                content_lines.append("")
            content_lines.append(f"## {time_str} {role.upper()}")
            current_time = time_str
            session_count += 1
        
        if text:
            # 截断过长消息
            if len(text) > 500:
                text = text[:500] + "..."
            content_lines.append(f"- {text}")
    
    content_lines.append("")
    content_lines.append(f"*共 {len(messages)} 条消息*")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content_lines))
    
    print(f"📝 已保存 {len(messages)} 条对话到: {filepath}")

def main():
    ensure_dir()
    
    # 获取今天的日期
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # 获取最新会话文件
    session_file = get_latest_session_file()
    
    if not session_file:
        print("未找到会话文件")
        # 仍然创建空文件
        save_conversation([], date_str)
        return
    
    print(f"📂 读取会话: {session_file}")
    
    # 提取消息
    messages = extract_messages_from_jsonl(session_file)
    
    print(f"📊 提取到 {len(messages)} 条消息")
    
    # 保存
    save_conversation(messages, date_str)

if __name__ == '__main__':
    main()
