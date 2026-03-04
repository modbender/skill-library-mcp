#!/usr/bin/env python3
"""
Nomtiq 小饭票 - 全球搜索（Google Places + Yelp + Reddit）
用于海外用户或海外华人场景

用法:
  python3 search_global.py "Italian restaurant Manhattan"
  python3 search_global.py "ramen Tokyo" --city Tokyo --source all
  python3 search_global.py "dim sum Flushing" --city "New York" --mode 2plus1
"""

import sys
import json
import argparse
import re
import os
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent.parent  # ~/.openclaw/workspace


def _hub_search(query: str, max_results: int = 20) -> list:
    """调用 search-hub"""
    try:
        result = subprocess.run(
            ['python3.13', 'skills/search-hub/scripts/hub.py', 'search', query, '-t', 'text', '-l', str(max_results)],
            cwd=str(WORKSPACE),
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return []
        data = json.loads(result.stdout)
        return data.get('results', [])
    except Exception as e:
        print(f"search-hub error: {e}", file=sys.stderr)
        return []


def search_google_places(query: str, city: str = '', max_results: int = 20) -> list:
    """搜索 Google Places（通过 search-hub 搜索 Google Maps）"""
    city_str = f' {city}' if city else ''
    search_query = f'site:maps.google.com OR site:google.com/maps {query}{city_str} restaurant'
    
    # 同时搜 TripAdvisor 作为补充
    tripadvisor_query = f'site:tripadvisor.com {query}{city_str} restaurant review'
    
    results = []
    for q in [search_query, tripadvisor_query]:
        raw = _hub_search(q, max_results // 2)
        for r in raw:
            parsed = _parse_global_result(r, source='google')
            if parsed:
                results.append(parsed)
    
    return results


def search_yelp(query: str, city: str = '', max_results: int = 20) -> list:
    """搜索 Yelp"""
    city_str = f' {city}' if city else ''
    search_query = f'site:yelp.com {query}{city_str}'
    
    raw = _hub_search(search_query, max_results)
    results = []
    for r in raw:
        parsed = _parse_global_result(r, source='yelp')
        if parsed:
            results.append(parsed)
    return results


def search_reddit(query: str, city: str = '', max_results: int = 10) -> list:
    """搜索 Reddit 本地推荐（最真实的本地人口碑）"""
    city_str = city or ''
    # 搜索城市 subreddit 的餐厅推荐
    search_query = f'site:reddit.com {query} {city_str} restaurant recommendation'
    
    raw = _hub_search(search_query, max_results)
    results = []
    for r in raw:
        parsed = _parse_reddit_result(r)
        if parsed:
            results.append(parsed)
    return results


def search_xiaohongshu_global(query: str, max_results: int = 10) -> list:
    """搜索小红书（海外华人场景）"""
    # 小红书上有大量海外华人的探店内容
    search_query = f'site:xiaohongshu.com {query} 探店 海外'
    
    raw = _hub_search(search_query, max_results)
    results = []
    for r in raw:
        results.append({
            'name': _extract_name_from_title(r.get('title', '')),
            'snippet': r.get('snippet', '')[:200],
            'url': r.get('url', ''),
            'source': 'xiaohongshu',
            'sentiment': _detect_sentiment(r.get('snippet', '')),
            'is_chinese_community': True,
        })
    return [r for r in results if r['name']]


def _parse_global_result(result: dict, source: str) -> dict | None:
    """解析全球搜索结果"""
    title = result.get('title', '')
    snippet = result.get('snippet', '')
    url = result.get('url', '')
    combined = f"{title} {snippet}"

    # 过滤非餐厅内容
    food_keywords = ['restaurant', 'cafe', 'bistro', 'bar', 'kitchen', 'grill', 'eatery',
                     'dining', 'food', 'cuisine', 'menu', 'reservation', '餐厅', '料理']
    if not any(kw.lower() in combined.lower() for kw in food_keywords):
        return None

    # 提取评分
    score = None
    # Yelp: "4.5 star rating" or "4.5/5"
    score_match = re.search(r'(\d\.?\d?)\s*(?:star|stars|/5|\s*out of 5)', combined, re.IGNORECASE)
    if score_match:
        score = float(score_match.group(1))
    # Google: "(4.5)" or "4.5 ★"
    if not score:
        score_match = re.search(r'[★⭐]\s*(\d\.?\d?)|(\d\.?\d?)\s*[★⭐]', combined)
        if score_match:
            score = float(score_match.group(1) or score_match.group(2))

    # 提取价格档次
    price_level = None
    if '$$$$' in combined: price_level = 4
    elif '$$$' in combined: price_level = 3
    elif '$$' in combined: price_level = 2
    elif '$' in combined: price_level = 1

    # 提取菜系
    cuisine_keywords = {
        'Chinese': ['chinese', 'dim sum', 'cantonese', 'sichuan', 'peking', 'dumpling', '中餐', '粤菜'],
        'Japanese': ['japanese', 'sushi', 'ramen', 'izakaya', 'omakase', 'tempura'],
        'Italian': ['italian', 'pizza', 'pasta', 'trattoria', 'osteria'],
        'French': ['french', 'bistro', 'brasserie', 'croissant'],
        'Korean': ['korean', 'bbq', 'bibimbap', 'kimchi'],
        'Thai': ['thai', 'pad thai', 'curry'],
        'Mexican': ['mexican', 'taco', 'burrito', 'enchilada'],
        'Indian': ['indian', 'curry', 'tandoor', 'biryani'],
        'American': ['american', 'burger', 'bbq', 'steakhouse'],
    }
    cuisines = []
    for cuisine, kws in cuisine_keywords.items():
        if any(kw.lower() in combined.lower() for kw in kws):
            cuisines.append(cuisine)

    name = _extract_name_from_title(title)
    if not name:
        return None

    return {
        'name': name,
        'score': score,
        'price_level': price_level,
        'cuisines': cuisines,
        'snippet': snippet[:200],
        'url': url,
        'source': source,
        'sources': [source],
        'cross_verified': False,
        'reddit_mentioned': False,
    }


def _parse_reddit_result(result: dict) -> dict | None:
    """解析 Reddit 结果"""
    title = result.get('title', '')
    snippet = result.get('snippet', '')
    url = result.get('url', '')

    if 'reddit.com' not in url:
        return None

    # 提取提到的餐厅名（通常在引号或大写中）
    mentioned = []
    # 引号内的名字
    quoted = re.findall(r'"([^"]{3,40})"', f"{title} {snippet}")
    mentioned.extend(quoted)

    return {
        'title': title[:100],
        'snippet': snippet[:300],
        'url': url,
        'source': 'reddit',
        'restaurants_mentioned': mentioned,
        'sentiment': _detect_sentiment(snippet),
        'is_local_recommendation': True,
    }


def _extract_name_from_title(title: str) -> str:
    """从标题提取餐厅名"""
    # "Restaurant Name - Yelp" → "Restaurant Name"
    # "Restaurant Name | TripAdvisor" → "Restaurant Name"
    # "Restaurant Name (City)" → "Restaurant Name"
    name = re.split(r'\s*[-|·]\s*(?:Yelp|TripAdvisor|Google|Maps|Reviews?|Menu)', title)[0]
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)  # 去掉括号内容
    name = name.strip()
    return name if len(name) > 2 else ''


def _detect_sentiment(text: str) -> str:
    """简单情感检测"""
    positive = ['great', 'amazing', 'excellent', 'best', 'love', 'recommend', 'delicious',
                '好吃', '推荐', '必去', '超棒', '喜欢', 'hidden gem', 'underrated']
    negative = ['bad', 'terrible', 'avoid', 'worst', 'disappointing', 'overrated',
                '难吃', '不推荐', '踩雷', '失望']
    text_lower = text.lower()
    pos = sum(1 for w in positive if w in text_lower)
    neg = sum(1 for w in negative if w in text_lower)
    if pos > neg: return 'positive'
    if neg > pos: return 'negative'
    return 'neutral'


def search_all_global(query: str, city: str = '', max_results: int = 20,
                      include_xhs: bool = False) -> list:
    """全球三源搜索：Google Places + Yelp + Reddit 交叉验证"""
    print(f"🌍 全球搜索中...", file=sys.stderr)

    # 1. Google Places / TripAdvisor
    print(f"  Google Places...", file=sys.stderr)
    google_results = search_google_places(query, city, max_results)
    print(f"  找到 {len(google_results)} 家", file=sys.stderr)

    # 2. Yelp
    print(f"  Yelp...", file=sys.stderr)
    yelp_results = search_yelp(query, city, max_results)
    print(f"  找到 {len(yelp_results)} 家", file=sys.stderr)

    # 3. Reddit 本地口碑
    print(f"  Reddit...", file=sys.stderr)
    reddit_results = search_reddit(query, city, 10)
    print(f"  找到 {len(reddit_results)} 条讨论", file=sys.stderr)

    # 4. 小红书（海外华人场景）
    xhs_results = []
    if include_xhs:
        print(f"  小红书（海外华人）...", file=sys.stderr)
        xhs_results = search_xiaohongshu_global(query, 10)
        print(f"  找到 {len(xhs_results)} 条笔记", file=sys.stderr)

    # 合并 Google + Yelp
    merged = {}
    for r in google_results + yelp_results:
        name = r['name'].lower()
        if name in merged:
            merged[name]['sources'].append(r['source'])
            merged[name]['cross_verified'] = True
            # 合并评分（取平均）
            if r.get('score') and merged[name].get('score'):
                merged[name]['score'] = (merged[name]['score'] + r['score']) / 2
            elif r.get('score'):
                merged[name]['score'] = r['score']
        else:
            merged[name] = r

    # Reddit 交叉验证
    for reddit_post in reddit_results:
        for mentioned in reddit_post.get('restaurants_mentioned', []):
            for key in merged:
                if mentioned.lower() in key or key in mentioned.lower():
                    merged[key]['reddit_mentioned'] = True
                    merged[key]['reddit_sentiment'] = reddit_post.get('sentiment')
                    break

    results = list(merged.values())

    # 海外华人：小红书加分
    if xhs_results:
        for xhs in xhs_results:
            xhs_name = (xhs.get('name') or '').lower()
            for key in merged:
                if xhs_name and (xhs_name in key or key in xhs_name):
                    merged[key]['xhs_verified'] = True
                    merged[key]['sources'].append('xiaohongshu')

    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Nomtiq - 全球餐厅搜索')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--city', default='', help='城市')
    parser.add_argument('--max', type=int, default=20, help='最大结果数')
    parser.add_argument('--xhs', action='store_true', help='包含小红书（海外华人模式）')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    args = parser.parse_args()

    results = search_all_global(args.query, args.city, args.max, include_xhs=args.xhs)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"\n🌍 找到 {len(results)} 家餐厅\n")
        for i, r in enumerate(results[:10], 1):
            score = f"⭐{r['score']}" if r.get('score') else ''
            price = '$' * r['price_level'] if r.get('price_level') else ''
            cuisines = '/'.join(r.get('cuisines', [])[:2])
            verified = '✅' if r.get('cross_verified') else ''
            reddit = '🗣️Reddit' if r.get('reddit_mentioned') else ''
            info = ' | '.join(p for p in [score, price, cuisines, verified, reddit] if p)
            print(f"{i}. {r['name']}")
            if info: print(f"   {info}")
            if r.get('snippet'): print(f"   {r['snippet'][:80]}")
            print()
