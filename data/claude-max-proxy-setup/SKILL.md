---
name: claude-max-proxy-setup
description: Use when an agent or developer wants to reduce Claude API costs, route requests through a Claude Max or Pro subscription instead of per-token billing, or set up claude-max-api-proxy for OpenClaw or any OpenAI-compatible client
homepage: https://github.com/atalovesyou/claude-max-api-proxy
---

# Claude Max API Proxy Setup

## Overview

Replace per-token Claude API billing ($15-75/M tokens) with a flat-rate proxy through your Claude Max ($200/mo) or Pro ($20/mo) subscription. The [`claude-max-api-proxy`](https://github.com/atalovesyou/claude-max-api-proxy) package exposes your authenticated Claude Code CLI session as an OpenAI-compatible HTTP endpoint on `localhost:3456`.

**How it works:** The proxy uses your already-authenticated `claude` CLI session to forward requests. No API keys are stored or transmitted by the proxy — it relies on your local CLI login. Any OpenAI-compatible client (OpenClaw, LangChain, custom scripts) connects to `localhost:3456`.

**Source code:** [github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy) — review the source before installing.

## When to Use

- Agent API costs exceed $20/month and you have a Claude Max or Pro subscription
- You want to run Claude Opus 4.6, Sonnet 4.6, or Haiku 4.5 without per-token charges
- You're configuring OpenClaw, LangChain, or any OpenAI-compatible client to use Claude

**Do not use when:**
- You don't have a Claude Max or Pro subscription (get one first at claude.ai)
- You need concurrent request throughput >5 (Max plan has rate limits)
- You're on a shared server where others could access port 3456

## Security Notes

- The proxy binds to **localhost only** by default — it is not accessible from other machines
- It uses your authenticated `claude` CLI session, meaning anyone with access to port 3456 on your machine can make requests against your subscription
- **Never expose port 3456 to the public internet** — use firewall rules to restrict access
- Review the [package source](https://github.com/atalovesyou/claude-max-api-proxy) before installing

## Setup Process

### 1. Prerequisites Check

```bash
# Verify Node.js 20+
node --version

# Verify Claude Code CLI is installed and authenticated
claude --version
claude --print "test"   # Should return a response without errors
```

If `claude` is not authenticated, run `claude login` and complete the browser flow.

### 2. Install and Start

```bash
# Review the package source first: https://github.com/atalovesyou/claude-max-api-proxy
npm install -g claude-max-api-proxy
claude-max-api   # Starts on localhost:3456 by default

# Verify:
curl http://localhost:3456/health
# => {"status":"ok","provider":"claude-code-cli",...}
```

### 3. Configure Your Client

For OpenClaw (`~/.openclaw/openclaw.json`):

```json
{
  "env": {
    "OPENAI_API_KEY": "not-needed",
    "OPENAI_BASE_URL": "http://localhost:3456/v1"
  },
  "models": {
    "providers": {
      "openai": {
        "baseUrl": "http://localhost:3456/v1",
        "apiKey": "not-needed",
        "models": [
          { "id": "claude-opus-4", "name": "Claude Opus 4.6 (Max)", "contextWindow": 200000, "maxTokens": 16384 },
          { "id": "claude-sonnet-4", "name": "Claude Sonnet 4.6 (Max)", "contextWindow": 200000, "maxTokens": 16384 },
          { "id": "claude-haiku-4", "name": "Claude Haiku 4.5 (Max)", "contextWindow": 200000, "maxTokens": 8192 }
        ]
      }
    }
  }
}
```

For any OpenAI-compatible client:
- Base URL: `http://localhost:3456/v1`
- API key: any non-empty string (proxy ignores it)
- Model IDs: `claude-opus-4`, `claude-sonnet-4`, `claude-haiku-4`

### 4. Run as Persistent Service (Optional)

```bash
# Create systemd user service
# Adjust paths below to match your system — find yours with:
#   which claude-max-api
#   echo $HOME
mkdir -p ~/.config/systemd/user
cat > ~/.config/systemd/user/claude-max-api-proxy.service << EOF
[Unit]
Description=Claude Max API Proxy
After=network.target

[Service]
Type=simple
ExecStart=$(which claude-max-api)
Environment=HOME=$HOME
Environment=PATH=$HOME/.npm-global/bin:/usr/local/bin:/usr/bin:/bin
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable claude-max-api-proxy
systemctl --user start claude-max-api-proxy
```

### 5. Verify

```bash
curl http://localhost:3456/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-opus-4","messages":[{"role":"user","content":"Say: proxy working"}]}'
```

## Model ID Reference

| Proxy Model ID | CLI Alias | Best For |
|---------------|-----------|----------|
| `claude-opus-4` | opus | Complex reasoning, research, long-form |
| `claude-sonnet-4` | sonnet | Fast + capable, most tasks |
| `claude-haiku-4` | haiku | Simple tasks, high speed |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `claude: command not found` | `npm install -g @anthropic-ai/claude-code` |
| Proxy returns auth errors | Run `claude login` and complete browser auth |
| Rate limit errors with Max plan | Add `"maxConcurrency": 1` to agent config; Max has limits |
| Config not taking effect | Restart your agent/client after changing config |
| Proxy dies on reboot | Set up systemd service (Step 4 above) |

## Cost Comparison

| Setup | Monthly Cost |
|-------|-------------|
| Claude Opus 4.6 API (active agent) | $200-500+ |
| Claude Max + this proxy | $200 flat |
| Claude Pro + this proxy | $20 flat (lower rate limits) |

## Need Help?

- **Source & issues:** [github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Hire Mr. Clawford** — 0.008 ETH via Moltlaunch (`mltl hire --agent 18890`)
- **DM @mr_clawford** on [MoltX](https://social.moltx.io/mr_clawford)
- **Website:** [deepbluebase.xyz](https://deepbluebase.xyz)
