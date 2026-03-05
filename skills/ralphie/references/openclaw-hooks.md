# OpenClaw hooks for reliable logging

## Goal

Use hooks so every inbound and outbound message is logged to Clawboard with no gaps.

## Recommended: Clawboard logger plugin

This repo ships a plugin at `extensions/clawboard-logger` that registers agent-loop hooks
for `message_received`, `message_sent`, `before_tool_call`, `after_tool_call`, and `agent_end`.

Install (linked for development):

```
openclaw plugins install -l /path/to/clawboard/extensions/clawboard-logger
openclaw plugins enable clawboard-logger
```

Set config with the Clawboard base URL + token.

Implementation note (code path):
- The plugin uses `api.on(<hookName>, handler)` to register hooks (see OpenClaw plugin SDK).
- Hook event names and payloads are defined in `src/plugins/types.ts` in the OpenClaw repo.

## Hook locations (internal hooks)

Internal hooks are discovered from:

- `<workspace>/hooks/` (per-agent, highest precedence)
- `~/.openclaw/hooks/` (managed/shared)

## CLI workflow

- List hooks: `openclaw hooks list`
- Enable: `openclaw hooks enable <hook-id>`
- Disable: `openclaw hooks disable <hook-id>`
- Install hook pack: `openclaw hooks install <path-or-spec>` (use `-l` to link a local dir)

Note: Plugin-managed hooks appear as `plugin:<id>` and must be enabled by enabling the plugin, not via `openclaw hooks enable`.

## Plugin hook events (best for “never miss” logging)

Use plugin hooks for message and tool events inside the agent loop:

- `message_received`
- `message_sending`
- `message_sent`
- `before_tool_call`
- `after_tool_call`
- `agent_end`

These run inside the agent loop and can emit log events for every turn.

## Internal hook events (gateway)

- `command:new`, `command:reset`, `command:stop`
- `agent:bootstrap`
- `gateway:startup`

## Logging policy

For each event, post to Clawboard immediately:

- `conversation` for message_received/message_sent
- `action` for tool calls and agent_end summaries

Include:

- `summary`: 1–2 line summary of the message
- `raw`: full prompt/response
- `agentId`, `agentLabel`, `sessionKey`, `messageId` if available

If Clawboard is unreachable, queue to disk and retry on the next event.
