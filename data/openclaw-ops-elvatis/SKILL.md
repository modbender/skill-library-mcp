---
name: openclaw-ops-elvatis
description: Operational commands - dashboards, monitoring, and management for OpenClaw deployments.
---

# OpenClaw Ops (Elvatis)

Operational tooling for OpenClaw deployments: dashboards, monitoring, config validation, safe restarts, and deployment management.

## Extension Commands

### Config Commands (`config-commands.ts`)
Validate and inspect OpenClaw configuration files. Ensures valid JSON, detects legacy keys, and guards against broken configs reaching production.

### Observer Commands (`observer-commands.ts`)
Monitor gateway health, track plugin status, and surface operational metrics for running OpenClaw instances.

### Phase 1 Commands (`phase1-commands.ts`)
Core operational commands for day-to-day management: status checks, restart orchestration, and deployment health verification.

### Skills Commands (`skills-commands.ts`)
Manage installed skills: list, inspect, and verify skill integrity across the workspace.

### Legacy Commands (`legacy-commands.ts`)
Backward-compatible command support for older OpenClaw configurations during migration periods.

## Scripts

### Config Validation (`openclaw-config-validate.py`)
Validates `openclaw.json` against known schema rules — checks for valid JSON, forbidden legacy keys (e.g. `plugins.paths`), and verifies a golden master config exists.

### Safe Restart (`openclaw-safe-restart.sh`)
Backup → validate → restart → restore-on-failure workflow. Prevents broken configs from taking down the gateway.

### GitHub Privacy Scanning
Automated scanning of repos for accidentally committed private files (MEMORY.md, TODO.md, HEARTBEAT.md, .env). Runs via daily cron.

### Issue Triage (`triage_labels.py`)
Automated GitHub issue labeling and triage for openclaw-* repositories.

## Installation

Install via ClawHub:
```bash
clawhub install openclaw-ops-elvatis
```
