#!/usr/bin/env python3
"""
WebDAV 备份脚本
将 OpenClaw 工作目录备份到 WebDAV 服务器
"""

import os
import sys
import argparse
import tarfile
import datetime
import json
import re
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET


def load_openclaw_config():
    """从 openclaw.json 加载 webdav-backup 配置"""
    config_paths = [
        os.path.expanduser('~/.openclaw/openclaw.json'),
        os.path.expanduser('~/.config/openclaw/openclaw.json'),
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # 查找 webdav-backup 技能配置
                skills = config.get('skills', {}).get('entries', {})
                skill_config = skills.get('webdav-backup', {})
                
                if skill_config and skill_config.get('enabled', False):
                    return skill_config.get('env', {})
            except Exception:
                pass
    
    return {}


# 加载 openclaw.json 配置
openclaw_env = load_openclaw_config()

# 配置 - 优先级: 环境变量 > openclaw.json > 默认值
DEFAULT_WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
WORKSPACE = os.environ.get('OPENCLAW_WORKSPACE', DEFAULT_WORKSPACE)
WEBDAV_URL = os.environ.get('WEBDAV_URL', openclaw_env.get('WEBDAV_URL', ''))
WEBDAV_USER = os.environ.get('WEBDAV_USERNAME', openclaw_env.get('WEBDAV_USERNAME', ''))
WEBDAV_PASS = os.environ.get('WEBDAV_PASS', 
              os.environ.get('WEBDAV_PASSWORD', 
              openclaw_env.get('WEBDAV_PASS', 
              openclaw_env.get('WEBDAV_PASSWORD', ''))))
RETENTION_DAYS = 60
MIN_KEEP_COUNT = 20
BACKUP_FILENAME_RE = re.compile(r'^(?P<prefix>.+)-(?P<timestamp>\d{8}-\d{6})\.tar\.gz$')

def check_config():
    """检查 WebDAV 配置"""
    if not WEBDAV_URL or not WEBDAV_USER or not WEBDAV_PASS:
        print("❌ WebDAV 配置缺失")
        print("")
        print("配置方式一：编辑 ~/.openclaw/openclaw.json")
        print('  {')
        print('    "skills": {')
        print('      "entries": {')
        print('        "webdav-backup": {')
        print('          "enabled": true,')
        print('          "env": {')
        print('            "WEBDAV_URL": "https://dav.jianguoyun.com/dav/",')
        print('            "WEBDAV_USERNAME": "your-email",')
        print('            "WEBDAV_PASSWORD": "your-password"')
        print('          }')
        print('        }')
        print('      }')
        print('    }')
        print('  }')
        print("")
        print("配置方式二：设置环境变量")
        print("  export WEBDAV_URL='https://dav.jianguoyun.com/dav/'")
        print("  export WEBDAV_USERNAME='your-email'")
        print("  export WEBDAV_PASSWORD='your-password'")
        return False
    
    print(f"📡 WebDAV URL: {WEBDAV_URL}")
    print(f"👤 用户名: {WEBDAV_USER}")
    return True

def create_backup(source_dir, backup_name=None):
    """创建备份压缩包"""
    timestamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
    if backup_name:
        backup_file = f"{backup_name}-{timestamp}.tar.gz"
    else:
        backup_file = f"openclaw-backup-{timestamp}.tar.gz"
    
    backup_path = Path('/tmp') / backup_file
    
    print(f"📦 正在创建备份: {backup_file}")
    
    with tarfile.open(backup_path, 'w:gz') as tar:
        source = Path(source_dir)
        if source.exists():
            tar.add(source, arcname=source.name)
            print(f"✅ 已添加: {source_dir}")
        else:
            print(f"⚠️  目录不存在: {source_dir}")
    
    # 显示文件大小
    size = backup_path.stat().st_size
    print(f"📊 备份大小: {size / 1024 / 1024:.2f} MB")
    
    return backup_path

def create_webdav_opener():
    """创建带认证的 WebDAV opener"""
    parsed = urllib.parse.urlparse(WEBDAV_URL)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    password_mgr = urllib.request.HTTPPasswordMgrWithDefaultRealm()
    password_mgr.add_password(None, base_url, WEBDAV_USER, WEBDAV_PASS)
    password_mgr.add_password(None, WEBDAV_URL, WEBDAV_USER, WEBDAV_PASS)
    handler = urllib.request.HTTPBasicAuthHandler(password_mgr)
    return urllib.request.build_opener(handler)

def ensure_webdav_directory():
    """确保 WebDAV 目录存在，不存在则创建"""
    # 解析 URL，获取基础 URL 和路径
    parsed = urllib.parse.urlparse(WEBDAV_URL)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    
    # 获取 WEBDAV_URL 中的路径部分（去掉开头的 /dav/）
    webdav_path = parsed.path.strip('/')
    if webdav_path.startswith('dav/'):
        webdav_path = webdav_path[4:]  # 去掉 'dav/'
    
    # 如果没有子目录，直接返回
    if not webdav_path:
        return
    
    opener = create_webdav_opener()
    
    # 逐级创建目录
    parts = webdav_path.split('/')
    current_path = "/dav"
    for part in parts:
        if not part:
            continue
        current_path += "/" + part
        dir_url = base_url + current_path
        
        try:
            req = urllib.request.Request(dir_url, method='MKCOL')
            opener.open(req)
        except urllib.error.HTTPError as e:
            # 405 = 目录已存在，忽略
            if e.code not in [405, 201]:
                pass

def parse_backup_filename(filename):
    """从备份文件名解析前缀和时间戳"""
    match = BACKUP_FILENAME_RE.match(filename)
    if not match:
        return None
    try:
        timestamp = datetime.datetime.strptime(match.group('timestamp'), '%Y%m%d-%H%M%S')
    except ValueError:
        return None
    return {
        'prefix': match.group('prefix'),
        'timestamp': timestamp,
        'name': filename,
    }

def list_remote_backups(opener, prefix):
    """列出指定前缀的远端备份（按时间倒序）"""
    remote_url = WEBDAV_URL.rstrip('/') + '/'
    data = b'<?xml version="1.0" encoding="utf-8"?><propfind xmlns="DAV:"><prop><resourcetype/></prop></propfind>'
    req = urllib.request.Request(remote_url, data=data, method='PROPFIND')
    req.add_header('Depth', '1')
    req.add_header('Content-Type', 'application/xml; charset=utf-8')

    with opener.open(req) as response:
        body = response.read()

    root = ET.fromstring(body)
    backups = []

    for response_node in root.iter():
        if not response_node.tag.endswith('response'):
            continue

        href = None
        for child in response_node:
            if child.tag.endswith('href'):
                href = child.text or ''
                break
        if not href:
            continue

        path = urllib.parse.unquote(urllib.parse.urlparse(href).path or href)
        filename = Path(path.rstrip('/')).name
        if not filename:
            continue

        parsed = parse_backup_filename(filename)
        if not parsed or parsed['prefix'] != prefix:
            continue
        backups.append(parsed)

    backups.sort(key=lambda item: item['timestamp'], reverse=True)
    return backups

def delete_remote_backup(opener, filename):
    """删除远端备份文件"""
    remote_url = WEBDAV_URL.rstrip('/') + '/' + urllib.parse.quote(filename)
    req = urllib.request.Request(remote_url, method='DELETE')
    with opener.open(req):
        return

def cleanup_old_backups(current_backup_name):
    """清理旧备份：保留3个月内或者最近20个备份"""
    current = parse_backup_filename(current_backup_name)
    if not current:
        print(f"⚠️  跳过清理：文件名不符合备份格式 {current_backup_name}")
        return

    print("🧹 正在清理旧备份...")
    opener = create_webdav_opener()
    try:
        backups = list_remote_backups(opener, current['prefix'])
    except urllib.error.HTTPError as e:
        print(f"⚠️  清理跳过：WebDAV 不支持 PROPFIND 或请求失败 ({e.code})")
        return
    except Exception as e:
        print(f"⚠️  清理跳过：无法列出远端备份 ({e})")
        return

    if len(backups) <= MIN_KEEP_COUNT:
        print(f"ℹ️  无需清理：当前共 {len(backups)} 个备份（<= {MIN_KEEP_COUNT}）")
        return

    cutoff = datetime.datetime.now() - datetime.timedelta(days=RETENTION_DAYS)
    keep_by_count = {item['name'] for item in backups[:MIN_KEEP_COUNT]}
    to_delete = [
        item for item in backups
        if item['timestamp'] < cutoff and item['name'] not in keep_by_count
    ]

    if not to_delete:
        print("ℹ️  无需清理：没有符合删除条件的旧备份")
        return

    deleted = 0
    failed = 0
    for item in to_delete:
        try:
            delete_remote_backup(opener, item['name'])
            deleted += 1
            print(f"🗑️  已删除: {item['name']}")
        except Exception as e:
            failed += 1
            print(f"⚠️  删除失败: {item['name']} ({e})")

    print(f"✅ 清理完成: 删除 {deleted} 个，失败 {failed} 个，保留 {len(backups) - deleted} 个")

def upload_to_webdav(local_file, remote_name):
    """上传到 WebDAV 服务器"""
    print(f"☁️  正在上传到 WebDAV...")
    
    remote_url = WEBDAV_URL.rstrip('/') + '/' + remote_name
    
    # 先确保目录存在
    ensure_webdav_directory()
    
    opener = create_webdav_opener()
    
    try:
        with open(local_file, 'rb') as f:
            data = f.read()
        
        req = urllib.request.Request(remote_url, data=data, method='PUT')
        req.add_header('Content-Type', 'application/octet-stream')
        
        with opener.open(req) as response:
            if response.status in [200, 201, 204]:
                print(f"✅ 上传成功: {remote_name}")
                return True
            else:
                print(f"❌ 上传失败: HTTP {response.status}")
                return False
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误: {e.code} - {e.reason}")
        if e.code == 409:
            print("💡 提示: 409 错误通常表示目录不存在或文件已存在")
            print("   坚果云需要在网页端手动创建文件夹")
            print("   请访问 https://www.jianguoyun.com/ 创建文件夹: openclaw-tencent-backup")
        elif e.code == 404:
            print("💡 提示: 404 错误通常表示 WebDAV 路径不存在")
            print("   请检查坚果云网页端是否有对应文件夹")
            print("   路径示例: https://dav.jianguoyun.com/dav/openclaw-backup/")
        elif e.code == 401:
            print("💡 提示: 401 错误表示认证失败")
            print("   请检查用户名和密码是否正确")
            print("   注意: 坚果云需要使用'应用密码'而非登录密码")
        return False
    except Exception as e:
        print(f"❌ 上传失败: {e}")
        return False

def list_backups():
    """列出 WebDAV 上的备份文件"""
    print("📋 WebDAV 备份列表")
    print("注意: 此功能需要 WebDAV 服务器支持 PROPFIND 方法")
    print(f"WebDAV URL: {WEBDAV_URL}")

def main():
    parser = argparse.ArgumentParser(description='WebDAV 备份工具')
    parser.add_argument('--source', '-s', default=WORKSPACE, help='要备份的源目录')
    parser.add_argument('--name', '-n', default='openclaw-backup', help='备份文件名前缀')
    parser.add_argument('--list', '-l', action='store_true', help='列出备份')
    parser.add_argument('--restore', '-r', help='恢复指定备份')
    
    args = parser.parse_args()
    
    if args.list:
        list_backups()
        return
    
    if args.restore:
        print("🚧 恢复功能开发中...")
        return
    
    # 检查配置
    if not check_config():
        sys.exit(1)
    
    # 创建备份
    backup_file = create_backup(args.source, args.name)
    
    # 上传到 WebDAV
    remote_name = backup_file.name
    if upload_to_webdav(backup_file, remote_name):
        cleanup_old_backups(remote_name)
        # 上传成功后删除本地临时文件
        backup_file.unlink()
        print(f"✅ 备份完成: {remote_name}")
    else:
        print(f"⚠️  上传失败，本地备份保留在: {backup_file}")
        sys.exit(1)

if __name__ == '__main__':
    main()
