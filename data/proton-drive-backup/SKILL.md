---
name: proton-drive-backup
version: 1.0.0
description: Automated backup to Proton Drive with age-based truncation — sync configs, memory files, content drafts, and media with configurable retention periods. Use when you need privacy-first cloud backup for AI workspaces. Requires Proton Drive desktop app.
metadata:
  {"openclaw": {"emoji": "☁️", "requires": {"bins": ["bash", "rsync"], "env": []}, "primaryEnv": null, "network": {"outbound": false, "reason": "Copies files to local Proton Drive sync folder. Proton Drive app handles encrypted upload separately."}}}
---

# Proton Drive Backup

Privacy-first cloud backup via Proton Drive's local sync folder. Copies workspace files with age-based truncation to keep storage manageable.

## Retention Policy

| Content Type | Retention | Rationale |
|---|---|---|
| Configs (plists, JSON) | Forever | Small, critical |
| Memory files | 60 days | Daily notes age out |
| Content drafts | Forever | Intellectual property |
| Images | 90 days | Large, reproducible |
| Audio | 30 days | Very large, reproducible |
| Video | 60 days | Largest files |
| Docker backups | Keep 3 | Rotated |

## Usage

```bash
bash scripts/backup_to_proton.sh
```

Safe to run multiple times — uses rsync for incremental sync.

## Files

- `scripts/backup_to_proton.sh` — Backup script with configurable paths and retention
