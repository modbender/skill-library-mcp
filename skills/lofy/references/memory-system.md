# Memory System — Brain-Inspired Architecture

## Design Philosophy

The human brain doesn't store raw data — it builds mental models. It forgets noise, strengthens what's used, and connects related ideas. This system mimics that.

**Core principle: More data should make you BETTER, not slower.**

## 5-Layer Architecture

### 1. Working Memory → Current Conversation
- Active chat context (what the LLM sees now)
- Brain analog: Prefrontal cortex, ~7±2 items
- Only load what's relevant to THIS conversation

### 2. Short-Term Memory → Daily Logs (`memory/YYYY-MM-DD.md`)
- Raw notes from each day — events, decisions, conversations
- Brain analog: Hippocampus (temporary storage)
- Lifespan: 14 days raw, then consolidated
- Max 30 lines per day, bullet points, just facts

### 3. Long-Term Declarative → `MEMORY.md`
- Curated facts, preferences, lessons, key events
- Brain analog: Neocortex (permanent storage)
- Max 100 lines — compress oldest when over limit
- Types:
  - **Semantic** (facts): "User likes Thai food", "Python is primary language"
  - **Episodic** (events): "2026-03-01: Got job offer from Acme"
- `[PINNED]` items are permanent — never auto-deleted

### 4. Long-Term Procedural → Profile Files & Skills
- How to do things, patterns, project knowledge
- Brain analog: Cerebellum (skills & procedures)
- Living documents — old info gets REPLACED, not appended

### 5. Salience Tagging
- How important something is
- Brain analog: Amygdala (emotional significance)
- High salience (always keep): career milestones, personal records, explicit "remember this"
- Low salience (can decay): routine events, weather, casual mentions

## Memory Lifecycle

```
Day 0-7:   Raw daily logs (full detail)
Day 7-14:  Compressed logs (key events only)
Day 14+:   Extract insights → MEMORY.md, delete raw logs
Permanent: [PINNED] items, profile facts, lessons learned
```

## Maintenance Schedule

During heartbeats (every few days):
1. Read recent `memory/YYYY-MM-DD.md` files
2. Identify significant events worth keeping long-term
3. Update `MEMORY.md` with distilled learnings
4. Remove outdated info from MEMORY.md
5. Compress or delete old daily logs past 14 days
