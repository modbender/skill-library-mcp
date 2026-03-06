---
name: zeroapi
version: 2.3.0
description: >
  Route tasks to the best AI model across paid subscriptions (Claude, ChatGPT,
  Codex, Gemini, Kimi) via OpenClaw gateway. Use when user mentions model routing,
  multi-model setup, "use Codex for this", "delegate to Gemini", "route to the
  best model", agent delegation, or has OpenClaw agents configured with multiple
  providers. Do NOT use for single-model conversations or general chat.
homepage: https://github.com/dorukardahan/ZeroAPI
user-invocable: true
compatibility: Requires OpenClaw 2026.2.6+ with at least one AI subscription. Bootstrap budget config requires 2026.2.14+.
metadata: {"openclaw":{"emoji":"⚡","category":"routing","os":["darwin","linux"],"requires":{"anyBins":["openclaw","claude"],"config":["agents"]}}}
---

# ZeroAPI — Subscription-Based Model Routing

Route incoming tasks to the optimal AI model across available providers. OpenClaw handles all API connections — this skill defines the classification and delegation logic. Classify each task by type and delegate to the appropriate agent/model.

## First-Time Setup

When this skill is first loaded, determine the user's available providers:

1. Ask: "Which AI subscriptions do you have?" (Claude Max 5x/20x, ChatGPT Plus/Pro, Gemini Advanced, Kimi)
2. Map subscriptions to available tiers (see table below)
3. Disable tiers for missing providers — those decision steps get skipped
4. Confirm the active configuration with the user

If only Claude is available, all tasks stay on Opus. No routing needed — but conflict resolution and collaboration patterns still apply for judging task complexity.

To verify providers are actually working after setup, ask the user to run:
```bash
openclaw models status
```
Any model showing `missing` or `auth_expired` is not usable. Remove it from your active tiers until the user fixes it.

For full provider configuration details, consult `references/provider-config.md` (in the same directory as this SKILL.md).

## Model Tiers

| Tier | Model | OpenClaw ID | Speed | TTFT | Intelligence | Context | Best At |
|------|-------|-------------|-------|------|-------------|---------|---------|
| SIMPLE | Gemini 2.5 Flash-Lite | `google-gemini-cli/gemini-2.5-flash-lite` | 495 tok/s | 0.23s | 21.6 | 1M | Low-latency pings, trivial format tasks |
| FAST | Gemini 3 Flash | `google-gemini-cli/gemini-3-flash-preview` | 206 tok/s | 12.75s | 46.4 | 1M | Instruction following, structured output, heartbeats |
| RESEARCH | Gemini 3 Pro | `google-gemini-cli/gemini-3-pro-preview` | 131 tok/s | 29.59s | 48.4 | 1M | Scientific research, long context analysis |
| CODE | GPT-5.3 Codex | `openai-codex/gpt-5.3-codex` | 113 tok/s | 20.00s | 51.5 | 200K | Code generation, math (99.0) |
| DEEP | Claude Opus 4.6 | `anthropic/claude-opus-4-6` | 67 tok/s | 1.76s | 53.0 | 200K | Reasoning, planning, judgment |
| ORCHESTRATE | Kimi K2.5 | `kimi-coding/k2p5` | 39 tok/s | 1.65s | 46.7 | 128K | Multi-agent orchestration (TAU-2: 0.959) |

**Key benchmark scores** (higher = better):
- **GPQA** (science): Gemini Pro 0.908, Opus 0.769, Codex 0.738*
- **Coding** (SWE-bench): Codex 49.3*, Opus 43.3, Gemini Pro 35.1
- **Math** (AIME '25): Codex 99.0*, Gemini Flash 97.0, Opus 54.0
- **IFBench** (instruction following): Gemini Flash 0.780, Opus 0.639, Codex 0.590*
- **TAU-2** (agentic tool use): Kimi K2.5 0.959, Codex 0.811*, Opus 0.780

Scores marked with * are estimated from vendor reports, not independently verified. Source: Artificial Analysis API v4, February 2026. Structured data in `benchmarks.json`.

## Decision Algorithm

Walk through these 9 steps IN ORDER for every incoming task. The FIRST match wins. If a required model is unavailable, skip that step and continue to the next.

**Estimating token count for Step 1**: Count characters in the input and divide by 4. 100k tokens ≈ 400,000 characters. If the user pastes a large file, codebase, or says "analyze this entire repo," assume it exceeds 100k.

| Step | Signals | Route to | Fallbacks |
|------|---------|----------|-----------|
| 1. Context >100k tokens | large file, long document, bulk, CSV, log dump, entire codebase, "analyze this PDF" | RESEARCH (Pro, 1M ctx) | Opus (200K) |
| 2. Math / proof | calculate, solve, equation, proof, integral, probability, optimize, formula | CODE (Codex, Math 99.0) | Flash (97.0), Opus |
| 3. Code writing | write code, implement, function, class, refactor, script, migration, test, PR, diff | CODE (Codex, Coding 49.3) | Opus |
| 4. Code review / architecture | review, audit, architecture, design, trade-off, security review, best practice | DEEP (Opus, Intel 53.0) | stays on main |
| 5. Speed critical / trivial | quick, fast, simple, format, convert, summarize, list, extract, translate, one-liner | FAST (Flash, 206 tok/s) | Flash-Lite, Opus |
| 6. Research / scientific | research, find out, explain, compare, analyze, paper, evidence, fact-check, deep dive | RESEARCH (Pro, GPQA 0.908) | Opus |
| 7. Multi-step tool pipeline | orchestrate, coordinate, pipeline, workflow, chain, parallel, fan-out | ORCHESTRATE (Kimi, TAU-2 0.959) | Codex, Opus |
| 8. Structured output | follow rules exactly, JSON schema, strict template, structured, checklist, table | FAST (Flash, IFBench 0.780) | Opus |
| 9. Default | no clear match | DEEP (Opus, Intel 53.0) | safest all-rounder |

**Step 5 note**: For sub-second TTFT needs (pings, health checks), use SIMPLE (Flash-Lite, 0.23s TTFT). For heartbeats and cron jobs, use FAST (Flash) — better instruction following (IFBench 0.780).

### Disambiguation Examples

When a task matches multiple steps:
- "Analyze this 200-page PDF and write a Python parser for it" -- Step 1 wins (context size), route to RESEARCH. Then delegate code writing to CODE as a follow-up.
- "Quickly solve this integral" -- Step 2 wins over Step 5 (math trumps speed).
- "Generate a JSON schema for this API" -- Step 8 wins (structured output, not code writing).
- "Review this code and refactor the authentication module" -- Step 4 wins for review, then Step 3 for the refactor (delegate to CODE).

## When NOT to Route

Do NOT route away from the current model when:

1. **User explicitly requests a model.** "Use Opus for this" or "don't delegate this" — always respect direct instructions.
2. **Security-sensitive tasks.** If the task involves credentials, private keys, secrets, or personally identifiable data, keep it on the main agent. Do not send sensitive content to sub-agents.
3. **Debugging a specific model.** If the user is testing or comparing model behavior, route to the model they specify.
4. **Mid-conversation continuity.** In a multi-turn conversation where the user asks a quick follow-up, do not switch models just because the follow-up is "simple." Stay on the current model for context continuity unless the user explicitly asks to delegate.

## Conflict Resolution

When multiple steps seem to match, resolve with these priority rules:

1. **Judgment trumps speed.** If the task has ambiguity, nuance, or risk — stay on Opus.
2. **Specialist trumps generalist.** If a model has a standout benchmark for the exact task type, prefer it.
3. **Code writing -- Codex. Code review -- Opus.** Different models for writing vs judging.
4. **Context overflow -- Gemini.** Only Gemini models handle 1M context.
5. **TTFT matters for interactive tasks.** Flash-Lite (0.23s), Kimi (1.65s), and Opus (1.76s) respond fast. Codex (20s) and Pro (29.59s) are slow to start — don't use them for quick back-and-forth.
6. **When truly tied -- Opus.** Highest general intelligence, lowest risk of subtle errors.

## Sub-Agent Delegation

Use OpenClaw's agent system to delegate:

```text
/agent <agent-id> <instruction>
```

1. You send `/agent codex <instruction>` — OpenClaw spawns the sub-agent with that instruction.
2. The sub-agent runs in its own workspace and returns a text response.
3. Sub-agents do NOT share your conversation context or workspace files. Pass ALL necessary context in the instruction.

**What to pass**: The specific task, relevant code snippets, output format expectations, and constraints.

### Examples

```text
/agent codex Write a Python function that parses RFC 3339 timestamps with timezone support. Return only the code.

/agent gemini-researcher Analyze the differences between SQLite WAL mode and journal mode. Include benchmarks and a recommendation.

/agent gemini-fast Convert the following list into a markdown table with columns: Name, Role, Status.

/agent kimi-orchestrator Coordinate: (1) gemini-researcher gathers data on X, (2) codex writes a parser, (3) report results.
```

## Error Handling and Retries

1. **Timeout** (no response within 60s): Retry once on same model. If it fails again, fall to next fallback.
2. **Auth error** (401/403): Do NOT retry — fall to next fallback immediately and tell user to re-authenticate. See `references/oauth-setup.md`.
3. **Rate limit** (429): Wait 30 seconds, retry once. If still limited, fall to next fallback.
4. **Partial/garbage response**: Retry once. If still broken, fall to next fallback.
5. **Model unavailable**: Skip that tier entirely and continue.

**Maximum retries**: 1 retry on same model, then next fallback. If ALL fallbacks fail, stay on Opus. Never retry more than 3 times total across all fallbacks.

When a fallback is triggered, briefly inform the user:
> "Codex is unavailable, routing to Opus instead."

## Multi-Turn Conversation Routing

- **Stay on the same model** for follow-up messages in the same topic. Context continuity matters more than optimal model selection.
- **Re-route only when the task type clearly changes.** Example: user discusses architecture (Opus) -- then says "now write the implementation" -- delegate code writing to Codex.

When switching models mid-conversation:
1. Summarize the relevant context from the current conversation.
2. Pass that summary as part of the delegation instruction.
3. Continue on the original model (Opus) with awareness of what the sub-agent produced.

## Workspace Isolation

- Sub-agents cannot read your files — paste content into the instruction.
- Sub-agents cannot write to your workspace — output comes back as text.
- Sub-agents share nothing with each other — complete isolation by design.

## Collaboration Patterns

| Pattern | Flow | Use when |
|---------|------|----------|
| Pipeline | Research Agent -- Main Agent -- Code Agent | Task requires gathering facts before implementing |
| Parallel + Merge | Main spawns Code (approach A) + Research (approach B), then merges | Exploring multiple solutions or under time pressure |
| Adversarial Review | Code Agent writes -- Main critiques -- Code revises | Security-sensitive or production-critical code |
| Orchestrated (Kimi) | `/agent kimi-orchestrator Plan and execute: <task>` | 3+ agents in complex dependency graphs (Kimi: slowest at 39 tok/s, best at TAU-2 0.959) |
Choose this for tasks requiring 3+ agents in complex dependency graphs. Caution: Kimi is slowest (39 tok/s) but best at tool orchestration (TAU-2: 0.959).

## Fallback Chains

When a model is unavailable or rate-limited, fall through in reliability order.

### Full Stack (4 providers)
| Task Type | Primary | Fallback 1 | Fallback 2 | Fallback 3 |
|-----------|---------|------------|------------|------------|
| Reasoning | Opus | Gemini Pro | Codex | Kimi K2.5 |
| Code | Codex | Opus | Gemini Pro | Kimi K2.5 |
| Research | Gemini Pro | Opus | Codex | Kimi K2.5 |
| Fast tasks | Flash-Lite | Flash | Opus | Codex |
| Agentic | Kimi K2.5 | Codex | Gemini Pro | Opus |

**Important**: Always use cross-provider fallbacks. Same-provider fallbacks (e.g., Gemini Pro -- Flash) help with model-specific issues but not provider outages. Every fallback chain should span at least 2 different providers.

### Claude + Gemini (2 providers)
| Task Type | Primary | Fallback 1 | Fallback 2 |
|-----------|---------|------------|------------|
| Reasoning | Opus | Gemini Pro | — |
| Code | Opus | Gemini Pro | — |
| Research | Gemini Pro | Opus | — |
| Fast tasks | Flash-Lite | Flash | Opus |

### Claude + Codex (2 providers)
| Task Type | Primary | Fallback 1 |
|-----------|---------|------------|
| Reasoning | Opus | Codex |
| Code | Codex | Opus |
| Everything else | Opus | Codex |

### Claude Only (1 provider)
All tasks route to Opus. No fallback needed.

## Provider Setup

For auth setup, OAuth flows (including headless VPS), and multi-device safety details, consult `references/oauth-setup.md` (in the same directory as this SKILL.md).

For provider configuration (openclaw.json, per-agent models.json, Google Gemini workarounds), consult `references/provider-config.md`.

Quick reference:

| Provider | Auth Method | Maintenance |
|----------|-----------|-------------|
| Anthropic | Setup-token (OAuth) | Low — auto-refresh |
| Google Gemini | OAuth (CLI plugin) | Very low — long-lived tokens |
| OpenAI Codex | OAuth (ChatGPT PKCE) | Low — auto-refresh |
| Kimi | Static API key | None — never expires |

## Troubleshooting

For detailed troubleshooting, consult `references/troubleshooting.md` (in the same directory as this SKILL.md). Common issues:

- **"No API provider registered for api: undefined"** -- Missing `api` field in provider config
- **"API key not valid" with Gemini subscription** -- Wrong API type; use `google-gemini-cli` not `google-generative-ai`
- **Model shows `missing`** -- Model ID mismatch; `gemini-2.5-flash-lite` (no `-preview` suffix)
- **Codex 401 Unauthorized** -- Token expired; re-run OAuth flow via `references/oauth-setup.md`
- **Sub-agent "Unknown model"** -- Provider missing from sub-agent's auth-profile

## Cost Summary

| Setup | Monthly | Notes |
|-------|---------|-------|
| **Claude only** (Max 5x) | $100 | No routing, Opus handles everything |
| **Claude only** (Max 20x) | $200 | No routing, 20x rate limits |
| **Balanced** (Max 20x + Gemini) | $220 | Adds Flash speed + Pro research |
| **Code-focused** (+ ChatGPT Plus) | $240 | Adds Codex for code + math |
| **Full stack** (all 4, ChatGPT Plus) | $250 | Full specialization |
| **Full stack Pro** (all 4, ChatGPT Pro) | $430 | Maximum rate limits |

Source: Artificial Analysis API v4, February 2026. Codex scores estimated (*) from OpenAI blog data. Structured benchmark data available in `references/benchmarks.json`.

## References

| File | Content |
|------|---------|
| [references/oauth-setup.md](references/oauth-setup.md) | Auth setup, OAuth flows, multi-device safety |
| [references/provider-config.md](references/provider-config.md) | openclaw.json, per-agent models.json, Gemini workarounds |
| [references/troubleshooting.md](references/troubleshooting.md) | Common errors and fixes |
| [references/benchmarks.json](references/benchmarks.json) | Raw benchmark data for all models |
