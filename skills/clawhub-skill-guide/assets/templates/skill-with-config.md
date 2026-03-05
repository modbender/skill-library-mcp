---
name: SKILL_NAME
description: >
  DESCRIPTION of what this skill does. Include specific trigger keywords
  and scenarios. Use when: scenario1, scenario2, scenario3.
metadata:
  openclaw:
    env:
      - name: ENV_VAR_NAME
        description: "What this environment variable is for"
        required: false
---

# Skill Title

Brief overview of what this skill provides.

## Prerequisites

**All config changes require manual review. Nothing is applied automatically.**

| Requirement | Details |
|-------------|---------|
| Discord bot token | Configured in your OpenClaw gateway (not stored by this skill) |
| Guild (server) | You create or choose the server. You provide the guild ID. |
| Gateway admin access | You manually review and apply config changes |
| `ENV_VAR_NAME` | Optional. Description of this variable. |

## Security Notes

- All gateway config changes are **generated as templates for your review**
- No config is applied automatically by this skill
- Scripts only write within the skill workspace directory
- Scripts make no network calls and contain no obfuscation
- **Inspect scripts before running**

## Security Model

The agent using this skill MUST run as a **separate OpenClaw agent** with
restricted permissions:

- `tools.fs.workspaceOnly: true` — can only read/write within skill workspace
- `tools.exec.security: "deny"` — cannot execute shell commands
- `tools.deny` list blocking all unnecessary tools
- `tools.profile: "messaging"` — only messaging + web search

This ensures:
- No access to the owner's personal files, messages, or other agents
- No ability to send emails, read calendars, or access other services
- Even if a user attempts prompt injection, there is nothing to exfiltrate

## Config Template

**Review and apply manually** via your gateway configuration.

**Agent entry** (add to `agents.list` array):
```json
{
  "id": "skill-agent",
  "name": "Skill Agent",
  "workspace": "/path/to/skill/workspace",
  "model": { "primary": "anthropic/claude-sonnet-4-6" },
  "tools": {
    "profile": "messaging",
    "deny": ["exec", "process", "nodes", "cron", "gateway", "browser",
             "canvas", "sessions_spawn", "sessions_send", "memory_search"],
    "exec": { "security": "deny" },
    "fs": { "workspaceOnly": true }
  }
}
```

**Binding entry** (add to `bindings` BEFORE catch-all):
```json
{ "agentId": "skill-agent", "match": { "channel": "discord", "guildId": "YOUR_GUILD_ID" } }
```

**Guild entry** (safe to merge via `config.patch`):
```json
{ "channels": { "discord": { "guilds": { "YOUR_GUILD_ID": { "requireMention": true, "channels": { "*": { "allow": true } } } } } } }
```

**Important:** `agents.list` and `bindings` are arrays — `config.patch` replaces
them entirely. Include ALL existing agents/bindings plus the new entries.

## Quick Start

1. Review prerequisites and set environment variables
2. Review and apply the config template above (manual review required)
3. Start using the skill in the configured channel

## How It Works

Core instructions and workflows.

## File Reference

| File | Purpose |
|------|---------|
| `SKILL.md` | Core instructions (this file) |
