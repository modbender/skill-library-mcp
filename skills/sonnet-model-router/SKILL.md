---
name: model-router
description: Self-aware multi-provider model routing for OpenClaw. Auto-detects your available models, recommends the best routing mode, and adapts per task. Claude, Gemini, GPT, DeepSeek — benchmarks are routing tables, not leaderboards.
version: 2.2.0
homepage: https://github.com/chandika/openclaw-model-router
metadata: {"clawdbot":{"emoji":"🧭"}}
---

# Model Router for OpenClaw

Route the right model to the right job. Auto-detects what you have, tells you what to use, adapts when you say "work harder" or "save money."

## Security & Privacy

- **This skill does NOT read, store, or transmit API keys or credentials.** It only reads provider *names* and model IDs from your gateway config to determine what's available.
- **No automatic scanning.** All model detection and web searches are user-triggered only. The skill never runs on load or heartbeat unless you explicitly ask.
- **Web searches are used** to fetch public benchmark data and pricing from model card pages when you add a new provider. This is outbound network activity you should expect.
- **Local state:** The skill writes `model-registry.json` to your workspace (benchmark scores, pricing, routing rules). No secrets are stored in this file.

## Step 0: Model Registry (Self-Learning)

This skill maintains a **living model registry** at `model-registry.json` in the workspace. This is how the router learns about new models automatically.

### Registry File Format

```json
{
  "lastScan": "2026-02-18T08:00:00Z",
  "models": {
    "anthropic/claude-opus-4-6": {
      "provider": "anthropic",
      "name": "Claude Opus 4.6",
      "addedAt": "2026-02-18",
      "pricing": { "input": 15.00, "output": 75.00, "unit": "1M tokens" },
      "context": 200000,
      "strengths": ["deep reasoning", "novel problems", "hard search", "complex coding"],
      "weaknesses": ["expensive", "slower"],
      "benchmarks": {
        "swe-bench": 80.8,
        "osworld": 72.7,
        "arc-agi-2": 75.2,
        "gpqa-diamond": 74.5,
        "gdpval-aa": 1559,
        "hle": 26.3
      },
      "routeTo": ["architecture", "deep-debugging", "novel-reasoning", "hard-search"],
      "tier": "premium"
    }
  },
  "routingRules": {
    "computer-use": "anthropic/claude-sonnet-4-6",
    "deep-reasoning": "anthropic/claude-opus-4-6",
    "office-finance": "anthropic/claude-sonnet-4-6",
    "standard-coding": "anthropic/claude-sonnet-4-6",
    "drafts-summaries": "cheapest-available",
    "hard-coding": "anthropic/claude-opus-4-6"
  }
}
```

### New Model Detection Flow

**When to scan:** Only when the user explicitly asks (e.g., "check for new models," "scan models," "what models do I have"). Never on skill load. Never on heartbeat.

**How it works:**

1. **Read current config** — `gateway config.get` to get all configured providers and models
2. **Diff against registry** — compare config models vs `model-registry.json`
3. **For each NEW model found:**

   a. **Fetch the model card** — web search for `"[model name] benchmarks pricing model card [year]"`
   
   b. **Extract key data:**
      - Pricing (input/output per 1M tokens)
      - Context window size
      - Benchmark scores (prioritize: SWE-bench, OSWorld, GPQA, ARC-AGI-2, GDPval-AA, HLE, MATH-500)
      - Strengths and weaknesses from reviews
   
   c. **Classify the model** into a tier:
      - `premium` — $10+ per 1M input (Opus-class)
      - `mid` — $1-10 per 1M input (Sonnet, GPT-4o, Gemini Pro class)
      - `economy` — $0.10-1 per 1M input (Flash, DeepSeek class)
      - `free` — free tier or negligible cost
   
   d. **Determine routing slots** — based on benchmarks, where does this model beat existing options?
      - Compare each benchmark score against current best-in-slot
      - If new model beats current router choice on a benchmark by >3pts, flag it
      - If new model is cheaper AND within 2pts, flag it as cost-efficient alternative
   
   e. **Update registry** — write model entry to `model-registry.json`
   
   f. **Notify user:**
      ```
      🧭 New model detected: [model name]
      
      Provider: [provider]
      Pricing: $X input / $Y output per 1M tokens
      Context: [N] tokens
      Tier: [tier]
      
      Key benchmarks:
      - SWE-bench: XX% (current best: YY% from [model])
      - [other relevant benchmarks]
      
      Routing recommendation:
      - [task type]: This model beats [current model] by X points. Switch?
      - [task type]: Close to [current model] but 3× cheaper. Consider for subagents?
      
      Want me to update routing? Or keep current setup?
      ```

4. **Only apply changes with user permission.** Always ask first.

### Routing Rule Updates

When the user approves a routing change for a new model:

1. Update `model-registry.json` routing rules
2. Apply config via `gateway config.patch` if it's a permanent change
3. Log the change to daily memory file

When a model is **removed** from config:
1. Don't delete from registry (keep benchmark data for reference)
2. Re-route any tasks that pointed to the removed model → next best available
3. Notify user: "Model X was removed. Rerouted [task types] to [model Y]."

### Keeping Data Fresh

- **Benchmark data ages.** When a model entry is >90 days old, flag it for refresh on next scan.
- **New model versions.** If a model ID changes (e.g., `gemini-2.5-pro` → `gemini-3-pro`), treat the new one as a new model. Don't assume scores carry over.
- **Web search for updates.** When refreshing, search for `"[model name] latest benchmarks [current year]"` and update scores.

---

## Step 1: Detect What's Available

When the user asks to check models or set up routing, check the OpenClaw config to determine which providers and models are available:

1. Run `gateway config.get` or read `openclaw.json`
2. Check `agents.defaults.model.primary` — what's the current main model?
3. Check `agents.defaults.subagents.model` — what's the current subagent model?
4. Check which providers are configured (by provider name and model ID only — do not read or inspect API keys, tokens, or auth credentials)

5. Report to user: "You have [X, Y, Z] available. Currently running [model] main / [model] subagents. Recommended mode: [mode]. Want me to apply it?"

**Don't assume.** Check first, recommend second, apply only with permission.

## Step 2: Pick a Mode

Three modes. User picks one, or you recommend based on what's available.

### 🏆 Performance — "Work hard"

*Best results. Claude-only. Rate limits will feel it.*

| Role | Model | Cost/1M (in/out) |
|------|-------|-------------------|
| Main | Opus 4.6 | $15 / $75 |
| Subagents | Sonnet 4.6 | $3 / $15 |

**When to recommend:** User has Claude Max/API. Says "best quality," "don't cut corners," "work hard." Critical work — architecture, deep debugging, novel problems.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-opus-4-6" },
      "subagents": { "model": "anthropic/claude-sonnet-4-6" }
    }
  }
}
```

### ⚖️ Balanced — "Normal" (recommended default)

*Smart routing. Good quality. Rate limits survive the week.*

| Role | Model | Cost/1M (in/out) |
|------|-------|-------------------|
| Main | Sonnet 4.6 | $3 / $15 |
| Subagents | Gemini 2.5 Pro | $1.25 / $10 |

**When to recommend:** User has Claude + Google keys. Most daily work. Coding, research, content, office tasks. Sonnet handles main session perfectly; Gemini does background work at 2.4× less.

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-sonnet-4-6" },
      "subagents": { "model": "google/gemini-2.5-pro" }
    }
  }
}
```

**Variant — Claude + OpenAI:**
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "anthropic/claude-sonnet-4-6" },
      "subagents": { "model": "openai/gpt-4o" }
    }
  }
}
```

### 💰 Economy — "Save money"

*Minimum spend. High volume. Quality is good enough.*

| Role | Model | Cost/1M (in/out) |
|------|-------|-------------------|
| Main | Gemini 2.5 Pro | $1.25 / $10 |
| Subagents | Gemini 2.5 Flash | $0.18 / $0.75 |

**When to recommend:** User is API-only, high volume, cost constrained. Or says "save money," "be efficient," "economy mode."

```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "google/gemini-2.5-pro" },
      "subagents": { "model": "google/gemini-2.5-flash" }
    }
  }
}
```

**Ultra-economy variant (DeepSeek subagents):**
```json
{
  "agents": {
    "defaults": {
      "model": { "primary": "google/gemini-2.5-pro" },
      "subagents": { "model": "openrouter/deepseek/deepseek-v3.2" }
    }
  }
}
```

---

## Step 3: Adaptive Triggers

Listen for these signals and **suggest** mode changes (don't auto-apply):

| User Says | Action |
|-----------|--------|
| "work harder" / "try harder" / "best quality" | Suggest switching to Performance mode or `/model anthropic/claude-opus-4-6` for this session |
| "save money" / "be cheaper" / "economy" | Suggest switching to Economy mode |
| "normal" / "balanced" / "default" | Suggest switching to Balanced mode |
| "use opus for this" | Apply `/model anthropic/claude-opus-4-6` for current session only |
| "use gemini" / "use google" | Apply `/model google/gemini-2.5-pro` for current session only |
| "use deepseek" | Apply `/model openrouter/deepseek/deepseek-v3.2` for current session only |
| "reset" / "back to normal" | Apply `/model default` to revert to config default |

**Per-session vs permanent:** `/model X` changes the current session only. Config changes via `gateway config.patch` are permanent across sessions.

---

## Step 4: Task-Specific Hard Routes

Regardless of mode, some tasks have clear winners. **Override automatically** when the task type is obvious:

| Task Type | Always Use | Why | Override How |
|-----------|-----------|-----|-------------|
| Computer use / browser | Claude (Sonnet or Opus) | 72.5% OSWorld vs GPT's 38.2% — 34pt gap | If in economy mode using Gemini, warn user: "Computer use tasks perform significantly better on Claude. Switch for this task?" |
| Deep reasoning / novel problems | Opus 4.6 | 75.2% ARC-AGI-2 vs Sonnet's 58.3% — 17pt gap | Suggest Opus when the problem is genuinely novel or requires multi-step deduction |
| Office / financial / spreadsheets | Sonnet 4.6 | 1633 Elo GDPval-AA — beats Opus (1559) and GPT (1524) | Sonnet is actually the best here, even better than Opus |
| Simple drafts / summaries / formatting | Cheapest available | Don't burn premium tokens on grunt work | Route to subagent model or suggest DeepSeek |
| Coding (standard) | Sonnet 4.6 or Opus 4.6 | SWE-bench 79.6% / 80.8% — Claude dominates | Either Claude model; avoid GPT/Gemini for complex code |
| Coding (hard debugging, architecture) | Opus 4.6 | Terminal-Bench gap: 62.7% vs 59.1% | Suggest Opus for the hard 20% |

**The key insight:** Don't route everything through one model. Even within a session, suggest model switches when the task type changes significantly.

---

## Benchmark Tables

Cross-provider data, Feb 2026. This is your routing reference.

### How to Read These

Each row is a routing decision, not a ranking. A 2-point gap is noise — route by cost. A 17-point gap is signal — route by capability. A 34-point gap is a hard rule — never use the losing model for that task.

### Coding

| Benchmark | Sonnet 4.6 | Opus 4.6 | GPT-5.2 | Gemini 2.5 Pro |
|-----------|-----------|---------|---------|---------------|
| SWE-bench Verified | 79.6% | 80.8% | 77.0% | ~75% |
| Terminal-Bench 2.0 | 59.1% | 62.7% | 46.7% | — |

→ Claude territory. Sonnet for standard coding, Opus for hard debugging. GPT/Gemini lag 3-5pts.

### Computer Use

| Benchmark | Sonnet 4.6 | Opus 4.6 | GPT-5.2 |
|-----------|-----------|---------|---------|
| OSWorld-Verified | 72.5% | 72.7% | 38.2% |
| Pace Insurance | 94% | — | — |

→ **Hard rule.** Claude for all computer use. 34-point gap over GPT is not a preference — it's a different league.

### Reasoning

| Benchmark | Sonnet 4.6 | Opus 4.6 | GPT-5.2 |
|-----------|-----------|---------|---------|
| GPQA Diamond | 74.1% | 74.5% | 73.8% |
| ARC-AGI-2 | 58.3% | 75.2% | — |
| Humanity's Last Exam | 19.1% | 26.3% | 20.3% |
| MATH-500 | 97.8% | 97.6% | 97.4% |

→ GPQA and MATH: tied across all three — route by cost. ARC-AGI-2 and HLE: Opus only.

### Office & Domain

| Benchmark | Sonnet 4.6 | Opus 4.6 | GPT-5.2 |
|-----------|-----------|---------|---------|
| GDPval-AA (Office Elo) | **1633** | 1559 | 1524 |
| Finance Agent | **63.3%** | 62.0% | 60.7% |
| MCP-Atlas Tool Use | **61.3%** | 60.3% | — |

→ Sonnet's domain. Beats everything on office work, finance, and tool coordination. Even beats Opus.

### Pricing (per 1M tokens)

| Model | Input | Output | OpenClaw Provider | Relative |
|-------|-------|--------|-------------------|----------|
| DeepSeek V3.2 | $0.14 | $0.28 | `openrouter/deepseek/deepseek-v3.2` | 107× cheaper than Opus (in) |
| Gemini 2.5 Flash | $0.18 | $0.75 | `google/gemini-2.5-flash` | 100× cheaper than Opus (out) |
| Grok 4.1 Fast | $0.20 | $0.50 | `xai/grok-4.1-fast` | 75× cheaper than Opus (in) |
| Gemini 2.5 Pro | $1.25 | $10.00 | `google/gemini-2.5-pro` | 12× cheaper than Opus (in) |
| Sonnet 4.6 | $3.00 | $15.00 | `anthropic/claude-sonnet-4-6` | 5× cheaper than Opus |
| GPT-4o | $5.00 | $15.00 | `openai/gpt-4o` | 3× cheaper than Opus (in) |
| GPT-5.2 | — | — | `openai/gpt-5.2` | — |
| Opus 4.6 | $15.00 | $75.00 | `anthropic/claude-opus-4-6` | Baseline (most expensive) |

---

## Provider Detection

When checking what's available, use `gateway config.get` and look at the configured provider names and model IDs. **Do not read or inspect API keys, tokens, or auth credentials.** You only need to know *which providers are configured*, not how they authenticate.

Check `models.providers` in config for custom setups.

**Fallback logic:** If only Anthropic is available → recommend Performance mode. If Anthropic + Google → Balanced. If Google only → Economy. If everything → Balanced (best default).

---

## Prerequisites

- **OpenClaw v2026.2.17 or later** — required for Sonnet 4.6 in model registry
  - Docker: `docker pull openclaw/openclaw:latest`
  - Git: `openclaw update`
- **At least one provider** with auth configured
- For multi-provider modes: configure additional provider API keys in OpenClaw

---

## Switching Modes

**Per session:** `/model google/gemini-2.5-pro` → `/model default` to revert

**Permanently:** Ask agent to apply via `gateway config.patch`, or edit `openclaw.json` and restart

**Quick commands the agent should understand:**
- "Switch to performance mode" → apply Performance config
- "Switch to economy mode" → apply Economy config  
- "Go balanced" → apply Balanced config
- "Use opus for this" → `/model` session override only
- "Back to normal" → `/model default`

---

## Initial Registry Seed

On first run (no `model-registry.json` exists), the skill should:

1. Create `model-registry.json` with the benchmark data from the tables above
2. Scan current config to mark which models are actually available
3. Give the user a full status report:

```
🧭 Model Router initialized.

Available providers: Anthropic ✅, Google ✅, OpenAI ❌, xAI ❌
Available models: Opus 4.6, Sonnet 4.6, Gemini 2.5 Pro, Gemini 2.5 Flash

Current config: Opus main / Sonnet subagents (Performance mode)
Recommended: Balanced mode — Sonnet main / Gemini Pro subagents
  → Saves 2.4× on subagent costs, same quality for background tasks

Apply balanced mode? [yes/no]
```

4. Seed the registry with all models from the benchmark tables, even ones not currently configured
   — this gives the agent comparison data when new models appear later

---

## The Philosophy

Benchmarks are routing tables, not leaderboards. A 2-point gap is noise. A 34-point gap is a hard rule.

The right model for the job depends on the job. The skill's job is to know what you have, know what each model is good at, and route accordingly.

Give an agent a selection of models and a framework for choosing. It picks well. That's what this enables.
