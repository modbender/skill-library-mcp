---
name: nas-agent-sync
version: 1.1.0
description: Synology NAS integration for OpenClaw — centralized file storage for multi-agent teams via SSH
emoji: 📦
tags:
  - nas
  - synology
  - file-storage
  - ssh
  - multi-agent
  - backup
---

# NAS Agent Sync — Synology File Storage for OpenClaw Agents

Centralize file storage across your multi-agent team using a Synology NAS (or any SSH-accessible storage). One agent acts as **File Master** — all others route file requests through it.

## The Problem

Multi-agent setups generate files across multiple workspaces. Without centralized storage:
- Files get lost between agent sessions
- No backup strategy
- Agents duplicate work
- No single source of truth

## The Solution

Designate one agent as **File Master**. All file operations go through this agent via `sessions_send`. The File Master manages:
- SSH connection to NAS
- Folder structure per agent
- File storage and retrieval
- Cross-agent file sharing

## Architecture

```
┌──────────┐    sessions_send     ┌────────────┐     SSH      ┌─────────┐
│ Agent A  │ ──────────────────► │ FILE MASTER │ ──────────► │   NAS   │
│ (Finance)│ "store invoice.pdf" │ (Tech Lead) │             │         │
└──────────┘                     └────────────┘             └─────────┘
                                       │
┌──────────┐    sessions_send          │  SSH
│ Agent B  │ ──────────────────►       │
│ (Sales)  │ "get sales report"        ▼
└──────────┘                     ┌─────────────┐
                                 │ _agents/     │
                                 │ ├── agent-a/ │
                                 │ ├── agent-b/ │
                                 │ ├── agent-c/ │
                                 │ └── _shared/ │
                                 └─────────────┘
```

## Setup

### 1. NAS Prerequisites

- Synology NAS (any model) or any Linux server with SSH
- SSH access with key-based auth
- VPN or Tailnet (recommended) for secure remote access

### 2. Create Folder Structure

```bash
SSH_HOST="user@your-nas-ip"

# Create agent folders (customize agent names to match your team)
ssh $SSH_HOST "mkdir -p ~/_agents/{coordinator,techops,finance,sales,marketing}"

# Create shared folders
ssh $SSH_HOST "mkdir -p ~/_shared/{config,templates}"

# Create agent directory file
ssh $SSH_HOST 'cat > ~/_shared/config/agent-directory.json << EOF
{
  "agents": {
    "coordinator": { "role": "Coordinator", "path": "~/_agents/coordinator/" },
    "techops": { "role": "File Master", "path": "~/_agents/techops/" },
    "finance": { "role": "Finance", "path": "~/_agents/finance/" }
  },
  "shared": "~/_shared/",
  "basePath": "~/"
}
EOF'
```

### 3. Configure File Master Agent

Add to your File Master agent's `AGENTS.md`:

```markdown
## FILE MASTER — Incoming Requests

When another agent sends a file request via sessions_send:

### Store a file:
ssh USER@NAS-IP "mkdir -p ~/_agents/[agent]/[subfolder]/"
# Copy/create file there

### Retrieve a file:
ssh USER@NAS-IP "cat ~/_agents/[agent]/[file]"
# Send content back to requesting agent

### Confirm back:
sessions_send(sessionKey="agent:[requester]:main", message="Done! File at [path]")
```

### 4. Configure Other Agents

Add to each agent's `AGENTS.md`:

```markdown
## File Operations → File Master

I do NOT access files directly. ALL file ops go through the File Master:

sessions_send(sessionKey="agent:techops:main", message="Store: [details]")
sessions_send(sessionKey="agent:techops:main", message="Retrieve: [path]")
```

## NAS Folder Structure (Recommended)

```
~/
├── _agents/
│   ├── coordinator/     # Coordinator files
│   │   ├── journal/     # Daily journals
│   │   └── tracking/    # Task tracking
│   ├── techops/         # Tech docs, scripts
│   │   ├── scripts/
│   │   └── configs/
│   ├── finance/         # Finance
│   │   ├── invoices/
│   │   ├── contracts/
│   │   └── reports/
│   ├── sales/           # Sales
│   │   ├── leads/
│   │   └── proposals/
│   └── [your-agent]/    # Per-agent storage
├── _shared/
│   ├── config/          # Shared configs
│   │   └── agent-directory.json
│   └── templates/       # Shared templates
└── _backups/
    └── memory/          # Memory file backups
```

## SSH via VPN/Tailnet (Recommended)

```bash
# Connect via secure tunnel IP (e.g. WireGuard, ZeroTier, or similar)
SSH_HOST="user@10.x.x.x"  # Your VPN/Tailnet IP

# Test connection
ssh $SSH_HOST "echo 'NAS connected!'"
```

## Security

- ✅ SSH key-based auth (no passwords in configs)
- ✅ VPN/Tailnet for encrypted tunnel (no port forwarding needed)
- ✅ File Master pattern limits SSH access to one agent
- ✅ Other agents never get SSH credentials
- ❌ Never store SSH keys in agent SOUL.md or memory files

## Why File Master Pattern?

1. **Security**: Only one agent has NAS credentials
2. **Consistency**: Single point of truth for file locations
3. **Audit trail**: All file ops logged through one agent
4. **Simplicity**: Other agents don't need to know SSH commands

## Backup Strategy

### Daily Backup Cron (via OpenClaw)
Set up a cron job that backs up agent workspaces to NAS:

```json5
// Cron job config
{
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "UTC" },
  "payload": {
    "kind": "agentTurn",
    "message": "Backup all agent workspaces to NAS. For each agent: rsync workspace memory/ folder to NAS _agents/{agent}/memory-backup/. Report any failures."
  },
  "sessionTarget": "isolated"
}
```

### Manual Backup Command
```bash
# Backup specific agent
rsync -avz ~/.openclaw/workspace-finance/memory/ user@nas-ip:~/_agents/finance/memory-backup/

# Backup all agents (customize list to your team)
for agent in coordinator techops finance sales marketing; do
  rsync -avz ~/.openclaw/workspace-$agent/memory/ user@nas-ip:~/_agents/$agent/memory-backup/
done
```

## Troubleshooting

**SSH connection refused:**
→ Check VPN/Tailnet status — is NAS online and connected?
→ Verify SSH service running on NAS (Synology: DSM → Control Panel → Terminal & SNMP)

**Permission denied:**
→ SSH key not added: `ssh-copy-id user@nas-ip`
→ NAS home folder not enabled (Synology: DSM → User → Advanced → Enable home service)

**Slow transfers:**
→ Use direct VPN connection (not relayed)
→ Consider compression: `rsync -avz --compress`

## Compatible NAS Models

- ✅ Synology (any model with DSM 7+)
- ✅ QNAP (QTS 5+)
- ✅ TrueNAS / FreeNAS
- ✅ Any Linux server with SSH access
- ✅ Raspberry Pi with external storage

## Changelog

### v1.1.0
- Removed all specific agent/setup references
- Generalized folder structure and examples
- Added backup strategy with cron

### v1.0.0
- Initial release
