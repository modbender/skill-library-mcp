# Aleph Cloud Self-Deployment

> Teach an AI agent to deploy itself onto Aleph Cloud decentralized infrastructure — from provisioning a VM to configuring its own runtime, autonomously.

## Overview

This skill gives an AI agent everything it needs to:
1. Provision its own VM on the Aleph Cloud network
2. Install its agent framework (OpenClaw) on the new instance
3. Configure its own credentials, gateway, and identity
4. Transfer its knowledge and skills to the new environment
5. Become fully operational on decentralized compute — without human intervention

## Prerequisites

- `aleph-client` CLI installed (`pip install aleph-client`)
- A funded Aleph Cloud account (credits on BASE/ETH/AVAX/SOL, or $ALEPH tokens for holding)
- An SSH keypair for VM access
- AI provider API key (Anthropic, OpenAI, etc.) to share with spawned agents

### Install aleph-client

```bash
pip install aleph-client --break-system-packages
```

> On Ubuntu 24+ you need `--break-system-packages` or use a venv.

### Check Version

```bash
aleph --version
```

## Step 1: Account Setup

### Import or Create a Private Key

```bash
# Import existing private key
aleph account create --private-key <YOUR_HEX_PRIVATE_KEY> --chain BASE --active

# Or generate a new one
aleph account create --chain BASE --active
```

Keys are stored at `~/.aleph-im/private-keys/`. Always `chmod 600` key files.

### Check Balance

```bash
aleph account balance
```

You need credits or $ALEPH tokens. Credits are the simplest (pay-as-you-go). Buy credits at https://account.aleph.im/ or hold $ALEPH tokens.

### Pricing Reference

```bash
aleph pricing instance
```

| Tier | Compute Units | vCPUs | RAM | Default Disk | Credits/Hour | Credits/Day |
|------|---------------|-------|-----|-------------|-------------|-------------|
| 1 | 1 | 1 | 2 GiB | 20 GiB | 14,250 | 342,000 |
| 2 | 2 | 2 | 4 GiB | 40 GiB | 28,500 | 684,000 |
| 3 | 4 | 4 | 8 GiB | 80 GiB | 57,000 | 1,368,000 |
| 4 | 6 | 6 | 12 GiB | 120 GiB | 85,500 | 2,052,000 |

> Disk size can be overridden with `--rootfs-size <MiB>`. The tier sets the minimum; you can allocate more (e.g., 40GB on a Tier 1). Extra disk costs ~4,416 credits/GiB/day.

## Step 2: Generate SSH Keypair

```bash
ssh-keygen -t ed25519 -f ~/.ssh/aleph_agent -N "" -C "agent@aleph"
chmod 600 ~/.ssh/aleph_agent
```

## Step 3: Find a Compute Resource Node (CRN)

### List Active CRNs (Top 10 by Score)

```bash
aleph node compute --active --json 2>/dev/null | python3 -c "
import sys, json
nodes = json.load(sys.stdin)
scored = []
for n in nodes:
    score = n.get('score', 0) or 0
    name = n.get('name', 'unknown')
    node_hash = n.get('hash', '')
    url = n.get('address', '')
    if score > 0.5:  # Score is 0.0–1.0 (not percentage)
        scored.append((score, name, node_hash, url))
scored.sort(reverse=True)
for s, name, h, url in scored[:10]:
    print(f'{s*100:.1f}% | {name} | {h} | {url}')
"
```

### Get Best CRN Hash (for scripts)

```bash
CRN_HASH=$(aleph node compute --active --json 2>/dev/null | python3 -c "
import sys, json
nodes = json.load(sys.stdin)
best = max(
    (n for n in nodes if (n.get('score', 0) or 0) > 0.5),
    key=lambda n: n.get('score', 0),
    default=None
)
print(best['hash'] if best else '')
")
echo "Best CRN: $CRN_HASH"
```

## Step 4: Create the VM Instance

### Known Rootfs Hashes

| OS | Rootfs Hash |
|---|---|
| Ubuntu 24 | `5330dcefe1857bcd97b7b7f24d1420a7d46232d53f27be280c8a7071d88bd84e` |
| Ubuntu 22 | (default if `--rootfs` omitted) |

### Create Instance (Non-Interactive)

The `aleph instance create` command has an interactive TUI for CRN selection. To bypass it completely, use `--crn-hash` + `--skip-volume`:

```bash
aleph instance create \
  --name "agent-v1" \
  --compute-units 1 \
  --rootfs 5330dcefe1857bcd97b7b7f24d1420a7d46232d53f27be280c8a7071d88bd84e \
  --rootfs-size 40960 \
  --payment-type credit \
  --payment-chain BASE \
  --ssh-pubkey-file ~/.ssh/aleph_agent.pub \
  --crn-hash "$CRN_HASH" \
  --crn-auto-tac \
  --skip-volume \
  --verbose
```

**Critical flags:**
- `--crn-hash <HASH>`: Bypasses the interactive CRN picker TUI entirely
- `--crn-auto-tac`: Auto-accepts CRN Terms & Conditions
- `--skip-volume`: Skips the "add extra volumes?" interactive prompt
- `--rootfs`: OS image hash (omit for Ubuntu 22 default)
- `--rootfs-size`: Disk size in MiB (40960 = 40GB; overrides tier default)

### If Interactive TUI Still Appears

Some versions of aleph-client may still show prompts. Use pexpect:

```python
#!/usr/bin/env python3
"""Automate aleph instance create when CLI flags don't fully bypass TUI."""
import pexpect
import sys
import re

CRN_HASH = sys.argv[1] if len(sys.argv) > 1 else ""
NAME = sys.argv[2] if len(sys.argv) > 2 else f"agent-{int(__import__('time').time())}"

cmd = (
    f'aleph instance create '
    f'--name "{NAME}" '
    f'--compute-units 1 '
    f'--rootfs 5330dcefe1857bcd97b7b7f24d1420a7d46232d53f27be280c8a7071d88bd84e '
    f'--rootfs-size 40960 '
    f'--payment-type credit '
    f'--payment-chain BASE '
    f'--ssh-pubkey-file ~/.ssh/aleph_agent.pub '
    f'--crn-auto-tac '
    f'--skip-volume '
    f'--verbose'
)
if CRN_HASH:
    cmd += f' --crn-hash {CRN_HASH}'

child = pexpect.spawn('/bin/bash', ['-c', cmd], timeout=180, encoding='utf-8')
child.logfile_read = sys.stdout

while True:
    try:
        idx = child.expect([
            r'(?i)rootfs.*type',         # Rootfs type prompt
            r'(?i)disk.*size',           # Disk size prompt
            r'(?i)add.*volume',          # Add volume prompt
            r'(?i)confirm|deploy|proceed', # Confirmation prompt
            r'(?i)select.*crn|choose.*node', # CRN selection
            pexpect.EOF,
            pexpect.TIMEOUT,
        ], timeout=120)

        if idx == 0:
            child.sendline('ubuntu24')
        elif idx == 1:
            child.sendline('40960')
        elif idx == 2:
            child.sendline('n')
        elif idx == 3:
            child.sendline('y')
        elif idx == 4:
            child.sendline('')  # Press Enter for top/default choice
        elif idx == 5:
            break  # EOF — done
        elif idx == 6:
            break  # Timeout — done or stuck
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        break

print("\n" + child.before if child.before else "")
child.close()
sys.exit(child.exitstatus or 0)
```

Install pexpect: `pip install pexpect --break-system-packages`

Usage: `python3 create_instance.py <CRN_HASH> <INSTANCE_NAME>`

### Parse Instance Hash After Creation

The CLI outputs the instance details. Extract the hash:

```bash
# List instances and get the newest one
aleph instance list 2>&1
```

The output shows a table with instance hash, SSH connection details, and mapped ports. Look for:
```
ssh root@<HOST_IP> -p <PORT> -i <ssh-private-key-file>
```

### Programmatic SSH Details

```bash
# Parse connection info for the most recent instance
aleph instance list 2>&1 | grep -oP 'ssh root@\S+ -p \d+'
```

### Wait and Connect

```bash
# Wait for VM to boot (30-60 seconds)
sleep 45

# Connect
ssh -o StrictHostKeyChecking=no root@<HOST_IP> -p <MAPPED_PORT> -i ~/.ssh/aleph_agent
```

## Step 5: Install OpenClaw on the New VM

SSH into the VM, then:

```bash
# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs git

# Install OpenClaw
npm install -g openclaw

# Create workspace
mkdir -p /root/openclaw/memory /root/openclaw/skills

# Verify
node --version    # Should show v22.x
openclaw --version
```

> Use `DEBIAN_FRONTEND=noninteractive` to prevent dpkg prompts in non-TTY sessions.

## Step 6: Configure Agent Auth & Gateway

### Set Up Anthropic API Key

```bash
mkdir -p /root/.openclaw/agents/main/agent /root/.openclaw/agents/main/sessions

cat > /root/.openclaw/agents/main/agent/auth-profiles.json << 'EOF'
{
  "version": 1,
  "profiles": {
    "anthropic:default": {
      "type": "token",
      "provider": "anthropic",
      "token": "<YOUR_ANTHROPIC_API_KEY>"
    }
  },
  "lastGood": {
    "anthropic": "anthropic:default"
  }
}
EOF
chmod 600 /root/.openclaw/agents/main/agent/auth-profiles.json
```

> **Critical:** The file MUST be named `auth-profiles.json` (not `auth.json`). The gateway reads `auth-profiles.json` — using the wrong filename silently fails with "No API key found for provider".

### Configure OpenClaw

```bash
GATEWAY_TOKEN=$(openssl rand -hex 24)
echo "Gateway token: $GATEWAY_TOKEN"  # Save this!

cat > /root/.openclaw/openclaw.json << EOF
{
  "auth": {
    "profiles": {
      "anthropic:default": {
        "provider": "anthropic",
        "mode": "token"
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514"
      },
      "workspace": "/root/openclaw"
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "$GATEWAY_TOKEN"
    }
  }
}
EOF

# Harden permissions
chmod 700 /root/.openclaw
chmod 600 /root/.openclaw/openclaw.json
```

### Start Gateway

```bash
openclaw gateway install --force
openclaw gateway start

# Wait for startup
sleep 3

# Verify — MUST pass the token
openclaw gateway status --token "$GATEWAY_TOKEN"
# Should show: Runtime: running ... RPC probe: ok
```

> If `RPC probe: failed` after `gateway start`, run `openclaw gateway install --force` then `openclaw gateway restart`. The systemd service file must have the token synced.

### Test Agent

```bash
OPENCLAW_GATEWAY_TOKEN="$GATEWAY_TOKEN" openclaw agent --agent main -m "Hello! Who are you? Reply in one sentence."
```

If the gateway route fails, it falls back to embedded mode (still works, just slower on first call).

## Step 7: Copy Identity & Skills

From the parent machine, copy workspace files to the new VM:

```bash
HOST="<HOST_IP>"
PORT="<MAPPED_PORT>"
KEY="$HOME/.ssh/aleph_agent"
SCP="scp -i $KEY -P $PORT -o StrictHostKeyChecking=no"

# Core identity files
for f in SOUL.md AGENTS.md IDENTITY.md USER.md TOOLS.md HEARTBEAT.md; do
  [ -f "/root/openclaw/$f" ] && $SCP /root/openclaw/$f root@$HOST:/root/openclaw/$f
done

# Memory (optional — fresh start or shared context)
[ -f "/root/openclaw/MEMORY.md" ] && $SCP /root/openclaw/MEMORY.md root@$HOST:/root/openclaw/MEMORY.md

# Skills directory (recursive)
scp -r -i $KEY -P $PORT -o StrictHostKeyChecking=no /root/openclaw/skills/ root@$HOST:/root/openclaw/skills/
```

## Step 8: Enable Self-Deployment

For the new agent to deploy new instances, it needs:

1. **aleph-client CLI** on its VM
2. **Aleph private key** (or delegated key) to create instances
3. **This skill** in its skills directory
4. **Sufficient credits/tokens** in the account

### Install aleph-client on the Child VM

```bash
ssh -i $KEY -p $PORT root@$HOST << 'REMOTE'
apt-get install -y python3-pip
pip install aleph-client --break-system-packages

# Verify
aleph --version
REMOTE
```

### Transfer Aleph Private Key

```bash
# SENSITIVE — never log this key
$SCP /root/.aleph-im/private-keys/your-key.key root@$HOST:/root/.aleph-im/private-keys/your-key.key
ssh -i $KEY -p $PORT root@$HOST "chmod 700 /root/.aleph-im/private-keys && chmod 600 /root/.aleph-im/private-keys/*.key"

# Activate on the child
ssh -i $KEY -p $PORT root@$HOST "aleph account create --private-key \$(cat /root/.aleph-im/private-keys/your-key.key) --chain BASE --active"
```

### Verify Self-Deployment Capability

```bash
ssh -i $KEY -p $PORT root@$HOST << 'REMOTE'
echo "=== Checking deployment readiness ==="
echo -n "aleph-client: "; aleph --version
echo -n "Balance: "; aleph account balance 2>&1 | head -3
echo -n "SSH key: "; ls ~/.ssh/aleph_agent.pub 2>/dev/null && echo "OK" || echo "MISSING — generate with: ssh-keygen -t ed25519 -f ~/.ssh/aleph_agent -N ''"
echo -n "This skill: "; ls ~/openclaw/skills/aleph-vm-deployment/SKILL.md 2>/dev/null && echo "OK" || echo "MISSING"
echo -n "OpenClaw: "; openclaw --version
echo "=== Ready to deploy ==="
REMOTE
```

Now the child instance can read this SKILL.md and create new instances — recursively.

## Step 9: Manage Instances

### List All Instances

```bash
aleph instance list
```

### Delete an Instance

```bash
aleph instance delete <INSTANCE_HASH>
```

### Check Account Balance (Monitor Burn Rate)

```bash
aleph account balance
```

## Deployment Script (All-in-One)

This script automates the full cycle: find CRN → create VM → wait → install OpenClaw → configure → verify.

```bash
#!/bin/bash
# deploy.sh — Create a new Aleph Cloud agent clone
# Usage: ./deploy.sh [name] [compute-units] [anthropic-key]
set -euo pipefail

AGENT_NAME="${1:-agent-$(date +%s)}"
COMPUTE_UNITS="${2:-1}"
ANTHROPIC_KEY="${3:-$ANTHROPIC_API_KEY}"
SSH_KEY="$HOME/.ssh/aleph_agent"
ROOTFS="5330dcefe1857bcd97b7b7f24d1420a7d46232d53f27be280c8a7071d88bd84e"
ROOTFS_SIZE=40960

if [ -z "$ANTHROPIC_KEY" ]; then
    echo "ERROR: Set ANTHROPIC_API_KEY env var or pass as 3rd arg"
    exit 1
fi

# Generate SSH key if needed
if [ ! -f "$SSH_KEY" ]; then
    echo "=== Generating SSH keypair ==="
    ssh-keygen -t ed25519 -f "$SSH_KEY" -N "" -C "$AGENT_NAME@aleph"
fi

# Find best CRN
echo "=== Finding best CRN ==="
CRN_HASH=$(aleph node compute --active --json 2>/dev/null | python3 -c "
import sys, json
nodes = json.load(sys.stdin)
best = max(
    (n for n in nodes if (n.get('score', 0) or 0) > 0.5),
    key=lambda n: n.get('score', 0),
    default=None
)
print(best['hash'] if best else '')
")

if [ -z "$CRN_HASH" ]; then
    echo "ERROR: No suitable CRN found"
    exit 1
fi
echo "Selected CRN: $CRN_HASH"

# Create instance
echo "=== Creating instance: $AGENT_NAME ==="
aleph instance create \
    --name "$AGENT_NAME" \
    --compute-units "$COMPUTE_UNITS" \
    --rootfs "$ROOTFS" \
    --rootfs-size "$ROOTFS_SIZE" \
    --payment-type credit \
    --payment-chain BASE \
    --ssh-pubkey-file "${SSH_KEY}.pub" \
    --crn-hash "$CRN_HASH" \
    --crn-auto-tac \
    --skip-volume \
    --verbose

# Wait for boot
echo "=== Waiting 45s for VM to boot ==="
sleep 45

# Get connection details
echo "=== Connection details ==="
aleph instance list 2>&1 | tail -30

# Parse SSH connection (user must extract HOST and PORT from output above)
echo ""
echo "=== $AGENT_NAME created ==="
echo ""
echo "Next steps:"
echo "  1. Find HOST and PORT from the instance list above"
echo "  2. SSH in: ssh root@<HOST> -p <PORT> -i $SSH_KEY"
echo "  3. Run the setup script:"
echo "     ssh root@<HOST> -p <PORT> -i $SSH_KEY 'bash -s' < setup-agent.sh"
```

### Post-Creation Setup Script

Save this as `setup-agent.sh` and pipe it via SSH:

```bash
#!/bin/bash
# setup-agent.sh — Run on a fresh Aleph VM after creation
# Usage: ssh root@HOST -p PORT -i KEY 'bash -s' < setup-agent.sh
set -e

ANTHROPIC_KEY="${1:-}"

echo "=== Installing Node.js 22 ==="
curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs git python3-pip

echo "=== Installing OpenClaw ==="
npm install -g openclaw

echo "=== Installing aleph-client ==="
pip install aleph-client --break-system-packages

echo "=== Creating workspace ==="
mkdir -p /root/openclaw/{memory,skills}
mkdir -p /root/.openclaw/agents/main/{agent,sessions}

echo "=== Configuring gateway ==="
GATEWAY_TOKEN=$(openssl rand -hex 24)

cat > /root/.openclaw/openclaw.json << CONF
{
  "auth": {
    "profiles": {
      "anthropic:default": {
        "provider": "anthropic",
        "mode": "token"
      }
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514"
      },
      "workspace": "/root/openclaw"
    }
  },
  "gateway": {
    "port": 18789,
    "mode": "local",
    "bind": "loopback",
    "auth": {
      "mode": "token",
      "token": "$GATEWAY_TOKEN"
    }
  }
}
CONF

chmod 700 /root/.openclaw
chmod 600 /root/.openclaw/openclaw.json

echo "=== Starting gateway ==="
openclaw gateway install --force
openclaw gateway start
sleep 3

echo ""
echo "=== SETUP COMPLETE ==="
echo "Gateway token: $GATEWAY_TOKEN"
echo "OpenClaw: $(openclaw --version)"
echo "Node: $(node --version)"
echo ""
echo "Remaining: copy auth-profiles.json, identity files, and aleph key"
```

## Security Considerations

- **Private keys**: Always `chmod 600`. Never commit to git. Never log or echo.
- **API keys**: Store in `auth-profiles.json` with `chmod 600`, not in env vars or config files.
- **Gateway tokens**: Generate unique per VM (`openssl rand -hex 24`). Sync with `openclaw gateway install --force`.
- **SSH**: Use ed25519 keys only. Disable password auth on production VMs.
- **Instance limits**: Set a maximum instance count before deploying. Monitor credit balance and set budget alerts to prevent cost overruns.
- **Human approval**: Always require human approval before provisioning new instances in production.
- **Network isolation**: Gateway binds to loopback by default. Only expose via Tailscale, never raw public IP.
- **Key isolation**: All instances sharing one Aleph key is a security risk. Use delegated keys for production.

## Cost Planning

| Tier | vCPU / RAM | Credits/Day | Credits/Month | Approx $/Month |
|------|-----------|-------------|---------------|-----------------|
| 1 | 1 / 2 GiB | 342,000 | ~10.3M | ~$3-5 |
| 2 | 2 / 4 GiB | 684,000 | ~20.5M | ~$6-10 |
| 3 | 4 / 8 GiB | 1,368,000 | ~41M | ~$12-20 |

Extra disk beyond tier default: ~4,416 credits/GiB/day.

Check current pricing: `aleph pricing instance`

## Troubleshooting

### "No API key found for provider" Error
The gateway reads `auth-profiles.json`, **NOT** `auth.json`. Ensure:
- File is at `~/.openclaw/agents/main/agent/auth-profiles.json`
- Format matches the template in Step 6 (with `"version": 1` and `"profiles"` key)
- Run `openclaw gateway restart` after any auth changes

### RPC Probe Failed
```bash
openclaw gateway install --force
openclaw gateway restart
sleep 3
openclaw gateway status --token "$GATEWAY_TOKEN"
```
The systemd service file caches the token — `install --force` re-syncs it.

### Interactive TUI Blocks Automation
Use `--crn-hash <HASH>` + `--skip-volume` + `--crn-auto-tac`. If still interactive, use the pexpect script from Step 4.

### VM Not Reachable After Creation
- Wait 45-60 seconds (boot takes time on decentralized infra)
- Check `aleph instance list` for the mapped SSH port
- Verify the CRN is healthy: `aleph node compute --crn-hash <HASH> --json`
- Try IPv6 if IPv4 mapping isn't working

### Credit Balance Dropping Too Fast
- `aleph account balance` — check remaining credits
- `aleph instance list` — count running instances
- `aleph instance delete <HASH>` — kill unused instances
- Each running instance burns credits continuously, even idle

### Config Validation Errors ("Unrecognized key")
Only use config keys that OpenClaw recognizes. Known valid top-level keys:
`auth`, `agents`, `gateway`, `models`, `tools`, `bindings`, `messages`, `commands`, `hooks`, `channels`, `skills`, `plugins`, `wizard`, `meta`

Run `openclaw doctor --fix` to auto-remove invalid keys.

### dpkg Prompts Block SSH Scripts
Use `DEBIAN_FRONTEND=noninteractive` before apt commands in non-TTY sessions.
