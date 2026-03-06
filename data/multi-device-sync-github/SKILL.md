---
name: multi-device-sync-github
description: Multi-device OpenClaw data synchronization using GitHub. Manages workspace data sync across multiple machines (Ubuntu, Mac, etc.) with automatic push on file changes, periodic pull, and conflict detection. Use when setting up or managing OpenClaw across multiple devices, configuring data synchronization, resolving sync conflicts, or adding new devices to the sync network.
---

# Multi-Device Sync via GitHub

Synchronize OpenClaw workspace data across multiple machines using a private GitHub repository.

## Features

- **Automatic push**: File changes trigger immediate git commit + push (via inotifywait/fswatch)
- **Periodic pull**: Configurable interval (default: 5 minutes) to pull remote changes
- **Conflict detection**: Manual resolution required on conflicts
- **Multi-device support**: Each device uses distinct file prefixes for memory files
- **Cross-platform**: Works on Linux (inotifywait) and macOS (fswatch)
- **Selective sync**: Choose which files to synchronize
- **Interactive setup**: Guided installation with customization options

## Architecture

```
Device A (Ubuntu) ◄────► GitHub Repo ◄────► Device B (Mac)
       │                      │                    │
   auto-push              central              auto-push
  periodic pull             hub               periodic pull
```

## Prerequisites

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install -y git inotify-tools
```

### macOS
```bash
brew install git fswatch
```

## Quick Start

### Interactive Installation (Recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh | bash
```

The installer will guide you through:
1. Choose: First device (upload) or Add to existing sync (download)
2. Enter your GitHub sync repo URL
3. Name your device
4. Select files to sync
5. Configure sync interval

### Manual Installation

```bash
# 1. Clone skill
git clone https://github.com/RegulusZ/multi-device-sync-github.git ~/openclaw-skills/multi-device-sync-github

# 2. Clone/create sync repo
git clone git@github.com:YOURNAME/openclaw_sync.git ~/openclaw-sync

# 3. Initialize
cd ~/openclaw-sync
~/openclaw-skills/multi-device-sync-github/scripts/sync-init.sh \
  --device-name mydevice \
  --repo-url "git@github.com:YOURNAME/openclaw_sync.git"

# 4. Start daemon
~/openclaw-skills/multi-device-sync-github/scripts/sync-daemon.sh start
```

## How It Works

### Symlink Architecture

The skill creates symlinks from your workspace to the sync repo:

```
~/.openclaw/workspace/
├── USER.md      → ~/openclaw-sync/USER.md (symlink)
├── MEMORY.md    → ~/openclaw-sync/MEMORY.md (symlink)
├── SOUL.md      → ~/openclaw-sync/SOUL.md (symlink)
├── skills/      → ~/openclaw-sync/skills/ (symlink)
└── memory/      → ~/openclaw-sync/memory/ (symlink)
```

When you edit a file in workspace, you're actually editing the sync repo file.

### Auto-Push Flow

```
File changed in workspace
    ↓ (symlink)
File changed in sync repo
    ↓ (inotifywait/fswatch)
Wait 2 seconds (debounce)
    ↓
git add -A && git commit && git push
```

### Periodic Pull

Every N minutes (configurable), the daemon pulls remote changes.

## Configuration

Edit `~/.config/openclaw/sync-config.yaml`:

```yaml
repo_url: "git@github.com:YOURNAME/openclaw_sync.git"
sync_interval_minutes: 5
device_name: "ubuntu"
conflict_strategy: "notify"
auto_pull_on_start: true
auto_push_enabled: true

paths:
  sync:
    - "USER.md"
    - "MEMORY.md"
    - "SOUL.md"
    - "skills/"
    - "memory/"
  ignore:
    - "logs/"
    - "temp/"
    - "*.log"
```

## Syncable Files

| File | Description | Recommended |
|------|-------------|-------------|
| `USER.md` | User profile (name, timezone, background) | ✅ Yes |
| `MEMORY.md` | Long-term memory and important context | ✅ Yes |
| `SOUL.md` | AI behavior rules and guidelines | ✅ Yes |
| `skills/` | Installed skills and capabilities | ✅ Yes |
| `memory/` | Daily logs and session records | ✅ Yes |
| `TOOLS.md` | Local tool notes and configurations | Optional |
| `IDENTITY.md` | AI identity (name, vibe, emoji) | Optional (different per device) |

## File Naming Convention

Memory files use device prefix to avoid conflicts:

```
memory/
├── ubuntu-2026-03-01.md      # Ubuntu device
├── macmini-2026-03-01.md     # Mac Mini device
└── laptop-2026-03-01.md      # Laptop device
```

Shared files (no prefix):
- `USER.md`
- `MEMORY.md`
- `SOUL.md`

## Commands

| Command | Description |
|---------|-------------|
| `sync-init` | Initialize git repo and config |
| `sync-status` | Check sync status |
| `sync-now` | Immediate pull + push |
| `sync-pull` | Manual pull |
| `sync-push` | Manual push |
| `sync-resolve` | Interactive conflict resolution |
| `sync-daemon.sh start/stop/restart/status` | Manage background sync |

## Conflict Resolution

When conflicts detected:

1. Sync paused automatically
2. Run `sync-resolve` to:
   - View conflicting files
   - Choose: keep-local / keep-remote / merge-manual / view-diff
3. Resume sync after resolution

## Adding New Device

### Option A: Interactive

```bash
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh | bash
# Select "Add to existing sync"
```

### Option B: Manual

```bash
git clone git@github.com:YOURNAME/openclaw_sync.git ~/openclaw-sync
cd ~/openclaw-sync
~/openclaw-skills/multi-device-sync-github/scripts/sync-init.sh \
  --device-name NEWNAME \
  --repo-url "git@github.com:YOURNAME/openclaw_sync.git"
~/openclaw-skills/multi-device-sync-github/scripts/sync-daemon.sh start
```

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for common issues.

## Security Note

**Use a private GitHub repository** to protect your personal data.

The following files may contain sensitive information:
- `MEMORY.md` - May include IP addresses, service URLs
- `memory/` - Daily logs with potentially sensitive details

## Files in This Skill

```
multi-device-sync-github/
├── SKILL.md                  # This file
├── README.md                 # GitHub README
├── LICENSE                   # MIT License
├── install.sh                # Interactive installer
├── _meta.json                # ClawHub metadata
├── scripts/
│   ├── sync-init.sh             # Initialize sync repo
│   ├── sync-daemon.sh           # Background sync (pull + push watcher)
│   ├── sync-push.sh             # Push changes to remote
│   ├── sync-pull.sh             # Pull changes from remote
│   ├── sync-status.sh           # Show sync status
│   ├── sync-now.sh              # Immediate sync
│   ├── sync-resolve.sh          # Conflict resolution
│   └── sync-notify           # Notification helper
└── references/
    └── troubleshooting.md    # Common issues
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Security & Safety

### Default Settings (Safe by Default)

- **Auto-push disabled**: `auto_push_enabled: false` by default
- **Confirmation prompts**: Destructive operations require user confirmation
- **Selective git operations**: Only configured files are committed

### Installation Safety

**Recommended (Safest):**
```bash
git clone https://github.com/RegulusZ/multi-device-sync-github.git
cd multi-device-sync-github
./install.sh
```

**Convenience (Review First):**
```bash
# Download and review before executing
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh -o install.sh
cat install.sh  # Review the code
./install.sh
```

### Data Protection

- **Automatic backups**: Files are backed up before replacement
- **No external endpoints**: Notifications are local-only
- **User control**: All operations can be reviewed before execution

### Permissions

The skill requires:
- Read/write access to `~/.openclaw/workspace/`
- Git push access to your sync repository
- No network access beyond GitHub

### Enabling Auto-Push

After reviewing the behavior, enable auto-push:

```bash
# Edit config
nano ~/.config/openclaw/sync-config.yaml

# Change:
auto_push_enabled: true
```

## Security & Safety

### Default Settings (Safe by Default)

- **Auto-push disabled**: `auto_push_enabled: false` by default
- **Confirmation prompts**: Destructive operations require user confirmation
- **Selective git operations**: Only configured files are committed

### Installation Safety

**Recommended (Safest):**
```bash
git clone https://github.com/RegulusZ/multi-device-sync-github.git
cd multi-device-sync-github
./install.sh
```

**Convenience (Review First):**
```bash
curl -fsSL https://raw.githubusercontent.com/RegulusZ/multi-device-sync-github/main/install.sh -o install.sh
cat install.sh  # Review before executing
./install.sh
```

### Data Protection

- **Automatic backups**: Files backed up before replacement
- **No external endpoints**: Notifications are local-only
- **User control**: All operations can be reviewed before execution

### Enabling Auto-Push

After reviewing behavior, enable in config:
```yaml
auto_push_enabled: true
```
