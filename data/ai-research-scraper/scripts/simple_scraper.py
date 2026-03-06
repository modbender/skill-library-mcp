#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import json

from scraper import translate_text, truncate_text

def main():
    # 使用tavily-search技能获取结果
    result = subprocess.run([
        'node', '/root/.openclaw/workspace/skills/tavily-search/scripts/search.mjs',
        'AI product development',
        '-n', '10',
        '--topic', 'news'
    ], capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        # 解析tavily-search的输出
        output = result.stdout.split('\n')
        i = 0
        while i < len(output):
            if output[i].startswith('## Answer'):
                i += 2
                continue
            if output[i].startswith('## Sources'):
                i += 2
                while i < len(output):
                    if output[i].startswith('- **') and len(output[i]) > 5:
                        title = output[i].split('**')[1]
                        title = title.split('(')[0].strip()
                        source = output[i + 1].strip() if (i + 1 < len(output) and output[i + 1].strip()) else ''
                        summary = output[i + 2].strip() if (i + 2 < len(output) and output[i + 2].strip()) else ''
                        i += 3
                        
                        # 处理摘要：截断并翻译
                        truncated_summary = truncate_text(summary, 200)
                        translated_summary = translate_text(truncated_summary)
                        
                        print(f"标题: {title}")
                        print(f"摘要: {translated_summary}")
                        print(f"来源: {source}")
                        print()
                    else:
                        i += 1
            else:
                i += 1
    else:
        print(f"  查询失败: {result.stderr}")

if __name__ == "__main__":
    main()