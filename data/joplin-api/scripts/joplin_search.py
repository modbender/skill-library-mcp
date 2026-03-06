#!/usr/bin/env python3
"""
搜索笔记

根据官方文档：GET /search
https://joplinapp.org/help/api/references/rest_api#searching

用法:
    python3 joplin_search.py "关键词" [--type note|folder|tag] [--limit 10]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def search(query, item_type='note', limit=10):
    """搜索笔记"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        print(f"🔍 搜索：{query}")
        print(f"   类型：{item_type}")
        print(f"   数量：最多 {limit} 条")
        print("=" * 50)
        
        url = f"{base_url}/search"
        query_params = {
            **params,
            'query': query,
            'limit': limit,
        }
        
        # 官方文档：type 参数指定项目类型
        type_map = {
            'note': '笔记',
            'folder': '笔记本',
            'tag': '标签',
        }
        
        if item_type in type_map:
            query_params['type'] = item_type
        
        response = requests.get(url, params=query_params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 搜索失败：HTTP {response.status_code}")
            return False
        
        result = response.json()
        items = result.get('items', [])
        
        if not items:
            print(f"💭 未找到匹配的{type_map.get(item_type, '项目')}")
            return True
        
        for i, item in enumerate(items, 1):
            title = item.get('title', '未命名')
            item_id = item.get('id', '未知')
            
            # 高亮显示
            print(f"\n{i}. {title}")
            print(f"   ID: {item_id}")
            
            # 笔记显示正文预览
            if item_type == 'note' and item.get('body'):
                body_preview = item['body'][:200]
                if len(item['body']) > 200:
                    body_preview += '...'
                print(f"   预览：{body_preview}")
            
            # 笔记本显示路径
            if item_type == 'folder' and item.get('parent_id'):
                print(f"   父笔记本：{item['parent_id']}")
        
        print(f"\n✅ 找到 {len(items)} 条结果")
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='搜索 Joplin 笔记')
    parser.add_argument('query', help='搜索关键词')
    parser.add_argument('--type', default='note', choices=['note', 'folder', 'tag'],
                        help='搜索类型 (默认：note)')
    parser.add_argument('--limit', type=int, default=10, help='最大结果数 (默认：10)')
    
    args = parser.parse_args()
    
    success = search(args.query, args.type, args.limit)
    sys.exit(0 if success else 1)
