---
name: org-memory
version: 0.3.0
description: "Structured knowledge base and task management using org-mode files. Query, mutate, link, and search org files and org-roam databases with the `org` CLI."
metadata: {"openclaw":{"emoji":"🦄","homepage":"https://github.com/dcprevere/org-cli","requires":{"bins":["org"],"env":["ORG_MEMORY_AGENT_DIR","ORG_MEMORY_HUMAN_DIR","ORG_MEMORY_AGENT_DATABASE_LOCATION","ORG_MEMORY_HUMAN_DATABASE_LOCATION"]},"install":[{"kind":"download","label":"Download from GitHub releases: https://github.com/dcprevere/org-cli/releases"}]}}
---

# org-memory

Use the `org` CLI to maintain structured, linked, human-readable knowledge in org-mode files. Org files are plain text with rich structure: headlines, TODO states, tags, properties, timestamps, and links. Combined with org-roam, they form a knowledge graph backed by a SQLite database.

## Shortcuts

When your human uses these patterns, act on them directly.

| Keyword | Meaning | Target |
|---|---|---|
| `Todo:` | Create a task with a date | `$ORG_MEMORY_HUMAN_DIR` |
| `Note:` | Write this down for me | `$ORG_MEMORY_HUMAN_DIR` |
| `Done:` / `Finished:` | Mark a task complete | `$ORG_MEMORY_HUMAN_DIR` |
| `Know:` | Store this for agent recall | `$ORG_MEMORY_AGENT_DIR` |

### Todo — create a task

`Todo: <text>` means "create a task." Extract any date or timeframe from the text and schedule it. If the text contains a relative date ("in 3 weeks", "by Friday", "next month"), compute the actual date and add `--scheduled <date>` or `--deadline <date>`.

Action: `org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" '<title>' --todo TODO --scheduled <date> --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json`

Use `--deadline` instead of `--scheduled` when the text implies a hard due date ("by Friday", "due March 1st"). Use `--scheduled` for softer timing ("in 3 weeks", "next month", "tomorrow").

Examples:
- "Todo: submit taxes in 3 weeks" → `org add .../inbox.org 'Submit taxes' --todo TODO --scheduled 2026-03-18`
- "Todo: renew passport by June" → `org add .../inbox.org 'Renew passport' --todo TODO --deadline 2026-06-01`
- "Todo: call dentist tomorrow" → `org add .../inbox.org 'Call dentist' --todo TODO --scheduled 2026-02-26`
- "Todo: book flights" → `org add .../inbox.org 'Book flights' --todo TODO` (no date mentioned)

### Note — for the human

`Note: <text>` means "add this to MY org files." It is always a task or reminder for the *human*, not for the agent.

Action: `org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" '<text>' --todo TODO -f json`

If the note includes a date or deadline, add `--scheduled <date>` or `--deadline <date>`. If there's no date, add it without one (the human will schedule it themselves, or ask you to).

Examples:
- "Note: Buy groceries" → `org add .../inbox.org 'Buy groceries' --todo TODO`
- "Note: Review PR #42 by Friday" → `org add .../inbox.org 'Review PR #42' --todo TODO --deadline 2026-02-28`
- "Note: we could add feature X to the app" → `org add .../inbox.org 'Add feature X to the app' --todo TODO`
- "Note: send email to Donna about safeguarding" → `org add .../inbox.org 'Send email to Donna about safeguarding' --todo TODO`

**Note vs Todo:** Both create TODO headings. The difference is intent — `Todo:` signals a concrete task (always try to extract a date), while `Note:` is broader (ideas, reminders, observations). When there's no date, add it without one.

**Edge case — ideas and observations:** If the human says "Note: we could do X" or "Note: idea for Y", it's still a Note. They're telling you to write it down for them. Add it as a TODO. Don't create a roam node, don't put it in the agent's knowledge base.

### Done — mark complete

`Done: <text>` or `Finished: <text>` means "mark this task as DONE." Search for the matching TODO and set its state.

Action:
1. Search: `org todos --state TODO --search '<text>' -d "$ORG_MEMORY_HUMAN_DIR" -f json`
2. If exactly one match: `org todo <file> '<title>' DONE -f json`
3. If multiple matches: show them to the human and ask which one
4. If no match: tell the human you couldn't find it

Examples:
- "Done: pay Nigel Kerry" → find and mark DONE
- "Finished: the PR review" → find and mark DONE
- "Done: groceries" → search for "groceries", mark DONE

### Know — for the agent

`Know: <info>` means "store this in YOUR knowledge base for future recall." This is information the agent should retain across sessions.

Action: Search for an existing node first (`org roam node find`), then create or update.

Examples:
- "Know: Sarah prefers morning meetings" → Create/update a node for Sarah in `$ORG_MEMORY_AGENT_DIR`
- "Know: The API uses OAuth2, not API keys" → Create/update a node for the API in `$ORG_MEMORY_AGENT_DIR`

### After every write — confirm

After every mutation to either directory, print a line in this exact format:

```
org-memory: <action> <file-path>
```

Examples: `org-memory: added TODO to ~/org/human/inbox.org`, `org-memory: created node ~/org/agent/sarah.org`, `org-memory: updated ~/org/agent/sarah.org`.

**This is mandatory.** Never silently write to either directory. The human should always see what you did and where.

## Output format

All commands accept `-f json` for structured output with `{"ok":true,"data":...}` envelopes. Errors return `{"ok":false,"error":{"type":"...","message":"..."}}`. Always use `-f json`.

## Command safety

User-provided text (task titles, note content, search terms) must be single-quoted to prevent shell expansion. Double quotes allow `$(…)`, backticks, and variable interpolation — single quotes do not.

```bash
# Correct
org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" 'User provided text' --todo TODO -f json

# Wrong — double quotes allow shell injection
org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" "User provided text" --todo TODO -f json
```

If the text contains a literal single quote, escape it with `'\''`:

```bash
org add "$ORG_MEMORY_HUMAN_DIR/inbox.org" 'Don'\''t forget' --todo TODO -f json
```

For multi-line content, pipe via stdin instead of interpolating:

```bash
printf '%s' 'Long text here' | org append k4t --stdin -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json
```

Environment variable paths (`$ORG_MEMORY_HUMAN_DIR`, etc.) must always be double-quoted to handle spaces, but never place user text inside double quotes.

## Discovery

Run `org schema` once to get a machine-readable description of all commands, arguments, and flags. Use this to construct valid commands without memorizing the interface.

## Setup

Configuration is via environment variables. Set them in `openclaw.json` so they are injected into every command automatically.

| Variable | Default | Purpose |
|---|---|---|
| `ORG_MEMORY_USE_FOR_AGENT` | `true` | Enable the agent's own knowledge base |
| `ORG_MEMORY_AGENT_DIR` | `~/org/agent` | Agent's org directory |
| `ORG_MEMORY_AGENT_DATABASE_LOCATION` | `~/.local/share/org-memory/agent/.org.db` | Agent's database |
| `ORG_MEMORY_USE_FOR_HUMAN` | `true` | Enable task management in the human's org files |
| `ORG_MEMORY_HUMAN_DIR` | `~/org/human` | Human's org directory |
| `ORG_MEMORY_HUMAN_DATABASE_LOCATION` | `~/.local/share/org-memory/human/.org.db` | Human's database |

If `ORG_MEMORY_USE_FOR_AGENT` is not `true`, skip the Knowledge management section. If `ORG_MEMORY_USE_FOR_HUMAN` is not `true`, skip the Task management and Batch operations sections.

Always pass `--db` to point at the correct database. The CLI auto-syncs the roam database after every mutation using the `--db` value. Without `--db`, the CLI defaults to the emacs org-roam database (`~/.emacs.d/org-roam.db`), which is not what you want.

Initialize each enabled directory. If the directories already contain org files, sync them first:

```bash
# Sync existing files into the roam database (skip if starting fresh)
org roam sync -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION"
org roam sync -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION"

# Create a seed node for the agent's knowledge base (skip if files already exist)
org roam node create 'Index' -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION" -f json

# Build the headline index (enables CUSTOM_ID auto-assignment and file-less commands)
org index -d "$ORG_MEMORY_AGENT_DIR" --db "$ORG_MEMORY_AGENT_DATABASE_LOCATION"
org index -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION"
```

The roam response includes the node's ID, file path, title, and tags.

## Stable identifiers (CUSTOM_ID)

Every headline created with `org add` is auto-assigned a short CUSTOM_ID (e.g. `k4t`) when an index database exists. This ID appears in the `custom_id` field of all JSON responses and as a column in text output.

Use CUSTOM_IDs to refer to headlines in subsequent commands — they are stable across edits and don't require a file path:

```bash
org todo k4t DONE -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
org schedule k4t 2026-03-15 -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
org note k4t 'Pushed back per manager request' -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
org append k4t 'Updated scope per review.' -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION" -f json
```

To backfill CUSTOM_IDs on existing headlines that don't have them:

```bash
org custom-id assign -d "$ORG_MEMORY_HUMAN_DIR" --db "$ORG_MEMORY_HUMAN_DATABASE_LOCATION"
```

**Never address headlines by position number (`pos`).** Positions change when files are edited — a mutation on one headline shifts the byte positions of everything after it.

Safe identifiers (in order of preference):
1. **CUSTOM_ID** (e.g. `k4t`) — stable, short, unique
2. **org-id** (UUID) — stable, unique
3. **Exact title** — stable as long as the title doesn't change

If you need to mutate multiple headlines in the same file, either:
- Use `org batch` for atomic multi-step operations (recommended)
- Use CUSTOM_IDs or titles, never `pos`
- If you must use `pos`, re-query after each mutation to get fresh positions

## Error handling

Branch on the `ok` field. Handle errors by `type`:

- `file_not_found`: wrong path or deleted file
- `headline_not_found`: identifier doesn't match; re-query to get current state
- `parse_error`: file has syntax the parser can't handle; don't retry
- `invalid_args`: check `org schema` or `org <command> --help`

## References

Read these on demand when the conversation requires them:

- **Knowledge management** (`{baseDir}/references/knowledge-management.md`): Read when `ORG_MEMORY_USE_FOR_AGENT=true` and you need to create/query/link roam nodes in the agent's knowledge base.
- **Task management** (`{baseDir}/references/task-management.md`): Read when `ORG_MEMORY_USE_FOR_HUMAN=true` and you need to query or mutate the human's tasks, use batch operations, or map natural-language queries to commands.
- **Memory architecture** (`{baseDir}/references/memory-architecture.md`): Read on first use (memory migration) and at session start (file structure, session routine, ambient capture guidelines).
