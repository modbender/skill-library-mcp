# OpenClaw — Platform Reference

## Session Locations

Session transcripts are stored at:

```
~/.openclaw/agents/{agent-name}/sessions/
```

Each agent directory contains a `sessions/` folder with `.jsonl` transcript files and a `sessions.json` index.

The default agent is `main`, so most sessions live under:

```
~/.openclaw/agents/main/sessions/
```

## Session Index

`sessions.json` maps session keys to metadata:

```json
{
  "agent:main:main": {
    "sessionId": "433d5b15-...",
    "updatedAt": 1770193116233,
    "chatType": "direct",
    "lastChannel": "telegram",
    ...
  }
}
```

This file provides quick access to session IDs and last-updated timestamps without parsing JSONL files.

## Project Matching

OpenClaw organizes sessions by agent, not by project directory. To find project-relevant sessions:

1. List all `.jsonl` files in `~/.openclaw/agents/*/sessions/`
2. Read the first line of each file — it is a `session` header entry containing a `cwd` field
3. Match the `cwd` value against the user's project name (fuzzy, case-insensitive)
4. If `cwd` is absent or empty, fall back to scanning the first few user messages for project references

## JSONL Schema

Each line is a JSON object. Every entry has a `type` field.

### Entry Types

| Type | Description | Action |
|------|-------------|--------|
| `session` | Session header (first line) | **Read** for `cwd` and timestamp, then skip |
| `message` | User, assistant, or tool result message | **Keep** (filtered) |
| `model_change` | Model switch event | **Skip** |
| `thinking_level_change` | Thinking level adjustment | **Skip** |
| `custom` | Custom events (e.g., `model-snapshot`) | **Skip** |
| `compaction` | Compaction marker | **Skip** |

### Session Header

The first line of every JSONL file:

```json
{
  "type": "session",
  "version": "0.x.x",
  "id": "session-uuid",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "cwd": "/Users/.../project-dir"
}
```

The `cwd` field indicates which project directory was active when the session started.

### Message Entries

All messages share this structure:

```json
{
  "type": "message",
  "id": "unique-message-id",
  "parentId": "parent-message-id",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "message": {
    "role": "user" | "assistant" | "toolResult",
    "content": [ ... ]
  }
}
```

Note the key differences from Claude Code:
- **`parentId`** (camelCase) instead of `parentUuid`
- **`role: "toolResult"`** is a distinct role (not `user` with `tool_result` content blocks)
- Session metadata (cwd, version, etc.) lives in the `session` header, not on each message

### Content Block Types

**Text block:**
```json
{ "type": "text", "text": "Let's build the auth system..." }
```

**Thinking block:**
```json
{ "type": "thinking", "thinking": "Analyzing the requirements...", "signature": "..." }
```

**Tool call block:**
```json
{
  "type": "toolCall",
  "id": "toolu_vrtx_017xm...",
  "name": "web_search",
  "arguments": { "query": "JWT best practices", "count": 8 }
}
```

Note: OpenClaw uses `toolCall` (camelCase) with `arguments` instead of Claude Code's `tool_use` with `input`.

**Tool result messages** use `role: "toolResult"` with text content blocks:
```json
{
  "type": "message",
  "message": {
    "role": "toolResult",
    "content": [{ "type": "text", "text": "result output..." }]
  }
}
```

### Custom Entries

Custom entries have a `customType` field:

```json
{
  "type": "custom",
  "customType": "model-snapshot",
  "data": { "timestamp": "...", "provider": "...", "modelId": "..." }
}
```

Skip all custom entries — they contain internal state, not conversation content.

## Discovery Instructions

To find sessions for a project name like "eastore":

1. List all agent directories under `~/.openclaw/agents/`
2. For each agent, list `.jsonl` files in `sessions/`
3. Read the first line (`type: "session"`) to get the `cwd` field
4. Fuzzy-match `cwd` against the project name
5. Optionally check `sessions.json` for `updatedAt` timestamps to filter by time range

If the user doesn't specify an agent, scan all agents (most will only have `main`).

## Reading Strategy

For each `.jsonl` file in a matched session:

**Building the session index (Phase 2):**
1. Read line 1 (`type: "session"`) for `cwd` and `timestamp`
2. Find the first entry where `type === "message"` and `role === "user"` — extract text as "first user message"
3. Find the last few entries where `type === "message"` and `role === "user"` — extract text as "last user messages"
4. Get file modification time
5. Count lines as a size proxy

**Reading full transcripts (Phase 3):**
1. Parse each line as JSON
2. Skip entries where `type` is not `message`
3. For `role === "user"` with text content → keep (my human's words)
4. For `role === "assistant"` with text content → keep (my words)
5. For `role === "assistant"` with `thinking` content → skip
6. For `role === "assistant"` with `toolCall` content → keep only `name` and the relevant path/query from `arguments`. Drop the full arguments body.
7. For `role === "toolResult"` → skip the body, but note if the text contains error indicators ("error", "Error", "failed", "FAILED")
