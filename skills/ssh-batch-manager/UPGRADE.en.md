# SSH Batch Manager v2.0 - Upgrade Guide

## 🆕 v2.0 New Features

### 1️⃣ JSON Configuration Format

**Old Format** (ssh-batch.conf):
```
root@10.0.0.2=AES256:encrypted_password
user1@10.8.8.1=AES256:encrypted_password
```

**New Format** (ssh-batch.json):
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
      "password": "AES256:encrypted_password"
    }
  ]
}
```

---

### 2️⃣ Key-based Authentication Support

**Configuration Example**:
```json
{
  "version": "2.0",
  "auth_method": "key",
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:encrypted_passphrase"
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

### 3️⃣ Mixed Mode Support

**Support both password and key authentication**:
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

### 4️⃣ ed25519 Key Support

**Generate ed25519 key**:
```bash
python3 ssh-batch-manager.py generate-ed25519
```

**Output**:
```
🔑 Generating ed25519 key pair...
✅ Key generated:
  Private: /home/subline/.ssh/id_ed25519
  Public: /home/subline/.ssh/id_ed25519.pub
```

---

## 🔄 Migrating Old Configuration

### Automatic Migration

```bash
python3 ssh-batch-manager.py migrate-config
```

**Process**:
1. Read old format `ssh-batch.conf`
2. Convert to new JSON format
3. Backup old config as `ssh-batch.conf.backup`
4. Save new config as `ssh-batch.json`

---

### Manual Migration

**Step 1**: Create new config file
```bash
cp ssh-batch.json.template ~/.openclaw/credentials/ssh-batch.json
```

**Step 2**: Edit config
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
      "password": "AES256:copy_from_old_config"
    }
  ]
}
```

---

## 📋 Complete Configuration Examples

### Scenario 1: All Password Authentication

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

### Scenario 2: All Key-based Authentication

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

### Scenario 3: Mixed Mode

```json
{
  "version": "2.0",
  "auth_method": "password",
  "key": {
    "path": "~/.ssh/id_ed25519",
    "passphrase": "AES256:passphrase"
  },
  "servers": [
    {
      "user": "root",
      "host": "10.0.0.2",
      "auth": "password",
      "password": "AES256:server_password"
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

## 🔧 Command Reference

### Configuration Management

| Command | Description |
|---------|-------------|
| `create-config` | Create sample configuration |
| `migrate-config` | Migrate from old format |

### Key Management

| Command | Description |
|---------|-------------|
| `generate-key` | Generate encryption key |
| `generate-ed25519` | Generate ed25519 SSH key pair |
| `encrypt <pwd>` | Encrypt password |

### SSH Operations

| Command | Description |
|---------|-------------|
| `enable-all` | Enable all servers |
| `disable-all` | Disable all servers |

---

## 🐛 Troubleshooting

### Problem 1: Configuration Load Failure

**Error**: `JSONDecodeError`

**Solution**:
```bash
# Validate JSON format
python3 -m json.tool ~/.openclaw/credentials/ssh-batch.json

# Recreate config
python3 ssh-batch-manager.py create-config
```

---

### Problem 2: ed25519 Key Not Found

**Error**: `Private key not found: ~/.ssh/id_ed25519`

**Solution**:
```bash
python3 ssh-batch-manager.py generate-ed25519
```

---

### Problem 3: Ubuntu/Alpine RSA Not Supported

**Error**: `no matching key exchange method found`

**Solution**: Use ed25519 key
```bash
# Generate ed25519 key
ssh-keygen -t ed25519 -a 100 -C "your_email@example.com"

# Update config
{
  "key": {
    "path": "~/.ssh/id_ed25519"
  }
}
```

---

## 📊 Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Config Format | Text | JSON ✅ |
| Password Auth | ✅ | ✅ |
| Key Auth | ❌ | ✅ |
| Mixed Mode | ❌ | ✅ |
| ed25519 Support | ❌ | ✅ |
| Custom Port | ❌ | ✅ |
| Config Migration | - | ✅ |

---

*Last updated: 2026-03-03*
