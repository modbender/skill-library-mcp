# Bolt-skill

[![Agent Skill](https://img.shields.io/badge/agentskills.io-compatible-6366f1?style=flat-square&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQTEwIDEwIDAgMCAwIDIgMTJhMTAgMTAgMCAwIDAgMTAgMTAgMTAgMTAgMCAwIDAgMTAtMTBBMTAgMTAgMCAwIDAgMTIgMm0wIDJhOCA4IDAgMCAxIDggOCA4IDggMCAwIDEtOCA4IDggOCAwIDAgMS04LTggOCA4IDAgMCAxIDgtOG0tMSA0djZsNS0zbC01LTN6Ii8+PC9zdmc+)](https://agentskills.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-22c55e?style=flat-square)](SKILL.md)
[![Bolt API](https://img.shields.io/badge/Bolt-REST%20API-0ea5e9?style=flat-square)](https://github.com/ndhill84/Bolt)
[![Works with Claude](https://img.shields.io/badge/Works%20with-Claude%20Code-d97706?style=flat-square&logo=anthropic&logoColor=white)](https://claude.ai/code)

> An [Agent Skill](https://agentskills.io) for managing sprints and stories in ⚡[Bolt](https://github.com/ndhill84/Bolt) — a collaborative software development platform built for human-AI teamwork.

---

## What This Skill Does

Once installed, any AI agent that supports the agentskills.io standard can:

- Browse and navigate **projects** and **sprints**
- **Create, update, and delete** stories
- Move stories through the Kanban workflow — `waiting` → `in_progress` → `completed`
- Track **blockers** and inter-story **dependencies**
- Add **notes** and **labels** to stories
- Get **sprint digests** — story counts, blocked list, assignee breakdown
- Log **AI activity** as agent session events (visible in the Bolt UI)
- **Upload and retrieve files** attached to stories or projects
- Poll for changes efficiently with **delta sync**
- Run **batch operations** — move or patch many stories in one request

---

## Installation

```bash
# Claude Code
git clone https://github.com/ndhill84/Bolt-skill ~/.claude/skills/bolt-sprint

# Codex CLI
git clone https://github.com/ndhill84/Bolt-skill ~/.codex/skills/bolt-sprint

# openClaw
git clone https://github.com/ndhill84/Bolt-skill ~/.openclaw/skills/bolt-sprint
```

Or via `npx skills` (if published to the skills registry):

```bash
npx skills install bolt-sprint
```

---

## Configuration

Set these environment variables before starting your AI session:

| Variable | Required | Description |
|----------|----------|-------------|
| `BOLT_BASE_URL` | Yes | Base URL of your Bolt instance, e.g. `http://localhost:3000` |
| `BOLT_API_TOKEN` | No | API token — only needed if the server was started with `BOLT_API_TOKEN` set |

```bash
export BOLT_BASE_URL="http://localhost:3000"
export BOLT_API_TOKEN="your-token-here"  # omit if not using auth
```

Verify connectivity:

```bash
curl -s "$BOLT_BASE_URL/health"
# → {"ok":true}
```

---

## Helper Script

`scripts/bolt.sh` provides a lightweight CLI wrapping the most common API operations.

```bash
# Add to PATH
export PATH="$PATH:$HOME/.claude/skills/bolt-sprint/scripts"
```

| Command | Description |
|---------|-------------|
| `bolt.sh health` | Check server connectivity |
| `bolt.sh projects` | List all projects |
| `bolt.sh sprints <projectId>` | List sprints for a project |
| `bolt.sh stories "<query>"` | List stories with query string filters |
| `bolt.sh digest sprint <sprintId>` | Sprint digest — counts, blockers, assignees |
| `bolt.sh digest daily <projectId>` | 24-hour project snapshot |
| `bolt.sh move <storyId> <status>` | Move story: `waiting` · `in_progress` · `completed` |
| `bolt.sh patch <storyId> '<json>'` | Update story fields |
| `bolt.sh note <storyId> '<text>'` | Add a note to a story |
| `bolt.sh label-add <storyId> <label>` | Add a label |
| `bolt.sh label-rm <storyId> <label>` | Remove a label |
| `bolt.sh log-event <sessionId> '<msg>'` | Log an agent event |
| `bolt.sh audit [projectId]` | Tail the audit log |

---

## Workflow Examples

Full recipes are in [`references/workflows.md`](references/workflows.md).

**Daily standup**
```bash
bolt.sh digest sprint $SPRINT_ID
bolt.sh stories "sprintId=$SPRINT_ID&blocked=true&fields=id,title,assignee"
```

**Pick up and complete a story**
```bash
bolt.sh move $STORY_ID in_progress
# ... implement ...
bolt.sh note $STORY_ID "Done. PR #42 opened."
bolt.sh move $STORY_ID completed
```

**Mark a blocker**
```bash
bolt.sh patch $STORY_ID '{"blocked":true}'
bolt.sh note $STORY_ID "Blocked: waiting for DB migration approval."
```

**Batch-close multiple stories**
```bash
curl -s -X POST -H "Content-Type: application/json" \
  ${BOLT_API_TOKEN:+-H "x-bolt-token: $BOLT_API_TOKEN"} \
  -d '{"items":[{"id":"s1","status":"completed"},{"id":"s2","status":"completed"}]}' \
  "$BOLT_BASE_URL/api/v1/stories/batch/move"
```

---

## API Coverage

| Resource | Operations |
|----------|-----------|
| **Health** | Liveness, readiness |
| **Projects** | List, create, update, delete |
| **Sprints** | List, create, update, start, close, assign stories |
| **Stories** | List (filtered), create, update, delete, move, batch move, batch patch |
| **Notes** | List, create |
| **Labels** | List, add, remove |
| **Dependencies** | List, add, remove |
| **Files** | List, register, upload binary, delete, get extracted text |
| **Agent Sessions** | List, log events |
| **Audit** | Monotonic changefeed |
| **Digests** | Sprint summary, daily project snapshot |

**Key behaviors:**

| Feature | Detail |
|---------|--------|
| Idempotency | Add `Idempotency-Key: <uuid>` to POST/PATCH — safe to retry (48h TTL) |
| Pagination | Cursor-based · default limit 50 · max 200 |
| Field projection | `?fields=id,title,status` — fetch only what you need |
| Delta sync | `?updated_since=<ISO8601>` — poll for changes efficiently |
| Rate limits | 120 writes/minute per IP |
| Error format | `{ "error": { "code": "...", "message": "..." } }` |

---

## File Structure

```
bolt-sprint/
├── SKILL.md                    # Skill entry point — agentskills.io spec
├── README.md                   # This file
├── references/
│   ├── api-reference.md        # Full endpoint docs with request/response schemas
│   └── workflows.md            # 10 workflow recipes
└── scripts/
    └── bolt.sh                 # Bash CLI helper
```

---

## Spec Compliance

This skill conforms to the [agentskills.io specification](https://agentskills.io/specification):

- `SKILL.md` at the repo root with valid YAML frontmatter (`name`, `description`)
- Skill name `bolt-sprint` matches the directory name
- Progressive disclosure model — metadata (~100 tokens) → instructions → on-demand references
- `allowed-tools: Bash` declared in frontmatter
- Supporting files organized under `references/` and `scripts/`

---

## License

MIT
