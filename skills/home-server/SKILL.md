---
name: Home Server
slug: home-server
version: 1.0.0
homepage: https://clawic.com/skills/home-server
description: Plan, secure, and maintain a home server with Docker services, remote access, backups, and incident recovery.
changelog: Initial release with practical home server planning, security, and recovery workflows.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":[]},"os":["linux","darwin","win32"],"configPaths":["~/home-server/"]}}
---

## Setup

On first use, read `setup.md`, explain planned local storage in `~/home-server/`, and ask for confirmation before creating files.

## When to Use

User needs help designing, deploying, or operating a home server environment.
Agent handles architecture choices, secure exposure, service operations, backup strategy, and recovery planning.

## Architecture

Memory lives in `~/home-server/`. See `memory-template.md` for setup.

```text
~/home-server/
├── memory.md                  # Current environment and preferences
├── services.md                # Service inventory and ownership
├── backup-status.md           # Backup coverage and restore checks
└── incidents.md               # Failure timeline and recovery notes
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup behavior | `setup.md` |
| Memory structure | `memory-template.md` |
| Service inventory model | `service-catalog.md` |
| Operational routines | `operations-checklists.md` |
| Incident response flow | `incident-playbook.md` |

## Core Rules

### 1. Define Trust Boundaries First
- Classify every service as LAN-only, VPN-only, or internet-facing before deployment.
- Never expose admin panels or databases directly to the internet.

### 2. Design Around Recoverable Data
- Identify where each service stores state before changing configs or images.
- Back up data paths first, then update workloads.
- Never request or store raw secrets, full `.env` dumps, or private keys in workspace memory.

### 3. Prefer Stable, Reproducible Deployments
- Use pinned image tags and declarative Compose files.
- Keep runtime variables documented so rebuilds are deterministic.

### 4. Secure the Host Before Scaling Services
- Enforce key-based SSH, minimal open ports, and regular security updates.
- Apply least privilege for containers, users, and file permissions.

### 5. Operate with Observable Signals
- Track health checks, disk usage, certificate expiry, and backup freshness.
- Treat silent failures as incidents and document root cause quickly.

### 6. Validate Recovery Paths Continuously
- Test restore procedures on a schedule, not only after failures.
- Require rollback plans before major upgrades or topology changes.

## Common Traps

- Installing services before defining backup paths -> data loss during first migration.
- Publishing many ports directly on the router -> large attack surface and hard troubleshooting.
- Using `latest` tags everywhere -> surprise upgrades and inconsistent behavior.
- Skipping restore drills -> backups exist but cannot be trusted in real incidents.
- Running all workloads on one Docker network -> accidental lateral access between services.

## Security & Privacy

**Data that may leave your machine (only when configured):**
- DNS or dynamic DNS updates to your selected provider.
- Telemetry from optional monitoring stacks you install.

**Data that stays local by default:**
- Service configs, logs, backup manifests, and incident notes in your home-server workspace.

**This skill does NOT:**
- Open ports automatically.
- Deploy services without explicit user instruction.
- Send undeclared external requests.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `self-host` — self-hosted service strategy and security baselines
- `server` — server deployment and troubleshooting patterns
- `docker` — container build and runtime discipline
- `docker-compose` — multi-service orchestration patterns
- `linux` — host administration and system diagnostics

## Feedback

- If useful: `clawhub star home-server`
- Stay updated: `clawhub sync`
