#!/usr/bin/env python3
"""
删除笔记

根据官方文档：DELETE /notes/:id
https://joplinapp.org/help/api/references/rest_api#delete-notesid

注意：默认移动到回收站，添加 --permanent 永久删除

用法:
    python3 joplin_delete.py --id <note_id> [--permanent]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def delete_note(note_id, permanent=False):
    """删除笔记"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/notes/{note_id}"
        query_params = params.copy()
        
        if permanent:
            query_params['permanent'] = '1'
        
        response = requests.delete(url, params=query_params, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 笔记不存在：{note_id}")
            return False
        elif response.status_code != 200:
            print(f"❌ 删除失败：HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
        
        if permanent:
            print(f"✅ 笔记已永久删除")
        else:
            print(f"✅ 笔记已移动到回收站")
        print(f"   ID: {note_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='删除 Joplin 笔记')
    parser.add_argument('--id', required=True, help='笔记 ID')
    parser.add_argument('--permanent', action='store_true',
                        help='永久删除 (默认：移动到回收站)')
    
    args = parser.parse_args()
    
    success = delete_note(args.id, args.permanent)
    sys.exit(0 if success else 1)
