---
name: Infrastructure
slug: infrastructure
version: 1.0.1
description: Design, provision, and connect cloud resources across servers, networks, and services.
changelog: User-driven credential model, explicit tool requirements
metadata: {"clawdbot":{"emoji":"🏗️","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Scope

This skill:
- ✅ Guides architecture decisions
- ✅ Provides provisioning commands for user to run
- ✅ Documents infrastructure patterns

**User-driven model:**
- User provides cloud credentials when needed
- User runs provisioning commands
- Skill guides decisions and generates commands

This skill does NOT:
- ❌ Store or access cloud credentials directly
- ❌ Run provisioning commands automatically
- ❌ Modify infrastructure without user confirmation

**For implementation:** User runs commands skill provides, or uses `server` skill for execution.

## Quick Reference

| Topic | File |
|-------|------|
| Architecture patterns | `patterns.md` |
| Provider commands | `providers.md` |
| Backup strategies | `backups.md` |

## Core Rules

### 1. User Runs Commands
Skill generates commands, user executes:
```
Agent: "To create the server, run:
        hcloud server create --name web1 --type cx21 --image ubuntu-24.04
        
        This requires HCLOUD_TOKEN in your environment."
User: [runs command]
```

### 2. Required Tools (User Installs)
| Provider | Tool | Install |
|----------|------|---------|
| Hetzner | `hcloud` | brew install hcloud |
| AWS | `aws` | brew install awscli |
| DigitalOcean | `doctl` | brew install doctl |
| Docker | `docker` | Docker Desktop |

### 3. Credential Handling
- User sets credentials in their environment
- Skill never stores or logs credential values
- Commands reference env vars: `$HCLOUD_TOKEN`, `$AWS_ACCESS_KEY_ID`

### 4. Architecture Guidance

| Stage | Recommended |
|-------|-------------|
| MVP | Single VPS + Docker Compose |
| Growth | Dedicated DB + load balancer |
| Scale | Multi-region + CDN |

### 5. Decision Framework
| Question | Answer |
|----------|--------|
| How to structure infra? | ✅ This skill |
| Should I add another server? | ✅ This skill |
| How to configure nginx? | Use `server` skill |
| How to write Dockerfile? | Use `docker` skill |

### 6. Backup Strategy
| Data | Method | Frequency |
|------|--------|-----------|
| Database | pg_dump → S3/B2 | Daily |
| Volumes | Snapshots | Weekly |
| Config | Git | Every change |
