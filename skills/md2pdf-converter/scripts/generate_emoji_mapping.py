#!/usr/bin/env python3
"""
generate_emoji_mapping.py
生成 Twemoji 到 Unicode 代码点的映射表
"""

import os
import json

# Twemoji 目录
TWEMOJI_DIR = os.path.expanduser("~/.cache/md2pdf/emojis")

# 解析 Twemoji 文件名
# 格式: codepoint(-codepoint).png
def parse_twemoji_filename(filename):
    """
    解析 Twemoji 文件名，返回 Unicode 代码点列表
    例如: "0023-fe0f-20e3.png" -> [0x23, 0xfe0f, 0x20e3] (⌛)
    例如: "1f600.png" -> [0x1f600] (🙀)
    """
    if not filename.endswith('.png'):
        return None

    basename = filename[:-4]  # 移除 .png
    parts = basename.split('-')

    codepoints = []
    for part in parts:
        try:
            codepoint = int(part, 16)
            codepoints.append(codepoint)
        except ValueError:
            # 忽略无效部分（如fe0f这是选择器）
            continue

    return codepoints if codepoints else None

# 生成映射表
def generate_mapping():
    """生成 emoji 到文件路径的映射表"""
    mapping = {}

    if not os.path.exists(TWEMOJI_DIR):
        print(f"错误: Twemoji 目录不存在: {TWEMOJI_DIR}")
        return None

    print(f"正在扫描 Twemoji 目录: {TWEMOJI_DIR}")

    # 扫描所有 PNG 文件
    for filename in os.listdir(TWEMOJI_DIR):
        if not filename.endswith('.png'):
            continue

        codepoints = parse_twemoji_filename(filename)
        if codepoints:
            # 将代码点转换为字符串
            emoji_str = ''.join(chr(cp) for cp in codepoints)

            # 存储映射
            mapping[emoji_str] = filename

    print(f"✅ 找到 {len(mapping)} 个 emoji")

    # 保存映射表
    mapping_file = os.path.join(os.path.dirname(TWEMOJI_DIR), "emoji_mapping.json")
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"✅ 映射表已保存至: {mapping_file}")

    return mapping

if __name__ == '__main__':
    generate_mapping()
