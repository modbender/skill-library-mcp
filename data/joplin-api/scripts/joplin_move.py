#!/usr/bin/env python3
"""
移动笔记到其他笔记本

根据官方文档：PUT /notes/:id (修改 parent_id)

用法:
    python3 joplin_move.py --note-id <id> --to-folder <folder_id>
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def find_folder_by_name(name):
    """通过名称查找笔记本"""
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

def move_note(note_id, folder_id):
    """移动笔记到其他笔记本"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        # 更新笔记的 parent_id
        url = f"{base_url}/notes/{note_id}"
        response = requests.put(url, params=params, json={'parent_id': folder_id}, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 笔记不存在：{note_id}")
            return False
        elif response.status_code != 200:
            print(f"❌ 移动失败：HTTP {response.status_code}")
            print(f"   {response.text}")
            return False
        
        print(f"✅ 笔记已移动")
        print(f"   笔记 ID: {note_id}")
        print(f"   新笔记本：{folder_id}")
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='移动笔记到其他笔记本')
    parser.add_argument('--note-id', required=True, help='笔记 ID')
    parser.add_argument('--to-folder', required=True, help='目标笔记本 ID 或名称')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    # 检查目标是 ID 还是名称
    folder_id = args.to_folder
    
    # 如果不是有效的 ID 格式（32 位 hex），尝试按名称查找
    if len(folder_id) != 32 or not all(c in '0123456789abcdef' for c in folder_id.lower()):
        folder_id = find_folder_by_name(args.to_folder)
        if not folder_id:
            print(f"❌ 找不到笔记本：{args.to_folder}")
            sys.exit(1)
        print(f"✅ 找到笔记本：{args.to_folder} (ID: {folder_id})")
    
    success = move_note(args.note_id, folder_id)
    sys.exit(0 if success else 1)
