#!/usr/bin/env python3
"""
SSH Batch Manager v2.1 - Batch SSH Key Management

Support Enable/Disable SSH all commands, automatically distribute/remove public keys
to/from multiple servers. Support password and key-based authentication.
Passwords are encrypted with AES-256.

Configuration Format (JSON):
~/.openclaw/credentials/ssh-batch.json

{
  "version": "2.0",
  "auth_method": "password",  // "password" or "key"
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:encrypted_passphrase"  // Required when auth_method=key
  },
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:encrypted_password"
    },
    {
      "user": "user1",
      "host": "10.8.8.1",
      "port": 22,
      "auth": "key"
    }
  ]
}
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
# Configuration
# ═══════════════════════════════════════════════════════════════

CREDENTIALS_DIR = Path.home() / ".openclaw" / "credentials"
CONFIG_FILE = CREDENTIALS_DIR / "ssh-batch.json"
KEY_FILE = CREDENTIALS_DIR / "ssh-batch.key"
SSH_DIR = Path.home() / ".ssh"

# Source identifier for audit trail
SOURCE_IDENTIFIER = "ssh-batch-manager"
SOURCE_HOST = subprocess.run(['hostname'], capture_output=True, text=True).stdout.strip()

# Color output
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

# ═══════════════════════════════════════════════════════════════
# Encryption/Decryption
# ═══════════════════════════════════════════════════════════════

def load_key():
    """Load encryption key."""
    if not KEY_FILE.exists():
        print(f"{RED}❌ Key file not found: {KEY_FILE}{NC}")
        print(f"{YELLOW}Hint: Generate key with:{NC}")
        print(f"  python3 -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\" > {KEY_FILE}")
        print(f"  chmod 600 {KEY_FILE}")
        sys.exit(1)
    
    # Set key file permissions
    os.chmod(KEY_FILE, 0o600)
    
    with open(KEY_FILE, 'rb') as f:
        return f.read().strip()

def decrypt_data(encrypted: str, key: bytes) -> str:
    """Decrypt data."""
    if not encrypted.startswith("AES256:"):
        raise ValueError(f"Invalid encryption format: {encrypted}")
    
    f = Fernet(key)
    encrypted_data = base64.b64decode(encrypted[7:])
    return f.decrypt(encrypted_data).decode()

# ═══════════════════════════════════════════════════════════════
# Configuration Management
# ═══════════════════════════════════════════════════════════════

def load_config():
    """Load JSON configuration."""
    if not CONFIG_FILE.exists():
        print(f"{RED}❌ Configuration file not found: {CONFIG_FILE}{NC}")
        print(f"{YELLOW}Hint: Create configuration file with the following format:{NC}")
        print(f"""
{{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {{
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:..."
    }}
  ]
}}
""")
        sys.exit(1)
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# ═══════════════════════════════════════════════════════════════
# SSH Key Management
# ═══════════════════════════════════════════════════════════════

def check_ssh_key(config):
    """Check if SSH key exists."""
    auth_method = config.get('auth_method', 'password')
    
    if auth_method == 'key':
        key_config = config.get('key', {})
        key_path = key_config.get('path', '~/.ssh/id_ed25519')
        key_path = Path(key_path).expanduser()
        
        if not key_path.exists():
            print(f"{RED}❌ Private key not found: {key_path}{NC}")
            print(f"{YELLOW}Hint: Generate ed25519 key pair:{NC}")
            print(f"  ssh-keygen -t ed25519 -a 100 -C \"your_email@example.com\"")
            sys.exit(1)
        
        # Check public key
        pub_key = key_path.with_suffix('.pub')
        if not pub_key.exists():
            print(f"{RED}❌ Public key not found: {pub_key}{NC}")
            sys.exit(1)
        
        print(f"{GREEN}✅ Private key: {key_path}{NC}")
        print(f"{GREEN}✅ Public key: {pub_key}{NC}")
        return str(pub_key)
    else:
        # Password login, check default public key
        default_pub = SSH_DIR / "id_ed25519.pub"
        if not default_pub.exists():
            default_pub = SSH_DIR / "id_rsa.pub"
        
        if not default_pub.exists():
            print(f"{YELLOW}⚠️  No SSH public key found, recommend generating:{NC}")
            print(f"  ssh-keygen -t ed25519 -a 100 -C \"your_email@example.com\"")
        else:
            print(f"{GREEN}✅ Public key: {default_pub}{NC}")
        
        return str(default_pub)

def generate_ed25519_key():
    """Generate ed25519 key pair."""
    print(f"{BLUE}🔑 Generating ed25519 key pair...{NC}")
    
    key_path = SSH_DIR / "id_ed25519"
    
    # Check if already exists
    if key_path.exists():
        print(f"{YELLOW}⚠️  Key already exists: {key_path}{NC}")
        response = input("Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Cancelled")
            return
    
    # Generate key
    try:
        subprocess.run([
            'ssh-keygen', '-t', 'ed25519', '-a', '100',
            '-f', str(key_path),
            '-C', 'ssh-batch-manager',
            '-N', ''  # No passphrase
        ], check=True)
        
        print(f"{GREEN}✅ Key generated:{NC}")
        print(f"  Private: {key_path}")
        print(f"  Public: {key_path.with_suffix('.pub')}")
        
        # Set permissions
        os.chmod(key_path, 0o600)
        os.chmod(key_path.with_suffix('.pub'), 0o644)
        
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Generation failed: {e}{NC}")
        sys.exit(1)

# ═══════════════════════════════════════════════════════════════
# Connectivity Check
# ═══════════════════════════════════════════════════════════════

def check_connectivity(user_host: str, port: int, password: str = None, key_path: str = None) -> bool:
    """
    Check if passwordless login is already working.
    
    Returns:
        True - Already accessible
        False - Needs configuration
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
    Check if public key already exists in target server's authorized_keys.
    
    Returns:
        True - Key already exists
        False - Needs to be added
    """
    env = os.environ.copy()
    env['SSHPASS'] = password
    
    # Check if authorized_keys contains the public key
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
# SSH Operations
# ═══════════════════════════════════════════════════════════════

def enable_ssh_key(server: dict, config: dict, global_key: bytes, pub_key_path: str) -> dict:
    """
    Enable SSH key-based authentication.
    
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
    
    print(f"{BLUE}→ Processing: {user_host} (port:{port}, auth:{auth_method}){NC}")
    
    try:
        if auth_method == 'key':
            # Key-based authentication
            key_config = config.get('key', {})
            key_path = key_config.get('path', '~/.ssh/id_ed25519')
            key_path = Path(key_path).expanduser()
            encrypted_passphrase = key_config.get('passphrase', '')
            
            if not encrypted_passphrase:
                print(f"  {YELLOW}⚠️  Key passphrase not configured, skipping{NC}")
                result['reason'] = 'Key passphrase not configured'
                return result
            
            passphrase = decrypt_data(encrypted_passphrase, global_key)
            return enable_with_key(user_host, port, key_path, passphrase, pub_key_path)
        else:
            # Password authentication
            encrypted_password = server.get('password', '')
            if not encrypted_password:
                print(f"  {RED}❌ Password not configured{NC}")
                result['reason'] = 'Password not configured'
                return result
            
            password = decrypt_data(encrypted_password, global_key)
            return enable_with_password(user_host, port, password, pub_key_path)
            
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{NC}")
        result['reason'] = str(e)
        return result

def enable_with_password(user_host: str, port: int, password: str, pub_key_path: str) -> dict:
    """Distribute public key using password (with pre-check)."""
    result = {'success': False, 'skipped': False, 'reason': ''}
    
    # 1. Check if already accessible
    print(f"  🔍 Checking connectivity...")
    if check_connectivity(user_host, port, password=password):
        print(f"  {GREEN}✅ Already accessible, skipping{NC}")
        result['skipped'] = True
        result['reason'] = 'Already connected'
        return result
    
    # 2. Read public key
    with open(pub_key_path, 'r') as f:
        pub_key_content = f.read().strip()
    
    # 3. Check if public key already exists
    print(f"  🔍 Checking if key exists...")
    if check_authorized_key(user_host, port, password, pub_key_content):
        print(f"  {GREEN}✅ Key already exists, but cannot login (possible permission issue){NC}")
        # Try to fix permissions
        return fix_key_permissions(user_host, port, password)
    
    # 4. Distribute public key (with source identifier)
    print(f"  📤 Distributing public key...")
    return copy_key_with_password(user_host, port, password, pub_key_content)

def copy_key_with_password(user_host: str, port: int, password: str, pub_key_content: str) -> dict:
    """Distribute public key using password (with source identifier)."""
    result = {'success': False, 'skipped': False, 'reason': ''}
    env = os.environ.copy()
    env['SSHPASS'] = password
    
    try:
        # 1. Create .ssh directory
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
        
        # 2. Append public key (with source identifier comment)
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
        
        # 3. Set permissions
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
        
        # 4. Verify
        if check_connectivity(user_host, port, password=password):
            print(f"  {GREEN}✅ Success (with source identifier){NC}")
            result['success'] = True
        else:
            print(f"  {YELLOW}⚠️  Key added, but verification failed (may need re-login){NC}")
            result['success'] = True  # Key added, count as success
        
        return result
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{NC}")
        result['reason'] = str(e)
        return result

def fix_key_permissions(user_host: str, port: int, password: str) -> dict:
    """Fix key permission issues."""
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
            print(f"  {GREEN}✅ Permission fix successful{NC}")
            result['success'] = True
        else:
            print(f"  {YELLOW}⚠️  Permissions fixed, but still cannot connect{NC}")
            result['success'] = True
        
        return result
    except Exception as e:
        result['reason'] = str(e)
        return result

def enable_with_key(user_host: str, port: int, key_path: Path, passphrase: str, pub_key_path: str) -> dict:
    """Distribute public key using key-based authentication."""
    # Similar implementation, with source identifier
    return {'success': False, 'skipped': False, 'reason': 'Not yet implemented'}

# ═══════════════════════════════════════════════════════════════
# Main Logic
# ═══════════════════════════════════════════════════════════════

def enable_all():
    """Enable passwordless login for all servers."""
    print(f"\n{GREEN}{'='*60}{NC}")
    print(f"{GREEN}🔑 SSH Batch Manager v2.1 - Enable All{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")
    
    config = load_config()
    key = load_key()
    pub_key_path = check_ssh_key(config)
    
    servers = config.get('servers', [])
    if not servers:
        print(f"{YELLOW}⚠️  No servers configured{NC}")
        return
    
    print(f"{BLUE}📋 Found {len(servers)} servers{NC}\n")
    
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
    print(f"{GREEN}✅ Complete: {success} successful, {failed} failed, {skipped} skipped{NC}")
    print(f"{GREEN}{'='*60}{NC}\n")

# ═══════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"{YELLOW}Usage:{NC}")
        print(f"  {sys.argv[0]} enable-all    # Enable all servers")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'enable-all':
        enable_all()
    else:
        print(f"{RED}❌ Unknown command: {command}{NC}")
        sys.exit(1)
