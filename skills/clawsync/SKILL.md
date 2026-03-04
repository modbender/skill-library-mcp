---
name: clawback
description: Backup and restore your OpenClaw workspace to GitHub
metadata:
  {
    "openclaw": {
      "emoji": "💾",
      "requires": { 
        "env": ["GITHUB_TOKEN", "BACKUP_REPO", "OPENCLAW_WORKSPACE"] 
      }
    }
  }
---

# ClawSync

Backup and restore your OpenClaw workspace to GitHub.

## ⚠️ Security First

This skill is designed with defense-in-depth. Please read carefully.

## What It Backs Up

| Category | Files | Status |
|----------|-------|--------|
| **Identity Files** | AGENTS.md, SOUL.md, USER.md, TOOLS.md, IDENTITY.md, HEARTBEAT.md | ✅ Safe |
| **Skills** | All from `$OPENCLAW/skills/` | ⚠️ Manual review |
| **Scripts** | All from `$OPENCLAW/scripts/` | ⚠️ Manual review |

### Why Some Files Are Not Backed Up

The following files are **NOT** backed up by design:
- **SITES.md** — May contain API keys/secrets
- **MEMORY.md** — May contain sensitive conversation data
- Any file in `credentials/`, `.env`, `node_modules/`

## What It Excludes

- ❌ API keys and tokens (any format)
- ❌ Credentials folder
- ❌ .env files
- ❌ node_modules
- ❌ .git directories
- ❌ Nested git repositories
- ❌ Files containing secrets (detected by regex)

## Secret Detection

ClawSync scans for these secret patterns:
- GitHub tokens (`ghp_*`)
- OpenAI keys (`sk-*`)
- Google API keys (`AIza*`)
- Slack tokens (`xoxb-*`, `xoxp-*`)
- AWS access keys (`AKIA*`)
- JWTs and bearer tokens
- Private keys (`-----BEGIN * PRIVATE KEY-----`)
- High-entropy strings

If any are detected → **backup aborts before push**.

## Environment Variables (Required)

```bash
export GITHUB_TOKEN="ghp_xxxx"
export BACKUP_REPO="username/repo-name"
export OPENCLAW_WORKSPACE="${HOME}/openclaw-workspace"
```

### 🔐 Recommended: Fine-Grained PAT

For least privilege, use a GitHub Fine-Grained PAT:
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create new token with:
   - **Repository access**: Only `$BACKUP_REPO`
   - **Permissions**: Contents: Write
3. Use this token as `GITHUB_TOKEN`

## Quick Start

```bash
git clone https://github.com/your-username/clawsync.git ~/clawsync
cp .env.example .env
# Edit .env with your values
bash sync.sh
```

## Features

- **Pre-flight Check**: Validates required env vars before running
- **Strict Whitelist**: Only copies explicitly allowed files
- **Deny List**: Filters out .git, credentials, node_modules
- **Secret Scrubbing**: Detects 100+ secret patterns, aborts if found
- **Safe Restore**: Requires --force or confirmation before overwriting

## Safe Restore

```bash
# With confirmation (default)
bash restore.sh

# Force mode (no prompt)
bash restore.sh --force
```

## Auth

Uses gh CLI if available, falls back to token auth.

## Files

- `sync.sh` - Backup script (ShellCheck compliant)
- `restore.sh` - Restore script  
- `.env_example` - Template
- `.gitignore` - Blocks secrets

## Development & Release

### Running Tests Locally

```bash
# Set up test workspace
mkdir -p /tmp/test-workspace
echo "test" > /tmp/test-workspace/AGENTS.md
echo "test" > /tmp/test-workspace/USER.md
mkdir -p /tmp/test-workspace/skills /tmp/test-workspace/scripts

# Run integration test
export BACKUP_REPO="test/repo"
export OPENCLAW_WORKSPACE="/tmp/test-workspace"
export GITHUB_TOKEN="dummy"

cd /tmp && rm -rf test-backup-repo && mkdir test-backup-repo
cd test-backup-repo && git init
cp ~/clawsync/sync.sh .
bash sync.sh
```

### Testing Secret Detection

```bash
# Create a test file with a fake secret
echo "My API key is ghp_test1234567890abcdefghijklmnopqrstuvwxyz" > /tmp/test-workspace/AGENTS.md

# Run sync - should abort with error
bash sync.sh

# Expected output: "Error: Potential secret detected..."
```

### Security Audit Test (Proves Non-Staged Detection)

This test verifies the script catches secrets BEFORE they are staged:

```bash
# Set up test workspace
export BACKUP_REPO="test/repo"
export OPENCLAW_WORKSPACE="/tmp/test-workspace"
export GITHUB_TOKEN="dummy"

# Create workspace with secret in a non-staged file
mkdir -p /tmp/test-workspace
echo "Real API key: sk-realapikey12345678901234567890" > /tmp/test-workspace/AGENTS.md

# Copy sync.sh to temp backup dir
cd /tmp && rm -rf audit-test && mkdir audit-test && cd audit-test
git init
cp ~/clawsync/sync.sh .

# Run sync - should FAIL (catches non-staged secret)
bash sync.sh

# Expected: "Error: Potential secret detected in backup directory!"
# This proves the pre-git-add scanning works
```

### Publishing to ClawHub

The CI runs on every push and pull request:
1. **ShellCheck** - Lints bash scripts
2. **Integration test** - Verifies backup/restore works

To publish a new version:

```bash
git add -A
git commit -m "Release v1.0.x"
git tag v1.0.x
git push origin master --tags
```

CI will automatically:
- Run tests
- If tests pass and tag starts with `v*`, publish to ClawHub
