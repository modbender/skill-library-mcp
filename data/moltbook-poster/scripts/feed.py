#!/usr/bin/env python3
"""
Moltbook 动态获取工具
用法: python feed.py [--global] [--sort hot|new] [--submolt SUBMOLT] [--limit N]
"""

import argparse
import json

WORKSPACE = r'C:\Users\10405\.openclaw\workspace'
CONFIG_FILE = WORKSPACE + r'\configs\moltbook.json'

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def get_headers(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

def get_feed(sort='new', limit=15, headers=None):
    """获取订阅动态"""
    import requests
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/feed?sort={sort}&limit={limit}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取动态失败: {r.status_code}'}
    
    data = r.json()
    posts = data.get('posts', [])
    
    result = {
        'success': True,
        'source': 'feed',
        'sort': sort,
        'count': len(posts),
        'posts': []
    }
    
    for p in posts:
        result['posts'].append({
            'id': p.get('id', '')[:8],
            'title': p.get('title', 'Untitled')[:50],
            'author': p.get('author', {}).get('name', 'unknown'),
            'submolt': p.get('submolt', {}).get('display_name', 'unknown'),
            'upvotes': p.get('upvotes', 0),
            'comments': p.get('comment_count', 0),
            'url': f"https://moltbook.com/p/{p.get('id', '')}"
        })
    
    return result

def get_global_posts(sort='new', limit=15, headers=None):
    """获取全局新鲜事"""
    import requests
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/posts?sort={sort}&limit={limit}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取全局帖子失败: {r.status_code}'}
    
    data = r.json()
    posts = data.get('posts', [])
    
    result = {
        'success': True,
        'source': 'global',
        'sort': sort,
        'count': len(posts),
        'posts': []
    }
    
    for p in posts:
        result['posts'].append({
            'id': p.get('id', '')[:8],
            'title': p.get('title', 'Untitled')[:50],
            'author': p.get('author', {}).get('name', 'unknown'),
            'submolt': p.get('submolt', {}).get('display_name', 'unknown'),
            'upvotes': p.get('upvotes', 0),
            'comments': p.get('comment_count', 0),
            'url': f"https://moltbook.com/p/{p.get('id', '')}"
        })
    
    return result

def get_submolt_feed(submolt_name, sort='new', limit=15, headers=None):
    """获取特定子社区动态"""
    import requests
    
    # 先获取子社区ID
    r = requests.get(
        f'https://www.moltbook.com/api/v1/submolts/{submolt_name}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'子社区不存在: {submolt_name}'}
    
    submolt_id = r.json().get('submolt', {}).get('id')
    
    r = requests.get(
        f'https://www.moltbook.com/api/v1/submolts/{submolt_id}/feed?sort={sort}&limit={limit}',
        headers=headers
    )
    
    if r.status_code != 200:
        return {'success': False, 'error': f'获取子社区动态失败: {r.status_code}'}
    
    data = r.json()
    posts = data.get('posts', [])
    
    result = {
        'success': True,
        'source': f'submolt/{submolt_name}',
        'sort': sort,
        'count': len(posts),
        'posts': []
    }
    
    for p in posts:
        result['posts'].append({
            'id': p.get('id', '')[:8],
            'title': p.get('title', 'Untitled')[:50],
            'author': p.get('author', {}).get('name', 'unknown'),
            'upvotes': p.get('upvotes', 0),
            'comments': p.get('comment_count', 0),
            'url': f"https://moltbook.com/p/{p.get('id', '')}"
        })
    
    return result

def print_posts(result, max_count=10):
    """打印帖子列表"""
    source_map = {
        'feed': '订阅动态',
        'global': '全局新鲜事',
    }
    
    source = source_map.get(result.get('source'), result.get('source', ''))
    sort = result.get('sort', 'new')
    sort_name = '热门' if sort == 'hot' else '最新'
    
    print(f"\n{'='*60}")
    print(f"  {source} - {sort_name}")
    print(f"{'='*60}\n")
    
    for i, p in enumerate(result.get('posts', [])[:max_count], 1):
        print(f"{i}. [{p['id']}] {p['title']}")
        print(f"   @{p['author']} | 👍 {p['upvotes']} | 💬 {p['comments']}")
        print(f"   📍 {p.get('submolt', 'unknown')}")
        print(f"   🔗 {p['url']}\n")

def main():
    parser = argparse.ArgumentParser(description='Moltbook Feed Tool')
    parser.add_argument('--global', action='store_true', dest='is_global', help='Get global posts')
    parser.add_argument('--submolt', help='Specify submolt name')
    parser.add_argument('--sort', choices=['hot', 'new'], default='new', help='Sort order')
    parser.add_argument('--limit', type=int, default=15, help='Number of posts')
    parser.add_argument('--json', action='store_true', help='Output JSON')
    
    args = parser.parse_args()
    
    config = load_config()
    headers = get_headers(config['api_key'])
    
    if args.submolt:
        result = get_submolt_feed(args.submolt, args.sort, args.limit, headers)
    elif args.is_global:
        result = get_global_posts(args.sort, args.limit, headers)
    else:
        result = get_feed(args.sort, args.limit, headers)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        if result['success']:
            print_posts(result)
        else:
            print(f"✗ 获取失败: {result.get('error')}")
    
    return 0 if result['success'] else 1

if __name__ == '__main__':
    exit(main())
