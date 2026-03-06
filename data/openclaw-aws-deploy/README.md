# openclaw-aws-deploy

**One-shot OpenClaw deployment to AWS** — VPC, EC2, Telegram, any AI model, all in one command.

[![ClawHub](https://img.shields.io/badge/ClawHub-openclaw--aws--deploy-blue)](https://clawhub.ai/skills/openclaw-aws-deploy)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What It Does

Deploys a fully working OpenClaw agent to AWS with a single command:

```
┌─────────────────────────────────────────────────────┐
│                    VPC (isolated)                    │
│  ┌───────────────────────────────────────────────┐  │
│  │      EC2 t4g.medium (ARM64, 4GB, encrypted)   │  │
│  │  ┌───────────────────────────────────────────┐│  │
│  │  │         OpenClaw Gateway                  ││  │
│  │  │  • Any model (Bedrock/Gemini/OpenRouter)  ││  │
│  │  │  • Telegram channel                       ││  │
│  │  │  • Node.js 22 + systemd                   ││  │
│  │  │  • CloudWatch monitoring                  ││  │
│  │  └───────────────────────────────────────────┘│  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
         ↑                              ↓
    SSM only (no SSH)         Outbound HTTPS only
```

**Cost:** ~$30/month (t4g.medium + EBS + public IP).

## Quick Start

### Step 1: Set Up AWS Permissions

You need an AWS identity with permissions to create VPC, EC2, IAM, SSM, and CloudWatch resources.

**Option A: Use the setup script (recommended)**

```bash
# Create a dedicated deployer IAM role with minimum permissions
./scripts/setup_deployer_role.sh --type role --name openclaw-deployer

# Or create an IAM user with access keys
./scripts/setup_deployer_role.sh --type user --name openclaw-deployer

# Just print the policy (no changes):
./scripts/setup_deployer_role.sh --dry-run
```

**Option B: Use an existing AWS profile/SSO**

If you already have an AWS profile with sufficient permissions:

```bash
# No .env.aws needed — just pass --profile
./scripts/deploy_minimal.sh --name starfish --profile my-aws-profile
```

**Option C: Use environment variables or .env.aws**

```bash
# .env.aws (in workspace root, never committed)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_DEFAULT_REGION=us-east-1
```

### Step 2: Create Telegram Bot + API Keys

```bash
# .env.starfish (or .env.<agent-name>)
TELEGRAM_BOT_TOKEN=from-botfather          # Required
GEMINI_API_KEY=from-aistudio.google.com    # Optional (for Gemini models)
```

- **Telegram bot:** Message [@BotFather](https://t.me/BotFather) → `/newbot`
- **Gemini API key:** [aistudio.google.com/apikey](https://aistudio.google.com/apikey) (free tier)
- **Bedrock models:** No API key needed — uses IAM role automatically

### Step 3: Deploy

```bash
# With AWS profile (recommended):
./scripts/deploy_minimal.sh --name starfish --profile openclaw-deployer

# With .env.aws:
./scripts/deploy_minimal.sh --name starfish --env-dir /path/to/workspace

# With Bedrock model (no Gemini key needed):
./scripts/deploy_minimal.sh --name starfish --profile openclaw-deployer \
  --model amazon-bedrock/minimax.minimax-m2.1

# With auto-pairing:
./scripts/deploy_minimal.sh --name starfish --profile openclaw-deployer \
  --pair-user 123456789
```

### Step 4: Pair Telegram

If you didn't use `--pair-user`, message your bot → get pairing code → approve:

```bash
aws ssm start-session --target <INSTANCE_ID> --region us-east-1
sudo -u openclaw bash -c "export HOME=/home/openclaw; openclaw pairing approve telegram <CODE>"
```

### Step 5: Teardown (when done)

```bash
./scripts/teardown.sh --from-output ./deploy-output.json --yes

# Or with AWS profile:
./scripts/teardown.sh --name starfish --profile openclaw-deployer --yes
```

## IAM Permissions

### Deployer Permissions (your machine)

The identity running the deploy script needs these permissions:

| Category | Actions | Why |
|----------|---------|-----|
| **EC2/VPC** | `CreateVpc`, `CreateSubnet`, `RunInstances`, `TerminateInstances`, etc. | Create/destroy infrastructure |
| **IAM** | `CreateRole`, `PutRolePolicy`, `PassRole`, `CreateInstanceProfile` | Set up instance role |
| **SSM** | `PutParameter`, `SendCommand`, `StartSession` | Store secrets, run commands |
| **CloudWatch** | `PutMetricAlarm`, `CreateLogGroup` | Monitoring (optional) |
| **STS** | `GetCallerIdentity` | Identity verification |

Run `./scripts/setup_deployer_role.sh --dry-run` to see the full policy JSON.

### Instance Permissions (on EC2)

The deployed instance gets a minimal IAM role with:

| Permission | Why |
|------------|-----|
| `AmazonSSMManagedInstanceCore` | SSM Session Manager access |
| `ssm:GetParameter` (scoped) | Read its own secrets from SSM |
| `bedrock:InvokeModel` | Call any Bedrock model |
| `bedrock:ListFoundationModels` | Auto-discover available models |
| `cloudwatch:PutLogEvents` | Ship logs (if monitoring enabled) |

## Model Support

Pass any model string via `--model`:

```bash
# Gemini (default, free tier)
--model google/gemini-2.0-flash

# Bedrock (uses IAM, no API key)
--model amazon-bedrock/minimax.minimax-m2.1
--model amazon-bedrock/deepseek.deepseek-r1

# Any provider (edit config post-deploy)
--model openrouter/anthropic/claude-sonnet-4
```

Bedrock IAM permissions are always included — switch to any Bedrock model by editing config.

## Personalities

| Personality | Description |
|-------------|-------------|
| `default` | Helpful, direct, efficient assistant |
| `sentinel` | Vigilant monitor — alerts, status reports, anomaly detection |
| `researcher` | Deep-thinking research assistant — sources, analysis |
| `coder` | Pragmatic software engineer — PRs, code review |
| `companion` | Warm, empathetic companion — check-ins, support |
| *custom path* | Provide path to your own `SOUL.md` file |

```bash
./scripts/deploy_minimal.sh --name watchdog --personality sentinel ...
./scripts/deploy_minimal.sh --name my-agent --personality ./my-soul.md ...
```

## Security

| Feature | Detail |
|---------|--------|
| **No SSH** | SSM Session Manager only — zero inbound ports |
| **Secrets from SSM** | Fetched at runtime on each service start, rewritten on each boot |
| **AWS auth chain** | Supports profiles, SSO, assume-role, env vars — no raw keys required |
| **Encrypted storage** | EBS volumes use AES-256 encryption |
| **IMDSv2 enforced** | Instance metadata requires session tokens |
| **Minimal IAM** | Instance role scoped to SSM + Bedrock only |
| **Tagged resources** | All resources tagged with `Project` + unique `DeployId` |
| **Node integrity** | SHA256 verification on Node.js tarball |
| **Preflight checks** | Validates permissions before creating resources |
| **Auto-rollback** | Failed deploys automatically clean up (by DeployId) |

## What Gets Created

| Resource | Purpose | Cost |
|----------|---------|------|
| VPC + subnet + IGW | Isolated network | Free |
| Security group | No inbound rules | Free |
| IAM role + profile | SSM + Bedrock access | Free |
| SSM parameters | Encrypted secret storage | Free |
| CloudWatch alarms | Health + CPU monitoring | Free tier |
| CloudWatch log group | Log retention (7 days) | ~$0.50/GB |
| EC2 t4g.medium | OpenClaw host (ARM64, 4GB) | ~$24.53/mo |
| EBS gp3 20GB | Encrypted root volume | ~$1.60/mo |
| Public IP | Outbound connectivity | ~$3.65/mo |
| **Total** | | **~$30/mo** |

## Files

```
scripts/
  deploy_minimal.sh        ← One-shot deploy (start here)
  teardown.sh              ← Clean removal of all resources
  setup_deployer_role.sh   ← Create IAM role/user with minimum permissions

assets/personalities/      ← Agent personality presets (SOUL.md files)

references/
  TROUBLESHOOTING.md       ← 22 documented issues + solutions
  config-templates/        ← OpenClaw config, systemd, auth templates
```

## Requirements

- AWS CLI v2 installed and configured
- `jq`, `openssl` available
- AWS account with permissions (see [IAM Permissions](#iam-permissions))
- Telegram bot token ([create one](https://t.me/BotFather))
- Optional: Gemini API key ([free](https://aistudio.google.com/apikey))

## Lessons Learned

This skill encodes **22 documented issues** discovered during real deployments. Every fix is baked into the scripts. See [`references/TROUBLESHOOTING.md`](references/TROUBLESHOOTING.md).

## Contributing

PRs welcome. If you hit a new issue, add it to `references/TROUBLESHOOTING.md`.

## License

MIT
