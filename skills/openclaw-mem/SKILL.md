---
name: openclaw-mem
version: 2.1.0
description: "Session-first memory curator for OpenClaw. Keeps RAM clean, recall precise, and durable knowledge safe."
---

# OpenClaw Memory Curator

A **session-first memory system** for OpenClaw.

It exists for one reason:
**important knowledge must survive session compaction without bloating the context window.**

---

## TL;DR (for humans)

- Session memory = temporary (RAM)
- Disk = source of truth
- **Decisions & preferences → `MEMORY.md`**
- **Daily work → `memory/YYYY-MM-DD.md`**
- This skill saves durable knowledge **before compaction**
- Retrieval always happens via `memory_search` → `memory_get`

If something matters later, **write it to disk**.

---

> ⚠️ **CRITICAL REQUIREMENT**
>
> Session memory indexing must be enabled.

## Enable Session Memory

**CLI**
```bash
clawdbot config set agents.defaults.memorySearch.experimental.sessionMemory true
```

**JSON**
```json
{
  "agents": {
    "defaults": {
      "memorySearch": {
        "experimental": { "sessionMemory": true },
        "sources": ["memory", "sessions"]
      }
    }
  }
}
```

---

## Mental Model (read this once)

OpenClaw memory has **three layers**. Confusion usually comes from mixing them up.

### 1. Session Memory (RAM)
- Lives in the current conversation
- Automatically compacted
- Indexed for retrieval
- **Never reliable long-term**

👉 Treat as short-term thinking space.

---

### 2. Daily Logs (`memory/YYYY-MM-DD.md`)
- Append-only
- What happened today
- Commands, edits, short-lived issues

👉 Treat as a work log, not a knowledge base.

---

### 3. Long-Term Memory (`MEMORY.md`)
- Curated
- Small
- High-signal only
- Indexed and retrievable

👉 Treat as facts the agent must not forget.

---

## When to Write Memory (simple rules)

### Write to `MEMORY.md` if it would still be true next week.
Examples:
- Decisions
- Preferences
- Invariants
- Policies

### Write to daily logs if it helps understand today.
Examples:
- Refactors
- Experiments
- Temporary blockers

If unsure: **write to daily log first**, promote later.

---

## Pre-Compaction Flush (why this exists)

Before OpenClaw compacts the session, it triggers a **silent reminder**.

This skill uses that moment as a **Save Game checkpoint**.

### What happens:
1. Durable knowledge is extracted
2. Daily notes are written to today’s log
3. Durable items are promoted to `MEMORY.md`
4. Agent replies `NO_REPLY` (user never sees this)

This prevents knowledge loss without interrupting you.

---

## Durable Memory Format (`MEMORY.md`)

Use IDs and tags so search works reliably.

```markdown
## DEC-2026-02-04-01
type: decision
area: memory

Decision:
Session memory is retrieval-only. Disk is the source of truth.

Reason:
Session compaction is lossy. Disk memory is stable.
```

### ID prefixes
- `DEC` – Decisions
- `PREF` – Preferences
- `FACT` – Durable facts
- `POLICY` – Rules / invariants

---

## Retrieval Strategy (how agents should recall)

1. Use `memory_search` (max ~6 results)
2. Pick the best 1–2 hits
3. Use `memory_get` with line ranges
4. Inject the minimum text required

This keeps context small and precise.

---

## Agent Playbook (rules for agents)

- Prefer disk over RAM
- Prefer `MEMORY.md` over daily logs for facts
- Use search before asking the user again
- Never copy raw chat into memory
- Write memory explicitly, do not assume it sticks

---

## Anti-Patterns (do not do these)

- ❌ Copy chat transcripts into memory
- ❌ Store secrets or credentials
- ❌ Treat daily logs as long-term memory
- ❌ Overwrite memory files instead of appending
- ❌ Store speculation as fact

---

## Privacy Rules

- Never store secrets (API keys, tokens, passwords)
- Ignore anything inside `<private>...</private>`
- If sensitive info exists: store only **that it exists**, not the value

---

## Retention & Cleanup

Default: **no deletion**

- Disk is cheap
- Recall quality is expensive

Optional:
- Move old daily logs to `memory/archive/YYYY-MM/`
- Only prune after durable knowledge is verified

---

## Usage (human-friendly)

Examples that work well:
- “Store this as a durable decision.”
- “This is a preference, remember it.”
- “Write this to today’s log.”

---

## Design Philosophy

- Disk is truth
- RAM is convenience
- Retrieval beats retention
- Fewer tokens > more tokens
- Memory should earn its place
