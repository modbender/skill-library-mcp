#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
保存章节文件
"""

import json
import os
import re

# 读取章节信息
with open('chapters_info.json', 'r', encoding='utf-8') as f:
    chapters = json.load(f)

# 读取原始文件
with open('/Users/chenkuan/Desktop/毕业论文/规模与杠杆对银行系统性风险的影响研究_王怡涵.txt', 'r', encoding='utf-8') as f:
    original_lines = f.readlines()

# 保存每个章节到chapters目录
for idx, chapter in enumerate(chapters, 1):
    # 清理标题
    title = chapter['title']
    title = re.sub(r'[^\w\u4e00-\u9fa5\-\s]', '', title)  # 只保留中文、英文、数字、连字符、空格
    title = re.sub(r'\s+', '_', title)  # 空格转为下划线
    title = title[:50]  # 限制长度

    # 生成文件名
    filename = f"{idx:02d}_{title}.md"
    filepath = os.path.join('chapters', filename)

    # 提取章节内容
    content_lines = chapter['content']
    content = ''.join(content_lines)

    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"保存: {filename} ({len(content_lines)} 行)")

print(f"\n完成！共保存 {len(chapters)} 个章节文件到 chapters/ 目录")
