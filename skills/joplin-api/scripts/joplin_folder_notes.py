#!/usr/bin/env python3
"""
获取笔记本内的所有笔记

根据官方文档：GET /folders/:id/notes

用法:
    python3 joplin_folder_notes.py --folder <folder_id|name> [--limit 50]
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

def get_folder_notes(folder_id, limit=50):
    """获取笔记本内的笔记"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        # 先获取笔记本信息
        folder_resp = requests.get(f"{base_url}/folders/{folder_id}", params=params, timeout=10)
        if folder_resp.status_code == 404:
            print(f"❌ 笔记本不存在：{folder_id}")
            return False
        elif folder_resp.status_code != 200:
            print(f"❌ 获取失败：HTTP {folder_resp.status_code}")
            return False
        
        folder = folder_resp.json()
        folder_name = folder.get('title', '未命名')
        
        print(f"📁 笔记本：{folder_name}")
        print(f"   ID: {folder_id}")
        print("=" * 50)
        
        # 获取笔记列表
        url = f"{base_url}/folders/{folder_id}/notes"
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
        
        notes = response.json().get('items', [])
        
        if not notes:
            print("💭 此笔记本内暂无笔记")
            return True
        
        print(f"📄 笔记列表 ({len(notes)} 条)")
        print("-" * 50)
        
        for i, note in enumerate(notes, 1):
            title = note.get('title', '未命名')
            note_id = note.get('id')
            print(f"{i}. {title}")
            print(f"   ID: {note_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='获取笔记本内的笔记')
    parser.add_argument('--folder', required=True, help='笔记本 ID 或名称')
    parser.add_argument('--limit', type=int, default=50, help='最大数量 (默认：50)')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    # 检查目标是 ID 还是名称
    folder_id = args.folder
    
    # 如果不是有效的 ID 格式，尝试按名称查找
    if len(folder_id) != 32 or not all(c in '0123456789abcdef' for c in folder_id.lower()):
        folder_id = find_folder_by_name(args.folder)
        if not folder_id:
            print(f"❌ 找不到笔记本：{args.folder}")
            sys.exit(1)
        print(f"✅ 找到笔记本：{args.folder} (ID: {folder_id})")
    
    success = get_folder_notes(folder_id, args.limit)
    sys.exit(0 if success else 1)
