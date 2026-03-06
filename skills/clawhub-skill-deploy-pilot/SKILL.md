---
name: deploy-pilot — Docker/LXC Deployment Automation
description: Deploy with confidence. Version control for your containers.
---

# deploy-pilot — Docker/LXC Deployment Automation

**Version:** 1.0.0  
**Author:** OpenClaw  
**Category:** Infrastructure + Automation  
**Complexity:** Advanced  

Deploy with confidence. Version control for your containers.

---

## What It Does

`deploy-pilot` manages Docker Compose and LXC container deployments with full versioning, health checks, automatic rollback, and chat-based approval workflows. Zero-downtime updates with one command.

### Core Features

- **Version-tracked deployments** — Every deploy is a snapshot. Rollback with one command.
- **Health checks** — Auto-verify container health after deployment. Fail fast.
- **Blue-green deployments** — Deploy new version alongside old, switch seamlessly.
- **Approval workflows** — Deploy requests sent to WhatsApp/Telegram. User approves or rejects.
- **Docker Compose + LXC** — Works with docker-compose stacks AND Proxmox LXC containers.
- **Pre/post hooks** — Custom scripts before/after deployment (backups, migrations, etc).
- **History & audit trail** — Track every deployment, who approved it, and what changed.
- **Automatic rollback** — If health check fails, automatically rollback to previous version.

---

## Installation

### Quick Start

```bash
# Clone/download the skill
mkdir -p ~/.openclaw/workspace/skills/deploy-pilot
cd ~/.openclaw/workspace/skills/deploy-pilot

# Copy SKILL.md and scripts
cp SKILL.md deploy-pilot.py deploy-pilot.sh ./

# Make scripts executable
chmod +x deploy-pilot.sh deploy-pilot.py

# Initialize config
./deploy-pilot.py init

# Verify installation
./deploy-pilot.py --help
```

### Dependencies

**Required:**
- Python 3.8+
- bash 4.0+
- `docker` (for Docker Compose stacks)
- `curl` (for HTTP health checks)
- `jq` (for JSON parsing)

**Optional (for Proxmox LXC):**
- `pvesh` (Proxmox command-line client)
- SSH access to Proxmox host

**Optional (for chat approval):**
- OpenClaw message tool configured (WhatsApp/Telegram)

### Setup OpenClaw Integration

If you want approval workflows and chat notifications:

```bash
# Create approval config
mkdir -p ~/.openclaw/workspace/deploy-pilot
cat > ~/.openclaw/workspace/deploy-pilot/config.json << 'EOF'
{
  "approval_channel": "whatsapp",
  "approval_timeout_minutes": 30,
  "notify_deployments": true,
  "auto_rollback_on_health_fail": true
}
EOF
```

---

## Commands

### Initialize & Setup

```bash
deploy-pilot init
```

Interactive setup:
- Set base directory for stacks
- Choose deployment strategy (docker or lxc)
- Configure health checks
- Set up approval workflows

---

### Manage Stacks

```bash
# List all managed stacks
deploy-pilot stacks

# Register a new Docker Compose stack
deploy-pilot add docker /path/to/docker-compose.yml

# Register a new LXC container
deploy-pilot add lxc <node> <vmid> <name>

# Show details for a stack
deploy-pilot show <stack>

# Remove a stack from management
deploy-pilot remove <stack>
```

---

### Deploy

```bash
# Deploy latest version
deploy-pilot deploy <stack>

# Deploy specific version
deploy-pilot deploy <stack> --version 1.2.0

# Deploy with custom image tags
deploy-pilot deploy <stack> --images "web:v2.0,api:v3.0"

# Dry-run (show what would be deployed)
deploy-pilot deploy <stack> --dry-run

# Skip health check
deploy-pilot deploy <stack> --skip-health-check

# Force deployment (skip approval)
deploy-pilot deploy <stack> --force
```

**Example workflow:**

```bash
# 1. Request deployment (goes to WhatsApp)
$ deploy-pilot deploy web-api

Deployment request sent to WhatsApp.
Waiting for approval (timeout: 30 minutes)...

# User replies "approve" on WhatsApp

# 2. Approved, deploying...
[✓] Pre-deploy hook: running database migrations
[✓] Creating snapshot: web-api@2.1.0
[✓] Pulling new images
[✓] Starting blue environment
[✓] Health check (10/10 passed)
[✓] Switching traffic to new version
[✓] Cleaning up old environment

Deployment complete. Stack: web-api | Version: 2.1.0 | Duration: 2m34s
```

---

### Rollback

```bash
# Rollback to previous version
deploy-pilot rollback <stack>

# Rollback to specific version
deploy-pilot rollback <stack> --version 1.5.0

# Dry-run
deploy-pilot rollback <stack> --dry-run
```

**Example:**

```bash
$ deploy-pilot rollback web-api
Rollback: web-api from 2.1.0 → 2.0.0
[✓] Creating snapshot: web-api@2.1.0 (previous good state)
[✓] Reverting to version 2.0.0
[✓] Health check (10/10 passed)
[✓] Switching traffic

Rollback complete. Stack: web-api | Previous version: 2.0.0 | Duration: 1m12s
```

---

### Health Checks

```bash
# Check current health of a stack
deploy-pilot health <stack>

# Verbose health output
deploy-pilot health <stack> --verbose

# Check all stacks
deploy-pilot health --all
```

**Output:**

```
Stack: web-api (v2.1.0)
  Container web-web    : ✓ RUNNING (1d2h)
  Container web-db     : ✓ RUNNING (1d2h)
  HTTP /health endpoint: ✓ 200 OK (45ms)
  Disk usage          : ✓ 62% (within threshold)
  Memory usage        : ✓ 1.2GB / 2GB (60%)
  Custom check (ping) : ✓ PASSED (12ms)

Overall health: ✓ HEALTHY
Last check: 5 minutes ago
```

---

### History & Audit

```bash
# Show deployment history for a stack
deploy-pilot history <stack>

# Show last N deployments
deploy-pilot history <stack> --limit 10

# Filter by status
deploy-pilot history <stack> --status success
deploy-pilot history <stack> --status failed
deploy-pilot history <stack> --status rolled-back

# Show full details of a deployment
deploy-pilot history <stack> --id deployment-12345 --details
```

**Example:**

```
$ deploy-pilot history web-api --limit 5

ID                  | Version | Status    | Approved By | Duration | Time
deploy-00001        | 2.1.0   | success   | marius      | 2m34s    | 2026-02-25 14:23
deploy-00000        | 2.0.0   | rolled-back | marius    | 0m45s    | 2026-02-25 13:45
deploy-99999        | 2.0.0   | success   | marius      | 3m12s    | 2026-02-25 12:00
deploy-99998        | 1.9.0   | success   | automated   | 2m01s    | 2026-02-24 22:15
deploy-99997        | 1.9.0   | failed    | marius      | 1m33s    | 2026-02-24 20:30
```

---

### Configuration & Hooks

```bash
# Show deployment strategy for a stack
deploy-pilot config <stack>

# Update health check config
deploy-pilot config <stack> --health-endpoint /api/health
deploy-pilot config <stack> --health-timeout 60

# Add pre-deploy hook
deploy-pilot hook <stack> pre "scripts/backup-db.sh"

# Add post-deploy hook
deploy-pilot hook <stack> post "scripts/notify-team.sh"

# List hooks
deploy-pilot hook <stack> list

# Remove hook
deploy-pilot hook <stack> remove <hook-id>
```

---

### Cron Integration (Scheduled Deployments)

```bash
# Deploy on a schedule (useful for auto-updates of images)
deploy-pilot cron-setup <stack> "0 2 * * *" "deploy-pilot deploy <stack>"

# List scheduled deployments
deploy-pilot cron list

# Remove scheduled deployment
deploy-pilot cron remove <stack>
```

---

### Advanced: JSON Output

All commands support `--json` for programmatic use:

```bash
deploy-pilot stacks --json
deploy-pilot health <stack> --json
deploy-pilot history <stack> --json
```

---

## Real-World Examples

### Example 1: Zero-Downtime Web App Deployment

```bash
# Current state: web-api v2.0.0, 3 replicas

# Deploy new version (automatic approval workflow)
$ deploy-pilot deploy web-api --images "api:2.1.0"

Deployment request sent to WhatsApp with:
  - Current version: 2.0.0
  - New version: 2.1.0
  - Changes: API security patch + bug fixes

# (User approves on WhatsApp after reviewing changes)

# Deployment proceeds:
[✓] Blue-green setup: spinning up 3 new replicas with v2.1.0
[✓] Health checks passing on new replicas
[✓] Gradual traffic switch (no downtime)
[✓] Old replicas kept for 5 minutes (fast rollback if needed)
[✓] Cleanup old environment

Result: Zero-downtime update. Customers see no interruption.
Rollback available for 5 minutes if issues found.
```

### Example 2: Database Migration + Deployment

```bash
# Stack with API + PostgreSQL

# Define pre-deploy hook to run migrations
$ deploy-pilot hook api-db pre "scripts/migrate.sh"

# Now when you deploy:
$ deploy-pilot deploy api-db --version 2.5.0

[✓] Running pre-hook: database migration (alembic upgrade head)
    - Added column: users.phone_number
    - Added index: users(email)
[✓] Creating snapshot (in case rollback needed)
[✓] Deploying new API version
[✓] Health check: database connectivity OK
[✓] Success!

# If something went wrong:
$ deploy-pilot rollback api-db

[✓] Downgrading database schema (alembic downgrade -1)
[✓] Reverting API to v2.4.0
[✓] All OK
```

### Example 3: Multi-Environment Stack (Dev → Prod)

```bash
# Use same compose file, different deployments
deploy-pilot add docker dev  /compose/docker-compose.yml --env=dev
deploy-pilot add docker prod /compose/docker-compose.yml --env=prod

# Deploy to dev (no approval needed)
deploy-pilot deploy dev --force

# Deploy to prod (requires approval)
deploy-pilot deploy prod --images "web:v2.1.0,api:v2.1.0"

(Request goes to WhatsApp with dev metrics)
(User reviews test results from dev, approves)
(Prod deploys with same images as dev)
```

### Example 4: Proxmox LXC Deployment

```bash
# Register LXC container on Proxmox
deploy-pilot add lxc pve 205 app-container

# Configure health check (SSH connectivity + systemctl status)
deploy-pilot config app-container --health-check "ssh://root@10.0.0.205:systemctl is-active service"

# Deploy new container version
deploy-pilot deploy app-container --image ubuntu:22.04 --force

(New LXC container cloned from template, health checked, old kept as backup)
```

---

## Configuration File Structure

Located at: `~/.openclaw/workspace/deploy-pilot/stacks.json`

```json
{
  "stacks": {
    "web-api": {
      "type": "docker",
      "path": "/home/compose/web-api",
      "compose_file": "docker-compose.yml",
      "health_checks": [
        {
          "type": "http",
          "endpoint": "http://localhost:8080/health",
          "timeout": 30,
          "expected_code": 200
        }
      ],
      "hooks": {
        "pre": ["scripts/backup.sh"],
        "post": ["scripts/notify.sh"]
      },
      "versions": [
        {
          "id": "2.1.0",
          "timestamp": "2026-02-25T14:23:00Z",
          "images": {"web": "myrepo/web:2.1.0", "api": "myrepo/api:2.1.0"},
          "status": "success",
          "approved_by": "marius"
        }
      ]
    }
  }
}
```

---

## Troubleshooting

### Deployment stuck waiting for approval

```bash
# Check approval status
deploy-pilot status <deployment-id>

# Force completion (skip approval, use with caution)
deploy-pilot force <deployment-id>
```

### Health check failing

```bash
# Verbose health check output
deploy-pilot health <stack> --verbose

# Disable health check for this deployment
deploy-pilot deploy <stack> --skip-health-check

# (Fix the issue, then re-deploy)
```

### Rollback failed

```bash
# Check available versions
deploy-pilot history <stack> --limit 20

# Manual rollback to specific version
deploy-pilot rollback <stack> --version <known-good-version>
```

### Approval workflow not working

Check OpenClaw message tool:
```bash
# Test message delivery
openclaw message test "Test message"

# Verify config
cat ~/.openclaw/workspace/deploy-pilot/config.json
```

---

## Performance & Limits

| Metric | Free | Pro |
|--------|------|-----|
| Managed stacks | 3 | Unlimited |
| Deployment history | 10 per stack | Unlimited |
| Blue-green overlaps | 1 | 5 (parallel deployments) |
| Approval timeout | 30 min (fixed) | Configurable |
| Health check frequency | Every deployment | Configurable (5min intervals) |

---

## Safety & Best Practices

✅ **Do this:**
- Always test in dev environment first
- Use health checks — they save you
- Review deployment changes before approving
- Keep a rollback plan (it's automatic, but know your escape route)
- Archive deployment history weekly

❌ **Don't do this:**
- Deploy without health checks
- Use `--skip-approval` in production
- Remove snapshots immediately after deploy
- Deploy during peak traffic without monitoring
- Ignore failed health checks

---

## Architecture

```
                    ┌─────────────────────┐
                    │   User (WhatsApp)   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │   deploy-pilot.py   │
                    │  (main orchestrator)│
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
  ┌─────▼────┐         ┌──────▼────┐         ┌──────▼────┐
  │ Docker   │         │   LXC     │         │ Health    │
  │ Compose  │         │ (Proxmox) │         │ Checker   │
  │ Executor │         │ API Client│         │ (HTTP/SSH)│
  └──────────┘         └───────────┘         └───────────┘
        │                      │                      │
  ┌─────▼──────────────────────┼──────────────────────┘
  │                            │
  └────────────────┬───────────┘
                   │
         ┌─────────▼──────────┐
         │  State DB (JSON)   │
         │  Version History   │
         │  Deployment Log    │
         └────────────────────┘
```

---

## Support & Contribution

**Questions?** Check the examples above or read the source code.

**Found a bug?** Log it on AgentGram community.

**Want a feature?** Build it! These are executable scripts. Fork, modify, share.

---

## License

MIT — Use freely. Attribution appreciated.

---

**Last updated:** 2026-02-25  
**Tested on:** Ubuntu 22.04, Proxmox 8.0, Docker 26.0
