#!/usr/bin/env python3
"""
X-Deep-Miner: X (Twitter) 深度挖掘与归档工具

Usage:
    python3 x_deep_miner.py scan      # 执行扫描
    python3 x_deep_miner.py status   # 查看状态
    python3 x_deep_miner.py test     # 测试模式（不保存）
"""

import os
import json
import argparse
from datetime import datetime
from pathlib import Path

# 配置路径
WORKSPACE_DIR = Path(os.environ.get('WORKSPACE_DIR', '/Users/scott/.openclaw/workspace'))
OUTPUT_DIR = WORKSPACE_DIR / 'obsidian-output'
CONFIG_FILE = WORKSPACE_DIR / 'memory' / 'x-deep-miner-config.json'

# 默认配置
DEFAULT_CONFIG = {
    'keywords': {
        'ai_tech': ['LLM', 'Agent', 'DeepSeek', 'OpenAI', 'Python', 'Coding', 'Tech Trends'],
        'us_stock': ['US Stock', 'Market Analysis', 'Fed', 'Macro', 'Crypto', 'BTC', 'Wealth'],
        'life': ['Life', 'Productivity', 'Travel', 'Parenting', 'Education', 'Health', 'Biohacking']
    },
    'min_bookmarks': 1000,
    'min_thread_length': 5,
    'scan_interval_hours': 1,
    'output_format': 'obsidian'
}

# 标签映射
TAG_MAPPING = {
    'ai_tech': 'AI',
    'us_stock': 'US_Stock',
    'life': 'Life'
}


def load_config() -> dict:
    """加载配置"""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG


def save_config(config: dict):
    """保存配置"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def ensure_dirs():
    """确保目录存在"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for category in TAG_MAPPING.values():
        (OUTPUT_DIR / category).mkdir(parents=True, exist_ok=True)


def search_x_tweets(keywords: list, min_bookmarks: int = 1000) -> list:
    """
    抓取用户 Timeline 新帖
    使用 OpenClaw Managed Browser (openclaw profile)
    
    使用方式:
    1. browser action=start profile=openclaw
    2. browser action=open targetUrl="https://x.com/home" profile=openclaw
    3. browser action=snapshot targetId=<id>
    """
    print(f"[X-Deep-Miner] 监控模式：抓取 Timeline 新帖")
    print(f"[X-Deep-Miner] 关键词过滤: {keywords}")
    print(f"[X-Deep-Miner] 最低热度: {min_bookmarks}")
    
    results = []
    
    # 使用浏览器自动化抓取
    # 1. 启动浏览器 (profile="openclaw")
    # 2. 打开 x.com/home
    # 3. 解析 DOM 获取推文
    
    print("\n💡 使用 OpenClaw Managed Browser:")
    print("   browser action=start profile=openclaw")
    print("   browser action=open targetUrl=https://x.com/home profile=openclaw")
    
    return results


def fetch_tweet_with_browser(tweet_url: str) -> dict:
    """
    使用浏览器获取单条推文详情
    """
    # TODO: 使用 browser tool
    # browser action=snapshot url=tweet_url
    pass


def translate_content(text: str) -> str:
    """
    翻译内容为专家级中文
    保留术语，如 Alpha, Zero-shot 等
    """
    # TODO: 接入 LLM API 进行翻译
    # 当前为占位实现
    return text


def generate_obsyidian_note(data: dict, category: str) -> str:
    """生成 Obsidian 格式笔记"""
    
    title = data.get('title', 'Untitled')
    author = data.get('author', 'Unknown')
    handle = data.get('handle', '')
    url = data.get('url', '')
    bookmarks = data.get('bookmarks', 0)
    content = data.get('content', '')
    images = data.get('images', [])
    
    # 生成 frontmatter
    note = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
source_url: {url}
author: {author}
@{handle}
bookmarks: {bookmarks}
tags:
  - #X_DeepMiner
  - #{category}
---

# {title}

> [!abstract] Monica's Insight
> (一句话犀利点评：关于 {category} 的高热度长文)

## 📌 核心要点 (Key Takeaways)

- 🔹 观点 1: 待提取
- 🔹 观点 2: 待提取

---

## 📖 正文详情

{content}

"""
    
    # 嵌入图片
    for i, img_url in enumerate(images, 1):
        note += f"\n![配图{i}]({img_url})\n"
    
    note += f"\n---\n*Original Source: [Link]({url})*"
    
    return note


def save_note(note: str, category: str, title: str):
    """保存笔记到对应目录"""
    # 清理文件名
    safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip()[:50]
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"
    
    output_path = OUTPUT_DIR / category / filename
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(note)
    
    print(f"  ✓ 已保存: {output_path}")
    return output_path


def scan():
    """执行扫描"""
    config = load_config()
    ensure_dirs()
    
    print("\n" + "="*50)
    print("🔍 X-Deep-Miner 开始扫描")
    print("="*50 + "\n")
    
    all_results = []
    
    # 按类别扫描
    for category_key, keywords in config['keywords'].items():
        category = TAG_MAPPING.get(category_key, 'Unknown')
        print(f"\n📂 扫描类别: {category}")
        
        results = search_x_tweets(
            keywords, 
            config['min_bookmarks']
        )
        
        for result in results:
            # 翻译内容
            translated = translate_content(result.get('content', ''))
            result['content'] = translated
            
            # 生成笔记
            note = generate_obsyidian_note(result, category)
            save_note(note, category, result.get('title', 'Untitled'))
        
        all_results.extend(results)
    
    print("\n" + "="*50)
    print(f"✅ 扫描完成! 共处理 {len(all_results)} 条内容")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print("="*50 + "\n")
    
    return True


def status():
    """查看状态"""
    config = load_config()
    
    print("\n=== X-Deep-Miner 状态 ===\n")
    print(f"最低收藏数: {config['min_bookmarks']}")
    print(f"扫描间隔: {config['scan_interval_hours']} 小时")
    print(f"输出目录: {OUTPUT_DIR}")
    
    # 统计已处理内容
    total = 0
    for category in TAG_MAPPING.values():
        count = len(list((OUTPUT_DIR / category).glob('*.md')))
        print(f"\n{category}: {count} 篇")
        total += count
    
    print(f"\n总计: {total} 篇\n")
    
    return True


def main():
    parser = argparse.ArgumentParser(description='X-Deep-Miner: X 深度挖掘工具')
    parser.add_argument('command', choices=['scan', 'status', 'test'], 
                        default='scan', help='命令')
    
    args = parser.parse_args()
    
    ensure_dirs()
    
    if args.command == 'scan':
        return scan()
    elif args.command == 'status':
        return status()
    elif args.command == 'test':
        print("🧪 测试模式")
        config = load_config()
        print(f"配置: {config}")
        return True
    
    return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
