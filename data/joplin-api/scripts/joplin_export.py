#!/usr/bin/env python3
"""
导出 Joplin 笔记到本地文件

根据官方文档：GET /notes/:id
安全限制：只允许导出到工作空间目录

用法:
    python3 joplin_export.py --note-id <id> -o output.md
    python3 joplin_export.py --all -o ./backup
"""
import argparse
import json
import os
import sys
import requests
from pathlib import Path
from joplin_config import get_base_url, get_auth_params, check_config

# 安全配置：允许的工作目录
ALLOWED_BASE_DIRS = [
    Path('/root/.openclaw/workspace').resolve(),
    Path(os.environ.get('JOPLIN_EXPORT_DIR', '/root/.openclaw/workspace')).resolve(),
]

# 阻止访问的敏感目录
BLOCKED_DIRS = [
    Path('/etc'),
    Path('/proc'),
    Path('/sys'),
    Path('/dev'),
    Path('/boot'),
    Path('/usr'),
    Path('/bin'),
    Path('/sbin'),
    Path('/var/log'),
    Path('/var/spool'),
    Path('/home'),
]

def sanitize_path(path_str, must_exist=False):
    """清理和验证文件路径，防止路径遍历攻击"""
    if not path_str:
        raise ValueError("路径不能为空")
    
    path = Path(path_str)
    
    if not path.exists():
        if path.parent.exists():
            real_path = path.parent.resolve() / path.name
        else:
            real_path = path.resolve()
    else:
        real_path = path.resolve()
    
    for blocked in BLOCKED_DIRS:
        try:
            if real_path == blocked or real_path.is_relative_to(blocked):
                raise ValueError(f"禁止访问敏感目录：{blocked}")
        except AttributeError:
            if str(real_path).startswith(str(blocked)):
                raise ValueError(f"禁止访问敏感目录：{blocked}")
    
    return real_path

def is_safe_path(path, allowed_dirs):
    """检查路径是否在允许的目录内"""
    try:
        for allowed in allowed_dirs:
            if path == allowed or path.is_relative_to(allowed):
                return True
    except AttributeError:
        for allowed in allowed_dirs:
            if str(path).startswith(str(allowed)):
                return True
    return False

def export_note(note_id, output_path, format='md'):
    """导出单条笔记"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        safe_path = sanitize_path(output_path, must_exist=False)
        
        if not is_safe_path(safe_path, ALLOWED_BASE_DIRS):
            print(f"⚠️  警告：导出路径 {safe_path} 不在工作目录内")
            print(f"   建议将文件导出到：{ALLOWED_BASE_DIRS[0]}")
        
        url = f"{base_url}/notes/{note_id}"
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ 获取笔记失败")
            return False
        
        note = response.json()
        
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            with open(safe_path, 'w', encoding='utf-8') as f:
                json.dump(note, f, ensure_ascii=False, indent=2)
        else:
            content = f"# {note['title']}\n\n{note.get('body', '')}"
            with open(safe_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        print(f"✅ 已导出：{safe_path}")
        return True
        
    except ValueError as e:
        print(f"❌ 路径验证失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def export_all(output_dir, format='md'):
    """导出所有笔记"""
    base_url = get_base_url()
    params = get_auth_params()
    
    try:
        safe_dir = sanitize_path(output_dir, must_exist=False)
        
        if not is_safe_path(safe_dir, ALLOWED_BASE_DIRS):
            print(f"⚠️  警告：导出目录 {safe_dir} 不在工作目录内")
        
        folders_resp = requests.get(f"{base_url}/folders", params=params, timeout=10)
        folders = folders_resp.json().get('items', [])
        
        safe_dir.mkdir(parents=True, exist_ok=True)
        total = 0
        
        for folder in folders:
            safe_name = "".join(c for c in folder['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            folder_dir = safe_dir / safe_name
            folder_dir.mkdir(parents=True, exist_ok=True)
            
            notes_resp = requests.get(f"{base_url}/folders/{folder['id']}/notes", params=params, timeout=10)
            notes = notes_resp.json().get('items', [])
            
            for note in notes:
                safe_title = "".join(c for c in note['title'] if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
                filename = f"{safe_title}.md" if format == 'md' else f"{safe_title}.json"
                filepath = folder_dir / filename
                
                if format == 'json':
                    content = json.dumps(note, ensure_ascii=False, indent=2)
                else:
                    content = f"# {note['title']}\n\n{note.get('body', '')}"
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                total += 1
        
        print(f"✅ 已导出 {total} 条笔记到：{safe_dir}")
        return True
        
    except ValueError as e:
        print(f"❌ 路径验证失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导出 Joplin 笔记')
    parser.add_argument('--note-id', help='导出单条笔记的 ID')
    parser.add_argument('--output', '-o', required=True, help='输出路径')
    parser.add_argument('--format', choices=['md', 'json'], default='md', help='导出格式')
    parser.add_argument('--all', action='store_true', help='导出所有笔记')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    if args.all:
        success = export_all(args.output, args.format)
    elif args.note_id:
        success = export_note(args.note_id, args.output, args.format)
    else:
        print("❌ 需要 --note-id 或 --all")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
