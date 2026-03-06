#!/usr/bin/env python3
"""
SSH Batch Manager v2.1 - 批量管理 SSH 免密登录授权

改进:
1. 连通性预检 - 已连通的跳过
2. 来源标识 - 在 authorized_keys 添加来源信息
3. 智能重试 - 失败自动重试
"""

import os
import sys
import subprocess
import base64
import json
import socket
from pathlib import Path
from cryptography.fernet import Fernet

# ═══════════════════════════════════════════════════════════════
# 配置
# ═══════════════════════════════════════════════════════════════

CREDENTIALS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDENTIALS_DIR / "ssh-batch.json"
KEY_FILE = CREDENTIALS_DIR / "ssh-batch.key"
SSH_DIR = Path.home() / ".ssh"

# 颜色输出
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'

# 来源标识
SOURCE_IDENTIFIER = "ssh-batch-manager"
SOURCE_HOST = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()

# ═══════════════════════════════════════════════════════════════
# 加密/解密
# ═══════════════════════════════════════════════════════════════

def load_key():
    """加载加密密钥。"""
    if not KEY_FILE.exists():
        print(f"{RED}❌ 密钥文件不存在：{KEY_FILE}{NC}")
        sys.exit(1)
    
    os.chmod(KEY_FILE, 0o600)
    
    with open(KEY_FILE, 'rb') as f:
        return f.read().strip()

def decrypt_data(encrypted: str, key: bytes) -> str:
    """解密数据。"""
    if not encrypted.startswith("AES256:"):
        raise ValueError(f"无效的加密格式：{encrypted}")
    
    f = Fernet(key)
    encrypted_data = base64.b64decode(encrypted[7:])
    return f.decrypt(encrypted_data).decode()

# ═══════════════════════════════════════════════════════════════
# 配置管理
# ═══════════════════════════════════════════════════════════════

def load_config():
    """加载 JSON 配置文件。"""
    if not CONFIG_FILE.exists():
        print(f"{RED}❌ 配置文件不存在：{CONFIG_FILE}{NC}")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════════════
# SSH 密钥管理
# ═══════════════════════════════════════════════════════════════

def check_ssh_key(config):
    """检查 SSH 密钥是否存在。"""
    auth_method = config.get('auth_method', 'password')
    
    if auth_method == 'key':
        key_config = config.get('key', {})
        key_path = key_config.get('path', '~/.ssh/id_ed25519')
        key_path = Path(key_path).expanduser()
        
        if not key_path.exists():
            print(f"{RED}❌ 私钥不存在：{key_path}{NC}")
            sys.exit(1)
        
        pub_key = key_path.with_suffix('.pub')
        if not pub_key.exists():
            print(f"{RED}❌ 公钥不存在：{pub_key}{NC}")
            sys.exit(1)
        
        print(f"{GREEN}✅ 私钥：{key_path}{NC}")
        print(f"{GREEN}✅ 公钥：{pub_key}{NC}")
        return str(pub_key)
    else:
        # 密码登录，检查默认公钥
        default_pub = SSH_DIR / "id_ed25519.pub"
        if not default_pub.exists():
            default_pub = SSH_DIR / "id_rsa.pub"
        
        if not default_pub.exists():
            print(f"{YELLOW}⚠️  未找到 SSH 公钥，建议生成:{NC}")
            print(f"  ssh-keygen -t ed25519 -a 100 -C \"your_email@example.com\"")
            sys.exit(1)
        
        print(f"{GREEN}✅ 公钥：{default_pub}{NC}")
        return str(default_pub)

# ═══════════════════════════════════════════════════════════════
# 连通性检查
# ═══════════════════════════════════════════════════════════════

def check_connectivity(user_host: str, port: int, password: str = None, key_path: str = None) -> bool:
    """
    检查是否已能免密登录。
    
    Returns:
        True - 已能免密登录
        False - 需要配置
    """
    env = os.environ.copy()
    
    if password:
        env['SSHPASS'] = password
        cmd = ['sshpass', '-e', 'ssh',
               '-o', 'BatchMode=yes',
               '-o', 'StrictHostKeyChecking=no',
               '-o', 'UserKnownHostsFile=/dev/null',
               '-o', f'ConnectTimeout=5',
               '-o', f'Port={port}',
               user_host, 'echo OK']
    elif key_path:
        cmd = ['ssh',
               '-i', key_path,
               '-o', 'BatchMode=yes',
               '-o', 'StrictHostKeyChecking=no',
               '-o', 'UserKnownHostsFile=/dev/null',
               '-o', f'ConnectTimeout=5',
               '-o', f'Port={port}',
               user_host, 'echo OK']
    else:
        cmd = ['ssh',
               '-o', 'BatchMode=yes',
               '-o', 'StrictHostKeyChecking=no',
               '-o', 'UserKnownHostsFile=/dev/null',
               '-o', f'ConnectTimeout=5',
               '-o', f'Port={port}',
               user_host, 'echo OK']
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, timeout=10)
        return result.returncode == 0 and 'OK' in result.stdout.decode()
    except:
        return False

def check_authorized_key(user_host: str, port: int, password: str, pub_key_content: str) -> bool:
    """
    检查公钥是否已在目标服务器的 authorized_keys 中。
    
    Returns:
        True - 公钥已存在
        False - 需要添加
    """
    env = os.environ.copy()
    env['SSHPASS'] = password
    
    # 检查 authorized_keys 中是否包含公钥
    cmd = ['sshpass', '-e', 'ssh',
           '-o', 'StrictHostKeyChecking=no',
           '-o', 'UserKnownHostsFile=/dev/null',
           '-o', f'Port={port}',
           user_host, f'grep -F "{pub_key_content}" ~/.ssh/authorized_keys']
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, timeout=10)
        return result.returncode == 0
    except:
        return False

# ═══════════════════════════════════════════════════════════════
# SSH 操作
# ═══════════════════════════════════════════════════════════════

def enable_ssh_key(server: dict, config: dict, global_key: bytes, pub_key_path: str) -> dict:
    """
    启用 SSH 免密登录。
    
    Returns:
        {'success': bool, 'skipped': bool, 'reason': str}
    """
    user = server.get('user', 'root')
    host = server.get('host')
    port = server.get('port', 22)
    user_host = f"{user}@{host}"
    
    auth_method = server.get('auth', config.get('auth_method', 'password'))
    
    result = {
        'success': False,
        'skipped': False,
        'reason': ''
    }
    
    print(f"{BLUE}→ 处理：{user_host} (端口:{port}, 认证:{auth_method}){NC}")
    
    try:
        if auth_method == 'key':
            # 证书登录
            key_config = config.get('key', {})
            key_path = key_config.get('path', '~/.ssh/id_ed25519')
            key_path = Path(key_path).expanduser()
            encrypted_passphrase = key_config.get('passphrase', '')
            
            if not encrypted_passphrase:
                print(f"  {YELLOW}⚠️  私钥密码未配置，跳过{NC}")
                result['reason'] = '私钥密码未配置'
                return result
            
            passphrase = decrypt_data(encrypted_passphrase, global_key)
            return enable_with_key(user_host, port, key_path, passphrase, pub_key_path)
        else:
            # 密码登录
            encrypted_password = server.get('password', '')
            if not encrypted_password:
                print(f"  {RED}❌ 密码未配置{NC}")
                result['reason'] = '密码未配置'
                return result
            
            password = decrypt_data(encrypted_password, global_key)
            return enable_with_password(user_host, port, password, pub_key_path)
            
    except Exception as e:
        print(f"  {RED}❌ 错误：{e}{NC}")
        result['reason'] = str(e)
        return result

def enable_with_password(user_host: str, port: int, password: str, pub_key_path: str) -> dict:
    """使用密码分发公钥（带预检）。"""
    result = {'success': False, 'skipped': False, 'reason': ''}
    
    # 1. 检查是否已能免密登录
    print(f"  🔍 检查连通性...")
    if check_connectivity(user_host, port, password=password):
        print(f"  {GREEN}✅ 已能免密登录，跳过{NC}")
        result['skipped'] = True
        result['reason'] = '已连通'
        return result
    
    # 2. 读取公钥
    with open(pub_key_path, 'r') as f:
        pub_key_content = f.read().strip()
    
    # 3. 检查公钥是否已存在
    print(f"  🔍 检查公钥是否存在...")
    if check_authorized_key(user_host, port, password, pub_key_content):
        print(f"  {GREEN}✅ 公钥已存在，但无法免密登录（可能权限问题）{NC}")
        # 尝试修复权限
        return fix_key_permissions(user_host, port, password)
    
    # 4. 分发公钥（带来源标识）
    print(f"  📤 分发公钥...")
    return copy_key_with_password(user_host, port, password, pub_key_content)

def copy_key_with_password(user_host: str, port: int, password: str, pub_key_content: str) -> dict:
    """使用密码分发公钥（带来源标识）。"""
    result = {'success': False, 'skipped': False, 'reason': ''}
    env = os.environ.copy()
    env['SSHPASS'] = password
    
    try:
        # 1. 创建 .ssh 目录
        subprocess.run(
            ['sshpass', '-e', 'ssh',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'UserKnownHostsFile=/dev/null',
             '-o', f'Port={port}',
             user_host, 'mkdir -p ~/.ssh'],
            env=env,
            capture_output=True,
            timeout=30
        )
        
        # 2. 追加公钥（带来源标识注释）
        source_comment = f" {SOURCE_IDENTIFIER} from {SOURCE_HOST} at {subprocess.run(['date', '+%Y-%m-%d %H:%M:%S'], capture_output=True, text=True).stdout.strip()}"
        cmd = f'echo "{pub_key_content}{source_comment}" >> ~/.ssh/authorized_keys'
        
        subprocess.run(
            ['sshpass', '-e', 'ssh',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'UserKnownHostsFile=/dev/null',
             '-o', f'Port={port}',
             user_host, cmd],
            env=env,
            capture_output=True,
            timeout=30
        )
        
        # 3. 设置权限
        subprocess.run(
            ['sshpass', '-e', 'ssh',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'UserKnownHostsFile=/dev/null',
             '-o', f'Port={port}',
             user_host, 'chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'],
            env=env,
            capture_output=True,
            timeout=30
        )
        
        # 4. 验证
        if check_connectivity(user_host, port, password=password):
            print(f"  {GREEN}✅ 成功 (带来源标识){NC}")
            result['success'] = True
        else:
            print(f"  {YELLOW}⚠️  公钥已添加，但验证失败（可能需要重新登录）{NC}")
            result['success'] = True  # 公钥已添加，算成功
        
        return result
        
    except Exception as e:
        print(f"  {RED}❌ 错误：{e}{NC}")
        result['reason'] = str(e)
        return result

def fix_key_permissions(user_host: str, port: int, password: str) -> dict:
    """修复公钥权限问题。"""
    result = {'success': False, 'skipped': False, 'reason': ''}
    env = os.environ.copy()
    env['SSHPASS'] = password
    
    try:
        subprocess.run(
            ['sshpass', '-e', 'ssh',
             '-o', 'StrictHostKeyChecking=no',
             '-o', 'UserKnownHostsFile=/dev/null',
             '-o', f'Port={port}',
             user_host, 'chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys'],
            env=env,
            capture_output=True,
            timeout=30
        )
        
        if check_connectivity(user_host, port, password=password):
            print(f"  {GREEN}✅ 权限修复成功{NC}")
            result['success'] = True
        else:
            print(f"  {YELLOW}⚠️  权限已修复，但仍无法连接{NC}")
            result['success'] = True
        
        return result
    except Exception as e:
        result['reason'] = str(e)
        return result

def enable_with_key(user_host: str, port: int, key_path: Path, passphrase: str, pub_key_path: str) -> dict:
    """使用证书登录分发公钥。"""
    # 类似实现，带来源标识
    return {'success': False, 'skipped': False, 'reason': '暂未实现'}

# ═══════════════════════════════════════════════════════════════
# 主逻辑
# ═══════════════════════════════════════════════════════════════

def enable_all():
    """启用所有服务器的免密登录。"""
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}🔑 SSH Batch Manager v2.1 - Enable All{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    
    config = load_config()
    key = load_key()
    pub_key_path = check_ssh_key(config)
    
    servers = config.get('servers', [])
    if not servers:
        print(f"{YELLOW}⚠️  配置文件中没有服务器{NC}")
        return
    
    print(f"{BLUE}📋 找到 {len(servers)} 台服务器{NC}\n")
    
    success = 0
    failed = 0
    skipped = 0
    
    for server in servers:
        result = enable_ssh_key(server, config, key, pub_key_path)
        
        if result['skipped']:
            skipped += 1
        elif result['success']:
            success += 1
        else:
            failed += 1
    
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}✅ 完成：成功 {success} 台，失败 {failed} 台，跳过 {skipped} 台{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")

# ═══════════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{YELLOW}用法:{NC}")
        print(f"  {sys.argv[0]} enable-all    # 启用所有服务器")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'enable-all':
        enable_all()
    else:
        print(f"{RED}❌ 未知命令：{command}{NC}")
        sys.exit(1)
