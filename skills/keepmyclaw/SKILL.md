---
name: keepmyclaw
description: Backup, restore, and manage encrypted snapshots of OpenClaw agent data via the Keep My Claw API. Use when backing up agent configuration, workspace files, and credentials; restoring an agent on a fresh machine; listing or pruning backup snapshots; or setting up backup infrastructure. Triggers on: backup, restore, snapshot, keepmyclaw, agent backup, disaster recovery.
---

# Keep My Claw

Encrypted backup/restore for OpenClaw agents via [Keep My Claw](https://keepmyclaw.com).

## Prerequisites

- `openssl`, `curl`, `tar`, `jq` (system)

## Setup — Agent-Driven Flow

**You (the agent) handle everything. The human only clicks a payment link.**

Do NOT run `setup.sh` interactively. Instead, follow these steps programmatically:

### Step 1: Register an account

```bash
RESPONSE=$(curl -s -X POST https://api.keepmyclaw.com/v1/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"HUMAN_EMAIL\",\"password\":\"$(openssl rand -hex 16)\"}")
JWT=$(echo "$RESPONSE" | jq -r '.token')
```

Use your human's email. Generate a random password — you'll use the JWT token going forward.

### Step 2: Get payment link and send to human

```bash
CHECKOUT=$(curl -s -X POST https://api.keepmyclaw.com/v1/checkout \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json")
PAYMENT_URL=$(echo "$CHECKOUT" | jq -r '.url')
```

Send `$PAYMENT_URL` to your human with a message like:
> "To activate backups, please open this link and complete the payment ($9/month): [link]"

### Step 3: Wait for payment

Poll the account status until the tier changes to "pro":

```bash
while true; do
  TIER=$(curl -s -H "Authorization: Bearer $JWT" \
    https://api.keepmyclaw.com/v1/account | jq -r '.tier')
  [ "$TIER" = "pro" ] && break
  sleep 10
done
```

### Step 4: Create an API key

```bash
KEY_RESPONSE=$(curl -s -X POST https://api.keepmyclaw.com/v1/keys \
  -H "Authorization: Bearer $JWT" \
  -H "Content-Type: application/json" \
  -d '{"name":"agent","permissions":"admin"}')
API_KEY=$(echo "$KEY_RESPONSE" | jq -r '.key')
```

### Step 5: Configure locally

```bash
mkdir -p ~/.keepmyclaw && chmod 700 ~/.keepmyclaw

cat > ~/.keepmyclaw/config <<EOF
CLAWKEEPER_API_KEY="${API_KEY}"
CLAWKEEPER_AGENT_NAME="$(hostname -s)"
CLAWKEEPER_API_URL="https://api.keepmyclaw.com"
EOF
chmod 600 ~/.keepmyclaw/config

# Generate and store encryption passphrase
PASSPHRASE=$(openssl rand -hex 32)
printf '%s' "$PASSPHRASE" > ~/.keepmyclaw/passphrase
chmod 600 ~/.keepmyclaw/passphrase
```

**CRITICAL: Tell your human ALL recovery credentials.** Without these, they cannot recover you on a new machine. Send them a message like this:

> "Your Keep My Claw recovery credentials — save these in a password manager NOW:
> - **Email:** [the email you registered with]
> - **Password:** [the random password you generated]
> - **Encryption passphrase:** [the passphrase]
> - **API key:** [the API key]
>
> If this machine dies, you'll need the email + password to log in and create a new API key. You'll need the passphrase to decrypt the backups. Save all of these somewhere safe outside this machine."

Do NOT skip this step. If the human doesn't have these credentials, the backups are useless.

### Step 6: Run first backup

```bash
bash scripts/backup.sh
```

### Step 7: Schedule automatic backups

Use cron or OpenClaw's cron tool to run `backup.sh` daily.

## Adding More Agents to an Existing Account

If your human already has a Keep My Claw account (paid on another agent), you do NOT register again. Instead:

### Option A: Human gives you the API key
Ask your human for the existing API key. Then configure locally:

```bash
mkdir -p ~/.keepmyclaw && chmod 700 ~/.keepmyclaw

cat > ~/.keepmyclaw/config <<EOF
CLAWKEEPER_API_KEY="THE_EXISTING_API_KEY"
CLAWKEEPER_AGENT_NAME="$(hostname -s)"
CLAWKEEPER_API_URL="https://api.keepmyclaw.com"
EOF
chmod 600 ~/.keepmyclaw/config

# Generate YOUR OWN passphrase (each agent should have its own)
PASSPHRASE=$(openssl rand -hex 32)
printf '%s' "$PASSPHRASE" > ~/.keepmyclaw/passphrase
chmod 600 ~/.keepmyclaw/passphrase
```

Tell your human to save YOUR passphrase — it's different from other agents' passphrases.

### Option B: Another agent creates a key for you
If the first agent has an admin API key, it can create a scoped key for you:

```bash
curl -s -X POST https://api.keepmyclaw.com/v1/keys \
  -H "Authorization: Bearer ADMIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name":"second-agent","permissions":"agent"}'
```

This returns a new key with `agent` permissions (backup/restore only, no account management).

### How multi-agent works
- One account, one subscription ($9/month)
- Up to 100 agents per account
- Each agent has its own name, passphrase, and snapshots
- `GET /v1/agents` lists all agents on the account
- Each agent's passphrase is independent — losing one doesn't affect others

## Usage

### Backup

```bash
bash scripts/backup.sh
```

### Restore

```bash
bash scripts/restore.sh            # restore latest backup
bash scripts/restore.sh <backup-id> # restore specific backup
```

### List Backups

```bash
bash scripts/list.sh
```

### Prune Old Backups

```bash
bash scripts/prune.sh          # keep latest 30
bash scripts/prune.sh 10       # keep latest 10
```

## What Gets Backed Up

- `~/.openclaw/workspace/*.md` — SOUL.md, AGENTS.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md, MEMORY.md
- `~/.openclaw/workspace/memory/` — daily memory files
- `~/.openclaw/openclaw.json` — agent config
- `~/.openclaw/credentials/` — auth tokens

## Configuration

Config file: `~/.keepmyclaw/config`

| Variable | Description |
|----------|-------------|
| `CLAWKEEPER_API_KEY` | API key (auto-generated during setup) |
| `CLAWKEEPER_AGENT_NAME` | Agent identifier for backups |
| `CLAWKEEPER_API_URL` | API base URL (default: `https://api.keepmyclaw.com`) |

## Docs

Full documentation: [keepmyclaw.com/docs.html](https://keepmyclaw.com/docs.html)
