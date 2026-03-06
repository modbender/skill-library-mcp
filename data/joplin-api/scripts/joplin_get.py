#!/usr/bin/env python3
"""
获取笔记详情

根据官方文档：GET /notes/:id
https://joplinapp.org/help/api/references/rest_api#get-notesid

用法:
    python3 joplin_get.py --id <note_id> [--fields title,body,updated_time]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def get_note(note_id, fields=None):
    """获取笔记详情"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/notes/{note_id}"
        
        if fields:
            params['fields'] = fields
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 笔记不存在：{note_id}")
            return False
        elif response.status_code != 200:
            print(f"❌ 获取失败：HTTP {response.status_code}")
            return False
        
        note = response.json()
        
        print(f"📄 笔记详情")
        print("=" * 50)
        print(f"标题：{note.get('title', '未命名')}")
        print(f"ID: {note.get('id')}")
        print()
        
        # 显示正文
        body = note.get('body', '')
        if body:
            print("内容:")
            print("-" * 50)
            print(body)
            print("-" * 50)
        else:
            print("内容：(空)")
        
        # 显示元数据
        print()
        print("元数据:")
        
        if note.get('parent_id'):
            print(f"  笔记本：{note['parent_id']}")
        
        if note.get('updated_time'):
            from datetime import datetime
            updated = datetime.fromtimestamp(note['updated_time'] / 1000)
            print(f"  更新时间：{updated.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if note.get('created_time'):
            from datetime import datetime
            created = datetime.fromtimestamp(note['created_time'] / 1000)
            print(f"  创建时间：{created.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if note.get('is_todo'):
            print(f"  待办：是")
            if note.get('todo_completed'):
                print(f"  状态：已完成")
            else:
                print(f"  状态：未完成")
        
        if note.get('tags'):
            print(f"  标签：{', '.join(note['tags'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取笔记详情')
    parser.add_argument('--id', required=True, help='笔记 ID')
    parser.add_argument('--fields', help='要获取的字段 (逗号分隔)')
    
    args = parser.parse_args()
    
    success = get_note(args.id, args.fields)
    sys.exit(0 if success else 1)
