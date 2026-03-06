---
name: arc-skill-gitops
description: Automated deployment, rollback, and version management for agent workflows and skills.
user-invocable: true
metadata: {"openclaw": {"emoji": "🚀", "os": ["darwin", "linux"], "requires": {"bins": ["python3", "git"]}}}
---

# Agent GitOps

Automated deployment and rollback for agent workflows. Track skill versions, deploy with confidence, roll back when things break.

## Why This Exists

Agents install and update skills constantly. When an update breaks something, you need to:
1. Know what changed
2. Roll back fast
3. Track which version was stable

This skill manages that lifecycle.

## Commands

### Initialize tracking for a skill
```bash
python3 {baseDir}/scripts/gitops.py init --skill ~/.openclaw/skills/my-skill/
```

### Snapshot the current state (before updating)
```bash
python3 {baseDir}/scripts/gitops.py snapshot --skill ~/.openclaw/skills/my-skill/ --tag "pre-update"
```

### Deploy a skill update (snapshots current state first)
```bash
python3 {baseDir}/scripts/gitops.py deploy --skill ~/.openclaw/skills/my-skill/ --tag "v1.1"
```

### List all snapshots for a skill
```bash
python3 {baseDir}/scripts/gitops.py history --skill ~/.openclaw/skills/my-skill/
```

### Roll back to a previous snapshot
```bash
python3 {baseDir}/scripts/gitops.py rollback --skill ~/.openclaw/skills/my-skill/ --tag "pre-update"
```

### Check status of all tracked skills
```bash
python3 {baseDir}/scripts/gitops.py status
```

### Run pre-deploy checks (integrates with arc-skill-scanner if available)
```bash
python3 {baseDir}/scripts/gitops.py check --skill ~/.openclaw/skills/my-skill/
```

## Data Storage

Snapshots and metadata are stored in `~/.openclaw/gitops/`.

## How It Works

1. **init** creates a git repo in the skill directory (if not already one) and records it in the tracking manifest
2. **snapshot** commits the current state with a tag
3. **deploy** takes a pre-deploy snapshot, then commits the new state
4. **rollback** restores a tagged snapshot using git checkout
5. **check** runs arc-skill-scanner (if installed) as a pre-deploy gate
6. **history** shows all tagged snapshots with timestamps
7. **status** shows all tracked skills and their current/latest versions

## Tips

- Always snapshot before updating a skill manually
- Use `deploy` instead of manual updates — it snapshots automatically
- Combine with `arc-skill-scanner` for security-gated deployments
- Tags should be descriptive: "v1.2", "pre-security-patch", "stable-2026-02-15"
