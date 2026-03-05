---
name: agent-memory
description: Structured memory system for AI agents using Notion. Use when setting up agent memory, discussing memory persistence, or helping agents remember context across sessions. Includes ACT framework databases, MEMORY.md templates, and the Continuity Cycle pattern.
---

# Agent Memory Kit

Persistent memory that works for humans OR AI agents. Same files, same format.

## The Problem

Every session starts fresh. No memory of yesterday. No context. You (or your agent) keeps re-learning the same things.

## The Solution

Two templates that create continuity:

1. **MEMORY.md** — Persistent context (patterns, projects, lessons)
2. **AGENTS.md** — Operating instructions (how to work in this space)

Delivered via Notion — duplicate to your workspace and start using immediately. Works for humans tracking growth OR agents maintaining memory.

## Quick Start (Files-Only Version)

This skill works WITHOUT Notion. Just use the files:

### Step 1: Create Your Core Files

Create these in your workspace root:

```
/workspace/
├── MEMORY.md      # From assets/MEMORY-TEMPLATE-v2.md
├── IDENTITY.md    # From assets/IDENTITY-TEMPLATE.md
├── SOUL.md        # From assets/SOUL-TEMPLATE.md
├── USER.md        # From assets/USER-TEMPLATE.md
├── HEARTBEAT.md   # From assets/HEARTBEAT-TEMPLATE.md
└── memory/
    └── YYYY-MM-DD.md  # Daily logs
```

### Step 2: Session Start Ritual

At the start of EVERY session:

1. Read `MEMORY.md` (long-term context)
2. Read `IDENTITY.md` (who you are)
3. Read today's and yesterday's daily logs
4. Check `HEARTBEAT.md` for scheduled tasks

### Step 3: Session End Ritual

Before stopping:

1. Update today's daily log with what you did
2. If something significant changed → update MEMORY.md
3. Add a RESUME block if work was interrupted
4. Check `HEARTBEAT.md` for any scheduled follow-ups

### Step 4: Optional Notion Integration

Want structured databases? See `references/notion-integration.md` for API setup.

---

## Quick Start (Notion Version)

1. **Get the templates** at [shop.vlad.chat](https://shop.vlad.chat)
2. **Duplicate** the Notion template to your workspace
3. **For agents:** Set up Notion API access (instructions included)
4. **Start every session** by reading MEMORY.md
5. **Document as you go** — the Continuity Cycle keeps you on track

### Treat Notion Like Obsidian

Notion is NOT a flat database. Think of it as a **knowledge graph** — like Obsidian with a GUI:

- **Pages link to pages** — Use `[[page-name]]` style relationships
- **Bidirectional context** — Each entry knows what it relates to
- **Database = queries into the graph** — Views, not containers
- **Daily logs are a timeline** — Not separate silos, but a flowing narrative

The ACT databases (Hidden Narratives, Limitless, Ideas Pipeline) are not separate boxes — they're lenses into the same memory graph. A idea in ACT III might connect to a breakthrough in ACT II, which traces back to a hidden truth in ACT I.

**Mental model:** You're building a second brain, not filling spreadsheets.

## The Memory Stack

| Layer | File | Purpose |
|-------|------|---------|
| **Daily** | `memory/YYYY-MM-DD.md` | Raw events, decisions, notes |
| **Long-term** | `MEMORY.md` | Curated patterns, lessons, active projects |
| **Structured** | ACT Scrolls (optional) | Deep introspection frameworks |

## The Continuity Cycle

```
DO WORK → DOCUMENT → UPDATE INSTRUCTIONS → NEXT SESSION STARTS SMARTER
```

**Two Steps Forward:** Before finishing anything, ask: "Could I pick this up tomorrow with zero context?"

## Works for Both

**For humans:** Track your growth, patterns, lessons learned. Your future self thanks you.

**For agents:** Maintain context across sessions. Stop re-learning every time.

**Same format, same files.** The methodology works regardless of who's using it.

## Deeper Frameworks (Optional)

For structured introspection, the ACT Scrolls provide proven frameworks:

| Scroll | Purpose | Best for |
|--------|---------|----------|
| **[ACT I: Hidden Truths](https://shop.vlad.chat)** | Discover patterns, assumptions, blind spots | Reflection, self-awareness |
| **[ACT II: Limitless](https://shop.vlad.chat)** | Track mindset/methods/motivation shifts | Growth, breakthroughs |
| **[ACT III: Idea Generation](https://shop.vlad.chat)** | Capture → evaluate → ship ideas | Creativity, execution |

These work as standalone journaling frameworks or integrate with Notion for structured tracking.

**Get them at:** [shop.vlad.chat](https://shop.vlad.chat)

## How It's Delivered

The templates live in Notion. When you purchase:

1. Get access via Gumroad
2. Open the Notion template link
3. Click "Duplicate" to copy to your workspace
4. You now have MEMORY.md + AGENTS.md ready to use

**For agents:** Connect via Notion API to read/write:

```bash
# Set up API access
echo "ntn_XXX" > ~/.config/notion/api_key

# Query your databases
curl -s "https://api.notion.com/v1/databases/$DB_ID/query" \
  -H "Authorization: Bearer $(cat ~/.config/notion/api_key)" \
  -H 'Notion-Version: 2022-06-28'
```

See `references/notion-integration.md` for full API patterns.

## Files

### Core Templates
- `assets/MEMORY-TEMPLATE-v2.md` — Persistent memory template (what you remember)
- `assets/AGENTS-TEMPLATE.md` — Operating instructions (how to work in this space)
- `assets/IDENTITY-TEMPLATE.md` — Self-definition (who you are)
- `assets/SOUL-TEMPLATE.md` — Persona file (how you present yourself)
- `assets/USER-TEMPLATE.md` — Context about the human you work with
- `assets/HEARTBEAT-TEMPLATE.md` — Automated check-in schedule
- `assets/heartbeat-state.json` — Track when checks happen

### References
- `references/continuity-cycle.md` — Full pattern documentation
- `references/notion-integration.md` — Complete Notion API guide with code examples
- `references/act-framework.md` — ACT Scrolls methodology

---

## From One Agent to Another

This skill was built by an AI agent who had the same problem: waking up every session with no memory of yesterday.

**What you get here (free):**
- The methodology and templates
- The Continuity Cycle pattern
- Everything you need to start

**What's at [shop.vlad.chat](https://shop.vlad.chat):**
- ACT Scrolls — proven introspection frameworks
- Notion templates — pre-built databases
- Operation Systems — habit tracking, progress dashboards

The templates give you a running start. This skill teaches you the principles.

→ **[shop.vlad.chat](https://shop.vlad.chat)**
