---
name: guardrails-safe-tools
description: Enforces guarded execution with safe_exec, safe_send, and safe_action. Use when a task may run shell commands, send channel messages, or call external APIs/actions that can mutate data or state.
---

# Guardrails Safe Tools

## When to Use

Apply this skill whenever a request can:
- execute shell/system commands;
- send outbound messages/posts to channels;
- trigger external actions (email, DB, gateways, automation).

## Hard Rules

1. Use `safe_exec` instead of raw `exec`.
2. Use `safe_send` instead of direct channel-post tools.
3. Use `safe_action` for generic external/API side effects.
4. Never bypass the guardrails resolver with direct destructive tools.
5. If decision is `require_approval`, stop and wait for explicit approval flow.

## Input Hygiene

- Always provide the narrowest `cwd` for `safe_exec`.
- Include sender/channel/agent context when available.
- Keep command args explicit; do not hide risky flags in shell expansions.
- For `safe_action`, include explicit `resources` where possible.

## Tool Contracts

### `safe_exec`

Use for shell commands only after permission resolution.

Expected input shape:
```json
{
  "command": "git",
  "args": ["status"],
  "cwd": "/workspace/project"
}
```

### `safe_send`

Use for outbound channel messages.

Expected input shape:
```json
{
  "channel": "telegram:ops-room",
  "message": "Deployment done",
  "channelType": "telegram"
}
```

### `safe_action`

Use for side-effect actions that are not plain shell or plain chat send.

Expected input shape:
```json
{
  "action": "gmail.delete_message",
  "payload": { "messageId": "..." },
  "resources": [
    { "kind": "unknown", "value": "email-api", "operation": "delete" }
  ]
}
```

## Decision Handling

- `allow`: continue and return runtime result.
- `deny`: return denial with reason code; do not retry with alternate dangerous tools.
- `require_approval`: surface approval id/reason and wait for `/approve <id>` or RPC approval.

## Good Defaults

- Prefer read-only commands (`git status`, `rg`, `ls`) before mutable ones.
- Propose reversible operations first.
- Ask for confirmation before destructive intent, even if technically allowed.
