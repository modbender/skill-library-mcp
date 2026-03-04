---
name: openclaw-git
description: Git automation for OpenClaw workspace. Use when user needs to commit and push changes from /home/roger/.openclaw to the remote repository. Triggers on: git commit, git push, save changes, backup openclaw.
---

# OpenClaw Git

Automated git commit and push for the OpenClaw workspace.

## Quick Start

### Commit and Push Changes

```bash
# Default commit message
~/.openclaw/workspace/skills/openclaw-git/scripts/git-push.sh

# Custom commit message
~/.openclaw/workspace/skills/openclaw-git/scripts/git-push.sh "Your commit message"
```

## What It Does

1. Changes to `/home/roger/.openclaw`
2. Stages all changes (`git add .`)
3. Commits with message (default: "update: $(date)")
4. Pushes to origin main

## Usage in Skill Upload Workflow

When uploading skills to ClawHub, use OpenClaw Git to backup all workspace changes:

### Skill Upload Complete Workflow

```bash
# Step 1: Upload skill to ClawHub (manual or scripted)
cd ~/.openclaw/workspace/skills/<skill-name>
clawhub publish . --version <version> --changelog "description"

# Step 2: Commit and push all workspace changes using OpenClaw Git
~/.openclaw/workspace/skills/openclaw-git/scripts/git-push.sh "Upload <skill-name> v<version> and sync workspace"

# Alternative: Use default timestamp message
~/.openclaw/workspace/skills/openclaw-git/scripts/git-push.sh
```

### What Gets Backed Up

- Skill code changes
- Documentation updates (SKILL.md, TOOLS.md, MEMORY.md)
- Configuration files
- Learning records (.learnings/)
- Daily memory files

### Integration Points

This script is automatically called at the end of the "skill upload" workflow to ensure all changes are persisted to Git before finishing.

---

## Prerequisites

- Git repository initialized at `/home/roger/.openclaw`
- Remote origin configured
- Credentials configured (or use SSH key)

## Credentials

GitHub:
- Username: Roger0808
- Token: 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

## Script Reference

See [scripts/git-push.sh](scripts/git-push.sh) for the automation script.
