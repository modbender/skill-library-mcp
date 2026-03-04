#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能切分学术论文为章节文件
按照large-document-reader技能规范实现
"""

import re
import os
from pathlib import Path

def extract_chapters(file_path):
    """提取文档中的所有章节"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    chapters = []
    current_section = None
    current_content = []

    for i, line in enumerate(lines):
        # 检查是否是章节标题
        # 匹配格式：1.1.1、1.1.2、一、1.1、1、(1)等
        stripped = line.strip()

        # 主章节：第1章、1、1.
        if re.match(r'^\s*(第\d+章|\d+\.\s+[^\s].*|^\d+\.\s*$)', stripped):
            # 保存前一个章节
            if current_section:
                chapters.append({
                    'start': current_section['start'],
                    'end': i,
                    'title': current_section['title'],
                    'content': current_section['content']
                })

            # 提取标题
            if re.match(r'^\s*(第\d+章)', stripped):
                title = re.sub(r'^\s*(第\d+章)\s*', '', stripped)
                title = re.sub(r'[\.\。、\s]+$', '', title)
            else:
                title = re.sub(r'^\s*(\d+)\.?\s*', '', stripped)
                title = re.sub(r'[\.\。、\s]+$', '', title)

            current_section = {
                'start': i,
                'title': title[:60],
                'content': []
            }

        # 子章节：1.1、1.2、1.1.1等
        elif re.match(r'^\s*\d+\.\d+\.\s+', stripped) or re.match(r'^\s*\d+\.\d+\.\d+\.\s+', stripped):
            # 保存前一个章节
            if current_section:
                chapters.append({
                    'start': current_section['start'],
                    'end': i,
                    'title': current_section['title'],
                    'content': current_section['content']
                })

            title = stripped
            parts = re.split(r'\s+', title)
            title = parts[0] if len(parts) > 0 else title
            title = re.sub(r'[\.\。、\s]+$', '', title)

            current_section = {
                'start': i,
                'title': title[:60],
                'content': []
            }

        # 中文小节：一、二、三、1.1等
        elif re.match(r'^\s*[一二三四五六七八九十]+[、\.]\s+', stripped) or re.match(r'^\s*(\d+\.\d+)\.?\s+', stripped):
            # 保存前一个章节
            if current_section:
                chapters.append({
                    'start': current_section['start'],
                    'end': i,
                    'title': current_section['title'],
                    'content': current_section['content']
                })

            title = re.sub(r'^\s*[一二三四五六七八九十]+[、\.]?\s*', '', stripped)
            title = re.sub(r'^\s*(\d+\.\d+)\.?\s*', r'\1', stripped)
            title = re.sub(r'[\.\。、\s]+$', '', title)

            current_section = {
                'start': i,
                'title': title[:60],
                'content': []
            }

        # 括号小节：(1)、(2)等
        elif re.match(r'^\s*\(\d+\)[\.、]\s*', stripped) or re.match(r'^\s*\(\d+\)\.?\s*', stripped):
            # 保存前一个章节
            if current_section:
                chapters.append({
                    'start': current_section['start'],
                    'end': i,
                    'title': current_section['title'],
                    'content': current_section['content']
                })

            title = re.sub(r'^\s*\(\d+\)[\.、]?\s*', '', stripped)
            title = re.sub(r'[\.\。、\s]+$', '', title)

            current_section = {
                'start': i,
                'title': title[:60],
                'content': []
            }

        # 继续添加内容
        elif current_section:
            current_section['content'].append(line)

    # 添加最后一个章节
    if current_section:
        chapters.append({
            'start': current_section['start'],
            'end': len(lines),
            'title': current_section['title'],
            'content': current_section['content']
        })

    return chapters

def main():
    file_path = "/Users/chenkuan/Desktop/毕业论文/规模与杠杆对银行系统性风险的影响研究_王怡涵.txt"

    print(f"正在读取文件: {file_path}")
    print("=" * 60)

    chapters = extract_chapters(file_path)

    print(f"\n总共找到 {len(chapters)} 个章节/小节")
    print("\n章节列表:")
    for idx, chapter in enumerate(chapters, 1):
        content_length = len(chapter['content'])
        print(f"{idx}. {chapter['title'][:50]} - 内容行数: {content_length}")

    return chapters

if __name__ == "__main__":
    chapters = main()

    # 保存到文件供后续使用
    with open('/Users/chenkuan/.openclaw/workspace/large-document-reader-1.0.0/chapters_info.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(chapters, f, ensure_ascii=False, indent=2)

    print("\n章节信息已保存到 chapters_info.json")
