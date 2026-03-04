# Claude Code — Platform Reference

## Session Locations

Session transcripts are stored at:

```
~/.claude/projects/{project-slug}/
```

Each project directory contains one or more `.jsonl` session files plus an optional `memory/` directory.

## Path Slug Format

Project slugs are derived from the absolute working directory path:
- Replace each `/` with `-`
- Prefix with `-`

Examples:
- `/Users/alice/dev/eastore` → `-Users-alice-dev-eastore`
- `/Users/alice/dev/filecoin/filecoin-pay` → `-Users-alice-dev-filecoin-filecoin-pay`

A single codebase may appear under multiple slugs if opened from different paths (e.g., a frontend and backend in the same repo).

## File Types

Inside each project directory:

| Pattern | Type | Action |
|---------|------|--------|
| `{uuid}.jsonl` | Main session | **Read** — primary conversation transcripts |
| `agent-{hash}.jsonl` | Standalone agent | **Read** — autonomous subagent sessions spawned at the top level |
| `{uuid}/subagents/` | Subagent directory | **Skip** — internal fragments, main session already references results |
| `memory/` | Project memory | **Skip** — not a transcript |

Main sessions use UUID-4 format filenames (e.g., `640ab4c7-d010-4b20-a591-b7172ef08e66.jsonl`).

## JSONL Schema

Each line is a JSON object. Every entry has a `type` field.

### Entry Types

| Type | Description | Action |
|------|-------------|--------|
| `user` | User (human) message | **Keep** |
| `assistant` | Assistant (agent) message | **Keep** |
| `system` | System event (API turn boundary, etc.) | **Skip** |
| `progress` | Streaming progress update | **Skip** |
| `file-history-snapshot` | File state tracking for undo | **Skip** |
| `summary` | Compaction summary marker | **Skip** |

### Top-Level Entry Fields

Every `user` and `assistant` entry shares these top-level fields:

```json
{
  "type": "user" | "assistant",
  "uuid": "unique-message-id",
  "parentUuid": "parent-message-id or null",
  "timestamp": "2026-01-12T10:30:00.000Z",
  "sessionId": "session-uuid",
  "cwd": "/Users/.../project-dir",
  "version": "2.1.32",
  "gitBranch": "main",
  "isSidechain": false,
  "message": { ... }
}
```

The `cwd` field on user entries confirms which project directory was active. The `parentUuid` field provides message threading.

### Message Structure

The `message` field follows the Anthropic API message format:

```json
{
  "role": "user" | "assistant",
  "content": [ ... ]
}
```

**User messages** — content can be:
- A plain string (first message in session, before slug is established)
- An array of content blocks with `type: "text"` or `type: "tool_result"`

**Assistant messages** — content is always an array of content blocks.

### Content Block Types

**Text block:**
```json
{ "type": "text", "text": "I'll set up the JWT middleware..." }
```

**Thinking block** (extended thinking):
```json
{ "type": "thinking", "thinking": "Let me analyze the auth flow...", "signature": "..." }
```

**Tool use block:**
```json
{
  "type": "tool_use",
  "id": "toolu_01ABC...",
  "name": "Edit",
  "input": { "file_path": "src/auth.ts", "old_string": "...", "new_string": "..." }
}
```

**Tool result block** (in user messages):
```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_01ABC...",
  "content": "file contents or output...",
  "is_error": false
}
```

Note: `tool_use_id` uses snake_case (not camelCase).

### Additional Entry-Specific Fields

- **User entries** may include: `thinkingMetadata`, `todos`, `permissionMode`, `toolUseResult`, `sourceToolAssistantUUID`
- **Assistant entries** may include: `requestId`, `slug` (present after first tool use)
- **System entries** include: `subtype`, `durationMs`, `isMeta`
- **Progress entries** include: `data`, `parentToolUseID`, `toolUseID`

## Discovery Instructions

To find sessions for a project name like "eastore":

1. List all directories under `~/.claude/projects/`
2. Fuzzy-match the project name against directory names (case-insensitive, partial match)
   - "eastore" matches `-Users-lordforever-dev-eastore-Eastore-frontend-v1`
   - Multiple matches may exist (frontend, backend, different paths)
3. If multiple matches, present them to the user to pick
4. List all `.jsonl` files in the matched directory (excluding subdirectories)
5. Filter to UUID-format filenames and `agent-*.jsonl` files

## Reading Strategy

For each `.jsonl` file in a matched project:

**Building the session index (Phase 2):**
1. Read the first few lines to get the session timestamp and `cwd`
2. Find the first entry where `type === "user"` — extract the text content as "first user message"
3. Find the last few entries where `type === "user"` — extract text as "last user messages"
4. Get file modification time (`stat -f %m` on macOS)
5. Count lines (`wc -l`) as a size proxy

**Reading full transcripts (Phase 3):**
1. Parse each line as JSON
2. Skip entries where `type` is not `user` or `assistant`
3. For `user` entries with text content → keep (my human's words)
4. For `user` entries with `tool_result` content → skip the body, but note if `is_error` is true
5. For `assistant` entries with `text` content → keep (my words)
6. For `assistant` entries with `thinking` content → skip (internal reasoning, not story material)
7. For `assistant` entries with `tool_use` content → keep only `name` and the file path from `input` (e.g., `input.file_path`, `input.command`). Drop the full input body.
