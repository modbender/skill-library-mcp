---
name: safe-update
description: Update OpenClaw from source code. Supports custom project path and branch. Includes pulling latest branch, rebasing, building and installing, restarting service. Triggered when user asks to update OpenClaw, sync source, rebase branch, or rebuild.
---

# Safe Update

Update OpenClaw from source to the latest version while preserving local changes.

## ⚠️ Important Warnings

- This script performs **git rebase** and **git push --force** - may lose local changes if not properly committed
- Uses **npm i -g .** for global installation - may require sudo
- Uses **systemctl --user restart** - will restart the OpenClaw service
- **Backup your config before running!** (see below)

## Requirements

Required binaries (must be installed):
- `git`
- `npm` / `node`
- `systemctl` (for restarting gateway)

## Configuration

### Environment Variables (optional)

```bash
# Set custom project path
export OPENCLAW_PROJECT_DIR="/path/to/openclaw"

# Set custom branch (default: main)
export OPENCLAW_BRANCH="your-feature-branch"

# Enable dry-run mode (no actual changes)
export DRY_RUN="true"
```

### Or Pass as Arguments

```bash
./update.sh --dir /path/to/openclaw --branch your-branch
```

## Workflow

### Step 1: Analyze Current State (Must Run First)

Before executing any update, check:
1. Whether the current branch has uncommitted changes
2. Whether the current branch has local modifications
3. Whether upstream has new commits
4. Recommend the most appropriate update strategy based on the situation

**Recommended Strategy:**

| Scenario | Recommended Method | Rationale |
|----------|-------------------|----------|
| Uncommitted local changes | Commit/stash first, then **merge** | Safe, no lost changes |
| Only clean local commits | **merge** or **rebase** | merge is safer, rebase keeps history clean |
| Preparing a PR | **rebase** recommended | Keeps history tidy |
| Routine dev update | **merge** recommended | Simple, less error-prone |

### Step 2: Ask User for Confirmation

After presenting the recommended options, **you must wait for user confirmation** before executing.

### Step 3: Execute Update

```bash
# 1. Enter project directory
cd "${OPENCLAW_PROJECT_DIR:-$HOME/projects/openclaw}"

# 2. Backup config files (good practice before update!)
echo "=== Backing up config files ==="
mkdir -p ~/.openclaw/backups
BACKUP_SUFFIX=$(date +%Y%m%d-%H%M%S)

# Backup main config
cp ~/.openclaw/openclaw.json ~/.openclaw/backups/openclaw.json.bak.$BACKUP_SUFFIX
echo "✅ Backed up: openclaw.json"

# Backup auth profiles (if exists)
if [ -f ~/.openclaw/agents/main/agent/auth-profiles.json ]; then
  cp ~/.openclaw/agents/main/agent/auth-profiles.json \
     ~/.openclaw/backups/auth-profiles.json.bak.$BACKUP_SUFFIX
  echo "✅ Backed up: auth-profiles.json"
fi

echo "💡 Backups saved to: ~/.openclaw/backups/"
echo ""

# 3. Add upstream repository (if not added)
git remote add upstream https://github.com/openclaw/openclaw.git 2>/dev/null || true

# 4. Fetch upstream changes
git fetch upstream

# 5. Update target branch (use merge or rebase based on user's choice)
git checkout $BRANCH
# merge: git merge upstream/$BRANCH
# rebase: git rebase upstream/$BRANCH

# 6. View changelog
echo "=== Full Changelog ==="
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v$(node -e 'console.log(require("./package.json").version)')")
echo "Current version: $CURRENT_TAG"
echo ""

# 7. Build and install
npm run build
npm i -g .

# 8. Reinstall systemd service (to update version number)
echo "=== Reinstalling Gateway service ==="
openclaw daemon install --force

# 9. Check version
NEW_VERSION=$(openclaw --version)
echo "✅ Update complete! New version: $NEW_VERSION"
echo ""

# 10. Ask user whether to restart
echo "=== Gateway needs restart to apply updates ==="
echo "Confirm restart? (y/N)"
```

## Quick Script

Run `scripts/update.sh` to automatically complete all steps above.

### Command Line Options

```bash
./update.sh [OPTIONS]

Options:
  --dir PATH       OpenClaw project directory (default: $HOME/projects/openclaw)
  --branch NAME    Git branch to update (default: main)
  --mode MODE      Update mode: merge or rebase (if not specified, will analyze and recommend)
  --dry-run       Show what would be done without executing
  --help          Show this help message
```

### Examples

```bash
# Update with defaults (will analyze and recommend)
./update.sh

# Update specific branch
./update.sh --branch feat/my-branch

# Force merge mode
./update.sh --mode merge

# Force rebase mode
./update.sh --mode rebase

# Dry run (preview only)
./update.sh --dry-run

# Custom project path
./update.sh --dir /opt/openclaw --branch main
```

## Notes

- **Rebase may cause conflicts** - if conflicts occur, resolve manually and continue
- **Force push** - after rebase, if pushing to fork, use `git push --force`
- **Service reinstall** - will update version in systemd unit file
- **User confirms restart** - Gateway will not restart until you confirm
- **Backup first** - always backup before updating!

## Troubleshooting

### Git Conflicts During Rebase

```bash
# Resolve conflicts manually, then:
git add .
git rebase --continue
# Continue with build steps
```

### Build Fails

```bash
# Clean and retry:
rm -rf node_modules dist
npm install
npm run build
```

### Gateway Won't Start

```bash
# Check status:
systemctl --user status openclaw-gateway

# View logs:
journalctl --user -u openclaw-gateway -n 50
```
