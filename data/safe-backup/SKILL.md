---
name: safe-backup
description: Backup OpenClaw state directory and workspace. Includes excluding sensitive files, packaging for backup. Triggered when user asks to backup, export, or save state.
---

# Safe Backup

Backup OpenClaw state directory and workspace with security best practices.

## ⚠️ Security Warnings

- **Backup may contain sensitive data** - review before sharing
- **If uploading to GitHub** - use a private repository and consider encryption
- **auth-profiles.json is EXCLUDED** - after restore, you must re-authenticate
- This script does NOT automatically push to any remote

## Quick Start

### 1. Run Backup

```bash
~/.openclaw/skills/safe-backup/scripts/backup.sh
```

### 2. Check Output

```
Backup file: /tmp/safe-backup-20260223.tar.gz  (Linux)
Backup file: /var/folders/xx/.../safe-backup-20260223.tar.gz  (macOS)
Backup file: C:\Users\xxx\AppData\Local\Temp\safe-backup-20260223.tar.gz  (Windows)
```

### 3. Store Securely

See "Storage Options" below.

---

## Cross-Platform Migration

### Platform Support

| Platform | Status | Requirements |
|----------|--------|--------------|
| **Linux** | ✅ Fully supported | Native bash |
| **macOS** | ✅ Fully supported | Native bash |
| **Windows (Git Bash)** | ✅ Supported | Git for Windows |
| **Windows (WSL)** | ✅ Supported | WSL Ubuntu/Debian |
| **Windows (Native CMD)** | ❌ Not supported | Requires bash |

### Important Notes for Migration

#### 1. Temporary Directory Auto-Detection

The script automatically detects the appropriate temp directory for each platform:

| Platform | Temp Directory | Environment Variable |
|----------|----------------|---------------------|
| Linux | `/tmp` | - |
| macOS | `/var/folders/xx/...` | `$TMPDIR` |
| Windows (Git Bash) | `C:\Users\xxx\AppData\Local\Temp` | `$TEMP` / `$TMP` |

#### 2. rsync Dependency

The script uses `rsync` for efficient file copying:

- **Linux/macOS**: ✅ Built-in
- **Windows**: ⚠️ **Git Bash includes rsync**

If rsync is not available, the script will fail. For Windows without Git Bash, you need to install rsync separately (e.g., via MSYS2 or Cygwin).

#### 3. Path Separators

The script uses Unix-style forward slashes (`/`). This works in:
- Linux ✅
- macOS ✅
- Git Bash ✅
- WSL ✅

Native Windows CMD uses backslashes (`\`) and won't work without modifications.

#### 4. Home Directory Detection

The script uses `$HOME` environment variable:
- Linux: `/home/username`
- macOS: `/Users/username`
- Windows (Git Bash): `C:\Users\username`

This works correctly in all supported platforms.

### Migration Checklist

When migrating from one platform to another:

- [ ] Run backup on source machine
- [ ] Transfer backup file securely (USB, encrypted cloud, etc.)
- [ ] Install Git Bash (Windows) or ensure bash is available
- [ ] Install OpenClaw on target machine
- [ ] Run restore script
- [ ] **Re-authenticate** all services (credentials are not backed up)

### Platform-Specific Notes

#### Windows (Git Bash)

```bash
# Run from Git Bash, NOT CMD or PowerShell
~/.openclaw/skills/safe-backup/scripts/backup.sh
```

If you get "rsync not found", install Git for Windows with all optional Unix tools.

#### macOS

```bash
# Native bash is available
~/.openclaw/skills/safe-backup/scripts/backup.sh
```

Temp directory will be in `$TMPDIR` (e.g., `/var/folders/xx/...`).

#### Linux

```bash
# Native bash is available
~/.openclaw/skills/safe-backup/scripts/backup.sh
```

Temp directory will be `/tmp`.

---

## What Gets Backed Up

### ✅ Included (Safe to Backup)

| Directory | Contents |
|-----------|----------|
| `~/.openclaw/` | OpenClaw configuration |
| `~/.openclaw/workspace/` | Agent workspace files |
| `agents/` | Agent definitions |
| `skills/` | Installed skills |
| `memory/` | Memory files |
| `hooks/` | Custom hooks |

### ❌ Excluded (Sensitive - Not Backed Up)

| Pattern | Reason |
|---------|--------|
| `*.log` | Log files |
| `*.log.*` | Log rotation files |
| `sessions.json` | Session data |
| `logs/` | Log directory |
| `auth-profiles.json` | API tokens & credentials |
| `.env` | Environment variables |
| `*.pem`, `*.key` | TLS/SSH keys |
| `credentials.json` | Stored credentials |
| `api-keys.json` | API keys |
| `sessions/` | Runtime sessions |
| `browser/` | Browser cache |
| `canvas/` | Canvas cache |
| `media/` | Temporary media files |
| `backups/` | Backup directory itself |
| `delivery-queue/` | Runtime queue |
| `devices/` | Device cache |
| `subagents/` | Runtime subagents |
| `completions/` | Auto-completion cache |
| `*.bak` | Backup files |
| `*.save` | Save files |
| `update-check.json` | Update check cache |

---

## Complete Workflow

### Use Cases

| Scenario | Recommended Solution | Description |
|----------|---------------------|-------------|
| **Regular Backup** | Local encrypted storage | Weekly backup, store in encrypted local directory |
| **Migrate to New Machine** | Local tarball + USB | Transfer between machines, avoid network transmission |
| **Cloud Disaster Recovery** | Private GitHub repo | Private repo + encryption, for offsite backup |
| **Server Environment** | rsync to backup server | Automated periodic sync, suitable for production |

---

### Phase 1: Backup

```bash
# Step 1: Run backup
~/.openclaw/skills/safe-backup/scripts/backup.sh

# Step 2: Find output path (check the last line of output)
# The script will display: "Backup file: /path/to/safe-backup-YYYYMMDD.tar.gz"

# Step 3: Verify backup contents
tar -tzf "$(ls -t /tmp/safe-backup-*.tar.gz | head -1)" | head -20

# Or use the exact path shown in output:
# tar -tzf /tmp/safe-backup-20260223.tar.gz | head -20
```

### Phase 2: Storage

Choose one:

#### Option A: Local Encrypted Storage (Recommended)

```bash
# Find the latest backup file
BACKUP_FILE=$(ls -t /tmp/safe-backup-*.tar.gz | head -1)

# Create encrypted archive
openssl enc -aes-256-cbc -salt -in "$BACKUP_FILE" -out ~/backups/safe-backup-$(date +%Y%m%d).tar.gz.enc

# Enter a strong password when prompted

# Delete unencrypted backup
rm "$BACKUP_FILE"
```

#### Option B: Private GitHub Repository

```bash
# One-time setup: Create private repo on GitHub

# Find the latest backup file
BACKUP_FILE=$(ls -t /tmp/safe-backup-*.tar.gz | head -1)

# Clone your private repo
git clone https://github.com/YOUR_USERNAME/safe-backup.git ~/safe-backup

# Extract backup
mkdir -p ~/safe-backup/$(date +%Y-%m-%d)
tar -xzf "$BACKUP_FILE" -C ~/safe-backup/$(date +%Y-%m-%d)/

# Commit and push
cd ~/safe-backup
git add .
git commit -m "Backup $(date +%Y-%m-%d)"
git push origin main

# Delete local copy
rm -rf ~/safe-backup
rm "$BACKUP_FILE"
```

#### Option C: rsync to Remote Server

```bash
# Example: sync to remote server
rsync -avz --delete \
  --exclude='*.log' \
  --exclude='sessions.json' \
  ~/.openclaw/ user@backup-server:/path/to/backups/
```

### Phase 3: Restore

#### Step 1: Locate Backup

```bash
# If encrypted
openssl enc -aes-256-cbc -d -in ~/backups/safe-backup-20260223.tar.gz.enc -out /tmp/safe-backup.tar.gz

# If plain tarball, find the file
# Check your backup location (USB, cloud download, etc.)
cp /path/to/your/backup/safe-backup-20260223.tar.gz /tmp/
```

#### Step 2: Stop Gateway

```bash
systemctl --user stop openclaw-gateway
```

#### Step 3: Restore Files

```bash
# Determine temp directory based on platform
if [[ -n "$TMPDIR" ]]; then
    TEMP_DIR="$TMPDIR"
elif [[ -n "$TEMP" ]]; then
    TEMP_DIR="$TEMP"
elif [[ -n "$TMP" ]]; then
    TEMP_DIR="$TMP"
else
    TEMP_DIR="/tmp"
fi

# Extract to temporary location
mkdir -p "$TEMP_DIR/restore"
tar -xzf "$TEMP_DIR/safe-backup.tar.gz" -C "$TEMP_DIR/restore"

# Restore state directory
cp -r "$TEMP_DIR/restore/state/"* ~/.openclaw/

# Restore workspace (if needed)
cp -r "$TEMP_DIR/restore/workspace/"* ~/.openclaw/workspace/
```

#### Step 4: Re-authenticate

Because `auth-profiles.json` was excluded, you must re-configure:

```bash
# Edit config to add authentication
openclaw config edit

# Or manually create auth-profiles.json
nano ~/.openclaw/agents/main/agent/auth-profiles.json
```

Required re-configuration:
- Telegram bot token
- Discord bot token  
- Feishu credentials
- Any other API keys

#### Step 5: Restart Gateway

```bash
systemctl --user start openclaw-gateway

# Verify
openclaw status
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_STATE_DIR` | `$HOME/.openclaw` | OpenClaw state directory |
| `OPENCLAW_WORKSPACE_DIR` | `$HOME/.openclaw/workspace` | Workspace directory |

Example:

```bash
OPENCLAW_STATE_DIR=/data/openclaw ~/.openclaw/skills/safe-backup/scripts/backup.sh
```

---

## Troubleshooting

### "State directory not found"

```bash
# Check if OpenClaw is installed
ls -la ~/.openclaw
```

### "Permission denied"

```bash
# Run with appropriate permissions
chmod +x ~/.openclaw/skills/safe-backup/scripts/backup.sh
```

### "rsync not found" (Windows)

```bash
# Install Git for Windows with Unix tools, or use WSL
# Alternatively, install rsync via MSYS2:
# pacman -S rsync
```

### Restore Fails

```bash
# Check backup integrity
tar -tzf /path/to/your/backup.tar.gz

# If encrypted, verify password
openssl enc -aes-256-cbc -d -in backup.enc -o /dev/null
```

---

## Best Practices

1. **Backup regularly** - at least weekly
2. **Test restore** - periodically verify backups work
3. **Store offsite** - keep backup in different location
4. **Encrypt** - never store unencrypted backups in cloud
5. **Document** - keep notes on what was re-configured after restore
