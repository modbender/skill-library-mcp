#!/usr/bin/env python3
"""
保存URL内容到本地
- 内容保存为 Markdown
- 图片下载到同级目录
"""

import os
import sys
import re
import requests
import hashlib
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, unquote

# 默认保存目录
DEFAULT_OUTPUT_DIR = "/Users/ys/laoyang知识库/nickys/素材"


def sanitize_filename(name: str, max_length: int = 50) -> str:
    """清理文件名，移除非法字符"""
    # 移除非法字符
    name = re.sub(r'[<>:"/\\|?*\n\r\t]', '', name)
    # 移除多余空格
    name = re.sub(r'\s+', ' ', name).strip()
    # 截断长度
    if len(name) > max_length:
        name = name[:max_length]
    return name or "untitled"


def extract_title_from_content(content: str) -> str:
    """从内容中提取标题"""
    # 尝试从 Markdown 标题提取
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        return match.group(1).strip()

    # 尝试从第一行提取
    lines = content.strip().split('\n')
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line) < 100:
            return first_line

    return "untitled"


def extract_images_from_content(content: str) -> list:
    """从内容中提取图片URL"""
    # Markdown 图片格式: ![alt](url)
    md_images = re.findall(r'!\[.*?\]\((https?://[^\s\)]+)\)', content)

    # 直接的图片URL
    direct_images = re.findall(r'(https?://[^\s\)]+\.(?:jpg|jpeg|png|gif|webp|bmp)[^\s\)]*)', content, re.IGNORECASE)

    # 小红书图片URL
    xhs_images = re.findall(r'(https?://sns-webpic[^\s\)]+)', content)

    # 合并去重
    all_images = list(dict.fromkeys(md_images + direct_images + xhs_images))

    return all_images


def download_image(url: str, save_dir: Path, index: int) -> str:
    """下载图片并返回本地文件名"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Referer': 'https://www.xiaohongshu.com/'
        }

        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # 确定文件扩展名
        content_type = response.headers.get('content-type', '')
        if 'webp' in content_type or 'webp' in url:
            ext = '.webp'
        elif 'png' in content_type or 'png' in url:
            ext = '.png'
        elif 'gif' in content_type or 'gif' in url:
            ext = '.gif'
        else:
            ext = '.jpg'

        # 生成文件名
        filename = f"img_{index:02d}{ext}"
        filepath = save_dir / filename

        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"  ✓ 下载图片: {filename}")
        return filename

    except Exception as e:
        print(f"  ✗ 下载失败: {url[:50]}... ({e})")
        return None


def save_content(content: str, url: str, output_dir: str = None, title: str = None) -> dict:
    """
    保存内容到本地

    Args:
        content: Markdown 内容
        url: 原始 URL
        output_dir: 输出目录
        title: 自定义标题（可选）

    Returns:
        保存结果信息
    """
    output_dir = Path(output_dir or DEFAULT_OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 提取或使用标题
    if not title:
        title = extract_title_from_content(content)

    # 生成文件夹名（日期_标题）
    date_str = datetime.now().strftime("%Y-%m-%d")
    folder_name = f"{date_str}_{sanitize_filename(title)}"

    # 创建内容目录
    content_dir = output_dir / folder_name
    content_dir.mkdir(parents=True, exist_ok=True)

    # 提取并下载图片
    images = extract_images_from_content(content)
    image_mapping = {}  # 原始URL -> 本地文件名

    if images:
        print(f"发现 {len(images)} 张图片，正在下载...")
        for i, img_url in enumerate(images, 1):
            local_name = download_image(img_url, content_dir, i)
            if local_name:
                image_mapping[img_url] = local_name

    # 替换内容中的图片URL为本地路径
    updated_content = content
    for orig_url, local_name in image_mapping.items():
        updated_content = updated_content.replace(orig_url, local_name)

    # 添加元信息
    meta = f"""---
title: {title}
url: {url}
saved_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
images: {len(image_mapping)}
---

"""

    # 保存 Markdown 文件
    md_path = content_dir / "content.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(meta + updated_content)

    print(f"\n✓ 内容已保存到: {content_dir}")
    print(f"  - Markdown: content.md")
    print(f"  - 图片: {len(image_mapping)} 张")

    return {
        'success': True,
        'dir': str(content_dir),
        'md_file': str(md_path),
        'images': len(image_mapping),
        'title': title
    }


def main():
    if len(sys.argv) < 2:
        print("用法: python save_content.py <markdown_file_or_content>")
        print(f"\n默认保存目录: {DEFAULT_OUTPUT_DIR}")
        return

    # 如果是文件路径
    if os.path.isfile(sys.argv[1]):
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            content = f.read()
        url = sys.argv[2] if len(sys.argv) > 2 else "unknown"
    else:
        content = sys.argv[1]
        url = sys.argv[2] if len(sys.argv) > 2 else "unknown"

    save_content(content, url)


if __name__ == "__main__":
    main()
