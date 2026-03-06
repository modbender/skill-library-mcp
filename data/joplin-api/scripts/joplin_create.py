#!/usr/bin/env python3
"""
创建 Joplin 笔记

根据官方文档：POST /notes
https://joplinapp.org/help/api/references/rest_api#post-notes

用法:
    python3 joplin_create.py --title "标题" --body "内容" [--folder "笔记本名称"]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def find_folder_by_name(name):
    """通过名称查找笔记本 (官方文档：GET /folders)"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/folders"
        response = requests.get(url, params=params, timeout=10)
        folders = response.json()
        
        for folder in folders.get('items', []):
            if folder['title'] == name:
                return folder['id']
        return None
    except:
        return None

def create_folder(name):
    """创建笔记本 (官方文档：POST /folders)"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/folders"
        response = requests.post(url, params=params, json={'title': name}, timeout=10)
        if response.status_code == 200:
            return response.json()['id']
        return None
    except:
        return None

def create_note(title, body, folder_id=None):
    """
    创建笔记 (官方文档：POST /notes)
    
    支持:
    - Markdown body
    - HTML body_html
    - 指定笔记本 parent_id
    """
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        data = {
            'title': title,
            'body': body
        }
        
        if folder_id:
            data['parent_id'] = folder_id
        
        url = f"{base_url}/notes"
        response = requests.post(url, params=params, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 笔记已创建")
            print(f"   标题：{title}")
            print(f"   ID: {result['id']}")
            if folder_id:
                print(f"   笔记本：{folder_id}")
            return True
        else:
            print(f"❌ 创建失败：HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='创建 Joplin 笔记')
    parser.add_argument('--title', required=True, help='笔记标题')
    parser.add_argument('--body', default='', help='笔记内容 (Markdown)')
    parser.add_argument('--folder', help='目标笔记本名称')
    parser.add_argument('--folder-id', help='目标笔记本 ID')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    folder_id = args.folder_id
    
    if args.folder and not folder_id:
        folder_id = find_folder_by_name(args.folder)
        if not folder_id:
            # 笔记本不存在，创建它
            folder_id = create_folder(args.folder)
            if folder_id:
                print(f"✅ 创建笔记本：{args.folder}")
            else:
                print(f"❌ 无法创建笔记本：{args.folder}")
                sys.exit(1)
    
    success = create_note(args.title, args.body, folder_id)
    sys.exit(0 if success else 1)
