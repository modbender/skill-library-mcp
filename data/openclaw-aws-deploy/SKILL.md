---
name: openclaw-aws-deploy
description: Deploy OpenClaw securely on AWS with a single command. Creates VPC, EC2 (ARM64), Telegram channel, and configurable AI model (Bedrock, Gemini, or any provider) — SSM-only access, no SSH. Use when setting up OpenClaw on AWS, deploying a new agent instance to EC2, or tearing down an existing AWS deployment.
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "requires": { "bins": ["aws", "jq", "openssl"] },
      },
  }
---

# OpenClaw AWS Deploy Skill

## Quick Start (Minimal Deployment ~$30/mo)

### Prerequisites
- **AWS credentials** — any of these methods:
  - `--profile <name>` flag (named AWS CLI profile)
  - `.env.aws` file in workspace root or skill directory (optional):
    ```
    AWS_ACCESS_KEY_ID=...
    AWS_SECRET_ACCESS_KEY=...
    AWS_DEFAULT_REGION=us-east-1
    ```
  - Existing environment variables, AWS SSO session, or IAM role
- `.env.starfish` in workspace root (recommended) or skill directory:
  ```
  TELEGRAM_BOT_TOKEN=...     # from @BotFather (required)
  TELEGRAM_USER_ID=...       # your Telegram user ID (optional, enables auto-approve pairing)
  GEMINI_API_KEY=...         # from aistudio.google.com (optional, for Gemini models)
  ```
- `aws` CLI installed OR Docker for sandboxed access
- `jq`, `openssl` available

### One-Shot Deploy

```bash
# From the skill directory:
./scripts/deploy_minimal.sh --name starfish --region us-east-1 \
  --env-dir /path/to/workspace

# Or with cleanup of previous deployment first:
./scripts/deploy_minimal.sh --name starfish --region us-east-1 \
  --env-dir /path/to/workspace --cleanup-first
```

This single command:
1. Creates VPC + subnet + IGW + route table
2. Creates security group (NO inbound ports — SSM only)
3. Creates IAM role with minimal permissions (SSM + Parameter Store + Bedrock)
4. Stores secrets in SSM Parameter Store (fetched at each service start — rewritten on each start, never stored in repo or static images)
5. Launches **t4g.medium** ARM64 instance with user-data bootstrap
6. User-data installs Node.js 22 + OpenClaw + configures everything
7. Runs smoke test via SSM
8. Saves all resource IDs to `deploy-output.json`

### After Deploy

1. **Message the Telegram bot** — you'll get a pairing code
2. **Approve pairing** via SSM:
   ```bash
   aws ssm start-session --target <INSTANCE_ID> --region us-east-1
   sudo -u openclaw bash
   export HOME=/home/openclaw
   openclaw pairing approve telegram <CODE>
   ```
3. Bot is live! ✅

### Teardown

```bash
# Using saved output:
./scripts/teardown.sh --from-output ./deploy-output.json --env-dir /path/to/workspace --yes

# Or by name (discovers via tags):
./scripts/teardown.sh --name starfish --region us-east-1 --env-dir /path/to/workspace --yes
```

## Model Support

### `--model` flag

Pass any model string — it goes directly into `openclaw.json` as `model.primary`:

```bash
# Default (MiniMax M2.1 on Bedrock — no API key needed, uses IAM role)
./scripts/deploy_minimal.sh --name starfish --region us-east-1

# Gemini Flash (needs GEMINI_API_KEY in .env.starfish)
./scripts/deploy_minimal.sh --name starfish --region us-east-1 \
  --model google/gemini-2.0-flash
```

### AWS Bedrock

Bedrock IAM permissions (`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`) are **always added** to the instance role — regardless of which model you choose. This means any deployed instance can use Bedrock models out of the box via IAM role credentials (no API key needed).

Known Bedrock model IDs:
| Model flag | Description |
|------------|-------------|
| `amazon-bedrock/minimax.minimax-m2.1` | MiniMax M2.1 |
| `amazon-bedrock/minimax.minimax-m2` | MiniMax M2 |
| `amazon-bedrock/deepseek.deepseek-r1` | DeepSeek R1 |
| `amazon-bedrock/moonshotai.kimi-k2.5` | Kimi K2.5 |

> **Note:** Bedrock models must be enabled in your AWS account via the Bedrock console before use.

### Gemini

If `GEMINI_API_KEY` is present in `.env.starfish`, it's stored in SSM and written to `auth-profiles.json`. If absent, it's simply skipped — no error.

### `.env.starfish`
```
TELEGRAM_BOT_TOKEN=...     # Required — from @BotFather
GEMINI_API_KEY=...         # Optional — from aistudio.google.com (needed for Gemini models)
```

## Architecture (Minimal)

```
┌─────────────────────────────────────────────────────┐
│                      VPC (10.50.0.0/16)             │
│  ┌───────────────────────────────────────────────┐  │
│  │           Public Subnet (10.50.0.0/24)        │  │
│  │  ┌─────────────────────────────────────────┐  │  │
│  │  │      EC2 t4g.medium (ARM64, 4GB)        │  │  │
│  │  │  ┌───────────────────────────────────┐  │  │  │
│  │  │  │       OpenClaw Gateway             │  │  │  │
│  │  │  │  • Node.js 22.14.0                 │  │  │  │
│  │  │  │  • Any model (Bedrock/Gemini/etc)   │  │  │  │
│  │  │  │  • Telegram channel                │  │  │  │
│  │  │  │  • Encrypted EBS (gp3, 20GB)       │  │  │  │
│  │  │  └───────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ↑                              ↓
    SSM (no SSH/inbound)      Outbound HTTPS only
```

## Critical Lessons Learned (22 Issues)

These are baked into the deploy script. See `references/TROUBLESHOOTING.md` for full details.

### Instance Sizing
- **t4g.medium (4GB) required** — t4g.small (2GB) OOMs during npm install + gateway startup
- **ARM64** — better price/performance than x86

### Node.js
- **Node 22+ required** — OpenClaw 2026.x requires Node ≥22.12.0
- **Official tarball install** — NodeSource setup_22.x unreliable on AL2023 ARM64
- **git required** — OpenClaw npm install has git-based dependencies

### npm
- **Use `openclaw@latest`** — bare `openclaw` may resolve to placeholder package (0.0.1)

### Gateway Startup
- **Use `openclaw gateway run --allow-unconfigured`** — NOT `gateway start` (which tries `systemctl --user` and fails)
- **Config file must be `openclaw.json`** — not `config.yaml`
- **`gateway.mode: "local"`** — required or you get "Missing config" error
- **`gateway.auth.mode: "token"`** — `"none"` is invalid

### Telegram
- **`plugins.entries.telegram.enabled: true`** — must be explicit
- **`dmPolicy: "pairing"`** — not `"allowlist"` (blocks everyone without user list)
- **`streamMode: "partial"`** — some models don't support streaming tools, use `"off"` as fallback

### Model
- **Gemini 2.0 Flash** — recommended (free tier: 15 RPM, 1M tokens/day, supports tools)
- **Auth profiles required** — create `auth-profiles.json` in agent dir
- **Bedrock format** — `amazon-bedrock/MODEL_ID` (not `bedrock/`)
- **Bedrock models need console enablement** — Anthropic requires use case form

### Systemd Service
- **Simplified service file** — removed `ProtectHome`, `ReadWritePaths=/tmp/openclaw`, `PrivateTmp` due to namespace issues
- **Use `NODE_OPTIONS="--max-old-space-size=1024"`** — helps prevent OOM

### Security
- **No inbound ports** — SSM Session Manager only
- **Secrets fetched from SSM at runtime** — startup script fetches secrets each time the service starts; config files are ephemeral (rewritten on each start, never stored in repo or static images)
- **Encrypted EBS** — enabled by default in deploy script
- **IMDSv2 required** — `HttpTokens=required`

## File Layout

```
scripts/
  deploy_minimal.sh        # One-shot deploy (VPC + EC2 + OpenClaw)
  teardown.sh              # Clean teardown of all resources
  setup_deployer_role.sh   # Create IAM role/user with minimum permissions
  preflight.sh             # Pre-deploy validation checks
  smoke_test.sh            # Post-deploy health verification

references/
  TROUBLESHOOTING.md   # All 22 issues + solutions
  config-templates/    # Ready-to-use config files
    gemini-flash.json  # OpenClaw config for Gemini Flash
    auth-profiles-gemini.json  # Auth profile template
    openclaw.service.txt  # Systemd unit file template
    startup.sh         # Startup script template
```

## Config Templates

### OpenClaw Config (gemini-flash.json)
See `references/config-templates/gemini-flash.json` — includes all required fields.

### Auth Profiles (auth-profiles-gemini.json)
Create at `~/.openclaw/agents/main/agent/auth-profiles.json`

### Systemd Service (openclaw.service)
Simplified for reliability — security hardening removed due to namespace issues.

## Cost Breakdown (~$30/mo)
| Resource | Cost |
|----------|------|
| t4g.medium (4GB ARM64) | ~$24.53/mo |
| EBS gp3 20GB | ~$1.60/mo |
| Public IP | ~$3.65/mo |
| Gemini Flash | Free tier / ~$0.30/1M tokens |
| **Total** | **~$29.78/mo** |

## Troubleshooting

### "No API key found for amazon-bedrock"

**Cause:** OpenClaw needs `models.providers` config in `openclaw.json` with `"auth": "aws-sdk"`. An `auth-profiles.json` entry alone is NOT sufficient.

**Fix:** Add to `openclaw.json` on the instance:
```bash
sudo -u openclaw bash
cd /home/openclaw/.openclaw
jq '.models = {
  "providers": {"amazon-bedrock": {"baseUrl": "https://bedrock-runtime.us-east-1.amazonaws.com", "api": "bedrock-converse-stream", "auth": "aws-sdk", "models": [{"id": "minimax.minimax-m2.1", "name": "MiniMax M2.1", "input": ["text"], "contextWindow": 128000, "maxTokens": 4096}]}},
  "bedrockDiscovery": {"enabled": true, "region": "us-east-1"}
}' openclaw.json > /tmp/oc.json && mv /tmp/oc.json openclaw.json
chown openclaw:openclaw openclaw.json
systemctl restart openclaw
```

### "API rate limit reached" (Gemini)

**Fix:** Switch to Bedrock (default in current version) or redeploy with `--model amazon-bedrock/minimax.minimax-m2.1`.

### Bedrock model returns errors

**Cause:** Model must be enabled in AWS Console → Bedrock → Model access. MiniMax models are auto-authorized; Anthropic/Meta models require use-case approval.

### Bot doesn't respond after deploy

**Fix:** Add `TELEGRAM_USER_ID` to `.env.starfish` for auto-pairing, or use `--pair-user <id>`. Manual: `openclaw pairing approve telegram <CODE>` via SSM.

## Safety Rules
- Never print secrets in logs
- Never open SSH/inbound ports; use SSM Session Manager only
- Use least-privilege IAM policies
- All resources tagged with `Project=<name>` and `DeployId=<unique-id>` for deterministic cleanup
- Encrypted EBS volumes always
