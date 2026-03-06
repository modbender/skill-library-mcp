#!/usr/bin/env python3
"""
小饭卡 - 小红书探店搜索
通过搜索引擎抓取小红书上的探店笔记。
用法:
  python3 search_xhs.py "三里屯 宝藏餐厅"
  python3 search_xhs.py "国贸 日料" --max 10 --json
"""

import sys
import json
import argparse
import re
import os


PROXY = os.environ.get('DDGS_PROXY') or None


def search_xiaohongshu(query: str, max_results: int = 10) -> list:
    """搜索小红书探店笔记"""
    from ddgs import DDGS
    ddgs = DDGS(proxy=PROXY)

    search_queries = [
        f'site:xiaohongshu.com {query} 探店',
        f'site:xiaohongshu.com {query} 餐厅 推荐',
        f'小红书 {query} 探店 好吃',
    ]

    all_results = []
    seen_urls = set()

    for sq in search_queries:
        try:
            results = ddgs.text(sq, max_results=max_results, region='cn-zh')
            for r in results:
                url = r.get('href', '')
                if url not in seen_urls:
                    seen_urls.add(url)
                    all_results.append(r)
        except Exception as e:
            print(f"搜索出错 [{sq}]: {e}", file=sys.stderr)

    notes = []
    for r in all_results:
        parsed = parse_xhs_result(r)
        if parsed:
            notes.append(parsed)

    return notes


def parse_xhs_result(result):
    """解析小红书搜索结果"""
    title = result.get('title', '')
    body = result.get('body', '')
    url = result.get('href', '')
    combined = f"{title} {body}"

    is_xhs = 'xiaohongshu.com' in url

    # 判断是否餐厅相关
    food_keywords = ['餐厅', '探店', '好吃', '美食', '菜', '馆', '料理', '打卡', '必吃', '推荐', '人均']
    if not any(kw in combined for kw in food_keywords):
        return None

    # 提取提到的餐厅名（通常在标题或正文中以书名号标注）
    restaurant_names = re.findall(r'[「『【《](.+?)[」』】》]', combined)

    # 提取人均
    price_match = re.search(r'[人均¥￥](\d+)', combined)
    avg_price = int(price_match.group(1)) if price_match else None

    # 判断情感（正面/负面）
    positive_words = ['好吃', '推荐', '绝了', '惊艳', '宝藏', '神仙', '必吃', '回购', '超赞', '满分', '爱了']
    negative_words = ['踩雷', '不好吃', '拔草', '失望', '难吃', '不推荐', '一般', '避雷', '翻车']
    
    pos_count = sum(1 for w in positive_words if w in combined)
    neg_count = sum(1 for w in negative_words if w in combined)
    
    if neg_count > pos_count:
        sentiment = 'negative'
    elif pos_count > 0:
        sentiment = 'positive'
    else:
        sentiment = 'neutral'

    return {
        'title': title[:60],
        'restaurants_mentioned': restaurant_names[:3],
        'avg_price': avg_price,
        'sentiment': sentiment,
        'snippet': body[:200] if body else '',
        'url': url,
        'source': 'xiaohongshu' if is_xhs else 'search',
    }


def main():
    parser = argparse.ArgumentParser(description='小饭卡 - 小红书搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--max', type=int, default=10, help='最大结果数')
    parser.add_argument('--json', action='store_true', help='JSON输出')
    args = parser.parse_args()

    notes = search_xiaohongshu(args.query, args.max)

    if args.json:
        print(json.dumps(notes, ensure_ascii=False, indent=2))
    else:
        if not notes:
            print("没有找到相关探店笔记")
            return

        sentiment_emoji = {'positive': '👍', 'negative': '👎', 'neutral': '😐'}
        print(f"📕 小红书探店: {args.query}\n")
        for i, n in enumerate(notes, 1):
            emoji = sentiment_emoji.get(n['sentiment'], '')
            price = f" ¥{n['avg_price']}" if n['avg_price'] else ''
            restaurants = f" → {', '.join(n['restaurants_mentioned'])}" if n['restaurants_mentioned'] else ''

            print(f"{i}. {emoji} {n['title']}{price}{restaurants}")
            if n['snippet']:
                print(f"   {n['snippet'][:80]}")
            print(f"   {n['url']}")
            print()


if __name__ == '__main__':
    main()
