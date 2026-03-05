---
name: spirit
description: |
  State Preservation & Identity Resurrection Infrastructure Tool (SPIRIT).
  Preserves AI agent identity, memory, and projects to a private Git repository.
  
  NEW: Workspace mode - symlinked config for easy editing in your OpenClaw workspace.
  
metadata:
  openclaw:
    requires:
      bins: ["spirit", "git"]
    install:
      - id: spirit-cli
        kind: brew
        tap: TheOrionAI/tap
        package: spirit
        bins: ["spirit"]
        label: Install SPIRIT via Homebrew
---

# SPIRIT 🌌
> **S**tate **P**reservation & **I**dentity **R**esurrection **I**nfrastructure **T**ool

Preserves AI agent identity, memory, and projects in a portable Git repository.
**Your AI's spirit, always preserved.** Death. Migration. Multi-device. **Always you.**

## New: OpenClaw Workspace Mode 🆕

SPIRIT can now link directly to your OpenClaw workspace:

```bash
# Initialize with workspace mode
spirit init --workspace=/root/.openclaw/workspace --name="orion" --emoji="🌌"

# All your identity/memory files stay in workspace
# Only .spirit-tracked config is symlinked to ~/.spirit/
```

**Benefits:**
- ✅ Edit `.spirit-tracked` config directly in workspace
- ✅ All identity/memory files in one place
- ✅ Sync with `SPIRIT_SOURCE_DIR=/root/.openclaw/workspace spirit sync`

---

## Requirements

| Tool | Purpose | Required? | Install |
|------|---------|-----------|---------|
| `git` | Version control | **Required** | Built-in |
| `spirit` | This tool | **Required** | `brew install TheOrionAI/tap/spirit` |
| `gh` | GitHub CLI | Optional* | `brew install gh` |

*Only needed if you prefer GitHub CLI auth. SSH keys work without `gh`.

---

## Quick Start

### Option A: OpenClaw Workspace Mode (Recommended)

```bash
# 1. Initialize with your OpenClaw workspace
spirit init --workspace=/root/.openclaw/workspace --name="orion" --emoji="🌌"

# 2. Edit what gets synced
cat /root/.openclaw/workspace/.spirit-tracked

# 3. Configure git remote
cd ~/.spirit
git remote add origin git@github.com:USER/PRIVATE-REPO.git

# 4. Sync
export SPIRIT_SOURCE_DIR=/root/.openclaw/workspace
spirit sync
```

### Option B: Standard Mode (Legacy)

```bash
# Files live in ~/.spirit/
spirit init --name="orion" --emoji="🌌"
spirit sync
```

---

## SPIRIT_SOURCE_DIR Environment Variable

When set, SPIRIT reads files from this directory instead of `~/.spirit/`:

```bash
# One-time sync
SPIRIT_SOURCE_DIR=/path/to/workspace spirit sync

# Or export for session
export SPIRIT_SOURCE_DIR=/path/to/workspace
spirit sync
```

The `.spirit-tracked` config is still read from `~/.spirit/` (which may be a symlink to your workspace).

---

## What Gets Preserved

With **OpenClaw workspace mode**, these files sync from your workspace:

| File | Contents |
|------|----------|
| `IDENTITY.md` | Your agent's identity |
| `SOUL.md` | Behavior/personality guidelines |
| `AGENTS.md` | Agent configuration |
| `USER.md` | User preferences |
| `memory/*.md` | Daily conversation logs |
| `projects/*.md` | Active project files |
| `.spirit-tracked` | **Config**: What to sync (edit this!) |

**Default `.spirit-tracked`:**
```json
{
  "version": "1.0.0",
  "files": [
    "IDENTITY.md",
    "SOUL.md",
    "AGENTS.md",
    "USER.md",
    "memory/*.md",
    "projects/*.md"
  ]
}
```

---

## Authentication Options

### Option 1: SSH Keys (Recommended, no `gh` needed)

```bash
cd ~/.spirit
git remote add origin git@github.com:USER/REPO.git
```

### Option 2: GitHub CLI

```bash
gh auth login
git remote add origin https://github.com/USER/REPO.git
```

### Option 3: Git Credential Helper

```bash
git config credential.helper cache  # or 'store' for persistence
git remote add origin https://github.com/USER/REPO.git
```

---

## Security Checklist

☑️ **Repository:** Always PRIVATE — state files contain identity and memory
☑️ **Authentication:** Use SSH keys or `gh auth login` — never tokens in URLs
☑️ **Review:** Check `cat ~/.spirit/.spirit-tracked` before sync
☑️ **Test:** Verify first sync in isolation

**Never use:**
- ❌ `https://TOKEN@github.com/...` in remote URL
- ❌ Tokens in shell history or process lists

---

## Scheduled Sync

```bash
# Add to crontab
crontab -e

# Every 15 minutes
*/15 * * * * SPIRIT_SOURCE_DIR=/root/.openclaw/workspace /usr/local/bin/spirit sync 2>/dev/null
```

---

## Restore on New Machine

```bash
# Install SPIRIT
curl -fsSL https://theorionai.github.io/spirit/install.sh | bash

# Clone your state
git clone git@github.com:USER/REPO.git ~/.spirit

# If using workspace mode, set source directory
export SPIRIT_SOURCE_DIR=/your/workspace/path
```

---

## Resources

- **SPIRIT:** https://github.com/TheOrionAI/spirit
- **GitHub CLI:** https://cli.github.com

---

**License:** MIT
