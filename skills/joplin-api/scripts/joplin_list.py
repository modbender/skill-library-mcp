#!/usr/bin/env python3
"""
列出 Joplin 笔记/笔记本/标签

根据官方文档:
- GET /notes - 列出所有笔记
- GET /folders - 列出所有笔记本
- GET /tags - 列出所有标签

用法:
    python3 joplin_list.py --type notes|folders|tags [--limit 10]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def list_items(item_type, limit=10):
    """列出项目"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    # 官方文档支持的类型
    type_map = {
        'notes': '笔记',
        'folders': '笔记本',
        'tags': '标签',
    }
    
    if item_type not in type_map:
        print(f"❌ 不支持的类型：{item_type}")
        print(f"   可用类型：{', '.join(type_map.keys())}")
        return False
    
    try:
        print(f"📋 {type_map[item_type]} (最多 {limit} 条)")
        print("=" * 50)
        
        url = f"{base_url}/{item_type}"
        query_params = {
            **params,
            'limit': limit,
            'order_by': 'updated_time',
            'order_dir': 'DESC'
        }
        
        response = requests.get(url, params=query_params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取失败：HTTP {response.status_code}")
            return False
        
        result = response.json()
        items = result.get('items', [])
        
        if not items:
            print(f"💭 暂无{type_map[item_type]}")
            return True
        
        for i, item in enumerate(items, 1):
            title = item.get('title', '未命名')
            item_id = item.get('id', '未知')
            
            if item_type == 'notes':
                # 笔记显示更多详情
                updated = item.get('updated_time', 0)
                if updated:
                    from datetime import datetime
                    updated_str = datetime.fromtimestamp(updated / 1000).strftime('%m-%d %H:%M')
                    print(f"{i}. {title}")
                    print(f"   ID: {item_id} | 更新：{updated_str}")
                else:
                    print(f"{i}. {title} (ID: {item_id})")
            
            elif item_type == 'folders':
                parent = item.get('parent_id', '')
                parent_info = f" (父：{parent[:8]}...)" if parent else ""
                print(f"{i}. {title} (ID: {item_id}{parent_info})")
            
            elif item_type == 'tags':
                print(f"{i}. #{title} (ID: {item_id})")
        
        # 检查是否有更多
        if result.get('has_more', False):
            print(f"\n⚠️  还有更多{type_map[item_type]}，使用 --limit 增加数量")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='列出 Joplin 笔记/笔记本/标签')
    parser.add_argument('--type', required=True, choices=['notes', 'folders', 'tags'],
                        help='要列出的类型')
    parser.add_argument('--limit', type=int, default=10, help='最大数量 (默认：10)')
    
    args = parser.parse_args()
    
    success = list_items(args.type, args.limit)
    sys.exit(0 if success else 1)
