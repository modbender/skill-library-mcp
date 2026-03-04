---
name: policy-engine
description: >
  Deterministic governance layer for OpenClaw tool execution. Enforces tool
  allowlists, deny patterns, path allowlists, risk tiers, dry-run mode, and
  escalation tracking via the before_tool_call hook. Every decision is logged
  for audit. Production-hardened with 88 tests and three deadlock classes fixed.
tags: [security, governance, policy, tools, audit]
type: plugin
---

# Policy Engine

A deterministic governance layer that hooks into `before_tool_call` to control which tools agents can use, block dangerous commands, enforce write-path restrictions, and audit every decision.

## Installation

```bash
clawhub install policy-engine
```

Then enable in your `openclaw.json`:

```jsonc
{
  "plugins": {
    "policy-engine": {
      "enabled": true
    }
  }
}
```

## Quick Start

Minimal restrictive config — limit a sub-agent to read-only tools:

```jsonc
{
  "plugins": {
    "policy-engine": {
      "enabled": true,
      "allowlists": {
        "readonly": ["read", "web_fetch", "web_search", "message"]
      },
      "routing": {
        "research-agent": { "toolProfile": "readonly" }
      }
    }
  }
}
```

## Features

### Tool Allowlists
Per-agent profiles controlling which tools are permitted. Assign profiles via `routing` rules keyed by agent ID.

### Deny Patterns
Built-in patterns block fork bombs, `rm -rf`, `mkfs`, disk wipes, and system path writes. Scoped matching checks only relevant params (e.g., `command` for exec, `path` for write) — never file content. Add custom patterns per tool.

### Path Allowlist Enforcement
Canonicalizes file paths via `path.resolve()` then checks against allowed directory prefixes. Prevents path traversal attacks (e.g., `../../etc/passwd`) even via prompt injection.

```jsonc
{
  "pathAllowlists": {
    "write": ["/Users/joe/.openclaw/workspace"],
    "edit": ["/Users/joe/.openclaw/workspace"]
  }
}
```

With this config, `write` to `/Users/joe/.openclaw/workspace/foo.txt` → allowed. `write` to `/Users/joe/.openclaw/workspace/../../etc/hosts` → **blocked** (resolves to `/Users/joe/etc/hosts`, outside prefix).

### Risk Tiers
- **T0** — read-only (read, web_fetch, search) — always allowed, even under escalation
- **T1** — write (write, edit, message)
- **T2** — exec/system (exec, browser, deploy)

Override with `riskTiers` map:

```jsonc
{ "riskTiers": { "my_custom_tool": "T2" } }
```

### Dry-Run Mode
Test policies without blocking. Essential tools (message, gateway, session_status) always pass through to prevent agent deadlock.

```jsonc
{ "dryRun": true, "dryRunAllowT0": true }
```

### Escalation Tracking
Counts blocked attempts per session. After `maxBlockedRetries` (default: 3), further non-essential calls are blocked with a remediation message.

### Hot-Reload
Config changes via `gateway config.patch` take effect immediately — no restart needed.

### Fail-Open on Error
If the engine itself throws, the tool call proceeds. Safety over availability of governance.

### Break-Glass
Set `OPENCLAW_POLICY_BYPASS=1` to bypass all checks. Logged as a warning for audit.

## Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `true` | Global kill-switch |
| `dryRun` | boolean | `false` | Log-only mode (no blocking) |
| `dryRunAllowT0` | boolean | `true` | Allow T0 tools in dry-run |
| `dryRunEssentialTools` | string[] | `[message, gateway, session_status, sessions_send, sessions_list, tts]` | Tools that always pass in dry-run |
| `maxBlockedRetries` | number | `3` | Escalation threshold per session |
| `riskTiers` | object | `{}` | Tool → "T0"\|"T1"\|"T2" overrides |
| `denyPatterns` | object | `{}` | Tool → string[] of blocked argument patterns |
| `allowlists` | object | `{}` | Profile → string[] of allowed tool names |
| `routing` | object | `{}` | AgentId → `{ model?, toolProfile? }` |
| `pathAllowlists` | object | `{}` | Tool → string[] of allowed directory prefixes |

## Common Patterns

### Restrictive Sub-Agent

```jsonc
{
  "allowlists": {
    "researcher": ["read", "web_fetch", "web_search", "message"],
    "coder": ["read", "write", "edit", "exec", "message"]
  },
  "routing": {
    "research-bot": { "toolProfile": "researcher" },
    "code-bot": { "toolProfile": "coder" }
  }
}
```

### Block Dangerous Commands + Custom Patterns

```jsonc
{
  "denyPatterns": {
    "exec": ["npm publish", "docker push"],
    "write": ["/secrets/", "/credentials/"]
  }
}
```

### Dry-Run Testing

Enable dry-run to see what *would* be blocked before enforcing:

```jsonc
{ "dryRun": true }
```

Check logs for `[policy-engine] DRYRUN` entries, then disable when satisfied.

### Per-Agent Model Routing

```jsonc
{
  "routing": {
    "cheap-tasks": { "model": "ollama/qwen2.5:latest" },
    "complex-tasks": { "model": "anthropic/claude-opus-4", "toolProfile": "full" }
  }
}
```

## Slash Command

The plugin registers a `/policy` command:
- `/policy status` — show current config and session stats
- `/policy reset` — reset escalation counters

## Architecture

See [DESIGN.md](DESIGN.md) for detailed design decisions, deadlock analysis, and the three deadlock classes that were discovered and fixed during development.
