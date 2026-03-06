#!/usr/bin/env python3
"""
查看最近更新的笔记

根据官方文档：GET /notes?order_by=updated_time&order_dir=DESC

用法:
    python3 joplin_recent.py [--limit 10]
"""
import sys
import argparse
import requests
from datetime import datetime
from joplin_config import get_base_url, get_auth_params, check_config

def get_recent_notes(limit=10):
    """获取最近更新的笔记"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        print(f"📝 最近笔记 (最多 {limit} 条)")
        print("=" * 50)
        
        url = f"{base_url}/notes"
        query_params = {
            **params,
            'limit': limit,
            'order_by': 'updated_time',
            'order_dir': 'DESC',
            'fields': 'id,title,updated_time,parent_id'
        }
        
        response = requests.get(url, params=query_params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取失败：HTTP {response.status_code}")
            return False
        
        notes = response.json().get('items', [])
        
        if not notes:
            print("💭 暂无笔记")
            return True
        
        for i, note in enumerate(notes, 1):
            title = note.get('title', '未命名')
            note_id = note.get('id')
            updated = note.get('updated_time', 0)
            parent = note.get('parent_id', '')
            
            # 格式化时间
            if updated:
                updated_dt = datetime.fromtimestamp(updated / 1000)
                updated_str = updated_dt.strftime('%m-%d %H:%M')
            else:
                updated_str = '未知'
            
            # 显示信息
            print(f"{i}. {title}")
            print(f"   ID: {note_id} | 更新：{updated_str} | 笔记本：{parent[:8] if parent else '无'}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='查看最近更新的笔记')
    parser.add_argument('--limit', type=int, default=10, help='最大数量 (默认：10)')
    
    args = parser.parse_args()
    
    success = get_recent_notes(args.limit)
    sys.exit(0 if success else 1)
