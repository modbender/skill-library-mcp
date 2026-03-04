#!/usr/bin/env python3
"""
会话记忆搜索工具
支持关键字快速搜索，自动脱敏，按日期存储
"""

import os
import re
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# 配置
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory" / "conversations"

# 脱敏正则规则
REDACTION_RULES = [
    # 邮箱
    (r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]'),
    # 手机号
    (r'1[3-9]\d{9}', '[PHONE]'),
    # API Key/Token (包含key/token/secret/password的长字符串)
    (r'(api[_-]?key|token|secret|password|access[_-]?key)[=:]\s*["\']?[\w-]{20,}["\']?', '[REDACTED]', re.IGNORECASE),
    # 通用密钥格式 (sk-xxx, ghp_xxx 等)
    (r'sk-[a-zA-Z0-9]{20,}', '[API_KEY]'),
    (r'ghp_[a-zA-Z0-9]{36,}', '[GITHUB_TOKEN]'),
    # 身份证号
    (r'\d{17}[\dXx]', '[ID_CARD]'),
    # 银行卡号
    (r'\d{16,19}', '[CARD]'),
    # IP地址
    (r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', '[IP]'),
    # Token (Bearer xxx)
    (r'Bearer\s+[a-zA-Z0-9_-]{20,}', '[BEARER_TOKEN]'),
]

def ensure_dir():
    """确保目录存在"""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)

def redact_text(text):
    """对文本进行脱敏处理"""
    for pattern, replacement, *flags in REDACTION_RULES:
        flags = flags[0] if flags else 0
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
    files = get_conversation_files(days)
    results = []
    
    for filepath in files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 搜索匹配行
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if keyword.lower() in line.lower():
                    # 获取上下文（前后各1行）
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
    files = get_conversation_files(days)
    
    print(f"\n📋 最近 {days} 天的会话记录:\n")
    for filepath in files:
        stat = filepath.stat()
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        # 读取会话摘要
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

def main():
    ensure_dir()
    
    if len(sys.argv) < 2:
        print("用法:")
        print("  search.py <关键词>          # 搜索关键字")
        print("  search.py <关键词> --days N # 搜索最近N天")
        print("  search.py --list           # 列出所有会话")
        print("  search.py --record         # 记录当前会话")
        sys.exit(1)
    
    if sys.argv[1] == '--list':
        days = 7
        if len(sys.argv) > 2 and sys.argv[2] == '--days':
            days = int(sys.argv[3] if len(sys.argv) > 3 else 7)
        list_conversations(days)
        return
    
    # 解析参数
    keyword = sys.argv[1]
    days = 7
    
    for i, arg in enumerate(sys.argv[2:], 2):
        if arg == '--days' and i < len(sys.argv):
            days = int(sys.argv[i])
    
    # 搜索
    results = search_keyword(keyword, days)
    
    if results:
        print(f"\n🔍 搜索 '{keyword}' (最近{days}天) - 找到 {len(results)} 条结果:\n")
        for r in results[:10]:  # 最多显示10条
            print(f"📄 {r['file']} (第{r['line']}行)")
            print(f"   {r['context']}")
            print()
    else:
        print(f"\n未找到关于 '{keyword}' 的会话记录\n")

if __name__ == '__main__':
    main()
