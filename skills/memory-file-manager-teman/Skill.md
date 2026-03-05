---
name: dream
description: >-
  A proactive memory distillation skill that maintains MEMORY.md. Trigger scenarios:
  (1) Scheduled distillation at 03:30 daily (runs when idle, deferred to 06:00 if busy);
  (2) User says "dream" / "review" / "organize memory" / "what do you remember about me";
  (3) User requests content to be indexed into Obsidian.
version: 0.2.2
metadata:
  openclaw:
    emoji: "🌙"
    homepage: https://github.com/teman2050/dream-skill
requires:
  bins:
    - jq
    - wc
config:
  - DREAM_VAULT_PATH
install:
  - kind: brew
    formula: jq
    bins: [jq]
---

# Dream — Proactive Memory Distillation v5

## Core Purpose

**OpenClaw natively solves capture and search:**
- Capture: compaction flush automatically writes important content to `memory/YYYY-MM-DD.md`
- Search: `openclaw memory search` provides hybrid vector + BM25 search

**The gaps Dream fills:**
- The native system never proactively maintains MEMORY.md (relying on occasional manual AI writes means content only grows, never shrinks)
- The native system has no active handling for MEMORY.md's 20,000-character limit: when exceeded, content is silently truncated — the AI receives no warning and quietly loses the latter half of context, which users rarely notice.
  Dream triggers compression at 18,000 characters, moving stale content into the ledger,
  ensuring MEMORY.md stays within effective bounds and always contains the most current, relevant content
- No permanent archive (ledger) in the native system
- No Re-emergence detection mechanism in the native system

Dream's role is **distiller**, not capturer — and it does not reinvent the search wheel.

---

## File Responsibilities

```
OpenClaw native (Dream read-only)
└── memory/YYYY-MM-DD.md     ← auto-written by compaction flush; Dream reads as source material

Dream actively maintains
├── MEMORY.md                ← updated each distillation, fully injected into context each conversation; brevity is paramount
│                               Hard limit: 18,000 chars (native truncation at 20,000, keeping 2,000 buffer)
│
{DREAM_VAULT_PATH}/
├── ledger.md                ← permanent archive, append-only, never deleted
├── ledger-index.json        ← structured index for ledger retrieval
├── meta/
│   ├── removed-entries.json ← summaries of entries removed from MEMORY.md (for Re-emergence)
│   ├── last-review.txt      ← timestamp of last completed distillation
│   └── dream-state.txt      ← active | hibernating | pending
└── obsidian-index/
    ├── _index.md            ← main content index (reverse chronological)
    └── topics/<topic>.md    ← topic-based classification
```

**Files intentionally omitted:**
- ~~cache.md~~ → handled natively by `memory/YYYY-MM-DD.md`
- ~~custom search index~~ → handled natively by `openclaw memory search`

---

## MEMORY.md Structure Spec

Dream maintains MEMORY.md in three sections, with total character count strictly capped at 15,000:

```markdown
## Current State
<!-- Active projects, unresolved decisions, recent important changes -->
<!-- Changes fastest — check for updates on every distillation -->

## Stable Knowledge
<!-- Tech stack, work environment, decision style, core preferences, repeatedly validated judgments -->
<!-- Changes slowly — only update when new evidence warrants it -->

## Relationships & Context
<!-- Important people, ongoing collaborations, key external context -->
<!-- Update as needed -->

## Dream
<!-- Auto-maintained by Dream skill — do not edit manually -->
<!-- Last 5 ledger entries as one-line summaries, so AI knows what was recently archived permanently -->
```

**Content NOT written to MEMORY.md:**
- Observable real-time facts (uses Mac, prefers dark theme)
- Granular log entries (these live in memory/YYYY-MM-DD.md, searchable anytime)
- Completed/expired state (moved to ledger, then removed from MEMORY.md)

---

## Real-time Capture (During Conversation, Without Waiting for Review)

When the following content is discovered mid-conversation, **write directly to the appropriate MEMORY.md section** (do not wait for 03:30), and also record in the current day's `memory/YYYY-MM-DD.md`:

**Write to MEMORY.md immediately:**
- User explicitly corrects the AI's judgment ("No, actually...") → update **Stable Knowledge**
- User announces an important decision outcome ("I've decided...") → update **Current State**
- User describes a newly started project → update **Current State**

**Write to memory/YYYY-MM-DD.md only, await the 03:30 distillation:**
- Emotional events, preference discussions, opinion expressions
- Single-occurrence information whose importance is not yet certain

Before writing, check MEMORY.md size (`dream-tools.sh --check-size`).
If over 16,000 characters, first compress the oldest completed entries in **Current State**, then write.

---

## Operations

### `dream review` — Daily Distillation (Core)

**Fully automatic, runs silently (no messages pushed when triggered at 03:30).**

Steps:

**Step 1 — Pre-flight Checks**
```
dream-tools.sh --check-idle   → busy? write "pending", retry in 15 min, max until 06:00
dream-tools.sh --check-size   → read current MEMORY.md character count
```

**Step 2 — Read Source Material**

Read `memory/YYYY-MM-DD.md` files added since the last distillation (incremental, no reprocessing).
If no new files exist, skip distillation and only update `last-review.txt`.

**Step 3 — AI Distillation Judgment**

For each journal entry, apply the following rules:

| Decision | Condition | Action |
|----------|-----------|--------|
| Update MEMORY.md | New progress or correction over existing entry | Replace the corresponding line |
| Add to MEMORY.md | Appears across 2+ dates, or single occurrence but clearly important | Append to appropriate section |
| Ledger only | Important but completed/expired; no need to stay in context | Remove from MEMORY.md, archive to ledger |
| Ignore | Filler content, single low-value occurrence, near-duplicate already exists | Discard |

**Re-emergence Check** (required on every distillation):
Compare against `meta/removed-entries.json`. If journal content is semantically similar (>70%) to a previously removed entry, rewrite that entry to MEMORY.md with a `[re-emerged]` tag; elevate its priority so it won't be easily removed in the next distillation. Also append a re-emergence event record to the ledger.

**Step 4 — Character Limit Protection (Run Before Writing)**

```
Projected post-write size > 15,000 chars?
  → Compress oldest completed entries in "Current State": move to ledger, remove from MEMORY.md
  → Compress highest-redundancy entries in "Stable Knowledge": merge similar entries
  → Repeat until projected post-write size ≤ 18,000 chars
```

**Step 5 — Atomic Write to MEMORY.md**
```
dream-tools.sh --atomic-write MEMORY.md <tmpfile>
# Write to .tmp first, validate format and char count (≤ 18,000), then mv to replace
```

**Step 6 — Archive Operations**

For entries judged "ledger only" during this distillation:
```
dream-tools.sh --ledger-append <id> <category> <content>
# Append block to ledger.md, update ledger-index.json
```

Ledger entry format:
```markdown
---
ID: a3f8c201
Archived: 2026-02-27 03:31
Category: [decision]
Content: Decided to use Obsidian instead of Notion for local data ownership and Git sync
Source: memory/2026-02-27.md, first occurrence
---
```

**Step 7 — Update Meta**
- Append today to `active-days.json` (deduplicated)
- Update `last-review.txt`
- Update `## Dream` section: one-line summaries of the last 5 ledger entries (overwrite)

**Step 8 — Review Log (Archived Monthly)**
```
# Append to meta/review-YYYY-MM.md
### YYYY-MM-DD 03:30
Updated: N | Added: N | Archived: N | Re-emerged: N | Ignored: N
MEMORY.md chars: N → N
```

When triggered manually, also output a summary:
```
🌙 Distillation complete
MEMORY.md: N chars (limit 15,000)
This run: updated N | added N | archived N
Permanent archive total: N records
```

---

### Search: Fully Delegated to Native — No Custom Index

```bash
# Everyday search (memory/ directory + MEMORY.md, hybrid vector+BM25)
openclaw memory search "<keyword>"

# Deep retrieval (including permanent archive)
# Step 1: Use native search for memory portion
openclaw memory search "<keyword>"
# Step 2: Search the ledger
dream-tools.sh --ledger-search "<keyword>"
# Step 3: Merge output with source labels
```

`dream search <keyword>` wraps both steps and clearly distinguishes sources in output:
```
🔍 Results for "Obsidian":

── OpenClaw Memory ──
· memory/2026-02-27.md: Decided to use Obsidian instead of Notion...
· MEMORY.md [Stable Knowledge]: Primary note tool: Obsidian...

── Permanent Archive ──
· [a3f8c201] 2026-02-27 [decision] Decided to use Obsidian instead of Notion (archive score 22)

── Obsidian Content Index ──
· OpenClaw + Obsidian Integration Notes (2026-02-15)
```

---

### `dream index <content>` — Add to Obsidian Index

1. Hash-based dedup on URL/title — skip if already exists
2. Extract metadata: title, source, date, topic tags (≤5), one-line summary
3. Append to `obsidian-index/_index.md` and the relevant `topics/<topic>.md`
4. If content clearly reflects user preferences, also write one record to the current day's `memory/YYYY-MM-DD.md` for the next distillation

---

### `dream status` — Status Overview (Read-only Meta, Low IO)

```
🌙 Dream Status — YYYY-MM-DD HH:MM
MEMORY.md: N chars / 18,000 limit (N%)
Permanent archive: N records
Last distillation: YYYY-MM-DD HH:MM (N hours ago)
System state: active / hibernating (dormant N days) / pending (deferred, waiting N min)
Obsidian index: N entries
Pending journals: N files (added since last distillation)
```

---

### `dream forget <description>` — Remove from Memory

Semantic search in `memory/YYYY-MM-DD.md` and MEMORY.md for matching entries and remove them.
No confirmation required — executes immediately.

**Re-emergence mechanism:**
On removal, write the entry summary to `meta/removed-entries.json` along with removal timestamp and content hash.
If the content reappears in a later conversation, automatically trigger re-emergence: rewrite to MEMORY.md and elevate priority.
Content that was forgotten and then reappears is more worth keeping than content that was never forgotten.

Ledger records are not affected by `dream forget` — they are permanently preserved.
On execution, inform the user: "Removed from memory. The permanent archive is unaffected."

---

### `dream init` — Cold-Start Setup

1. Create `{DREAM_VAULT_PATH}` directory structure
2. If MEMORY.md is empty or missing, ask 5 seed questions:
   tool preferences, work environment, the most important current project, core value judgments, the most important relationships
3. Write answers directly into the appropriate MEMORY.md sections (no waiting for distillation)
4. Write `dream-state.txt` = `active`

---

### `dream wakeup` — Wake from Hibernation

Automatically triggered on the first new conversation after 7 consecutive inactive calendar days:
1. Output last 3 ledger entries + current MEMORY.md snapshot summary
2. Restore active state — no content is deleted

---

## Utility Script `dream-tools.sh`

```bash
dream-tools.sh --check-idle
# Query openclaw agent status, return idle / busy

dream-tools.sh --check-size
# Return current MEMORY.md character count (using wc -c)

dream-tools.sh --hash "<content>"
# Return 8-char MD5 short hash for ID generation and dedup

dream-tools.sh --atomic-write <target-file> <tmp-file>
# Validate tmp-file format and char count, then mv to replace target-file

dream-tools.sh --ledger-append <id> <category> <content> [<note>]
# Append a block to ledger.md, update ledger-index.json

dream-tools.sh --ledger-search "<keyword>"
# Search ledger-index.json, return matching entries

dream-tools.sh --dedup-index "<url-or-hash>"
# Check if obsidian-index already has this entry, return exists / new
```

Dependencies: `jq` (JSON), `wc` (character count), `md5sum` (hashing).
No Python or Node required.

---

## Scheduled Trigger (Add to SOUL.md)

```
Run dream review --scheduled every day at 03:30
```

Deferral logic:
- 03:30: check idle → busy → write "pending" → retry in 15 minutes
- Retry window: 03:45 / 04:00 / ... / 06:00
- 06:00: force execute, no further deferral
- Fully silent — no messages pushed; results written to meta/review-YYYY-MM.md

---

## Hibernation Protection

| Condition | Behavior |
|-----------|----------|
| 7 consecutive inactive calendar days | Write "hibernating"; 03:30 heartbeat skips entirely, zero IO |
| First new conversation | Trigger `dream wakeup`; no content deleted |

---

## IO Principles

- All writes go to `.tmp` first, then atomically replaced — crash-safe
- ledger / obsidian-index are append-only, never rewritten
- `status` reads only small meta files — never touches ledger or MEMORY.md body
- In hibernation state, 03:30 heartbeat is skipped entirely — zero file operations
- Character count is forcibly checked before any MEMORY.md write; exceeding 18,000 is not permitted
