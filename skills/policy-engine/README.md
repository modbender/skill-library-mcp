# openclaw-policy-engine

**Deterministic governance layer for OpenClaw tool execution.**

An OpenClaw plugin that enforces allowlists, deny patterns, risk tiers, dry-run mode, and escalation tracking — providing a predictable, auditable policy layer between the LLM and tool execution.

## The Problem

LLM agents have tool access. Tools have side effects. Without governance, every tool call is implicitly trusted — the model decides what to run and when. This is fine for personal use with a trusted model, but becomes a liability when:

- Running multiple models (some less trusted than others)
- Exposing agents to external content (emails, web pages, group chats)
- Operating in environments where mistakes have consequences (production servers, messaging)
- You want an audit trail of what tools were invoked and why

## What This Plugin Does

Hooks into OpenClaw's `before_tool_call` lifecycle to evaluate every tool invocation against a declarative policy before execution.

### Evaluation Chain (v1.1)

```
1. Kill-switch (enabled=false → allow all)
2. Dry-run mode (essential/T0 tools pass, everything else stubbed)
3. Deny patterns (scoped to relevant params only)
4. Essential tool / T0 early exit (always allowed — prevents deadlock)
5. Allowlist check (per-profile tool lists)
6. Escalation counter (track blocked retries per session)
7. Default allow (if no rule matched)
```

Every decision is logged with tool name, tier, session ID, and result.

### Risk Tiers

| Tier | Description | Examples |
|------|-------------|----------|
| **T0** | Read-only, no side effects | `read`, `memory_search`, `memory_get`, `session_status` |
| **T1** | Moderate / controlled writes | `write`, `edit`, `message`, `browser`, `cron` |
| **T2** | Powerful / external effects | `exec`, `process`, `gateway`, `nodes` |

### Key Features

- **Allowlists** — per-profile lists of permitted tools
- **Deny patterns** — block specific argument patterns (e.g., `rm -rf`, `DROP TABLE`), scoped to relevant parameters only (command for exec, file_path for write/edit)
- **Dry-run mode** — stub non-essential tool calls for safe testing
- **Essential tools bypass** — `message`, `gateway`, `session_status`, `sessions_send`, `sessions_list`, `tts` always pass through to prevent agent deadlock
- **Escalation tracking** — counts consecutive blocked retries per session (1-hour TTL)
- **Break-glass** — `OPENCLAW_POLICY_BYPASS=1` env var overrides all policy (logged as warning)

## Three Deadlock Classes (Discovered & Fixed)

Building this plugin revealed three ways a policy engine can brick an agent:

1. **Dry-run blocks essential tools** — If `message` and `gateway` are stubbed, the agent can't communicate or recover. Fix: `dryRunEssentialTools` config always passes these through.

2. **Escalation counter blocks T0/essential tools** — After N blocked retries, if the counter blocks everything including read-only tools, the agent is stuck. Fix: Essential and T0 tools exit before the escalation check.

3. **Deny patterns match file content, not paths** — If deny patterns scan all parameters, writing a file that *discusses* dangerous commands (like this README) triggers a false positive. Fix: `TOOL_RELEVANT_PARAMS` scoping — exec checks `command`, write/edit checks `file_path`, unknown tools check all params.

## Installation

```bash
# Clone into your OpenClaw extensions directory
cd ~/.openclaw/extensions/
git clone https://github.com/joetomasone/openclaw-policy-engine.git policy-engine
cd policy-engine
npm install
```

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "policy-engine": {
        "enabled": true,
        "config": {
          "enabled": true,
          "dryRun": false,
          "maxBlockedRetries": 3,
          "allowlists": {
            "default": [
              "read", "write", "edit", "exec", "process",
              "message", "memory_search", "memory_get",
              "web_fetch", "browser", "gateway",
              "session_status", "sessions_list", "sessions_send",
              "sessions_spawn", "cron", "tts", "image",
              "nodes", "canvas", "agents_list",
              "sessions_history", "voice_call"
            ]
          }
        }
      }
    }
  }
}
```

## Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | boolean | `true` | Master switch |
| `dryRun` | boolean | `false` | Stub non-essential tool calls |
| `dryRunAllowT0` | boolean | `true` | Allow T0 (read-only) tools in dry-run |
| `dryRunEssentialTools` | string[] | `["message","gateway",...]` | Tools that bypass dry-run |
| `maxBlockedRetries` | number | `3` | Escalation counter threshold |
| `riskTiers` | object | (built-in defaults) | Override tool → tier mapping |
| `denyPatterns` | object | `{}` | Tool → blocked argument patterns |
| `allowlists` | object | `{}` | Profile → allowed tools |
| `routing` | object | `{}` | Agent → model/profile routing |

## Tests

```bash
npm test
```

73 tests covering the full evaluation chain, deadlock prevention, deny pattern scoping, escalation tracking, and dry-run mode.

## How It Was Built

- Architecture audit of OpenClaw source (48 questions about plugin system, hooks, config)
- V1 scope defined collaboratively between human + AI
- BUILD-SPEC.md pattern: detailed spec with TypeScript types → Claude Code (Opus) generated entire plugin in ~20 minutes
- 3 deadlock classes discovered and fixed during live testing
- Running in production since February 2026

## Complementary Work

- **[openclaw-provenance](https://github.com/zeroaltitude/openclaw-plugins/tree/main/openclaw-provenance)** by zeroaltitude — Taint-tracking provenance DAGs. Where this plugin governs *which tools* can be called, provenance tracks *what's in the context* when tools are called. The two are complementary: provenance provides trust classification, policy engine enforces restrictions.
- **[PR #6095](https://github.com/openclaw/openclaw/pull/6095)** — Upstream modular guardrails framework with content scanning + AI injection detection.

## License

MIT

## Author

Joe Tomasone ([@joetomasone](https://github.com/joetomasone)) with [Clawd](https://github.com/openclaw/openclaw) 🐾
