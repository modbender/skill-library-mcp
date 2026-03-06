#!/usr/bin/env python3
"""
Daily AI News Aggregator
Fetches AI-related content from HackerNews, GitHub Trending, and ArXiv
"""

import json
import re
import sys
import argparse
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.parse import quote
from xml.etree import ElementTree as ET

# ============ 配置 ============
CONFIG = {
    "max_hackernews": 5,
    "max_github": 5,
    "max_arxiv": 3,
    "keywords": ["ai", "ml", "machine learning", "llm", "gpt", "neural", 
                 "deep learning", "transformer", "openai", "anthropic",
                 "stable diffusion", "midjourney", "langchain", "vector"],
}

# ============ 工具函数 ============
def fetch_json(url):
    """获取 JSON 数据"""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def fetch_text(url):
    """获取文本数据"""
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def contains_ai_keywords(text):
    """检查文本是否包含 AI 关键词"""
    text_lower = text.lower()
    return any(kw in text_lower for kw in CONFIG["keywords"])

def truncate(text, max_len=100):
    """截断文本"""
    if len(text) <= max_len:
        return text
    return text[:max_len-3] + "..."

# ============ 数据源 ============
def fetch_hackernews():
    """获取 HackerNews AI 相关热帖"""
    # 使用 Algolia API 搜索 AI 相关内容
    query = quote("AI OR machine-learning OR LLM OR GPT")
    url = f"https://hn.algolia.com/api/v1/search_by_date?query={query}&tags=story&numericFilters=points>50&hitsPerPage={CONFIG['max_hackernews']*2}"
    
    data = fetch_json(url)
    if not data or 'hits' not in data:
        return []
    
    results = []
    for hit in data['hits'][:CONFIG['max_hackernews']]:
        title = hit.get('title', '')
        url = hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        points = hit.get('points', 0)
        
        results.append({
            'title': title,
            'url': url,
            'points': points,
            'source': 'HN'
        })
    
    return results

def fetch_github_trending():
    """获取 GitHub AI 趋势项目"""
    # GitHub trending 没有官方 API，使用搜索 API 找最近更新的热门项目
    url = "https://api.github.com/search/repositories?q=AI+OR+LLM+OR+GPT+created:>2025-12-01&sort=stars&order=desc&per_page=20"
    
    data = fetch_json(url)
    if not data or 'items' not in data:
        return []
    
    results = []
    for item in data['items'][:CONFIG['max_github']]:
        name = item.get('full_name', '')
        desc = item.get('description', '') or 'No description'
        stars = item.get('stargazers_count', 0)
        url = item.get('html_url', '')
        
        # 过滤非 AI 项目
        if not contains_ai_keywords(name + ' ' + desc):
            continue
            
        results.append({
            'name': name,
            'description': truncate(desc, 80),
            'stars': stars,
            'url': url,
            'source': 'GitHub'
        })
    
    return results[:CONFIG['max_github']]

def fetch_arxiv_papers():
    """获取 ArXiv AI 论文"""
    # 搜索 CS.AI 和 CS.LG 类别的最新论文
    categories = "cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL"
    url = f"http://export.arxiv.org/api/query?search_query={categories}&sortBy=submittedDate&sortOrder=descending&max_results={CONFIG['max_arxiv']*2}"
    
    xml_data = fetch_text(url)
    if not xml_data:
        return []
    
    try:
        root = ET.fromstring(xml_data)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        results = []
        for entry in root.findall('atom:entry', ns)[:CONFIG['max_arxiv']*2]:
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ''
            summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ''
            link = entry.find('atom:id', ns).text.strip() if entry.find('atom:id', ns) is not None else ''
            
            # 过滤非 AI 论文
            if not contains_ai_keywords(title + ' ' + summary):
                continue
            
            # 清理标题中的换行符
            title = title.replace('\n', ' ').strip()
            
            results.append({
                'title': truncate(title, 80),
                'summary': truncate(summary, 100),
                'url': link,
                'source': 'ArXiv'
            })
            
            if len(results) >= CONFIG['max_arxiv']:
                break
        
        return results
    except Exception as e:
        print(f"Error parsing ArXiv XML: {e}", file=sys.stderr)
        return []

# ============ 格式化输出 ============
def format_digest(hn_items, gh_items, arxiv_items):
    """格式化日报"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    lines = [
        f"📰 每日 AI 资讯 - {today}",
        "",
        "## 🔥 HackerNews 热门",
    ]
    
    if hn_items:
        for i, item in enumerate(hn_items, 1):
            lines.append(f"{i}. [{item['title']}]({item['url']}) ({item['points']}👍)")
    else:
        lines.append("暂无数据")
    
    lines.extend(["", "## ⭐ GitHub 趋势项目"])
    
    if gh_items:
        for i, item in enumerate(gh_items, 1):
            lines.append(f"{i}. **{item['name']}** ⭐{item['stars']:,}")
            lines.append(f"   {item['description']} [链接]({item['url']})")
    else:
        lines.append("暂无数据")
    
    lines.extend(["", "## 📄 ArXiv 最新论文"])
    
    if arxiv_items:
        for i, item in enumerate(arxiv_items, 1):
            lines.append(f"{i}. [{item['title']}]({item['url']})")
            lines.append(f"   {item['summary']}")
    else:
        lines.append("暂无数据")
    
    lines.extend([
        "",
        "---",
        "🤖 由 OpenClaw daily-ai-news Skill 生成"
    ])
    
    return '\n'.join(lines)

def send_to_openclaw(message, channel=None):
    """通过 OpenClaw 发送消息"""
    import subprocess
    
    cmd = ["openclaw", "message", "send"]
    if channel:
        cmd.extend(["--channel", channel])
    
    # 使用 stdin 传递消息
    result = subprocess.run(
        cmd,
        input=message,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error sending message: {result.stderr}", file=sys.stderr)
        return False
    
    return True

# ============ 主函数 ============
def main():
    parser = argparse.ArgumentParser(description='Daily AI News Aggregator')
    parser.add_argument('--send', action='store_true', help='Send to OpenClaw channel')
    parser.add_argument('--channel', type=str, help='Target channel (e.g., feishu, telegram)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()
    
    print("正在抓取 AI 资讯...", file=sys.stderr)
    
    # 并行抓取（简化版，实际可用 asyncio）
    hn_items = fetch_hackernews()
    gh_items = fetch_github_trending()
    arxiv_items = fetch_arxiv_papers()
    
    if args.json:
        output = json.dumps({
            'hackernews': hn_items,
            'github': gh_items,
            'arxiv': arxiv_items,
            'timestamp': datetime.now().isoformat()
        }, ensure_ascii=False, indent=2)
    else:
        output = format_digest(hn_items, gh_items, arxiv_items)
    
    if args.send:
        success = send_to_openclaw(output, args.channel)
        if success:
            print("✅ 已发送到频道", file=sys.stderr)
        else:
            print("❌ 发送失败", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)

if __name__ == '__main__':
    main()
