---
name: intelligent-router
description: Intelligent model routing for sub-agent task delegation. Choose the optimal model based on task complexity, cost, and capability requirements. Reduces costs by routing simple tasks to cheaper models while preserving quality for complex work.
version: 3.2.0
core: true
---

# Intelligent Router — Core Skill

> **CORE SKILL**: This skill is infrastructure, not guidance. Installation = enforcement.
> Run `bash skills/intelligent-router/install.sh` to activate.

## What It Does

Automatically classifies any task into a tier (SIMPLE/MEDIUM/COMPLEX/REASONING/CRITICAL)
and recommends the cheapest model that can handle it well.

**The problem it solves:** Without routing, every cron job and sub-agent defaults to Sonnet
(expensive). With routing, monitoring tasks use free local models, saving 80-95% on cost.

---

## MANDATORY Protocol (enforced via AGENTS.md)

### Before spawning any sub-agent:
```bash
python3 skills/intelligent-router/scripts/router.py classify "task description"
```

### Before creating any cron job:
```bash
python3 skills/intelligent-router/scripts/spawn_helper.py "task description"
# Outputs the exact model ID and payload snippet to use
```

### To validate a cron payload has model set:
```bash
python3 skills/intelligent-router/scripts/spawn_helper.py --validate '{"kind":"agentTurn","message":"..."}'
```

### ❌ VIOLATION (never do this):
```python
# Cron job without model = Sonnet default = expensive waste
{"kind": "agentTurn", "message": "check server..."}  # ← WRONG
```

### ✅ CORRECT:
```python
# Always specify model from router recommendation
{"kind": "agentTurn", "message": "check server...", "model": "ollama/glm-4.7-flash"}
```

---

## Tier System

| Tier | Use For | Primary Model | Cost |
|------|---------|---------------|------|
| 🟢 SIMPLE | Monitoring, heartbeat, checks, summaries | `anthropic-proxy-6/glm-4.7` (alt: proxy-4) | $0.50/M |
| 🟡 MEDIUM | Code fixes, patches, research, data analysis | `nvidia-nim/meta/llama-3.3-70b-instruct` | $0.40/M |
| 🟠 COMPLEX | Features, architecture, multi-file, debug | `anthropic/claude-sonnet-4-6` | $3/M |
| 🔵 REASONING | Proofs, formal logic, deep analysis | `nvidia-nim/moonshotai/kimi-k2-thinking` | $1/M |
| 🔴 CRITICAL | Security, production, high-stakes | `anthropic/claude-opus-4-6` | $5/M |

**SIMPLE fallback chain:** `anthropic-proxy-4/glm-4.7` → `nvidia-nim/qwen/qwen2.5-7b-instruct` ($0.15/M)

> ⚠️ **`ollama-gpu-server` is BLOCKED** for cron/spawn use. Ollama binds to `127.0.0.1` by default — unreachable over LAN from the OpenClaw host. The `router_policy.py` enforcer will reject any payload referencing it.

**Tier classification uses 4 capability signals (not cost alone):**
- `effective_params` (50%) — extracted from model ID or `known-model-params.json` for closed-source models
- `context_window` (20%) — larger = more capable
- `cost_input` (20%) — price as quality proxy (weak signal, last resort for unknown sizes)
- `reasoning_flag` (10%) — bonus for dedicated thinking specialists (R1, QwQ, Kimi-K2)

---

## Policy Enforcer (NEW in v3.2.0)

`router_policy.py` catches bad model assignments **before they are created**, not after they fail.

### Validate a cron payload before submitting
```bash
python3 skills/intelligent-router/scripts/router_policy.py check \
  '{"kind":"agentTurn","model":"ollama-gpu-server/glm-4.7-flash","message":"check server"}'
# Output: VIOLATION: Blocked model 'ollama-gpu-server/glm-4.7-flash'. Recommended: anthropic-proxy-6/glm-4.7
```

### Get enforced model recommendation for a task
```bash
python3 skills/intelligent-router/scripts/router_policy.py recommend "monitor alphastrike service"
# Output: Tier: SIMPLE  Model: anthropic-proxy-6/glm-4.7

python3 skills/intelligent-router/scripts/router_policy.py recommend "monitor alphastrike service" --alt
# Output: Tier: SIMPLE  Model: anthropic-proxy-4/glm-4.7  ← alternate key for load distribution
```

### Audit all existing cron jobs
```bash
python3 skills/intelligent-router/scripts/router_policy.py audit
# Scans all crons, reports any with blocked or missing models
```

### Show blocklist
```bash
python3 skills/intelligent-router/scripts/router_policy.py blocklist
```

### Policy rules enforced
1. **Model must be set** — no model field = Sonnet default = expensive waste
2. **No blocked models** — `ollama-gpu-server/*` and bare `ollama/*` are rejected for cron use
3. **CRITICAL tasks** — warns if using a non-Opus model for classified-critical work

---

## Installation (Core Skill Setup)

Run once to self-integrate into AGENTS.md:
```bash
bash skills/intelligent-router/install.sh
```

This patches AGENTS.md with the mandatory protocol so it's always in context.

---

## CLI Reference

```bash
# ── Policy enforcer (run before creating any cron/spawn) ──
python3 skills/intelligent-router/scripts/router_policy.py check '{"kind":"agentTurn","model":"...","message":"..."}'
python3 skills/intelligent-router/scripts/router_policy.py recommend "task description"
python3 skills/intelligent-router/scripts/router_policy.py recommend "task" --alt  # alternate proxy key
python3 skills/intelligent-router/scripts/router_policy.py audit     # scan all crons
python3 skills/intelligent-router/scripts/router_policy.py blocklist

# ── Core router ──
# Classify + recommend model
python3 skills/intelligent-router/scripts/router.py classify "task"

# Get model id only (for scripting)
python3 skills/intelligent-router/scripts/spawn_helper.py --model-only "task"

# Show spawn command
python3 skills/intelligent-router/scripts/spawn_helper.py "task"

# Validate cron payload has model set
python3 skills/intelligent-router/scripts/spawn_helper.py --validate '{"kind":"agentTurn","message":"..."}'

# List all models by tier
python3 skills/intelligent-router/scripts/router.py models

# Detailed scoring breakdown
python3 skills/intelligent-router/scripts/router.py score "task"

# Config health check
python3 skills/intelligent-router/scripts/router.py health

# Auto-discover working models (NEW)
python3 skills/intelligent-router/scripts/discover_models.py

# Auto-discover + update config
python3 skills/intelligent-router/scripts/discover_models.py --auto-update

# Test specific tier only
python3 skills/intelligent-router/scripts/discover_models.py --tier COMPLEX
```

---

## Scoring System

15-dimension weighted scoring (not just keywords):

1. **Reasoning markers** (0.18) — prove, theorem, derive
2. **Code presence** (0.15) — code blocks, file extensions
3. **Multi-step patterns** (0.12) — first...then, numbered lists
4. **Agentic task** (0.10) — run, fix, deploy, build
5. **Technical terms** (0.10) — architecture, security, protocol
6. **Token count** (0.08) — complexity from length
7. **Creative markers** (0.05) — story, compose, brainstorm
8. **Question complexity** (0.05) — multiple who/what/how
9. **Constraint count** (0.04) — must, require, exactly
10. **Imperative verbs** (0.03) — analyze, evaluate, audit
11. **Output format** (0.03) — json, table, markdown
12. **Simple indicators** (0.02) — check, get, show (inverted)
13. **Domain specificity** (0.02) — acronyms, dotted notation
14. **Reference complexity** (0.02) — "mentioned above"
15. **Negation complexity** (0.01) — not, never, except

Confidence: `1 / (1 + exp(-8 × (score - 0.5)))`

---

## Config

Models defined in `config.json`. Add new models there, router picks them up automatically.
Local Ollama models have zero cost — always prefer them for SIMPLE tasks.

---

## Auto-Discovery (Self-Healing)

The intelligent-router can **automatically discover working models** from all configured providers via **real live inference tests** (not config-existence checks).

### How It Works

1. **Provider Scanning:** Reads `~/.openclaw/openclaw.json` → finds all models
2. **Live Inference Test:** Sends `"hi"` to each model, checks it actually responds (catches auth failures, quota exhaustion, 404s, timeouts)
3. **OAuth Bypass:** Providers with `sk-ant-oat01-*` tokens (Anthropic OAuth) are skipped in raw HTTP — OpenClaw refreshes these transparently, so they're always marked available
4. **Thinking Model Support:** Models that return `content=None` + `reasoning_content` (GLM-4.7, Kimi-K2, Qwen3-thinking) are correctly detected as available
5. **Auto-Classification:** Tiers assigned via `tier_classifier.py` using 4 capability signals
6. **Config Update:** Removes unavailable models, rebuilds tier primaries from working set
7. **Cron:** Hourly refresh (cron id: `a8992c1f`) keeps model list current, alerts if availability changes by >2

### Usage

```bash
# One-time discovery
python3 skills/intelligent-router/scripts/discover_models.py

# Auto-update config with working models only
python3 skills/intelligent-router/scripts/discover_models.py --auto-update

# Set up hourly refresh cron
openclaw cron add --job '{
  "name": "Model Discovery Refresh",
  "schedule": {"kind": "every", "everyMs": 3600000},
  "payload": {
    "kind": "systemEvent",
    "text": "Run: bash skills/intelligent-router/scripts/auto_refresh_models.sh",
    "model": "ollama/glm-4.7-flash"
  }
}'
```

### Benefits

✅ **Self-healing:** Automatically removes broken models (e.g., expired OAuth)
✅ **Zero maintenance:** No manual model list updates
✅ **New models:** Auto-adds newly released models
✅ **Cost optimization:** Always uses cheapest working model per tier

### Discovery Output

Results saved to `skills/intelligent-router/discovered-models.json`:

```json
{
  "scan_timestamp": "2026-02-19T21:00:00",
  "total_models": 25,
  "available_models": 23,
  "unavailable_models": 2,
  "providers": {
    "anthropic": {
      "available": 2,
      "unavailable": 0,
      "models": [...]
    }
  }
}
```

### Pinning Models

To preserve a model even if it fails discovery:

```json
{
  "id": "special-model",
  "tier": "COMPLEX",
  "pinned": true  // Never remove during auto-update
}
```
