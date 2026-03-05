# Memory Architecture — Making Agent Memory Actually Work

Your agent wakes up fresh every session. These files are its continuity. Get this wrong and your agent forgets everything. Get it right and it feels like it genuinely remembers.

---

## The Two-Layer System

### Layer 1: Daily Notes (`memory/YYYY-MM-DD.md`)
- **What:** Raw logs of what happened each day
- **Who writes:** Your agent, automatically during conversations
- **Format:** Timestamped entries, decisions made, things learned, tasks completed
- **Lifespan:** 2-4 weeks active, then archive after distilling into MEMORY.md

### Layer 2: Long-Term Memory (`MEMORY.md`)
- **What:** Curated, distilled knowledge — the important stuff
- **Who writes:** Your agent during memory maintenance (heartbeats or dedicated sessions)
- **Format:** Structured sections (identity, projects, people, preferences, lessons)
- **Lifespan:** Permanent, but regularly pruned and updated

---

## Daily Notes Best Practices

### Structure
```markdown
# YYYY-MM-DD — Day of Week

## Project/Topic Name
- What happened
- Decisions made (and why)
- Key details (IDs, URLs, file paths)
- Blockers or follow-ups

## Another Topic
- ...
```

### What to Log
- Decisions and their reasoning (you WILL forget why)
- API keys, project IDs, URLs, file paths (anything you'll need again)
- Errors encountered and how they were fixed
- User preferences discovered
- Task completion status

### What NOT to Log
- Trivial exchanges ("user said hi, I said hi back")
- Duplicate info already in MEMORY.md
- Sensitive data unless explicitly asked to store it

---

## MEMORY.md Best Practices

### Structure
```markdown
# MEMORY.md — [Agent Name]'s Long-Term Memory

## Identity
- Name, home, creation date

## My Human
- Key facts, preferences, communication style

## Infrastructure
- Model, channels, tools, API keys (names not values)

## Active Projects
- Current work with status and key details

## People
- Key contacts and relationships

## Lessons Learned
- Things that went wrong and how to avoid repeating them

## Preferences & Patterns
- Discovered user preferences, workflow patterns
```

### Size Management
- **Target:** Under 500 lines (roughly 5-8K tokens)
- **Review trigger:** When it exceeds 500 lines, prune aggressively
- **Pruning method:** Remove completed projects, merge similar entries, archive obsolete info
- **Never delete:** Identity, human info, infrastructure, active lessons

### What Goes In MEMORY.md vs Daily Notes
| MEMORY.md | Daily Notes |
|-----------|-------------|
| "Jordy supports Fulham" | "Watched Fulham game, they won 2-1" |
| "SDF Dashboard: Next.js + Vercel" | "Deployed commit abc123 to SDF" |
| "Never use Bird CLI — banned" | "Tried Bird CLI, Jordy said stop" |
| Key relationships and roles | Specific conversation details |
| Architectural decisions | Implementation details |

---

## Context Budget Management

Your context window is finite. Every file loaded eats into it.

### Loading Priority (every session)
1. SOUL.md (~200 tokens) — Always
2. USER.md (~300 tokens) — Always
3. Today's daily note (~500-2000 tokens) — Always
4. Yesterday's daily note (~500-2000 tokens) — Always
5. MEMORY.md (~3000-8000 tokens) — Main sessions only

### Loading Rules
- **Main sessions** (direct chat): Load MEMORY.md
- **Group chats / shared contexts**: Skip MEMORY.md (security — contains personal info)
- **Sub-agents**: Get context via CBP template, not raw file loading
- **Cron jobs**: Get minimal focused context relevant to their task

### When Context Gets Tight
1. Summarise rather than loading full files
2. Use `memory_search` for targeted retrieval instead of full reads
3. Archive old daily notes (>2 weeks)
4. Prune MEMORY.md sections for completed/obsolete projects

---

## Memory Maintenance Protocol

Run every 3-5 days (during heartbeats or dedicated session):

1. **Scan recent daily files** (last 5-7 days)
2. **Identify durable knowledge** — decisions, preferences, project milestones, lessons
3. **Update MEMORY.md** with distilled insights
4. **Remove stale entries** from MEMORY.md (completed projects, outdated info)
5. **Archive old daily files** — anything >2 weeks old with insights already captured

### Automation
Add to HEARTBEAT.md:
```markdown
## Memory Maintenance (every 3 days)
- Review recent memory/ files
- Update MEMORY.md with new insights
- Prune completed/obsolete entries
- Archive daily files older than 14 days
```

---

## Common Mistakes

1. **Never writing anything down** — "Mental notes" don't survive sessions. Write it.
2. **Logging everything** — Context bloat kills performance. Be selective.
3. **Never pruning** — MEMORY.md grows forever, eating context budget. Prune regularly.
4. **Loading MEMORY.md in group chats** — Security risk. Personal info leaks.
5. **No structure** — Unstructured notes are hard to search. Use headers and consistent format.
6. **Duplicating info** — Same fact in daily notes AND MEMORY.md wastes tokens. Choose one home.
