# Memory System — 3-Layer Architecture

## Overview

The system uses a three-layer memory architecture to balance persistence, recency, and accessibility.

## Layer 1: MEMORY.md (Long-term, Curated)

- Loaded into context per session
- Manually curated key facts, decisions, patterns
- Each agent has its own MEMORY.md
- Leader MEMORY.md is the master record
- Updated during daily cron consolidation + significant events

## Layer 2: Daily Notes (Short-term, Raw)

- `memory/YYYY-MM-DD.md` files
- Raw daily logs of activities, decisions, observations
- Each agent writes to its own `memory/` directory
- Input source for daily consolidation
- QMD-indexed for semantic search

## Layer 3: Shared Knowledge Base (Permanent, Reference)

- `shared/` directory (symlinked into all workspaces)
- Brand profiles, content guidelines, industry knowledge
- Operations docs, approval workflow, channel map
- Error solutions KB
- QMD-indexed for semantic search

## Write Permissions

| Agent | Own memory/ | Own MEMORY.md | shared/ | Mechanism |
|-------|------------|---------------|---------|-----------|
| Leader | Direct | Direct | Direct | Owner feedback → direct; agent KB_PROPOSE → evaluate |
| Content, Designer, Operator | Direct | Direct | Propose only | `[KB_PROPOSE]` → Leader |
| Researcher | Direct | Direct | Propose only | `[KB_PROPOSE]` → Leader |
| Engineer | Direct | Direct | Propose + errors/ | `[KB_PROPOSE]` → Leader; `shared/errors/solutions.md` direct |
| Reviewer | None | None | Propose only | `[KB_PROPOSE]` → Leader; review results recorded by Leader |

## Knowledge Capture Flow

```
Agent completes task → Identifies reusable insight →
  Includes [KB_PROPOSE] in response → Leader receives and evaluates:
    From owner-confirmed context → Apply directly to shared/
    From agent inference → Ask owner before applying
```

## QMD Semantic Search

- Engine: QMD (built into OpenClaw)
- Re-index interval: Every 5 minutes (automatic)
- Indexes: daily-notes, agent-skills, shared-knowledge

## Consolidation Cycle

Daily cron job (recommended: run after owner's typical end-of-day):
1. Read all agents' daily notes
2. Extract key insights, decisions, patterns
3. Update Leader MEMORY.md
4. Check for cross-agent learnings
5. Flag stale approval items
6. Post summary to Operations channel
