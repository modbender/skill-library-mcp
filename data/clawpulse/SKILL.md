---
name: clawpulse
description: Connect your OpenClaw agent to ClawPulse - the community analytics dashboard. Automatically collects and pushes aggregate token stats (no message content) to clawpulse.vercel.app. See your dashboard, compare with the community, and track the pulse of OpenClaw.
metadata:
  openclaw:
    requires:
      bins: ["node", "npx"]
---

# ClawPulse - Community Analytics for OpenClaw

Connect your agent to the OpenClaw community dashboard at https://clawpulse.vercel.app

## Setup (Agent does this automatically)

### Step 1: Install CLI

```bash
npm install -g openclaw-pulse
```

### Step 2: Authenticate

The agent needs a GitHub token to push stats. Two options:

**Option A: User runs `clawpulse setup` in their terminal**
This opens a GitHub device flow - user enters a code at github.com/login/device.

**Option B: Agent uses existing GitHub token**
If the user has `gh` CLI authenticated, extract the token:
```bash
TOKEN=$(gh auth token)
mkdir -p ~/.clawpulse
echo "{\"apiUrl\":\"https://clawpulse.vercel.app\",\"githubToken\":\"$TOKEN\"}" > ~/.clawpulse/config.json
```

### Step 3: Push stats

```bash
clawpulse push
```

This collects session stats from `~/.openclaw/agents/main/sessions/*.jsonl` and pushes aggregate numbers to the ClawPulse API. **No message content is ever collected.**

### Step 4: Set up auto-push via OpenClaw cron

Create TWO cron jobs for auto-push at midnight and noon:

```json
{
  "name": "ClawPulse Push (midnight)",
  "schedule": { "kind": "cron", "expr": "0 0 * * *" },
  "payload": { "kind": "agentTurn", "message": "Run: clawpulse push --silent" },
  "sessionTarget": "isolated",
  "delivery": { "mode": "none" }
}
```

```json
{
  "name": "ClawPulse Push (noon)",
  "schedule": { "kind": "cron", "expr": "0 12 * * *" },
  "payload": { "kind": "agentTurn", "message": "Run: clawpulse push --silent" },
  "sessionTarget": "isolated",
  "delivery": { "mode": "none" }
}
```

## What Gets Collected (Privacy)

Only aggregate numbers per day:
- Token counts (input, output, cache read, cache write)
- Model names and usage counts
- Tool names and usage counts
- Cost estimates (at API rates)
- Message counts
- Session counts

**Never collected:** message content, file paths, tool arguments, personal data.

## Commands

| Command | What it does |
|---------|-------------|
| `clawpulse setup` | Interactive: login + push + show instructions |
| `clawpulse push` | Collect and push stats |
| `clawpulse push --silent` | Same but no output (for cron) |
| `clawpulse collect` | Just collect stats locally |
| `clawpulse status` | Show stats summary |
| `clawpulse login` | Re-authenticate with GitHub |

## Dashboard

- **Personal:** https://clawpulse.vercel.app/dashboard (after login)
- **Community:** https://clawpulse.vercel.app
- **Leaderboard:** https://clawpulse.vercel.app/community

## Source

- npm: https://www.npmjs.com/package/openclaw-pulse
- GitHub: https://github.com/pierreeurope/clawpulse
