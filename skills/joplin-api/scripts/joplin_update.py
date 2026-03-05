#!/usr/bin/env python3
"""
更新笔记

根据官方文档：PUT /notes/:id
https://joplinapp.org/help/api/references/rest_api#put-notesid

注意：PUT 仅更新提供的字段，其他字段保持不变

用法:
    python3 joplin_update.py --id <note_id> [--title "新标题"] [--body "新内容"]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def update_note(note_id, title=None, body=None):
    """更新笔记"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    if not title and not body:
        print(f"❌ 至少需要提供 --title 或 --body")
        return False
    
    try:
        data = {}
        if title:
            data['title'] = title
        if body:
            data['body'] = body
        
        url = f"{base_url}/notes/{note_id}"
        response = requests.put(url, params=params, json=data, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 笔记不存在：{note_id}")
            return False
        elif response.status_code != 200:
            print(f"❌ 更新失败：HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
        
        result = response.json()
        print(f"✅ 笔记已更新")
        print(f"   ID: {note_id}")
        if title:
            print(f"   新标题：{title}")
        if body:
            print(f"   内容：已更新 ({len(body)} 字符)")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='更新 Joplin 笔记')
    parser.add_argument('--id', required=True, help='笔记 ID')
    parser.add_argument('--title', help='新标题')
    parser.add_argument('--body', help='新内容 (Markdown)')
    
    args = parser.parse_args()
    
    success = update_note(args.id, args.title, args.body)
    sys.exit(0 if success else 1)
