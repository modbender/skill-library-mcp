# SSH Batch Manager v2.0 - 升级指南

## 🆕 v2.0 新功能

### 1️⃣ JSON 配置文件格式

**旧格式** (ssh-batch.conf):
```
root@10.0.0.2=AES256:加密密码
user1@10.8.8.1=AES256:加密密码
```

**新格式** (ssh-batch.json):
```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:加密密码"
    }
  ]
}
```

---

### 2️⃣ 支持证书登录

**配置示例**:
```json
{
  "version": "2.0",
  "auth_method": "key",
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:加密后的私钥密码"
  },
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "auth": "key"
    }
  ]
}
```

---

### 3️⃣ 混合模式支持

**同时支持密码和证书登录**:
```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "auth": "password",
      "password": "AES256:..."
    },
    {
      "user": "user1",
      "host": "10.8.8.1",
      "auth": "key"
    }
  ]
}
```

---

### 4️⃣ ed25519 密钥支持

**生成 ed25519 密钥**:
```bash
python3 ssh-batch-manager.py generate-ed25519
```

**输出**:
```
🔑 生成 ed25519 密钥对...
✅ 密钥已生成:
  私钥：/home/subline/.ssh/id_ed25519
  公钥：/home/subline/.ssh/id_ed25519.pub
```

---

## 🔄 迁移旧配置

### 自动迁移

```bash
python3 ssh-batch-manager.py migrate-config
```

**执行**:
1. 读取旧格式 `ssh-batch.conf`
2. 转换为新 JSON 格式
3. 备份旧配置为 `ssh-batch.conf.backup`
4. 保存新配置为 `ssh-batch.json`

---

### 手动迁移

**步骤 1**: 创建新配置文件
```bash
cp ssh-batch.json.template ~/.openclaw/credentials/ssh-batch.json
```

**步骤 2**: 编辑配置
```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:从旧配置复制"
    }
  ]
}
```

---

## 📋 完整配置示例

### 场景 1：全部密码登录

```json
{
  "version": "2.0",
  "auth_method": "password",
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "password",
      "password": "AES256:Z0FBQUFB..."
    },
    {
      "user": "root",
      "host": "10.0.0.3",
      "port": 22,
      "auth": "password",
      "password": "AES256:YWJjZGVm..."
    }
  ]
}
```

---

### 场景 2：全部证书登录

```json
{
  "version": "2.0",
  "auth_method": "key",
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:Z0FBQUFB..."
  },
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "port": 22,
      "auth": "key"
    },
    {
      "user": "root",
      "host": "10.0.0.3",
      "port": 22,
      "auth": "key"
    }
  ]
}
```

---

### 场景 3：混合模式

```json
{
  "version": "2.0",
  "auth_method": "password",
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:私钥密码"
  },
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "auth": "password",
      "password": "AES256:服务器密码"
    },
    {
      "user": "deploy",
      "host": "10.8.8.1",
      "auth": "key"
    },
    {
      "user": "admin",
      "host": "192.168.1.100",
      "port": 2222,
      "auth": "key"
    }
  ]
}
```

---

## 🔧 命令参考

### 配置管理

| 命令 | 说明 |
|------|------|
| `create-config` | 创建示例配置文件 |
| `migrate-config` | 从旧格式迁移 |

### 密钥管理

| 命令 | 说明 |
|------|------|
| `generate-key` | 生成加密密钥 |
| `generate-ed25519` | 生成 ed25519 SSH 密钥对 |
| `encrypt <pwd>` | 加密密码 |

### SSH 操作

| 命令 | 说明 |
|------|------|
| `enable-all` | 启用所有服务器 |
| `disable-all` | 禁用所有服务器 |

---

## 🐛 故障排查

### 问题 1: 配置加载失败

**错误**: `JSONDecodeError`

**解决**:
```bash
# 验证 JSON 格式
python3 -m json.tool ~/.openclaw/credentials/ssh-batch.json

# 重新创建配置
python3 ssh-batch-manager.py create-config
```

---

### 问题 2: ed25519 密钥不存在

**错误**: `私钥不存在：~/.ssh/id_ed25519`

**解决**:
```bash
python3 ssh-batch-manager.py generate-ed25519
```

---

### 问题 3: Ubuntu/Alpine RSA 不支持

**错误**: `no matching key exchange method found`

**解决**: 使用 ed25519 密钥
```bash
# 生成 ed25519 密钥
ssh-keygen -t ed25519 -a 100 -C "your_email@example.com"

# 更新配置
{
  "key": {
    "path": "~/.ssh/id_ed25519"
  }
}
```

---

## 📊 版本对比

| 特性 | v1.0 | v2.0 |
|------|------|------|
| 配置文件格式 | 文本 | JSON ✅ |
| 密码登录 | ✅ | ✅ |
| 证书登录 | ❌ | ✅ |
| 混合模式 | ❌ | ✅ |
| ed25519 支持 | ❌ | ✅ |
| 自定义端口 | ❌ | ✅ |
| 配置迁移 | - | ✅ |

---

*最后更新：2026-03-03*
