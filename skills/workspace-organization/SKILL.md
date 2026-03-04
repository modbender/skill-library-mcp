---
name: workspace-organization
version: 1.0.0
description: Automated workspace health checks and entropy prevention for OpenClaw. Detects broken symlinks, empty dirs, large files, malformed names. Maintenance audit script with cron support. Keeps deployments clean and structured.
homepage: https://clawhub.com
changelog: Initial release - Maintenance audit, setup script, organization standards
metadata:
  openclaw:
    emoji: "📁"
    requires:
      bins: ["bash", "find", "du"]
    os:
      - linux
      - darwin
---

# Workspace Organization

Standards and automated maintenance for clean OpenClaw deployments.

## Files Included

- `SKILL.md` — Agent instructions
- `README.md` — Setup guide
- `maintenance-audit.sh` — Run to audit workspace health
- `setup.sh` — Run once to initialize standard structure

**Note:** Scripts auto-detect your workspace. Pass a path as argument to override: `./maintenance-audit.sh /custom/path`

## Problem Solved

Workspaces degrade over time:
- Broken symlinks from moved files
- Empty directories from deleted projects
- Large files eating disk space
- Malformed names breaking scripts
- No visibility into workspace health

This skill provides automated audits + cleanup guidance to prevent entropy.

## When to Use

- **New workspace setup** — Initialize standard directory structure
- **Periodic maintenance** — Weekly/monthly health checks (cron recommended)
- **Pre-deployment cleanup** — Remove cruft before backups
- **Debugging workspace issues** — Find broken symlinks, malformed names
- **Disk space review** — Identify large files and bloat

## What It Provides

### 1. maintenance-audit.sh
Automated health check script that detects:
- ✅ Broken symlinks
- ✅ Empty directories (excluding node_modules, .git)
- ✅ Large files (>10MB)
- ✅ Malformed file/directory names (spaces, special chars)
- ✅ Disk usage by top-level directory
- ✅ File/directory counts
- ✅ Recent changes (last 24 hours)

### 2. setup.sh
Initializes standard workspace structure:
```
~/.openclaw/workspace/
├── projects/           # Active work
│   ├── writing/        # Writing projects
│   └── code/           # Code projects
├── notes/              # Organized notes
│   ├── daily-reviews/
│   ├── decisions/
│   └── cost-tracking.md
├── memory/             # Long-term memory
│   ├── owner/          # Cross-channel user memory
│   └── sessions/       # Per-session isolated memory
├── skills/             # Custom skills
├── subagents/          # Permanent specialists
│   └── _archived/      # Old/deprecated subagents
├── docs/               # Documentation
└── scripts/            # Utility scripts
```

### 3. Organization Standards (docs/)
Best practices for:
- File naming conventions (kebab-case, no spaces)
- Directory structure guidelines
- Cleanup policies (what to keep/delete)
- Git integration patterns

## Setup

1. **Install skill:**
```bash
cd ~/.openclaw/workspace/skills
clawhub install workspace-organization
# Or: download from ClawHub and extract
```

2. **Initialize workspace (optional, if starting fresh):**
```bash
cd ~/.openclaw/workspace/skills/workspace-organization
./setup.sh
```

3. **Run first audit:**
```bash
cd ~/.openclaw/workspace/skills/workspace-organization
./maintenance-audit.sh
```

4. **Schedule automated audits (recommended):**
```bash
openclaw cron add \
  --name "Weekly Workspace Audit" \
  --schedule "0 4 * * 0" \
  --task "Run workspace maintenance audit: bash skills/workspace-organization/maintenance-audit.sh. Log results to notes/maintenance-log.md"
```

## Usage

### Manual Audit

```bash
cd ~/.openclaw/workspace/skills/workspace-organization
./maintenance-audit.sh
```

**Example output:**
```
=== Workspace Maintenance Audit ===
Date: 2026-02-21 16:00
Path: /home/user/.openclaw/workspace

1. Checking for broken symlinks...
⚠️  Found broken symlinks:
/home/user/.openclaw/workspace/old-project/link-to-deleted

2. Checking for empty directories...
ℹ️  Found empty directories:
/home/user/.openclaw/workspace/projects/abandoned

3. Checking for large files (>10MB)...
ℹ️  Found large files:
24M	/home/user/.openclaw/workspace/logs/debug.log

4. Checking for malformed file/directory names...
⚠️  Found malformed names:
/home/user/.openclaw/workspace/projects/my project/file.md

5. Disk usage by top-level directory:
150M	skills
80M	notes
50M	projects
30M	memory

6. File counts:
  Total files: 1,234
  Total directories: 156
  Skills: 18
  Subagents: 3

7. Recently modified files (last 24 hours):
/home/user/.openclaw/workspace/notes/cost-tracking.md
/home/user/.openclaw/workspace/memory/owner/decisions.md

=== Audit Complete ===
```

### Agent-Driven Audit

Ask your agent:
```
"Run workspace maintenance audit"
"Check workspace health"
"Audit my workspace"
```

Agent will execute script and present findings with cleanup recommendations.

## Common Issues Caught

### 1. Broken Symlinks
**Causes:**
- Moved/renamed files
- Deleted dependencies
- Incorrect relative paths

**Fix:** Remove symlink or update target

### 2. Empty Directories
**Causes:**
- Deleted projects
- Failed installations
- Incomplete migrations

**Fix:** Remove unless intentionally placeholder

### 3. Large Files
**Common culprits:**
- Uncompressed logs (`debug.log`, `error.log`)
- Binary artifacts (`.zip`, `.tar.gz`)
- Downloaded datasets
- Video/media files

**Fix:** Compress, move to external storage, or delete

### 4. Malformed Names
**Problems caused by:**
- Spaces in filenames → breaks scripts
- Special characters → shell escaping issues
- Braces/brackets → glob conflicts

**Fix:** Rename using `kebab-case` or `snake_case`

**Example:**
```bash
# Bad
my project/file (copy).md

# Good
my-project/file-copy.md
```

## Workspace Health Score

After running `maintenance-audit.sh`, your workspace gets a score:

| Score | Status | Meaning |
|-------|--------|---------|
| 90-100 | 🟢 Healthy | Minor issues or none |
| 70-89 | 🟡 Fair | Some cleanup needed |
| 50-69 | 🟠 Degraded | Multiple issues accumulating |
| <50 | 🔴 Critical | Immediate cleanup required |

Score is calculated based on: broken symlinks (-10 each), empty dirs (-2 each), files >100MB (-5 each), malformed names (-3 each).

## Automation Strategy

| Frequency | Action | Reason |
|-----------|--------|--------|
| **Daily** | None | Too aggressive, creates noise |
| **Weekly** | Audit only, log results | Catch issues early |
| **Monthly** | Audit + present to user | Review & approve cleanup |
| **On-demand** | Before backups/deployments | Reduce backup size |

## Companion Skills

- **system-resource-monitor** — Disk usage alerts complement workspace health
- **cost-governor** — Track subagent costs alongside workspace hygiene

## Integration with Other Skills

- **openclaw-backup:** Audit before backup to reduce size
- **cost-governor:** Track disk usage for storage costs
- **drift-guard:** Organizational entropy as drift indicator

## Customization

### Adjust Large File Threshold

Edit `maintenance-audit.sh`:
```bash
# Change from 10MB to 50MB
find "$WS" -type f -size +50M 2>/dev/null
```

### Exclude Directories

Add to script:
```bash
find "$WS" -type d -empty 2>/dev/null \
  | grep -v "node_modules" \
  | grep -v ".git" \
  | grep -v "your-custom-dir"
```

### Add Custom Checks

Extend script with:
- Git repo status checks
- Dependency vulnerability scans
- License compliance audits

## Philosophy

- **Prevent entropy** — Structure degrades without maintenance
- **Automate detection** — Scripts catch what humans miss
- **User-approved cleanup** — Never auto-delete without permission
- **Standards over rigidity** — Guidelines, not laws

## Troubleshooting

**"Script fails on macOS"**
- Install GNU findutils: `brew install findutils`
- Use `gfind` instead of `find`

**"Too many empty directories flagged"**
- Exclude more dirs in script (e.g., `.cache`, `.venv`)

**"Large files are necessary"**
- Document in `notes/workspace-notes.md` why they're kept
- Consider moving to external storage (S3, NAS)

## Advanced: Multi-Workspace Support

If managing multiple OpenClaw instances:

```bash
# Audit all workspaces
for ws in ~/.openclaw-*; do
  WS="$ws/workspace" ./maintenance-audit.sh
done
```

---

**Author:** OpenClaw Community  
**License:** MIT  
**Requires:** Bash, GNU coreutils (find, du, sort)
