#!/usr/bin/env python3
"""
导入 Markdown 文件到 Joplin

根据官方文档：POST /notes
安全限制：只允许从工作空间目录读取文件

用法:
    python3 joplin_import.py file.md [--folder "笔记本名称"]
    python3 joplin_import.py ./notes_dir --folder "批量导入"
"""
import argparse
import os
import sys
import requests
from pathlib import Path
from joplin_config import get_base_url, get_auth_params, check_config

# 安全配置：允许的工作目录
ALLOWED_BASE_DIRS = [
    Path('/root/.openclaw/workspace').resolve(),
    Path(os.environ.get('JOPLIN_IMPORT_DIR', '/root/.openclaw/workspace')).resolve(),
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

def sanitize_path(path_str, must_exist=True):
    """清理和验证文件路径，防止路径遍历攻击"""
    if not path_str:
        raise ValueError("路径不能为空")
    
    path = Path(path_str)
    
    if must_exist and not path.exists():
        raise FileNotFoundError(f"路径不存在：{path_str}")
    
    real_path = path.resolve()
    
    for blocked in BLOCKED_DIRS:
        try:
            if real_path == blocked or real_path.is_relative_to(blocked):
                raise ValueError(f"禁止访问敏感目录：{blocked}")
        except AttributeError:
            if str(real_path).startswith(str(blocked)):
                raise ValueError(f"禁止访问敏感目录：{blocked}")
    
    if not is_safe_path(real_path, ALLOWED_BASE_DIRS):
        raise ValueError(
            f"路径 {real_path} 不在允许的工作目录内\n"
            f"   允许的工作目录：{ALLOWED_BASE_DIRS[0]}\n"
            f"   如需导入其他目录的文件，请先复制到工作目录"
        )
    
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

def create_folder(name):
    """创建笔记本"""
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

def import_file(file_path, folder_id=None, folder_name=None):
    """导入单个文件"""
    base_url = get_base_url()
    params = get_auth_params()
    
    if folder_name and not folder_id:
        folder_id = find_folder_by_name(folder_name)
        if not folder_id:
            folder_id = create_folder(folder_name)
            if folder_id:
                print(f"✅ 创建笔记本：{folder_name}")
    
    try:
        safe_path = sanitize_path(file_path, must_exist=True)
        
        with open(safe_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = safe_path.name
        title = safe_path.stem
        
        lines = content.split('\n')
        if lines and lines[0].startswith('# '):
            title = lines[0][2:].strip()
            content = '\n'.join(lines[1:]).strip()
        
        data = {'title': title, 'body': content}
        if folder_id:
            data['parent_id'] = folder_id
        
        url = f"{base_url}/notes"
        response = requests.post(url, params=params, json=data, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ 已导入：{title}")
            return True
        else:
            print(f"❌ 导入失败：{filename}")
            return False
            
    except ValueError as e:
        print(f"❌ 路径验证失败：{e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

def import_directory(dir_path, folder_name=None):
    """导入整个目录"""
    imported = 0
    failed = 0
    
    try:
        safe_dir = sanitize_path(dir_path, must_exist=True)
        
        if not safe_dir.is_dir():
            print(f"❌ 不是目录：{dir_path}")
            return False
        
        for root, dirs, files in os.walk(safe_dir):
            rel_path = Path(root).relative_to(safe_dir)
            if rel_path == Path('.'):
                current_folder = folder_name
            else:
                current_folder = folder_name or str(rel_path).replace(os.sep, '/')
            
            for file in files:
                if file.endswith('.md'):
                    file_path = Path(root) / file
                    if import_file(str(file_path), folder_name=current_folder):
                        imported += 1
                    else:
                        failed += 1
        
        print(f"\n📊 导入完成：{imported} 成功，{failed} 失败")
        return failed == 0
        
    except ValueError as e:
        print(f"❌ 路径验证失败：{e}")
        return False
    except Exception as e:
        print(f"❌ 错误：{e}")
        return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='导入 Markdown 到 Joplin')
    parser.add_argument('path', help='文件或目录路径（必须在工作空间内）')
    parser.add_argument('--folder', help='目标笔记本名称')
    parser.add_argument('--folder-id', help='目标笔记本 ID')
    
    args = parser.parse_args()
    
    ok, msg = check_config()
    if not ok:
        print(f"❌ {msg}")
        sys.exit(1)
    
    try:
        safe_path = sanitize_path(args.path, must_exist=False)
    except (ValueError, FileNotFoundError) as e:
        print(f"❌ {e}")
        sys.exit(1)
    
    if safe_path.exists() and safe_path.is_file():
        success = import_file(str(safe_path), args.folder_id, args.folder)
    elif safe_path.exists() and safe_path.is_dir():
        success = import_directory(str(safe_path), args.folder)
    else:
        print(f"❌ 路径不存在：{args.path}")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
