# Gemini CLI — Platform Reference

## Session Locations

Session transcripts are stored as JSON files in project-hash-scoped directories:

```
~/.gemini/tmp/<project_hash>/chats/session-<timestamp>-<uuid8>.json
```

The base directory defaults to `~/.gemini` but can be overridden via the `GEMINI_CLI_HOME` environment variable.

The `<project_hash>` is the SHA256 hex digest of the absolute project root path:

```
sha256("/Users/alice/dev/myproject") → "a1b2c3d4..."
```

## File Naming

Session filenames follow this pattern:

```
session-YYYY-MM-DDThh-mm-<uuid_first_8>.json
```

- The timestamp uses ISO 8601 format with colons replaced by hyphens (filesystem-safe), truncated to minutes
- The UUID suffix is the first 8 characters of the session UUID
- File prefix constant: `session-`
- Example: `session-2026-01-27T15-21-a82545c4.json`

## Project Matching

Gemini CLI does **not** store the project root path inside session files — only the `projectHash`. To find sessions for a project:

1. Determine Gemini home: `$GEMINI_CLI_HOME` if set, otherwise `~/.gemini`
2. Compute `sha256(absolute_project_path)` for candidate directories matching the project name
3. Check if `~/.gemini/tmp/<hash>/chats/` exists and contains session files
4. As a fallback, scan all hash directories and try to extract the project root from tool call file paths within sessions

Candidate directories are found by scanning common development locations (`~/dev`, `~/projects`, `~/src`, `~/code`, `~`, etc.) up to 3-4 levels deep for directories whose name fuzzy-matches the given project name.

## JSON Schema

Each session file is a single JSON object (not JSONL):

```json
{
  "sessionId": "a82545c4-4f3f-4c3d-8b12-0a580eae4df4",
  "projectHash": "901d83c8...",
  "startTime": "2026-01-27T15:22:34.666Z",
  "lastUpdated": "2026-01-27T15:30:46.002Z",
  "summary": "Optional AI-generated summary",
  "messages": [ ... ]
}
```

### Top-Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `sessionId` | string | UUID-4 session identifier |
| `projectHash` | string | SHA256 hex of project root path |
| `startTime` | string | ISO 8601 session start timestamp |
| `lastUpdated` | string | ISO 8601 last modification timestamp |
| `summary` | string? | Optional AI-generated session summary |
| `messages` | array | Array of `MessageRecord` objects |

### Message Types

Each message has a `type` field that determines its structure:

| `type` | Description | Action |
|--------|-------------|--------|
| `user` | Human's input message | **Keep** — human's words |
| `gemini` | AI assistant response | **Keep** — agent's words + tool calls |
| `info` | Informational system message | **Skip** |
| `error` | Error message | **Keep** — note errors |
| `warning` | Warning message | **Skip** |

### User Message

```json
{
  "id": "3bbb4a75-...",
  "timestamp": "2026-01-27T15:22:34.666Z",
  "type": "user",
  "content": "Help me configure TypeScript for my project"
}
```

The `content` field is a `PartListUnion` — it can be:
- A plain string (most common for user messages)
- A `Part` object: `{ "text": "..." }` or multimodal part
- An array of `Part` objects

### Gemini (Assistant) Message

```json
{
  "id": "7ffb3e31-...",
  "timestamp": "2026-01-27T15:22:57.473Z",
  "type": "gemini",
  "content": "I'll help you set up TypeScript configuration.",
  "model": "gemini-3-pro-preview",
  "toolCalls": [ ... ],
  "thoughts": [ ... ],
  "tokens": { ... }
}
```

#### Tool Call Records

Each tool call in the `toolCalls` array:

```json
{
  "id": "read_file-1769527377007-d0d9aad62d73a8",
  "name": "read_file",
  "args": {
    "file_path": "src/auth.ts"
  },
  "result": [
    {
      "functionResponse": {
        "id": "read_file-...",
        "name": "read_file",
        "response": {
          "output": "file contents or result text"
        }
      }
    }
  ],
  "status": "success",
  "timestamp": "2026-01-27T15:23:09.302Z",
  "displayName": "ReadFile",
  "description": "Tool description...",
  "resultDisplay": "Short display of result",
  "renderOutputAsMarkdown": true
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique tool call ID |
| `name` | string | Tool function name (e.g., `read_file`, `run_shell_command`, `write_file`, `edit_file`, `list_directory`) |
| `args` | object | Tool arguments as a JSON object (NOT a string — already parsed) |
| `result` | array? | Array of `functionResponse` wrappers, or null |
| `status` | string | Execution status: `"success"`, `"error"`, `"pending"` |
| `timestamp` | string | ISO 8601 timestamp |
| `displayName` | string? | Human-readable tool name (e.g., `"ReadFile"`, `"Shell"`, `"WriteFile"`) |
| `resultDisplay` | string? | Short display string for the result |

Common tool names: `read_file`, `write_file`, `edit_file`, `run_shell_command`, `list_directory`, `search_files`, `web_search`.

#### Thought Records

```json
{
  "subject": "Investigating File Distribution",
  "description": "I'm currently focused on the file structure...",
  "timestamp": "2026-01-27T15:22:40.290Z"
}
```

Thoughts represent the model's internal reasoning. **Skip** when building transcripts.

#### Token Summary

```json
{
  "input": 5252,
  "output": 92,
  "cached": 2840,
  "thoughts": 709,
  "tool": 0,
  "total": 6053
}
```

Token metadata. **Skip** when building transcripts.

## Discovery Instructions

To find sessions for a project name like "myproject":

1. Determine Gemini home: `$GEMINI_CLI_HOME` if set, otherwise `~/.gemini`
2. Scan common base directories (`~`, `~/dev`, `~/projects`, `~/src`, `~/code`, etc.) up to 3 levels deep
3. For each directory whose name matches the project name (case-insensitive substring), compute its SHA256 hash
4. Check if `<gemini_home>/tmp/<hash>/chats/` exists
5. List `session-*.json` files in matching chat directories
6. If no match found, fall back to scanning all hash directories and extracting paths from tool call arguments

## Reading Strategy

**Building the session index (Phase 2):**
1. Parse the full JSON file
2. Read `sessionId`, `startTime`, `lastUpdated`, `summary`
3. Iterate `messages` to find first and last messages with `type: "user"`
4. Extract text from `content` (handle string, Part, or Part[] formats)
5. Use `lastUpdated` as the modification timestamp

**Reading full transcripts (Phase 3):**
1. Parse the full JSON file
2. Iterate through `messages` array
3. For `type: "user"` → keep as human's words (extract text from `content`)
4. For `type: "gemini"` → keep content as agent's words, then process `toolCalls`
5. For each tool call: extract `name` and key arguments (`file_path`, `command`, `path`, `pattern`, `query`)
6. For tool calls with `status: "error"` → note as error
7. Skip `thoughts`, `tokens`, `info`, and `warning` messages
8. For `type: "error"` → note the error content
