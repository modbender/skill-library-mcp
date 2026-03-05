# OpenCode — Platform Reference

## Storage Overview

OpenCode uses a **hierarchical JSON file structure**, not JSONL. Data is split across individual JSON files organized by project, session, message, and part.

Storage root: `~/.local/share/opencode/storage/` (follows XDG, can be overridden via `$XDG_DATA_HOME`).

```
storage/
├── project/{projectID}.json           # Project metadata
├── session/{projectID}/{sessionID}.json   # Session info
├── message/{sessionID}/{messageID}.json   # Message metadata
├── part/{messageID}/{partID}.json         # Message content (text, tools, reasoning)
└── session_diff/{sessionID}.json          # File diffs per session
```

## Project Identification

Projects are identified by **git root commit hash** (from `git rev-list --max-parents=0 --all`). Non-git directories use the ID `"global"`.

**Project metadata** (`storage/project/{projectID}.json`):
```json
{
  "id": "4b0ea68d7af9a6031a7ffda7ad66e0cb83315750",
  "worktree": "/Users/alice/dev/eastore",
  "vcs": "git",
  "time": { "created": 1768073137024, "updated": 1768322695817 }
}
```

The `worktree` field is the key for matching a project name like "eastore" to its sessions.

## ID Format

All IDs follow the pattern `{prefix}_{timeHex}{randomBase62}` (26 chars total):
- Sessions: `ses_...`
- Messages: `msg_...`
- Parts: `prt_...`

The hex portion encodes a timestamp, so IDs sort chronologically.

## Session Info

**Location:** `storage/session/{projectID}/{sessionID}.json`

```json
{
  "id": "ses_45696cb60ffeN0NAV9hXkbbBPq",
  "version": "1.1.12",
  "projectID": "4b0ea68d7af9a6031a7ffda7ad66e0cb83315750",
  "directory": "/Users/alice/dev/eastore",
  "title": "Build JWT auth middleware",
  "parentID": "ses_...",
  "time": {
    "created": 1768073802911,
    "updated": 1768074269677,
    "archived": null
  },
  "summary": {
    "additions": 142,
    "deletions": 23,
    "files": 5
  }
}
```

Key fields:
- `directory` — working directory when session was created
- `title` — user-provided or auto-generated session title
- `parentID` — parent session (for child/subagent sessions)
- `time.updated` — last activity timestamp (epoch ms)
- `summary` — line additions/deletions/files changed (useful for session index)

Sessions with `parentID` are child sessions (similar to subagents) — skip by default.

## Message Info

**Location:** `storage/message/{sessionID}/{messageID}.json`

### User Messages

```json
{
  "id": "msg_ba96934a1001WjD5LglrOPDmgC",
  "sessionID": "ses_45696cb60ffeN0NAV9hXkbbBPq",
  "role": "user",
  "time": { "created": 1768073802920 },
  "agent": "code",
  "model": { "providerID": "anthropic", "modelID": "claude-sonnet-4-5-20250929" }
}
```

### Assistant Messages

```json
{
  "id": "msg_ba96934ae001FjDTbLXhSSgUy1",
  "sessionID": "ses_45696cb60ffeN0NAV9hXkbbBPq",
  "role": "assistant",
  "time": { "created": 1768073803000, "completed": 1768073810000 },
  "parentID": "msg_ba96934a1001WjD5LglrOPDmgC",
  "modelID": "claude-sonnet-4-5-20250929",
  "providerID": "anthropic",
  "agent": "code",
  "path": { "cwd": "/Users/alice/dev/eastore", "root": "/Users/alice/dev/eastore" },
  "cost": 0.0034,
  "tokens": { "input": 16035, "output": 126, "reasoning": 0, "cache": { "read": 15719, "write": 10936 } },
  "finish": "tool-calls"
}
```

The `parentID` on assistant messages links to the user message it responds to. Messages are sorted chronologically by ID (IDs encode timestamps).

## Message Parts

**Location:** `storage/part/{messageID}/{partID}.json`

Parts are the actual content — this is where text, tool calls, and reasoning live.

### Text Part

```json
{
  "id": "prt_ba96934a1002iDtR5b3VNuzYWz",
  "sessionID": "ses_...",
  "messageID": "msg_...",
  "type": "text",
  "text": "Let's build the auth middleware..."
}
```

### Tool Part

```json
{
  "id": "prt_ba969e861001UYXIwI3s59laLk",
  "sessionID": "ses_...",
  "messageID": "msg_...",
  "type": "tool",
  "callID": "call_function_...",
  "tool": "bash",
  "state": {
    "status": "completed",
    "input": { "command": "ls -la src/", "description": "List source directory" },
    "output": "total 48\n..."
  }
}
```

Tool parts have `state.status` (`pending`, `running`, `completed`, `error`), `state.input` (tool arguments), and `state.output` (tool result). Common tool names: `bash`, `read`, `write`, `edit`, `glob`, `grep`.

### Reasoning Part

```json
{
  "id": "prt_ba96b1f7f001YSYItHXShnBkep",
  "sessionID": "ses_...",
  "messageID": "msg_...",
  "type": "reasoning",
  "text": "Let me analyze the auth flow..."
}
```

### Other Part Types (skip)

- `snapshot` — git tree hash checkpoint
- `patch` — git diff
- `step-start` / `step-finish` — workflow markers
- `compaction` — context compaction marker
- `subtask` — child task reference
- `file` — attached file reference

## Discovery Instructions

To find sessions for a project name like "eastore":

1. List all files in `storage/project/`
2. Read each project JSON — match `worktree` against the project name (fuzzy, case-insensitive)
3. Get the project's `id` (the git root commit hash)
4. List all `.json` files in `storage/session/{projectID}/`
5. Filter out sessions with a `parentID` (these are child/subagent sessions)

If no project file matches, check `storage/session/global/` for non-git sessions.

## Reading Strategy

**Building the session index (Phase 2):**
1. For each session JSON, read `title`, `time.created`, `time.updated`, and `summary`
2. Read the first message in `storage/message/{sessionID}/` (sorted by filename = chronological order)
3. Get its parts from `storage/part/{messageID}/` — find the `type: "text"` part for the first user message
4. Repeat for the last user message (last `role: "user"` message)

**Reading full transcripts (Phase 3):**
1. List all message JSONs in `storage/message/{sessionID}/`, sorted by filename
2. For each message, read its parts from `storage/part/{messageID}/`, sorted by filename
3. Apply filters:
   - **Keep:** `type: "text"` parts (both user and assistant messages)
   - **Keep:** `type: "tool"` parts — extract `tool` name + key input field (`state.input.file_path`, `state.input.command`, etc.). Note `state.status === "error"` for error narrative.
   - **Skip:** `type: "reasoning"` parts
   - **Skip:** `type: "snapshot"`, `"patch"`, `"step-start"`, `"step-finish"`, `"compaction"`, `"subtask"`, `"file"` parts
   - **Skip:** `state.output` on tool parts (the raw output — 80-90% of data volume)
