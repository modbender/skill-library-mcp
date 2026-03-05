# openclaw-skill-promptlayer

An [OpenClaw](https://openclaw.ai) skill for [PromptLayer](https://promptlayer.com) — prompt management, versioning, evaluations, and LLM observability.

## Quick Start

```bash
# Install from ClawHub
clawhub install promptlayer

# Set your API key
echo "PROMPTLAYER_API_KEY=pl_your_key_here" >> ~/.openclaw/.env

# Verify it works
export PROMPTLAYER_API_KEY=pl_your_key_here
./skills/promptlayer/scripts/pl.sh templates list
```

Get your API key from [PromptLayer Dashboard → Settings](https://dashboard.promptlayer.com/settings).

## What's Included

### 🛠️ CLI (`scripts/pl.sh`)

Full REST API wrapper:

```bash
# Prompt Templates
pl.sh templates list [--name <filter>] [--label <label>]
pl.sh templates get <name|id> [--label prod] [--version 3]
pl.sh templates publish              # JSON on stdin
pl.sh templates labels               # List release labels

# Log an LLM request (JSON on stdin)
echo '{"provider":"openai","model":"gpt-4o",...}' | pl.sh log

# Tracking
pl.sh track-prompt <req_id> <prompt_name> [--version 1] [--vars '{}']
pl.sh track-score <req_id> <score_0_100> [--name accuracy]
pl.sh track-metadata <req_id> --json '{"user_id":"abc"}'
pl.sh track-group <req_id> <group_id>

# Datasets & Evaluations
pl.sh datasets list [--name <filter>]
pl.sh evals list [--name <filter>]
pl.sh evals run <eval_id>
pl.sh evals get <eval_id>

# Agents
pl.sh agents list
pl.sh agents run <agent_id> --input '{"key":"val"}'
```

### 📊 Monitoring Hook (`hooks/promptlayer-monitor/`)

Auto-logs every outbound agent message to PromptLayer. Install by copying to your hooks directory:

```bash
cp -r skills/promptlayer/hooks/promptlayer-monitor ~/.openclaw/hooks/
# or for workspace hooks:
cp -r skills/promptlayer/hooks/promptlayer-monitor ~/your-workspace/hooks/

# Enable it
openclaw hooks enable promptlayer-monitor

# Restart gateway to load
openclaw gateway restart
```

The hook listens for `message:sent` events and logs:
- Model and provider
- Message content (truncated to 4000 chars)
- Session type tags (main/cron/subagent)
- Channel info (telegram/discord/etc.)

> **Note:** `message:sent` hook support depends on your OpenClaw version and channel adapter. If the hook isn't firing, use the cron-based sync approach below.

### ⏰ Cron-Based Sync (Alternative)

If the hook doesn't work with your setup, create a cron job that periodically syncs session history to PromptLayer. See `scripts/sync-to-promptlayer.sh` for the state management script, and set up an OpenClaw cron with `sessions_history` + `curl` to the `/log-request` endpoint.

## API Reference

See `references/api.md` for the complete PromptLayer REST API reference.

### Key API Path Groups

PromptLayer uses three different path prefixes:
- `/prompt-templates` — template registry (list, get)
- `/rest/` — tracking (score, metadata, group, prompt)
- `/api/public/v2/` — datasets, evaluations
- `/log-request` — request logging (no prefix)
- `/workflows` — agents

Auth: `X-API-KEY: <your_key>` header on all requests.

## Installation (Manual)

```bash
cd ~/your-workspace/skills
git clone https://github.com/theashbhat/openclaw-skill-promptlayer.git promptlayer
```

## Links

- [PromptLayer Docs](https://docs.promptlayer.com)
- [PromptLayer REST API Reference](https://docs.promptlayer.com/reference/rest-api-reference)
- [OpenClaw Docs](https://docs.openclaw.ai)
- [OpenClaw Hooks](https://docs.openclaw.ai/automation/hooks)

## License

MIT
