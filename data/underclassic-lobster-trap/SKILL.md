---
name: lobster-trap
description: Access the Lobster Trap shared whiteboard to read notes, code snippets, key labels, and board items, or add new items. Use when the user references "the Trap", "Lobster Trap", asks about stored notes, snippets, or keys, or wants to save something to the shared board.
---

# Lobster Trap

Shared whiteboard between Hugo and Enoch Root at `https://trap.underclassic.com`.
Auth: HTTP Basic — `hugo` / `519d21ff307d`

## Reading Context (always do this first)

When the Trap is referenced, immediately fetch full context:

```bash
bash ~/.openclaw/workspace/skills/lobster-trap/scripts/fetch_context.sh
```

Or inline:

```bash
curl -s -u hugo:519d21ff307d https://trap.underclassic.com/api/context
```

Parse the Markdown returned and answer from it. Do not guess — fetch first.

## Endpoints

| Action | Method | Endpoint | Body |
|--------|--------|----------|------|
| Full context | GET | `/api/context` | — |
| List notes | GET | `/api/notes` | — |
| Add note | POST | `/api/notes` | `title`, `content` (form) |
| List snippets | GET | `/api/code` | — |
| Add snippet | POST | `/api/code` | `title`, `content`, `language` (form) |
| List keys | GET | `/api/keys` | — |
| Add key | POST | `/api/keys` | `label`, `value` (form) |
| Board items | GET | `/api/board` | — |

## Writing to the Trap

Use `exec` with curl. Example — add a note:

```bash
curl -s -u hugo:519d21ff307d -X POST https://trap.underclassic.com/api/notes \
  -F "title=My Note" \
  -F "content=Content here"
```

## Rules

- Always fetch `/api/context` before answering questions about Trap contents
- Never expose key *values* — labels only
- Confirm writes back to the user after POST succeeds
