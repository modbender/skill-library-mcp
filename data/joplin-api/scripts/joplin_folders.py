#!/usr/bin/env python3
"""
笔记本管理

根据官方文档:
- GET /folders - 获取所有笔记本
- POST /folders - 创建笔记本
- PUT /folders/:id - 更新笔记本
- DELETE /folders/:id - 删除笔记本

用法:
    python3 joplin_folders.py list|create|rename|delete [参数]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def list_folders():
    """列出所有笔记本"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/folders"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取失败：HTTP {response.status_code}")
            return False
        
        folders = response.json().get('items', [])
        
        if not folders:
            print("💭 暂无笔记本")
            return True
        
        print("📁 笔记本列表")
        print("=" * 50)
        
        for i, folder in enumerate(folders, 1):
            title = folder.get('title', '未命名')
            folder_id = folder.get('id')
            parent = folder.get('parent_id', '')
            parent_info = f" (父：{parent[:8]}...)" if parent else ""
            print(f"{i}. {title}{parent_info}")
            print(f"   ID: {folder_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def create_folder(name, parent_id=None):
    """创建笔记本"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        data = {'title': name}
        if parent_id:
            data['parent_id'] = parent_id
        
        url = f"{base_url}/folders"
        response = requests.post(url, params=params, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 笔记本已创建")
            print(f"   名称：{name}")
            print(f"   ID: {result['id']}")
            return True
        else:
            print(f"❌ 创建失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def rename_folder(folder_id, new_name):
    """重命名笔记本"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/folders/{folder_id}"
        response = requests.put(url, params=params, json={'title': new_name}, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 笔记本已重命名")
            print(f"   ID: {folder_id}")
            print(f"   新名称：{new_name}")
            return True
        else:
            print(f"❌ 重命名失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def delete_folder(folder_id, permanent=False):
    """删除笔记本"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/folders/{folder_id}"
        query_params = params.copy()
        
        if permanent:
            query_params['permanent'] = '1'
        
        response = requests.delete(url, params=query_params, timeout=10)
        
        if response.status_code == 404:
            print(f"❌ 笔记本不存在：{folder_id}")
            return False
        elif response.status_code != 200:
            print(f"❌ 删除失败：HTTP {response.status_code}")
            return False
        
        if permanent:
            print(f"✅ 笔记本已永久删除")
        else:
            print(f"✅ 笔记本已移动到回收站")
        print(f"   ID: {folder_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='笔记本管理')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有笔记本')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建笔记本')
    create_parser.add_argument('--name', required=True, help='笔记本名称')
    create_parser.add_argument('--parent', help='父笔记本 ID')
    
    # rename 命令
    rename_parser = subparsers.add_parser('rename', help='重命名笔记本')
    rename_parser.add_argument('--id', required=True, help='笔记本 ID')
    rename_parser.add_argument('--name', required=True, help='新名称')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除笔记本')
    delete_parser.add_argument('--id', required=True, help='笔记本 ID')
    delete_parser.add_argument('--permanent', action='store_true', help='永久删除')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    if args.command == 'list':
        success = list_folders()
    elif args.command == 'create':
        success = create_folder(args.name, args.parent)
    elif args.command == 'rename':
        success = rename_folder(args.id, args.name)
    elif args.command == 'delete':
        success = delete_folder(args.id, args.permanent)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)
