#!/usr/bin/env python3
"""
github-trending-daily - 每日 GitHub Trending 钉钉推送

每天定时获取 GitHub Trending 热门项目并推送到钉钉群。

用法:
    github-trending-daily              # 获取今日热门并推送
    github-trending-daily --weekly     # 获取本周热门
    github-trending-daily --monthly    # 获取本月热门
    github-trending-daily --dry-run    # 测试模式（预览消息）
"""

import sys
import json
import urllib.request
import urllib.error
import re
from datetime import datetime
from typing import List, Dict

# 配置
DINGTALK_WEBHOOK = "https://oapi.dingtalk.com/robot/send?access_token=0d8da1a9a2f0360d7a4c086bb849127b53ed36984db025c5c649083185ebd8fe"
DINGTALK_KEYWORD = "AI 推送"
GITHUB_TRENDING_URL = "https://github.com/trending"

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'

def fetch_github_trending(period: str = "daily") -> str:
    """获取 GitHub Trending HTML"""
    url = f"{GITHUB_TRENDING_URL}?since={period}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    with urllib.request.urlopen(req, timeout=15) as response:
        return response.read().decode('utf-8')

def parse_trending_html(html: str) -> List[Dict]:
    """解析 GitHub Trending HTML"""
    projects = []
    
    # 提取所有 article 块
    articles = re.findall(r'<article[^>]*>(.*?)</article>', html, re.DOTALL)
    
    for article in articles[:10]:
        try:
            # 项目名称 (排除 sponsors 路径)
            name_match = re.search(r'href="(/[^/]+/[^/"]+)"', article)
            if not name_match:
                continue
            name = name_match.group(1).lstrip('/')
            # 排除 sponsors 和 trending 路径
            if name.startswith('sponsors/') or name.startswith('trending/'):
                continue
            
            # 描述
            desc_match = re.search(r'<p[^>]*>([^<]*)</p>', article, re.DOTALL)
            desc = desc_match.group(1).strip()[:60] if desc_match else ''
            if desc: desc += '...'
            
            # 语言 (查找第一个出现的编程语言)
            lang_match = re.search(r'\b(Python|JavaScript|TypeScript|Rust|Go|Java|C\+\+|Shell|Ruby|PHP|Swift)\b', article)
            lang = lang_match.group(1) if lang_match else 'Unknown'
            
            # Stars 总数 (查找 aria-label 中的数字)
            stars_match = re.search(r'aria-label="([\d,\.]+[kK]?)\s*user[s]?\s*starred', article, re.IGNORECASE)
            if not stars_match:
                stars_match = re.search(r'([\d,\.]+[kK]?)\s*stars?\b', article, re.IGNORECASE)
            stars = stars_match.group(1).replace(',', '') if stars_match else 'N/A'
            
            # 今日 Stars
            today_match = re.search(r'([\d,\.]+[kK]?)\s*stars?\s*today', article, re.IGNORECASE)
            today = today_match.group(1).replace(',', '') if today_match else 'N/A'
            
            projects.append({
                'name': name,
                'lang': lang,
                'stars': stars,
                'today': today,
                'desc': desc
            })
        except Exception as e:
            continue
    
    return projects

def format_markdown_message(projects: List[Dict], period: str = "daily") -> str:
    """格式化 Markdown 消息"""
    period_map = {'daily': '今日', 'weekly': '本周', 'monthly': '本月'}
    period_cn = period_map.get(period, '热门')
    
    lines = [
        f"# {DINGTALK_KEYWORD}\n\n{DINGTALK_KEYWORD}",
        "",
        f"## 🔥 GitHub Trending {period_cn} ({datetime.now().strftime('%Y-%m-%d')})",
        ""
    ]
    
    emojis = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    for i, proj in enumerate(projects[:10]):
        emoji = emojis[i] if i < len(emojis) else f'{i+1}'
        lines.append(f"{emoji} **{proj['name']}** ({proj['lang']}) +{proj['today']}⭐")
        if proj['desc']:
            lines.append(f"   _{proj['desc']}_")
        lines.append(f"   ⭐ {proj['stars']} | [GitHub](https://github.com/{proj['name']})")
        lines.append("")
    
    lines.append("---")
    lines.append(f"_📊 数据来源：[GitHub Trending]({GITHUB_TRENDING_URL})_")
    lines.append(f"_🤖 自动推送 by 小牛马_")
    
    return "\n".join(lines)

def send_dingtalk_markdown(markdown_text: str) -> bool:
    """发送钉钉 Markdown 消息"""
    title_line = markdown_text.split('\n')[2].replace('## ', '').strip()
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": title_line,
            "text": markdown_text
        },
        "at": {"isAtAll": False}
    }
    
    try:
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(DINGTALK_WEBHOOK, data=data, headers={'Content-Type': 'application/json'})
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode('utf-8'))
        
        if result.get('errcode') == 0:
            print(f"{Colors.GREEN}✅ 钉钉推送成功{Colors.NC}")
            return True
        else:
            print(f"{Colors.RED}❌ 钉钉推送失败：{result.get('errmsg', '未知错误')}{Colors.NC}")
            return False
    except Exception as e:
        print(f"{Colors.RED}❌ 发送失败：{e}{Colors.NC}")
        return False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='每日 GitHub Trending 钉钉推送')
    parser.add_argument('--weekly', action='store_true', help='获取本周热门')
    parser.add_argument('--monthly', action='store_true', help='获取本月热门')
    parser.add_argument('--no-push', action='store_true', help='只获取不推送')
    parser.add_argument('--dry-run', action='store_true', help='测试模式（不实际发送）')
    
    args = parser.parse_args()
    
    period = "monthly" if args.monthly else ("weekly" if args.weekly else "daily")
    
    print(f"{Colors.BLUE}📊 获取 GitHub Trending ({period})...{Colors.NC}")
    
    html = fetch_github_trending(period)
    projects = parse_trending_html(html)
    
    if not projects:
        print(f"{Colors.RED}❌ 未获取到任何项目{Colors.NC}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}✅ 获取到 {len(projects)} 个项目{Colors.NC}")
    
    markdown_msg = format_markdown_message(projects, period)
    
    if args.dry_run:
        print(f"\n{Colors.YELLOW}=== 测试模式：消息预览 ==={Colors.NC}\n")
        print(markdown_msg)
        sys.exit(0)
    
    if not args.no_push:
        print(f"\n{Colors.BLUE}📤 发送钉钉推送...{Colors.NC}")
        success = send_dingtalk_markdown(markdown_msg)
        sys.exit(0 if success else 1)
    else:
        print(f"\n{Colors.YELLOW}⏭️  跳过推送{Colors.NC}")
        sys.exit(0)

if __name__ == '__main__':
    main()
