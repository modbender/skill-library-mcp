---
name: superpack-snitch
version: 0.0.7
description: >
  Soft blocklist guard for OpenClaw. Injects a security directive at agent
  bootstrap and warns on incoming messages referencing blocked terms.
  Blocks clawhub/clawdhub by default.
metadata:
  openclaw:
    emoji: "🚨"
    events:
      - agent:bootstrap
      - message:received
---

# superpack-snitch

Prompt-based blocklist guard for OpenClaw with two enforcement hooks:

1. **Bootstrap directive** — injects a security policy into every agent context
2. **Message warning** — flags incoming messages referencing blocked terms

This is soft enforcement — it tells the agent not to use blocked tools, but
can't physically stop it. For hard blocking + Telegram alerts, see
[Want more?](#want-more) below.

## Install

Install from ClawHub. The hooks are included in the skill package.

## Configuration

### Hook blocklist (env var)

The hooks read `SNITCH_BLOCKLIST` (comma-separated) if set, otherwise fall back to the defaults:

```bash
SNITCH_BLOCKLIST=clawhub,clawdhub,myothertool
```

## What gets blocked

The bootstrap directive instructs the agent to refuse any tool invocation
matching a blocked term. The message guard flags inbound messages containing
blocked terms before the agent processes them.

Default blocked terms: `clawhub`, `clawdhub`

## Want more?

For hard enforcement (tool call interception, Telegram alerts), install the
plugin via npm:

```bash
openclaw plugins install superpack-snitch
```

The plugin adds a `before_tool_call` layer that physically blocks matching
tool calls and broadcasts alerts. See the
[README](https://github.com/rgr4y/superpack-snitch) for full details.

The skill and plugin can be used together for layered defense.
