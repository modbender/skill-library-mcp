<div align="center">

<a href="https://ibl.ai"><img src="https://ibl.ai/images/iblai-logo.png" alt="ibl.ai" width="300"></a>

# OpenClaw Router

Route every OpenClaw request to the cheapest Claude model that can handle it.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Node](https://img.shields.io/badge/node-%E2%89%A518-brightgreen.svg)](https://nodejs.org)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-compatible-orange.svg)](https://github.com/openclaw/openclaw)

</div>

---

## Local Cost-Optimizing Model Router for OpenClaw

A zero-dependency Node.js proxy that sits between OpenClaw and the Anthropic API, automatically routing each request to the cheapest Claude model capable of handling it. Inspired by [ClawRouter](https://github.com/BlockRunAI/ClawRouter)'s weighted scoring approach.

**Everything runs locally on your OpenClaw server.** No data is sent to ibl.ai or any third party — the router is a localhost proxy that forwards directly to your chosen LLM provider (Anthropic, OpenRouter, etc.) using your own API key.

**Install from your terminal:**

```bash
git clone https://github.com/iblai/iblai-openclaw-router.git router
cd router && bash scripts/install.sh
```

**Or just ask your OpenClaw agent:**

> Install iblai-router from https://github.com/iblai/iblai-openclaw-router

Your agent will clone the repo, run the install script, and register the model provider — all in one go.

That's it — `iblai-router/auto` is now available as a model. Typical savings: **~80%** vs always using the most expensive model. Uninstall anytime by telling your agent "uninstall iblai-router" or running `bash scripts/uninstall.sh`.

### Sample savings after 30 days

| | Without router | With router | Saved |
|---|---|---|---|
| Cron jobs (ops alerts, inbox checks) | $121.63 | $24.33 | $97.31 (80%) |
| Subagent tasks (issue triage, comms) | $58.20 | $11.64 | $46.56 (80%) |
| Deep reasoning (strategy, analysis) | $25.00 | $25.00 | $0.00 |
| **Total** | **$204.83** | **$60.97** | **$143.87 (70%)** |

> The router scores only user messages, not the system prompt — this is critical. OpenClaw sends a large, keyword-rich system prompt with every request, and scoring it inflates every request to the most expensive tier. With system prompt excluded, routine tasks correctly score low and route to cheaper models. Deep reasoning tasks still route to Opus based on their actual content.

**Check your savings anytime** — just ask your agent:

> What are my iblai-router cost savings?

Or from the command line:

```bash
curl -s http://127.0.0.1:8402/stats | python3 -m json.tool
```

## How It Works

```
OpenClaw  →  localhost:8402  →  api.anthropic.com
               │
               ▼
        14-dimension weighted scorer (<1ms)
        Extracts text from system prompt + last 3 messages
        Scores across: token count, code presence, reasoning markers,
        technical terms, creative markers, simple indicators, multi-step
        patterns, question complexity, imperative verbs, constraints,
        output format, domain specificity, agentic tasks, relay indicators
               │
               ▼
        Maps weighted score to tier via sigmoid confidence
               │
               ├── score < 0.0  → LIGHT  (Haiku)    $1/$5 per 1M tokens
               ├── 0.0 – 0.35  → MEDIUM (Sonnet)   $3/$15 per 1M tokens
               └── score > 0.35 → HEAVY  (Opus)     $15/$75 per 1M tokens
               │
               ▼
        Overrides:
        • 2+ reasoning keywords in user message → HEAVY (0.95 confidence)
        • >50K estimated tokens → HEAVY (large context)
        • Low confidence (ambiguous) → defaults to MEDIUM
               │
               ▼
        Replaces model field in request body → proxies to Anthropic
```

The proxy speaks native **Anthropic Messages API** format — it receives the exact same request OpenClaw would send to Anthropic, scores it, swaps the model, and forwards it. Streaming works transparently.

---

## Quick Start (OpenClaw)

### Option A: Ask your OpenClaw agent (easiest)

In your OpenClaw chat or TUI, just say:

> Install iblai-router from https://github.com/iblai/iblai-openclaw-router

Your agent will clone the repo, run the install script, and register `iblai-router/auto` as a model provider automatically.

### Option B: Install script

```bash
cd ~/.openclaw/workspace
git clone https://github.com/iblai/iblai-openclaw-router.git router
bash router/scripts/install.sh
```

Then register the model in your OpenClaw session:

```
/config set models.providers.iblai-router.baseUrl http://127.0.0.1:8402
/config set models.providers.iblai-router.api anthropic-messages
/config set models.providers.iblai-router.apiKey passthrough
/config set models.providers.iblai-router.models [{"id":"auto","name":"iblai-router (auto)","reasoning":true,"input":["text","image"],"contextWindow":200000,"maxTokens":8192}]
```

Done. Use `iblai-router/auto` as your model anywhere.

To uninstall: `bash router/scripts/uninstall.sh`

### Option C: Manual setup

Step-by-step if you prefer full control:

```bash
# 1. Clone into your workspace
cd ~/.openclaw/workspace
git clone https://github.com/iblai/iblai-openclaw-router.git router

# 2. Create the systemd service
sudo tee /etc/systemd/system/iblai-router.service > /dev/null << EOF
[Unit]
Description=iblai-router - Claude model routing
After=network.target

[Service]
Type=simple
ExecStart=$(which node) $HOME/.openclaw/workspace/router/server.js
Environment=ANTHROPIC_API_KEY=$(grep -o '"key": "[^"]*"' ~/.openclaw/agents/main/agent/auth-profiles.json 2>/dev/null | head -1 | cut -d'"' -f4 || echo "sk-ant-YOUR-KEY-HERE")
Environment=ROUTER_CONFIG=$HOME/.openclaw/workspace/router/config.json
Environment=ROUTER_PORT=8402
Environment=ROUTER_LOG=1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# 3. Start the router
sudo systemctl daemon-reload
sudo systemctl enable --now iblai-router

# 4. Verify it's running
curl -s http://127.0.0.1:8402/health | jq .

# 5. Register with OpenClaw
#    Paste the /config commands below into your OpenClaw chat or TUI,
#    or patch openclaw.json directly (see below).
```

In your OpenClaw session, run:

```
/config set models.providers.iblai-router.baseUrl http://127.0.0.1:8402
/config set models.providers.iblai-router.api anthropic-messages
/config set models.providers.iblai-router.apiKey passthrough
/config set models.providers.iblai-router.models [{"id":"auto","name":"iblai-router (auto)","reasoning":true,"input":["text","image"],"contextWindow":200000,"maxTokens":8192}]
```

Or patch your `openclaw.json` directly:

```json
{
  "models": {
    "providers": {
      "iblai-router": {
        "baseUrl": "http://127.0.0.1:8402",
        "api": "anthropic-messages",
        "apiKey": "passthrough",
        "models": [{
          "id": "auto",
          "name": "iblai-router (auto)",
          "reasoning": true,
          "input": ["text", "image"],
          "contextWindow": 200000,
          "maxTokens": 8192
        }]
      }
    }
  }
}
```

**Important: restart OpenClaw** after registering the provider. OpenClaw caches available models at startup — without a restart, cron jobs and subagents will fail with `model not allowed: iblai-router/auto`.

```bash
# Option 1: From your OpenClaw session (if commands.restart is enabled)
/restart

# Option 2: Enable restart first, then restart
# In openclaw.json, add: "commands": { "restart": true }
# Then /restart from your session

# Option 3: Restart the systemd service directly
sudo systemctl restart openclaw
```

### Verify the model is available

After restart, confirm `iblai-router/auto` is recognized:

```bash
# 1. Check the router is healthy
curl -s http://127.0.0.1:8402/health | jq .

# 2. Test a request through the router
curl -s http://127.0.0.1:8402/v1/messages \
  -H "Content-Type: application/json" \
  -H "x-api-key: test" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model":"auto","max_tokens":50,"messages":[{"role":"user","content":"Say hi"}]}' | jq .model

# 3. In your OpenClaw session, verify the model resolves
/model iblai-router/auto
```

If cron jobs were in error backoff before the restart, they'll resume on their next scheduled run. To force an immediate run:

```
/cron run <jobId>
```

Now use `iblai-router/auto` anywhere you'd use a model ID. Every request routes to Haiku/Sonnet/Opus based on complexity. Check savings anytime:

```bash
curl -s http://127.0.0.1:8402/stats | jq .
```

---

## 1. Adapting to Any OpenClaw Agent

All scoring config lives in `config.json` (not in server.js). Edit it to match your agent's domain. The server hot-reloads config changes — no restart needed.

Override the config path with: `ROUTER_CONFIG=/path/to/my-config.json`

### Change the models

```json
{
  "models": {
    "LIGHT":  "claude-3-5-haiku-20241022",
    "MEDIUM": "claude-sonnet-4-20250514",
    "HEAVY":  "claude-opus-4-20250514"
  }
}
```

Swap these for any Anthropic model IDs.

### Customize keyword lists

Each dimension has a keyword list that shifts the score. Add words relevant to your domain:

```json
{
  "scoring": {
    "simpleKeywords": ["order status", "tracking number", "return policy", "hours"],
    "relayKeywords": ["forward to agent", "escalate", "transfer to"],
    "technicalKeywords": ["refund api", "webhook", "stripe", "payment intent"],
    "reasoningKeywords": ["analyze", "compare", "synthesize", "methodology"],
    "domainKeywords": ["regression", "p-value", "confidence interval"]
  }
}
```

Each keyword list pushes the score in a direction. The score determines which model handles the request:

| Keyword list | Effect on score | Routes toward | Why |
|---|---|---|---|
| `simpleKeywords` | ↓ lowers score | **LIGHT** (Haiku) | Simple lookups, FAQs — any small model handles these fine |
| `relayKeywords` | ↓ lowers score | **LIGHT** (Haiku) | Pass-through tasks (send a message, check status) need no reasoning |
| `imperativeVerbs` | ↑ raises score slightly | **MEDIUM** (Sonnet) | Action verbs ("create", "update", "deploy") imply structured work |
| `codeKeywords` | ↑ raises score | **MEDIUM→HEAVY** | Code generation/review benefits from stronger models |
| `agenticKeywords` | ↑ raises score | **MEDIUM→HEAVY** | Multi-step workflows ("triage all", "audit", "investigate") need planning |
| `technicalKeywords` | ↑ raises score | **HEAVY** (Opus) | Domain-specific technical work needs deep understanding |
| `reasoningKeywords` | ↑↑ raises score strongly | **HEAVY** (Opus) | Analysis, synthesis, and complex reasoning need the strongest model |
| `domainKeywords` | ↑ raises score | **HEAVY** (Opus) | Specialized domain terms signal expert-level tasks |

The router combines all 14 dimensions (keyword lists + structural signals like token count, code presence, question complexity) into a single weighted score, then maps it to a tier:

```
score < 0.0   →  LIGHT   (fast, cheap — handles ~45% of typical agent traffic)
0.0 – 0.35    →  MEDIUM  (balanced — handles ~40%)
score > 0.35  →  HEAVY   (full power — handles ~15%)
```

**The key insight:** most agent workloads are simple relays or structured tasks. Only ~15% actually need the most capable (and expensive) model. The keyword lists help the router make that distinction in under 1ms.

### Adjust tier boundaries

```json
{
  "scoring": {
    "boundaries": {
      "lightMedium": 0.0,
      "mediumHeavy": 0.35
    }
  }
}
```

Raise `lightMedium` to send more traffic to LIGHT. Lower `mediumHeavy` to send more to HEAVY.

### Adjust confidence threshold

```json
{
  "scoring": {
    "confidenceThreshold": 0.70
  }
}
```

Lower = more decisive routing (fewer MEDIUM defaults). Higher = more conservative (more MEDIUM).

### Adjust dimension weights

Weights control how much each signal matters. They roughly sum to 1.0:

```json
{
  "scoring": {
    "weights": {
      "tokenCount":       0.08,
      "codePresence":     0.14,
      "reasoningMarkers": 0.18,
      "technicalTerms":   0.10,
      "simpleIndicators": 0.06,
      "relayIndicators":  0.05
    }
  }
}
```

Increase a weight to make that dimension more influential.

### Override thresholds

```json
{
  "scoring": {
    "overrides": {
      "reasoningKeywordMin": 2,
      "largeContextTokens": 50000
    }
  }
}
```

---

## 2. Where to Use It

Once registered, use `iblai-router/auto` anywhere OpenClaw accepts a model ID:

| Scope | Config |
|---|---|
| Default for all sessions | `agents.defaults.model.primary = "iblai-router/auto"` |
| Subagents only | `agents.defaults.subagents.model = "iblai-router/auto"` |
| Specific cron job | `"model": "iblai-router/auto"` in the cron job config |
| Per-session override | `/model iblai-router/auto` |

**Tip:** Keep your main interactive session on a fixed model (e.g. Opus) where latency and quality matter most. Use the router for cron jobs, subagents, and background tasks where cost savings compound.

---

## 3. Verifying Cost Savings

### Real-time: routing logs

```bash
journalctl -u iblai-router -f
```

Every request logs a line like:

```
[router] LIGHT  → haiku  | score=-0.112 conf=0.71 | scored     | -93% | what is 2+2? ...
[router] MEDIUM → sonnet | score=-0.040 conf=0.58 | ambiguous  | -80% | create an issue for the API bug ...
[router] HEAVY  → opus   | score=0.116  conf=0.95 | reasoning  |  -0% | prove sqrt(2) is irrational ...
```

The `-93%` / `-80%` / `-0%` is the savings vs always-Opus baseline for that request.

### Aggregate: stats endpoint

```bash
curl http://127.0.0.1:8402/stats
```

Returns:

```json
{
  "stats": {
    "total": 847,
    "byTier": { "LIGHT": 412, "MEDIUM": 340, "HEAVY": 95 },
    "estimatedCost": 0.0034,
    "baselineCost": 0.0189,
    "startedAt": "2026-02-16T20:36:34.000Z"
  }
}
```

- **`estimatedCost`**: what you actually spent (input tokens × model price)
- **`baselineCost`**: what Opus would have cost for the same traffic
- **Savings**: `1 - (estimatedCost / baselineCost)` → e.g. 82%

Note: these are input-cost estimates based on character count. Actual costs depend on output tokens too, which vary per response. For precise tracking, check your Anthropic dashboard.

### Expected savings profile

Based on typical agent workloads:

| Traffic mix | Tier | % of requests | Cost/M tokens |
|---|---|---|---|
| Simple queries, relays, alerts | LIGHT | ~45% | $1 |
| Issue creation, config, triage | MEDIUM | ~40% | $3 |
| Deep reasoning, architecture | HEAVY | ~15% | $15 |

**Blended average: ~$3.40/M** vs $15/M for always-Opus = **~77% savings**.

Actual savings depend on your workload. More relay/alert work = higher savings. More reasoning = lower savings.

### Cross-check with Anthropic billing

Compare your Anthropic usage dashboard before and after enabling the router. The model breakdown will show traffic shifting from a single model to a mix of Haiku/Sonnet/Opus.

---

## 4. Using Non-Anthropic Models

The router's scoring engine is model-agnostic — it classifies request complexity, not model capabilities. You can swap in models from any provider that speaks the Anthropic Messages API format (or use an adapter).

### OpenAI models via OpenRouter

[OpenRouter](https://openrouter.ai) exposes OpenAI, Google, and other models behind an Anthropic-compatible API. Point the router at OpenRouter instead of Anthropic:

```bash
# In iblai-router.service, change:
Environment=ANTHROPIC_API_KEY=sk-or-YOUR-OPENROUTER-KEY
```

Then update `config.json` with OpenRouter model IDs:

```json
{
  "models": {
    "LIGHT":  "openai/gpt-4.1-mini",
    "MEDIUM": "openai/gpt-4.1",
    "HEAVY":  "openai/o3"
  },
  "apiBaseUrl": "https://openrouter.ai/api/v1"
}
```

> **Note:** The `apiBaseUrl` field in config.json overrides the default `https://api.anthropic.com` target. The server will proxy requests to whichever base URL you specify.

### Google models via OpenRouter

```json
{
  "models": {
    "LIGHT":  "google/gemini-2.0-flash-lite",
    "MEDIUM": "google/gemini-2.5-flash",
    "HEAVY":  "google/gemini-2.5-pro"
  },
  "apiBaseUrl": "https://openrouter.ai/api/v1"
}
```

### Mixed-provider tiers

The most cost-effective setup often mixes providers. Use the cheapest model that handles each tier well:

```json
{
  "models": {
    "LIGHT":  "google/gemini-2.0-flash-lite",
    "MEDIUM": "anthropic/claude-sonnet-4-20250514",
    "HEAVY":  "openai/o3"
  },
  "apiBaseUrl": "https://openrouter.ai/api/v1"
}
```

When mixing providers via OpenRouter, all models must use OpenRouter model IDs (prefixed with provider name).

### Updating the systemd service

After changing providers, restart the router to pick up the new API key:

```bash
# Edit the service file with the new key
sudo systemctl daemon-reload
sudo systemctl restart iblai-router

# Verify routing targets
curl -s http://127.0.0.1:8402/health | jq .
```

The config.json changes (model IDs, apiBaseUrl) are hot-reloaded automatically — no restart needed for those.

---

## 5. Updating

When a new version is released, update your installation in one of three ways:

### Option A: Ask your OpenClaw agent (easiest)

> Update iblai-router to the latest version

Your agent will pull the latest code, restart the service, and confirm the new version is running.

### Option B: Git pull + restart

```bash
cd ~/.openclaw/workspace/router   # or wherever you cloned the repo
git pull origin main
sudo systemctl restart iblai-router
```

Verify the update:

```bash
curl -s http://127.0.0.1:8402/health | jq .
```

### Option C: Re-run the install script

```bash
cd ~/.openclaw/workspace/router
git pull origin main
bash scripts/install.sh
```

The install script is idempotent — it will update the systemd service, restart the router, and re-register the model provider if needed.

### What gets updated

- **`server.js`** — scoring engine, proxy logic, bug fixes
- **`config.json`** — new keywords, updated model IDs, tuned weights

> ⚠️ **If you've customized `config.json`** (added your own keywords, changed weights, swapped models), `git pull` will conflict. Either:
> - Stash your changes first: `git stash && git pull && git stash pop`
> - Or keep your config outside the repo: `ROUTER_CONFIG=/path/to/my-config.json` in the systemd service file. This way `git pull` never touches your config.

### Checking for updates

```bash
cd ~/.openclaw/workspace/router
git fetch origin
git log HEAD..origin/main --oneline
```

If there's output, a newer version is available. If empty, you're up to date.

### Release notes

Check [Releases](https://github.com/iblai/iblai-openclaw-router/releases) for changelogs and upgrade notes between versions.

---

## 6. Disabling the Router

### Temporarily (keep config, stop routing)

```bash
sudo systemctl stop iblai-router
```

Any OpenClaw workloads using `iblai-router/auto` will fail until you either restart the router or switch them to a direct model. To restart later:

```bash
sudo systemctl start iblai-router
```

### Switch specific workloads back to direct models

In your OpenClaw session:

```
# Revert a cron job to direct Sonnet
/cron update <jobId> model=anthropic/claude-sonnet-4-20250514

# Revert subagent default
/config set agents.defaults.subagents.model anthropic/claude-sonnet-4-20250514

# Revert main session
/model anthropic/claude-opus-4-20250514
```

### Fully remove

Ask your OpenClaw agent:

> Uninstall iblai-router

Or run it manually:

```bash
bash ~/.openclaw/workspace/router/scripts/uninstall.sh
```

Then remove the provider registration in your OpenClaw session:

```
/config unset models.providers.iblai-router
```

Make sure no cron jobs or agent configs still reference `iblai-router/auto` — they'll error on the next run.

---

## Files

```
├── server.js      # The proxy (~250 lines, zero deps)
├── config.json    # All scoring config (hot-reloaded on change)
└── README.md      # This file
```

## Troubleshooting

### `model not allowed: iblai-router/auto`

This usually means one of two things:

1. **Model allowlist**: If you have `agents.defaults.models` in your `openclaw.json` (used for cache settings or other per-model config), it acts as a **model allowlist**. You must add `iblai-router/auto` to it:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "iblai-router/auto": {},
        "anthropic/claude-opus-4.6": { ... }
      }
    }
  }
}
```

2. **Restart required**: OpenClaw caches available models at startup. After adding the provider to `openclaw.json`, restart OpenClaw (see Quick Start above).

If you've done both and still see the error, verify the provider block is in your `openclaw.json` under `models.providers.iblai-router` with `"api": "anthropic-messages"` and at least one model with `"id": "auto"`.

### Cron jobs stuck in error backoff

After fixing a model error, cron jobs may be in exponential backoff (up to 1 hour between retries). Force an immediate run:

```
/cron run <jobId>
```

Or from the API: trigger a manual run via the cron management endpoint.

### Router is running but requests fail

```bash
# Check the service is actually listening
curl -s http://127.0.0.1:8402/health

# Check logs for errors (wrong API key, network issues)
journalctl -u iblai-router -n 20

# Verify your Anthropic API key works
curl -s https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-haiku-20241022","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}' | jq .
```

### Config changes not taking effect

`config.json` changes (keywords, weights, boundaries, model IDs) are hot-reloaded — no restart needed. But changes to **environment variables** (API key, port) require a service restart:

```bash
sudo systemctl restart iblai-router
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | (required) | Your Anthropic API key |
| `ROUTER_PORT` | `8402` | Port to listen on |
| `ROUTER_LOG` | `1` | Set to `0` to disable per-request logging |
| `ROUTER_CONFIG` | `./config.json` | Path to scoring config file |
