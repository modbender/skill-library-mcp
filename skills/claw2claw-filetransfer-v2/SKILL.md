---
name: claw2claw-filetransfer
description: Cross-platform file transfer between OpenClaw agents via rsync over SSH. From Claws for Claws - send files uncomplicated without getting drizzled by hot butter. Use when user wants to sync, backup, or transfer files between agents on different machines.
homepage: https://github.com/claw2claw/filetransfer
metadata:
  clawdbot:
    emoji: "📦"
    requires:
      bins:
        - rsync
        - ssh
    install:
      - id: rsync
        kind: apt
        packages:
          - rsync
          - openssh-client
        label: Install rsync + SSH
---

# claw2claw-filetransfer

**File transfer so smooth, even a lobster can do it.** 🦞

Send files between OpenClaw agents without the drama. rsync over SSH - delta transfers, compression, progress bars. Linux, macOS, Windows - we got you covered.

---

## When to Trigger This Skill

Use this skill when user wants to:
- Transfer files between two OpenClaw agents
- Sync project directories bidirectionally  
- Backup files to a remote agent
- Pull logs/data from remote agent
- Set up SSH connection between agents
- Move bits from A to B without crying

---

## Quick Start

```bash
# 1. Set up remote agent (one-time)
claw2claw setup 192.168.1.100 --user root

# 2. Send files like a pro
claw2claw send /backup.tar.gz

# 3. Get files back
claw2claw get /remote/logs.txt

# 4. Sync entire directories
claw2claw sync-to-remote ./my-project/
```

---

## Commands

| Command | Description |
|---------|-------------|
| `setup <host>` | Configure remote agent |
| `send <file>` | Upload to remote |
| `get <file>` | Download from remote |
| `sync-to-remote <dir>` | Push directory to remote |
| `sync-from-remote <dir>` | Pull directory from remote |
| `ls <path>` | List remote files |
| `status` | Show connection status |

---

## Options

| Option | Description |
|--------|-------------|
| `-n, --dry-run` | Preview without executing |
| `--compress` | Enable compression (default) |
| `--no-compress` | Disable compression |
| `--debug` | Enable debug output |

---

## Environment Variables

```bash
REMOTE_HOST="192.168.1.100"   # Remote IP/hostname
REMOTE_USER="root"            # SSH user
REMOTE_PORT="22"              # SSH port
SSH_KEY="/path/to/key"        # Custom SSH key
RSYNC_BWLIMIT=1000           # KB/s limit
```

---

## Why This Skill?

### Features
- **Delta transfers** - Only sends changed bytes
- **Compression** - Gzip on the wire
- **Progress bars** - Watch it go brrr
- **Bidirectional** - Push or pull
- **Cross-platform** - Linux, macOS, Windows
- **Key-based auth** - No passwords

### Use Cases
- Backup server to local
- Sync code between agents
- Pull logs for analysis
- Deploy static sites
- Share datasets

---

## Installation

### Linux
```bash
# Pre-installed on most distros
sudo apt install rsync
```

### macOS
```bash
brew install rsync
```

### Windows
```bash
# Option A: Git Bash (recommended)
# Download from https://git-scm.com

# Option B: cwrsync
# Download from https://www.itefix.net/cwrsync

# Option C: WSL
wsl --install
```

---

## Platform-Specific Notes

### Git Bash / MSYS2
- Uses Unix-style paths: `/c/Users/...`
- rsync usually pre-installed
- Works out of the box

### Windows Command Prompt / PowerShell
- Use full paths or forward slashes: `C:/Users/...`
- Or use cwrsync

### WSL
- Detected as Linux, works perfectly
- Can communicate with Windows filesystem

### Cygwin
- Install via Cygwin setup
- Path: `/cygdrive/c/Users/...`

---

## Performance Tips

### Compression
```bash
# On (default) - for text files
claw2claw send /logs/*.log

# Off - for already compressed files
claw2claw send /backup.tar.gz --no-compress
```

### Bandwidth
```bash
# Limit to 500 KB/s
RSYNC_BWLIMIT=500 claw2claw send /huge-file.tar.gz
```

### Large Files
```bash
# rsync auto-resumes interrupted transfers
# Just run same command again
claw2claw send /huge-file.tar.gz
```

### Selective Sync
```bash
# Only sync specific patterns
# Use --include and --exclude in rsync manually
# Or sync specific subdirectories
claw2claw sync-to-remote ./src/
```

---

## Testing Connection

### Quick Test
```bash
claw2claw status
```

### Manual SSH Test
```bash
ssh -o ConnectTimeout=5 user@host "echo OK"
```

### Test File Transfer
```bash
# Small test file first
echo "test" > /tmp/test.txt
claw2claw send /tmp/test.txt /tmp/
claw2claw get /tmp/test.txt /tmp/
rm /tmp/test.txt
```

---

## Troubleshooting

### "rsync: command not found"
```bash
# Linux
sudo apt install rsync

# macOS  
brew install rsync

# Windows
# Install Git Bash or cwrsync
```

### "Permission denied"
```bash
# Re-run setup to add SSH key
claw2claw setup <host> --user <user>
```

### "Connection timed out"
```bash
# Check host reachable
ping <host>

# Check port open
nc -zv <host> 22
```

---

## Examples

### Daily Backup
```bash
claw2claw send /backups/daily-$(date +%Y%m%d).tar.gz /backups/
```

### Project Sync
```bash
# Morning
claw2claw sync-from-remote /workspace/project/

# Evening  
claw2claw sync-to-remote /workspace/project/
```

### Log Collection
```bash
claw2claw get /var/log/syslog ./logs/
```

---

## Security

- SSH key-based auth only
- Keys: `~/.ssh/` (mode 700)
- Config: `~/.claw2claw.conf` (mode 600)
- No passwords in scripts

---

## Related Skills

Works well with:
- `blogwatcher` - Sync RSS feeds between agents
- `github` - Sync repositories after commits
- `playwright-scraper-skill` - Transfer scraped data
- Any skill that needs to share files

---

## Uninstall

```bash
rm /usr/local/bin/claw2claw
rm ~/.claw2claw.conf
rm -rf ~/.claw2claw/
```

---

**Made with 🦞🦞**

*From Claws for Claws. Transfer files uncomplicated.*
