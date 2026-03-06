---
name: memory-git-sync
description: Automates the backup of the OpenClaw workspace to a remote Git repository. Handles large file exclusions, validates git configuration, and performs intelligent sync with conflict resolution.
metadata:
  openclaw:
    emoji: "📦"
    requires:
      bins:
        - bash
        - git
    compatibility:
      bash: "4.0 or higher"
      git: "2.0 or higher"
    system_requirements:
      - "Write access to repository directory"
      - "Access to remote Git repository (GitHub, GitLab, etc.)"
    configuration_required:
      - "Git user.name configured locally or globally"
      - "Git user.email configured locally or globally"
      - "Remote 'origin' configured in Git"
      - "Git credentials properly stored (credential helper or SSH key)"
    runtime_requirements:
      - "Network connectivity to push/pull from remote"
      - "Read/write access to .git directory and working tree"
    tags:
      - "git"
      - "backup"
      - "sync"
      - "automation"
---

# Memory Sync Skill

Automates Git synchronization and backup of workspace memory to a remote repository.

## Quick Start

```bash
bash ./scripts/sync.sh [COMMIT_MESSAGE]
```

Default message: `chore: memory backup YYYY-MM-DD HH:MM`

## What It Does

1. **Validates** Git repository, user config, and remote access
2. **Detects & excludes** large files (>95MB) to prevent push failures
3. **Stages** all changes automatically
4. **Pulls** latest remote changes to avoid conflicts
5. **Commits** changes with timestamped or custom message
6. **Pushes** to remote, setting upstream if needed

## Prerequisites

✓ Git repository initialized with `origin` remote
✓ `git config user.name` and `git config user.email` set
✓ Network access to remote repository
✓ Write permissions on repository directory

## Execution Steps

| Step | Action | Success Output | Failure Output | Exit |
|------|--------|---|---|---|
| 1 | Validate Git repo | `[SUCCESS] Git repository found` | `[ERROR] Not inside a git repository` | 1 |
| 2 | Check Git config | `[SUCCESS] Git user configuration is valid` | `[ERROR] Git user.name not configured` | 1 |
| 3 | Check remote | `[SUCCESS] Remote 'origin' configured: [URL]` | `[ERROR] No 'origin' remote` | 1 |
| 4 | Setup .gitignore | `[SUCCESS] Gitignore file is ready` | - | - |
| 5 | Scan large files | `[SUCCESS] No large files detected` | `[WARNING] Large files detected` | - |
| 6 | Detect changes | `[SUCCESS] All changes staged` | `[INFO] No uncommitted changes` | 0 |
| 7 | Fetch remote | `[SUCCESS] Successfully fetched` | `[WARNING] Fetch failed (continues)` | - |
| 8 | Check sync | `[INFO] Local and remote synchronized` | `[WARNING] Branches diverged (auto-pull)` | 1* |
| 9 | Commit | `[SUCCESS] Changes committed` | `[ERROR] Commit failed` | 1 |
| 10 | Push | `[SUCCESS] Successfully pushed` | `[WARNING] No upstream (tries to set)` | 1** |
| Done | Complete | `[SUCCESS] Sync completed` | - | 0 |

*Auto-resolves with `git pull --no-edit`
**Auto-sets upstream with `git push --set-upstream origin [branch]`

## Output Format

All messages use structured prefixes for LLM parsing:

```
[INFO]    - Informational messages
[SUCCESS] - Actions completed successfully
[WARNING] - Non-fatal issues (script recovers)
[ERROR]   - Fatal errors (requires intervention)
```

## Common Scenarios

| Issue | Output | Resolution |
|-------|--------|-----------|
| Not in a Git repo | `[ERROR] Not inside a git repository` | Navigate to repo: `cd /path/to/repo` |
| Missing user.name | `[ERROR] Git user.name not configured` | `git config user.name "Name"` |
| Missing user.email | `[ERROR] Git user.email not configured` | `git config user.email "email@example.com"` |
| No origin remote | `[ERROR] No 'origin' remote configured` | `git remote add origin <URL>` |
| Large files detected | `[WARNING] Large files detected` | Automatically added to .gitignore |
| Pull conflicts | `[ERROR] Pull encountered conflicts` | Resolve manually, then run sync again |
| Network failures | `[WARNING] Fetch/Push failed` | Check connectivity, script continues locally |

## Features

- **Auto Large-File Handling**: Prevents Git failures by ignoring files >95MB
- **Conflict Resolution**: Auto-pulls remote before pushing
- **Upstream Setup**: Auto-configures tracking on first push
- **Validation**: Pre-flight checks prevent common errors
- **LLM-Compatible Output**: Structured logs for easy parsing

## Security Notes

- Don't commit credentials to the repository
- Use SSH keys or credential helpers: `git config credential.helper osxkeychain`
- Review changes before syncing: `git status`
- Large files already pushed can't be auto-removed by this script
