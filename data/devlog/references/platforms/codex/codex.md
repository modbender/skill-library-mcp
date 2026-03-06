# Codex — Platform Reference

## Session Locations

Session transcripts (rollout files) are stored in date-partitioned directories:

```
~/.codex/sessions/YYYY/MM/DD/rollout-{timestamp}-{threadId}.jsonl
```

The base directory defaults to `~/.codex` but can be overridden via the `CODEX_HOME` environment variable.

Archived sessions are moved to:

```
~/.codex/archived_sessions/
```

A supplemental global history file exists at `~/.codex/history.jsonl` containing per-message summaries (`{conversation_id, ts, text}`), but it is **not** used for transcript reconstruction — rollout files are authoritative.

## File Naming

Rollout filenames follow this pattern:

```
rollout-YYYY-MM-DDThh-mm-ss-{uuid}.jsonl
```

- The timestamp uses ISO 8601 format with hyphens replacing colons (filesystem-safe)
- The UUID is a standard UUID-4 thread identifier
- Example: `rollout-2025-05-07T17-24-21-5973b6c0-94b8-487b-a530-2aeb6098ae0e.jsonl`

## Project Matching

Codex identifies project context through the `cwd` field in each session's metadata line. To find sessions for a project:

1. Walk the `sessions/YYYY/MM/DD/` directory tree
2. Read the first line of each rollout file (`session_meta` type) to get the `cwd` field
3. Fuzzy-match the project name against the `cwd` path (case-insensitive)
4. Optionally check the `git` field for `repository_url` or `branch` to disambiguate

## JSONL Schema

Each line is a JSON object (a `RolloutLine`) with a consistent envelope:

```json
{
  "timestamp": "2025-05-07T17:24:21.500Z",
  "type": "<item_type>",
  "payload": { ... }
}
```

The `timestamp` is ISO 8601 with millisecond precision. The `type` and `payload` come from the flattened `RolloutItem` enum (Rust serde: `tag = "type", content = "payload", rename_all = "snake_case"`).

### Line Types

| `type` | Description | Action |
|--------|-------------|--------|
| `session_meta` | Session metadata (first line) | **Read** for `cwd`, `id`, git info |
| `response_item` | API-level conversation items | **Keep** (filtered) |
| `event_msg` | Real-time execution events | **Keep** (filtered) |
| `turn_context` | Turn configuration (model, policy) | **Skip** |
| `compacted` | Context compaction marker | **Skip** |

### session_meta Payload

The first line of every rollout file. Contains session identity and context:

```json
{
  "id": "5973b6c0-94b8-487b-a530-2aeb6098ae0e",
  "cwd": "/Users/alice/dev/myproject",
  "timestamp": "2025-05-07T17:24:21Z",
  "originator": "user",
  "cli_version": "0.1.0",
  "source": "cli",
  "model_provider": "openai",
  "git": {
    "commit_hash": "abc1234",
    "branch": "main",
    "repository_url": "https://github.com/user/repo"
  }
}
```

The `source` field indicates how the session was started: `cli`, `vscode`, `exec`, `mcp`, `sub_agent`, or `unknown`.

### response_item Payload Types

The `payload` contains a nested `type` field identifying the item kind (Rust serde: `tag = "type", rename_all = "snake_case"`):

| `payload.type` | Description | Action |
|-----------------|-------------|--------|
| `message` | User or assistant text message | **Keep** — extract text from content blocks |
| `local_shell_call` | Shell command execution | **Keep** — extract command |
| `function_call` | Function/tool invocation | **Keep** — extract name and key arguments |
| `function_call_output` | Tool result output | **Skip** body, note errors |
| `custom_tool_call` | MCP or custom tool call | **Keep** — extract name |
| `custom_tool_call_output` | Custom tool result | **Skip** body |
| `reasoning` | Model reasoning/thinking | **Skip** |
| `web_search_call` | Web search action | **Skip** |
| `ghost_snapshot` | Git state snapshot | **Skip** |
| `compaction` | Encrypted compaction | **Skip** |

#### Message Items

```json
{
  "type": "message",
  "role": "user",
  "content": [
    { "type": "input_text", "text": "Let's add authentication" }
  ]
}
```

```json
{
  "type": "message",
  "role": "assistant",
  "content": [
    { "type": "output_text", "text": "I'll start with the middleware..." }
  ],
  "phase": "final_answer"
}
```

Content blocks use `input_text` for user messages and `output_text` for assistant messages. Assistant messages may have a `phase` field: `commentary` (mid-turn) or `final_answer`.

#### Shell Command Items

```json
{
  "type": "local_shell_call",
  "call_id": "call_abc123",
  "status": "completed",
  "action": {
    "type": "exec",
    "command": ["bash", "-c", "npm test"],
    "working_directory": "/Users/alice/dev/myproject"
  }
}
```

The `status` field is `completed`, `in_progress`, or `incomplete`.

#### Function Call Items

```json
{
  "type": "function_call",
  "name": "read_file",
  "arguments": "{\"path\": \"src/auth.ts\"}",
  "call_id": "call_xyz789"
}
```

Note: `arguments` is a JSON-encoded **string**, not a nested object. Parse it to extract paths.

#### Custom Tool Call Items

```json
{
  "type": "custom_tool_call",
  "call_id": "call_mcp01",
  "name": "search_docs",
  "input": "{\"query\": \"auth setup\"}"
}
```

### event_msg Payload Types

Event messages also have a nested `type` field (Rust serde: `tag = "type", rename_all = "snake_case"`):

| `payload.type` | Description | Action |
|-----------------|-------------|--------|
| `user_message` | User's input text | **Keep** — human's words |
| `agent_message` | Agent's output text | **Keep** — agent's words |
| `exec_command_begin` | Shell command starting | Use for command + cwd |
| `exec_command_end` | Shell command finished | Note exit status |
| `patch_apply_begin` | File write/edit starting | **Keep** — extract file paths from `changes` |
| `patch_apply_end` | File write/edit finished | Note if `success` is false |
| `error` | Error event | **Keep** — extract error message |
| `mcp_tool_call_begin` | MCP tool start | **Keep** — name only |
| `mcp_tool_call_end` | MCP tool end | **Skip** body |
| `task_started` | Turn lifecycle start | **Skip** |
| `task_complete` | Turn lifecycle end | **Skip** |
| `agent_message_delta` | Streaming text delta | **Skip** |
| `agent_reasoning` | Reasoning output | **Skip** |
| `token_count` | Token usage | **Skip** |
| All others | Internal events | **Skip** |

#### User Message Event

```json
{
  "type": "user_message",
  "message": "Let's add JWT authentication"
}
```

#### Agent Message Event

```json
{
  "type": "agent_message",
  "message": "I'll set up the middleware and token validation..."
}
```

#### Patch Apply Events

```json
{
  "type": "patch_apply_begin",
  "call_id": "call_abc",
  "turn_id": "turn_123",
  "auto_approved": true,
  "changes": {
    "/Users/alice/dev/myproject/src/auth.ts": { ... },
    "/Users/alice/dev/myproject/src/middleware.ts": { ... }
  }
}
```

The keys of `changes` are the absolute file paths being modified.

```json
{
  "type": "patch_apply_end",
  "call_id": "call_abc",
  "turn_id": "turn_123",
  "success": true,
  "stdout": "...",
  "stderr": ""
}
```

#### Error Event

```json
{
  "type": "error",
  "message": "Command failed with exit code 1",
  "code": "exec_error"
}
```

## Duplication Note

Rollout files record **both** `event_msg` entries (real-time events) and `response_item` entries (API-level items) for the same logical actions. For example, an agent's text may appear as both an `agent_message` event and a `message` response item. When building transcripts, prefer `event_msg` for text messages (simpler format) and `response_item` for tool calls (structured data), deduplicating by content comparison when both appear.

## Discovery Instructions

To find sessions for a project name like "myproject":

1. Determine codex home: `$CODEX_HOME` if set, otherwise `~/.codex`
2. Walk `sessions/` recursively to find `rollout-*.jsonl` files
3. Read the first line of each file (the `session_meta` entry)
4. Extract the `cwd` field from the payload
5. Fuzzy-match the project name against `cwd` (case-insensitive substring match)
6. If multiple matches, present them to the user to pick

## Reading Strategy

For each rollout file in a matched project:

**Building the session index (Phase 2):**
1. Read line 1 (`session_meta`) for `cwd`, `id`, `timestamp`, and git info
2. Scan for first `event_msg`/`user_message` or `response_item`/`message` with `role: "user"` — extract as "first user message"
3. Scan the last ~100 lines for the last user message
4. Get file modification time
5. Count lines as a size proxy

**Reading full transcripts (Phase 3):**
1. Parse each line as JSON
2. Skip lines where `type` is `turn_context` or `compacted`
3. For `event_msg`/`user_message` → keep (my human's words)
4. For `event_msg`/`agent_message` → keep (my words)
5. For `response_item`/`message` → keep text only if not already seen via event_msg (deduplicate by content)
6. For `response_item`/`local_shell_call` → keep command (e.g., `["bash", "-c", "npm test"]` → `npm test`)
7. For `response_item`/`function_call` → keep `name` and extract path/query from `arguments` JSON string
8. For `response_item`/`custom_tool_call` → keep `name`
9. For `event_msg`/`patch_apply_begin` → keep file paths from `changes` keys
10. For `event_msg`/`error` → keep error message
11. For `event_msg`/`patch_apply_end` with `success: false` → note as error
12. Skip all reasoning, deltas, token counts, snapshots, and other internal events
