#!/usr/bin/env python3
"""
Joplin 统计信息

用法: python3 joplin_stats.py
"""
import sys
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def get_stats():
    """获取 Joplin 统计信息"""
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        return False
    
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        print("📊 Joplin 统计信息")
        print("=" * 50)
        
        # 获取笔记本数量 (官方文档：GET /folders)
        folders_resp = requests.get(f"{base_url}/folders", params={**params, 'fields': 'id'}, timeout=10)
        folders = folders_resp.json().get('items', [])
        folder_count = len(folders)
        
        # 获取笔记数量 (官方文档：GET /notes)
        notes_resp = requests.get(f"{base_url}/notes", params={**params, 'fields': 'id'}, timeout=10)
        notes = notes_resp.json().get('items', [])
        note_count = len(notes)
        
        # 获取标签数量 (官方文档：GET /tags)
        tags_resp = requests.get(f"{base_url}/tags", params={**params, 'fields': 'id'}, timeout=10)
        tags = tags_resp.json().get('items', [])
        tag_count = len(tags)
        
        print(f"📁 笔记本：{folder_count} 个")
        print(f"📄 笔记：{note_count} 条")
        print(f"🏷️  标签：{tag_count} 个")
        print()
        
        # 笔记本详情
        if folder_count > 0:
            print("📈 笔记本详情:")
            for folder in folders:
                # 获取每个笔记本的笔记数量
                notes_in_folder = requests.get(
                    f"{base_url}/folders/{folder['id']}/notes",
                    params={**params, 'fields': 'id'},
                    timeout=10
                ).json().get('items', [])
                print(f"   • {folder.get('title', '未命名')}: {len(notes_in_folder)} 条笔记")
        else:
            print("💡 提示：还没有笔记本，可以创建一个开始使用")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    success = get_stats()
    sys.exit(0 if success else 1)
