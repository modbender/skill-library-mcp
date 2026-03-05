# Workspace Organization - Installation & Setup

Automated maintenance and organization standards for OpenClaw workspaces.

## Quick Install

```bash
# Via ClawHub (when published)
clawhub install workspace-organization

# Or manual install
cd ~/.openclaw/workspace/skills
# Download from ClawHub or extract package
```

## First-Time Setup

1. **Initialize workspace structure (optional, if starting fresh):**
```bash
cd ~/.openclaw/workspace/skills/workspace-organization
./setup.sh
```

This creates:
```
workspace/
├── projects/       # writing/, code/
├── notes/          # daily-reviews/, decisions/, cost-tracking.md
├── memory/         # owner/, sessions/
├── skills/         # Custom skills
├── subagents/      # Permanent specialists + _archived/
├── docs/           # Documentation
└── scripts/        # Utility scripts
```

2. **Run first audit:**
```bash
./maintenance-audit.sh
```

3. **Schedule automated audits (recommended):**
```bash
openclaw cron add \
  --name "Weekly Workspace Audit" \
  --schedule "0 4 * * 0" \
  --task "Run workspace maintenance audit: bash skills/workspace-organization/maintenance-audit.sh. Log findings to notes/maintenance-log.md"
```

## Usage

### Manual Audit

```bash
cd ~/.openclaw/workspace/skills/workspace-organization
./maintenance-audit.sh
```

### Agent-Driven

Ask your agent:
```
"Run workspace maintenance audit"
"Check workspace health"
"What's taking up disk space?"
```

### Example Output

```
=== Workspace Maintenance Audit ===
Date: 2026-02-21 16:00
Path: /home/user/.openclaw/workspace

1. Checking for broken symlinks...
✓ No broken symlinks

2. Checking for empty directories...
ℹ️  Found empty directories:
/home/user/.openclaw/workspace/projects/abandoned

3. Checking for large files (>10MB)...
ℹ️  Found large files:
24M	logs/debug.log

4. Checking for malformed file/directory names...
⚠️  Found malformed names:
/home/user/.openclaw/workspace/my project/file.md
   Recommendation: Rename to 'my-project/file.md'

5. Disk usage by top-level directory:
150M	skills
80M	notes
50M	projects

6. File counts:
  Total files: 1,234
  Total directories: 156
  Skills: 18
  Subagents: 3

7. Recently modified files (last 24 hours):
notes/cost-tracking.md
memory/owner/decisions.md

=== Audit Complete ===
```

## What Gets Checked

| Check | What It Finds | Action |
|-------|---------------|--------|
| **Broken symlinks** | Dead links from moved/deleted files | Remove or update target |
| **Empty directories** | Leftover from deleted projects | Remove unless placeholder |
| **Large files** | >10MB files eating disk space | Compress, archive, or delete |
| **Malformed names** | Spaces, special chars in filenames | Rename to kebab-case |
| **Disk usage** | Space used by top-level dirs | Archive or cleanup |
| **Recent changes** | Files modified in last 24h | Review for unexpected edits |
| **Git status** | Unstaged/untracked files (if .git exists) | Commit or ignore |

## Automation Schedule

| Frequency | Action | Reason |
|-----------|--------|--------|
| **Daily** | None | Too noisy |
| **Weekly** | Audit + log | Catch issues early |
| **Monthly** | Audit + review with user | Approve cleanup |
| **On-demand** | Before backups | Reduce backup size |

## Customization

### Change Large File Threshold

Edit `maintenance-audit.sh`:
```bash
# From 10MB to 50MB
find "$WS" -type f -size +50M
```

### Exclude More Directories

Add to empty directory check:
```bash
| grep -v "your-custom-dir"
```

### Add Custom Checks

Example: Check for old log files
```bash
echo "9. Checking for old log files (>30 days)..."
find "$WS" -name "*.log" -mtime +30 2>/dev/null
```

## Integration

**Works with:**
- **openclaw-backup:** Audit before backup to reduce size
- **cost-governor:** Track disk usage for storage costs
- **drift-guard:** Organizational entropy as behavioral drift indicator

## Troubleshooting

**"Script fails on macOS"**
```bash
brew install findutils
# Use gfind instead of find
```

**"Too many empty directories"**
- Exclude more in script (e.g., `.cache`, `.venv`)

**"Large files are intentional"**
- Document why in `notes/workspace-notes.md`
- Consider external storage (S3, NAS)

## Organization Standards

### File Naming
- ✅ Use kebab-case: `my-project-file.md`
- ✅ Use snake_case: `my_script.py`
- ❌ Avoid spaces: `my project.md`
- ❌ Avoid special chars: `file(copy).md`

### Directory Structure
- Keep related files together
- Use top-level dirs for major categories
- Archive old work to `_archived/`
- Use README.md in each major dir

### Cleanup Policy
**Keep:**
- Active projects
- Recent notes (<3 months)
- Custom skills in use

**Archive:**
- Completed projects
- Old research
- Deprecated skills

**Delete:**
- Broken symlinks
- Empty directories (unless placeholder)
- Logs older than 30 days
- Temp files (`*.tmp`, `*.cache`)

## Contributing

Submit improvements to detection logic or additional checks. Open PRs welcome.

## License

MIT - Free to use, modify, distribute.

## Credits

Created by the OpenClaw community. Keep your workspace clean.
