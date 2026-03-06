---
name: memory-architect
description: "Restructure flat MEMORY.md files into a tiered memory system with an entity graph. Use when: (1) MEMORY.md is growing unwieldy or exceeds 150 lines, (2) user asks to organize/restructure/tier memory, (3) context compaction is losing important details, (4) you need structured entity lookup (people, projects, properties, contacts) instead of scanning markdown. Triggers on organize my memory, memory is too big, restructure memory, tier my memory, make memory more efficient."
---

# Memory Architect

Split a monolithic MEMORY.md into three tiers plus a structured entity graph.

## Architecture

```
MEMORY.md              → Router (30 lines max). Points to tiers.
memory/protocols.md    → HOT: Stable workflows, shortcuts, procedures. Read on session start.
memory/active.md       → WARM: Current projects, waiting-on, live context. Check before acting.
memory/archive.md      → COLD: Completed work, historical reference. Search when needed.
memory/ontology/graph.jsonl → Structured entities + relations (JSONL append-only)
```

## Process

### 1. Analyze the existing MEMORY.md

Read the full file. Classify each section:

| Content type | Tier | Examples |
|-------------|------|---------|
| Stable workflow / procedure | protocols | Emoji shortcuts, deploy steps, tool usage rules |
| Active project / waiting-on | active | Current builds, pending replies, live URLs |
| Completed work / reference data | archive | Done tasks, contact lists, account tables, old decisions |
| Named entity with properties | ontology | People, orgs, projects, properties, locations |

### 2. Create the tier files

Write each tier file with a header comment explaining its purpose and update frequency.

**protocols.md rules:**
- Only procedures that rarely change
- Include the exact commands (copy-pasteable)
- No project-specific state

**active.md rules:**
- Only things with a next action or pending status
- Include "Waiting On" section at bottom
- Prune completed items to archive on each update

**archive.md rules:**
- Completed work grouped by date or category
- Reference data (contacts, accounts, chat IDs)
- Keep searchable — use headers and tables

### 3. Extract entities to ontology

For each named person, organization, project, property, or location, create a JSONL entry:

```jsonl
{"op":"create","entity":{"id":"p_alice","type":"Person","properties":{"name":"Alice","email":"alice@example.com","role":"Engineer"}},"timestamp":"2026-01-01T00:00:00Z"}
{"op":"relate","from":"p_alice","rel":"member_of","to":"org_acme","timestamp":"2026-01-01T00:00:00Z"}
```

**ID conventions:**
- People: `p_shortname`
- Organizations: `grp_name` or `org_name`
- Projects: `proj_name`
- Properties/locations: `prop_name` or `loc_name`

**Relation types:** `member_of`, `owns`, `collaborates_on`, `interested_in`, `guides`, `uses`, `listed_by`, `located_at`

### 4. Rewrite MEMORY.md as router

Replace MEMORY.md with a ~25-line index that:
- Lists the three tiers with one-line descriptions
- Notes the ontology location
- Preserves any system directives (NO_REPLY rules, heartbeat instructions)
- Contains zero project-specific content

### 5. Verify

```bash
wc -l MEMORY.md memory/protocols.md memory/active.md memory/archive.md memory/ontology/graph.jsonl
```

Targets: MEMORY.md under 30, protocols under 100, active under 80, graph = 1 line per entity/relation.

## Maintenance

### On each session
- Read `memory/protocols.md` (always)
- Scan `memory/active.md` (always)
- `memory/archive.md` — only on `memory_search` or explicit request

### When adding new information
- New procedure → protocols.md
- New project/active item → active.md
- Completed item → move active → archive
- New person/org/project → append to graph.jsonl

### Entity queries
```bash
grep "p_forrest" memory/ontology/graph.jsonl
grep '"type":"Project"' memory/ontology/graph.jsonl
cat memory/ontology/graph.jsonl | jq -r 'select(.entity?.type=="Person") | .entity.properties.name'
```
