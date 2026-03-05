# SSH 技能详细使用指南

## 为什么用 paramiko？

在 Windows 上进行 SSH 自动化时，paramiko 是最可靠的方案：

| 方法 | Windows | Linux | 自动化友好 |
|------|---------|-------|-----------|
| paramiko | ✅ | ✅ | ✅ |
| sshpass | ❌ | ✅ | ⚠️ |
| plink | ⚠️ | ⚠️ | ⚠️ |
| OpenSSH | ⚠️ | ✅ | ❌ |

## 安装 paramiko

```bash
pip install paramiko
```

## 基础用法

### 1. 执行单个命令

```python
import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.0.3.120', username='root', password='7758258Cc')

stdin, stdout, stderr = ssh.exec_command('ls -la /')
print(stdout.read().decode())

ssh.close()
```

### 2. 交互式 Shell

```python
import paramiko
import time

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('10.0.3.120', username='root', password='7758258Cc')

shell = ssh.invoke_shell()

# 执行一系列命令
commands = [
    'cd /var/www',
    'ls -la',
    'cat app.log | tail -50',
    'exit'
]

for cmd in commands:
    shell.send(cmd + '\n')
    time.sleep(1)
    output = shell.recv(4096).decode()
    print(output)

ssh.close()
```

### 3. 使用脚本文件

```bash
# 单命令模式
python scripts/ssh.py 10.0.3.120 root 7758258Cc "uptime"

# 多命令模式
python scripts/ssh.py 10.0.3.120 root 7758258Cc --shell "cd /var;ls;pwd"
```

## 常见场景

### 查看系统信息

```python
commands = [
    'uname -a',
    'whoami',
    'pwd',
    'echo $HOME'
]
```

### 文件操作

```python
# 上传文件
sftp = ssh.open_sftp()
sftp.put('local_file.txt', '/remote/path/file.txt')
sftp.close()

# 下载文件
sftp = ssh.open_sftp()
sftp.get('/remote/path/file.txt', 'local_file.txt')
sftp.close()
```

### 服务管理

```python
commands = [
    'systemctl status nginx',
    'systemctl restart nginx',
    'journalctl -u nginx --tail -20'
]
```

## 错误处理

```python
import paramiko

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=user, password=passwd, timeout=10)
    
    stdin, stdout, stderr = ssh.exec_command(command)
    
    output = stdout.read().decode()
    errors = stderr.read().decode()
    
    if errors:
        print(f"Warning: {errors}")
    
    return output
    
except paramiko.AuthenticationException:
    print("认证失败，请检查用户名和密码")
except paramiko.SSHException as e:
    print(f"SSH 错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
finally:
    ssh.close()
```

## 安全建议

1. **不要在代码中硬编码密码** - 使用环境变量或配置文件
2. **使用密钥认证** - 比密码更安全
3. **限制权限** - 只给必要用户 root 权限
4. **记录日志** - 记录所有 SSH 操作

```python
# 使用密钥认证
private_key = paramiko.RSAKey.from_private_key_file('~/.ssh/id_rsa')
ssh.connect(host, username=user, pkey=private_key)
```
