#!/usr/bin/env python3
"""
标签管理

根据官方文档:
- GET /tags - 获取所有标签
- POST /tags - 创建标签
- DELETE /tags/:id - 删除标签
- POST /tags/:id/notes/:note_id - 添加标签到笔记
- DELETE /tags/:id/notes/:note_id - 从笔记移除标签

用法:
    python3 joplin_tags.py list|add|remove [参数]
"""
import sys
import argparse
import requests
from joplin_config import get_base_url, get_auth_params, check_config

def list_tags():
    """列出所有标签"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/tags"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取失败：HTTP {response.status_code}")
            return False
        
        tags = response.json().get('items', [])
        
        if not tags:
            print("💭 暂无标签")
            return True
        
        print("🏷️  标签列表")
        print("=" * 50)
        
        for i, tag in enumerate(tags, 1):
            title = tag.get('title', '未命名')
            tag_id = tag.get('id')
            print(f"{i}. #{title}")
            print(f"   ID: {tag_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def create_tag(name):
    """创建标签"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/tags"
        response = requests.post(url, params=params, json={'title': name}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 标签已创建")
            print(f"   名称：#{name}")
            print(f"   ID: {result['id']}")
            return True
        else:
            print(f"❌ 创建失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def add_tag_to_note(note_id, tag_name):
    """添加标签到笔记"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        # 先查找或创建标签
        tags_resp = requests.get(f"{base_url}/tags", params=params, timeout=10)
        tags = tags_resp.json().get('items', [])
        
        tag_id = None
        for tag in tags:
            if tag['title'] == tag_name:
                tag_id = tag['id']
                break
        
        if not tag_id:
            # 标签不存在，创建它
            create_result = create_tag(tag_name)
            if not create_result:
                return False
            # 重新获取标签 ID
            tags_resp = requests.get(f"{base_url}/tags", params=params, timeout=10)
            for tag in tags_resp.json().get('items', []):
                if tag['title'] == tag_name:
                    tag_id = tag['id']
                    break
        
        # 添加标签到笔记
        url = f"{base_url}/tags/{tag_id}/notes/{note_id}"
        response = requests.post(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 标签已添加")
            print(f"   笔记：{note_id}")
            print(f"   标签：#{tag_name}")
            return True
        else:
            print(f"❌ 添加失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def remove_tag_from_note(note_id, tag_id):
    """从笔记移除标签"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/tags/{tag_id}/notes/{note_id}"
        response = requests.delete(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 标签已移除")
            print(f"   笔记：{note_id}")
            print(f"   标签 ID: {tag_id}")
            return True
        else:
            print(f"❌ 移除失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def delete_tag(tag_id):
    """删除标签"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        url = f"{base_url}/tags/{tag_id}"
        response = requests.delete(url, params=params, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 标签已删除")
            print(f"   ID: {tag_id}")
            return True
        else:
            print(f"❌ 删除失败：HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='标签管理')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list 命令
    subparsers.add_parser('list', help='列出所有标签')
    
    # create 命令
    create_parser = subparsers.add_parser('create', help='创建标签')
    create_parser.add_argument('--name', required=True, help='标签名称')
    
    # add 命令
    add_parser = subparsers.add_parser('add', help='添加标签到笔记')
    add_parser.add_argument('--note-id', required=True, help='笔记 ID')
    add_parser.add_argument('--tag', required=True, help='标签名称')
    
    # remove 命令
    remove_parser = subparsers.add_parser('remove', help='从笔记移除标签')
    remove_parser.add_argument('--note-id', required=True, help='笔记 ID')
    remove_parser.add_argument('--tag-id', required=True, help='标签 ID')
    
    # delete 命令
    delete_parser = subparsers.add_parser('delete', help='删除标签')
    delete_parser.add_argument('--id', required=True, help='标签 ID')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    if args.command == 'list':
        success = list_tags()
    elif args.command == 'create':
        success = create_tag(args.name)
    elif args.command == 'add':
        success = add_tag_to_note(args.note_id, args.tag)
    elif args.command == 'remove':
        success = remove_tag_from_note(args.note_id, args.tag_id)
    elif args.command == 'delete':
        success = delete_tag(args.id)
    else:
        parser.print_help()
        sys.exit(1)
    
    sys.exit(0 if success else 1)
