#!/usr/bin/env python3
"""
小饭卡 - 双源搜索（大众点评 + 小红书）
分阶段搜索 + 2+1 推荐模式

用法:
  python3 search_all.py "三里屯 创意菜"
  python3 search_all.py "国贸 日料" --city 北京 --max 50 --mode 2plus1
"""

import sys
import json
import argparse
import os
from pathlib import Path

# 导入同目录的搜索模块
sys.path.insert(0, str(Path(__file__).parent))
from search import search_dianping
from search_xhs import search_xiaohongshu

DATA_DIR = Path(__file__).parent.parent / 'data'
PROFILE_PATH = DATA_DIR / 'taste-profile.json'


def load_preferences() -> dict:
    """加载用户偏好"""
    if PROFILE_PATH.exists():
        with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
            profile = json.load(f)
            return profile.get('preferences', {})
    return {}


def match_score(restaurant: dict, preferences: dict) -> float:
    """计算餐厅与用户偏好的匹配度 (0-100)"""
    if not preferences:
        return 50  # 无画像时给中间分

    score = 50  # 基础分
    liked_tags = set(preferences.get('liked_tags', []))
    disliked_tags = set(preferences.get('disliked_tags', []))
    price_range = preferences.get('price_range', [])
    top_areas = set(preferences.get('top_areas', []))

    restaurant_tags = set(restaurant.get('categories', []) + restaurant.get('tags', []))

    # 标签匹配 (+5 每个匹配)
    matched = liked_tags & restaurant_tags
    score += len(matched) * 5

    # 踩雷标签 (-10 每个)
    anti_matched = disliked_tags & restaurant_tags
    score -= len(anti_matched) * 10

    # 价位匹配
    price = restaurant.get('avg_price')
    if price and price_range and len(price_range) == 2:
        low, high = price_range
        margin = (high - low) * 0.3  # 30% 容差
        if low - margin <= price <= high + margin:
            score += 5
        elif price > high * 1.5 or price < low * 0.5:
            score -= 5

    # 区域匹配
    area = restaurant.get('area', '')
    if area and area in top_areas:
        score += 3

    # 小红书好评加分
    if restaurant.get('xhs_sentiment') == 'positive':
        score += 5
    elif restaurant.get('xhs_sentiment') == 'negative':
        score -= 8

    # 双源验证加分
    if restaurant.get('cross_verified'):
        score += 10

    # 陈晓卿定律：评分可信度
    # 街边小店 3.5-4.2 才真实，过高反而要警惕
    rating = restaurant.get('score')
    if rating:
        if 3.5 <= rating <= 4.2:
            score += 8   # 甜蜜区间，最可信
        elif 4.2 < rating <= 4.5:
            score += 3   # 还不错
        elif 4.5 < rating <= 4.7:
            score += 0   # 中性，不加不减
        elif rating > 4.7:
            score -= 6   # 过高警惕，可能刷评
        elif rating < 3.5:
            score -= 12  # 质量有问题

    # 新店全好评警惕：评分极高 + snippet 含新开关键词
    if rating and rating >= 4.8:
        snippet = (restaurant.get('snippet', '') + restaurant.get('name', '')).lower()
        new_shop_hints = ['新开', '刚开', '开业', '试营业', '新店']
        if any(hint in snippet for hint in new_shop_hints):
            score -= 10  # 新店全好评，额外降权

    return min(max(score, 0), 100)


def merge_results(dianping_results: list, xhs_results: list) -> list:
    """合并大众点评和小红书结果"""
    merged = {}

    # 大众点评结果为基础
    for r in dianping_results:
        name = r['name']
        merged[name] = {
            **r,
            'tags': r.get('categories', []),
            'sources': ['dianping'],
            'xhs_notes': [],
            'cross_verified': False,
        }

    # 匹配小红书结果
    for note in xhs_results:
        mentioned = note.get('restaurants_mentioned', [])
        for rname in mentioned:
            # 精确匹配或包含匹配
            matched_key = None
            for key in merged:
                if rname in key or key in rname:
                    matched_key = key
                    break

            if matched_key:
                # 交叉验证！
                merged[matched_key]['cross_verified'] = True
                merged[matched_key]['sources'].append('xiaohongshu')
                merged[matched_key]['xhs_notes'].append({
                    'title': note['title'],
                    'sentiment': note['sentiment'],
                    'url': note['url'],
                })
                if note['sentiment']:
                    merged[matched_key]['xhs_sentiment'] = note['sentiment']
            else:
                # 小红书独有的餐厅
                if rname and rname not in merged:
                    merged[rname] = {
                        'name': rname,
                        'avg_price': note.get('avg_price'),
                        'score': None,
                        'categories': [],
                        'tags': [],
                        'snippet': note.get('snippet', ''),
                        'url': note.get('url'),
                        'source': 'xiaohongshu',
                        'sources': ['xiaohongshu'],
                        'xhs_notes': [{'title': note['title'], 'sentiment': note['sentiment']}],
                        'xhs_sentiment': note.get('sentiment'),
                        'cross_verified': False,
                        'is_shop_page': False,
                    }

    return list(merged.values())


def select_2plus1(merged: list, preferences: dict) -> tuple:
    """
    2+1 推荐模式
    返回：(2 家精准推荐，1 家探索推荐)
    """
    # 精准推荐：匹配度>70 + 双源验证
    precise = [r for r in merged if r.get('match_score', 50) >= 70 and r.get('cross_verified')]
    
    # 探索推荐：匹配度 60-75 + 有特色（新发现/小红书高分）
    explorer = [r for r in merged if 60 <= r.get('match_score', 50) <= 75 and r.get('xhs_sentiment') == 'positive']
    
    # 如果精准推荐不足 2 家，用高匹配度补充
    if len(precise) < 2:
        precise = sorted(merged, key=lambda x: x.get('match_score', 50), reverse=True)[:2]
    
    # 如果探索推荐没有，用匹配度 65+ 的补充
    if not explorer:
        explorer = [r for r in merged if r.get('match_score', 50) >= 65][:1]
    
    return precise[:2], explorer[:1]


def main():
    parser = argparse.ArgumentParser(description='小饭票 - 分阶段搜索（执行层，场景理解由 agent 负责）')
    parser.add_argument('query', help='搜索关键词（由 agent 场景理解后传入）')
    parser.add_argument('--city', default='', help='城市')
    parser.add_argument('--budget', type=int, help='人均预算（影响匹配度计算）')
    parser.add_argument('--max', type=int, default=15, help='最大结果数（默认 15 家）')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    parser.add_argument('--mode', choices=['normal', '2plus1'], default='normal', help='推荐模式')
    args = parser.parse_args()

    print(f"🔍 分阶段搜索中...\n", file=sys.stderr)

    # 场景理解由 agent（LLM）负责，search_all.py 只做执行
    # 如果传入了 budget，覆盖画像里的 price_range 用于匹配度计算
    preferences = load_preferences()
    if args.budget:
        b = args.budget
        preferences['price_range'] = [int(b * 0.6), int(b * 1.2)]

    # 阶段 1: 大众点评海选 50 家
    print(f"阶段 1: 大众点评海选...", file=sys.stderr)
    dp_results = search_dianping(args.query, args.city, max_results=args.max)
    for r in dp_results:
        r['match_score'] = match_score(r, preferences)
    
    # 保留匹配度>=50 的
    dp_filtered = [r for r in dp_results if r.get('match_score', 50) >= 50]
    print(f"  画像匹配后剩下 {len(dp_filtered)} 家\n", file=sys.stderr)

    # 阶段 2: 小红书交叉验证（只搜前 15-20 家）
    print(f"阶段 2: 小红书交叉验证...", file=sys.stderr)
    top_names = [r['name'] for r in dp_filtered[:15]]
    xhs_queries = [f"{name} 探店" for name in top_names]
    
    all_xhs_results = []
    for xq in xhs_queries:
        xhs_results = search_xiaohongshu(xq, max_results=5)
        all_xhs_results.extend(xhs_results)
    
    print(f"  找到 {len(all_xhs_results)} 条笔记\n", file=sys.stderr)

    # 合并
    merged = merge_results(dp_filtered, all_xhs_results)

    # 重新计算匹配度（含小红书加分）
    for r in merged:
        r['match_score'] = match_score(r, preferences)

    # 排序
    merged.sort(key=lambda x: (x.get('cross_verified', False), x['match_score']), reverse=True)

    if args.mode == '2plus1':
        precise, explorer = select_2plus1(merged, preferences)
        if args.json:
            print(json.dumps({'precise': precise, 'explorer': explorer}, ensure_ascii=False, indent=2))
            return
    elif args.json:
        print(json.dumps(merged, ensure_ascii=False, indent=2))
        return
        
        print(f"\n🍜 小饭卡 2+1 推荐：{args.query}")
        if has_prefs:
            print(f"   (已根据你的口味画像筛选)\n")
        
        print("━━━ 精准推荐 (2 家) ━━━\n")
        for i, r in enumerate(precise, 1):
            print_recommendation(i, r, has_prefs)
        
        if explorer:
            print("\n━━━ 探索推荐 (1 家) ━━━\n")
            print_recommendation(1, explorer[0], has_prefs, is_explorer=True)
    else:
        # 正常模式：输出前 10 家
        print(f"\n🍜 小饭卡推荐：{args.query} (前 10 家)")
        if has_prefs:
            print(f"   (已根据你的口味画像排序)\n")
        
        for i, r in enumerate(merged[:10], 1):
            print_recommendation(i, r, has_prefs)


def print_recommendation(index: int, r: dict, has_prefs: bool, is_explorer: bool = False):
    """打印推荐餐厅"""
    name = r['name']
    price = f"¥{r['avg_price']}" if r.get('avg_price') else ''
    score = f"⭐{r['score']}" if r.get('score') else ''
    match = f"匹配{r['match_score']:.0f}%" if has_prefs else ''

    # 来源标记
    sources = r.get('sources', [])
    if r.get('cross_verified'):
        src_mark = '✅双源验证'
    elif 'dianping' in sources and 'xiaohongshu' in sources:
        src_mark = '📊点评 +📕小红书'
    elif 'xiaohongshu' in sources:
        src_mark = '📕小红书'
    else:
        src_mark = '📊点评'

    prefix = "🎁 " if is_explorer else ""
    info = ' | '.join(p for p in [price, score, match, src_mark] if p)
    print(f"{prefix}{index}. {name}")
    if info:
        print(f"   {info}")

    # 小红书评价
    for note in r.get('xhs_notes', [])[:1]:
        sentiment_emoji = {'positive': '👍', 'negative': '⚠️', 'neutral': ''}
        s_emoji = sentiment_emoji.get(note.get('sentiment', ''), '')
        print(f"   📕 {s_emoji} {note['title'][:50]}")

    if r.get('snippet'):
        print(f"   {r['snippet'][:60]}")
    print()


if __name__ == '__main__':
    main()
