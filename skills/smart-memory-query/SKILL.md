---
name: smart-memory-query
description: "Enforce proactive, query-optimized memory_search usage. Must run memory_search when (1) prior context is referenced, (2) a new task starts, or (3) a proper noun appears. Build short 2–4 token queries by splitting intent to avoid empty AND-based FTS results."
always: true
---

# Smart Memory Query

## Trigger: run `memory_search` when any of these apply

- **T1 Prior context**: user references previous decisions, agreements, or history (e.g., “we decided this before”).
- **T2 New task**: before starting a new topic/task, check prior preferences/decisions.
- **T3 Proper noun**: project, tool, service, or person name appears.

If unsure, search. Missed context costs more than one extra search. If multiple triggers fire, run separate searches per trigger.

## Query-building rules (required)

1. **Split intent** — break search intent into 2–3 independent angles. Do not overpack one query.
2. **Extract core tokens** — keep only 2–3 key nouns per angle; prioritize proper nouns.
3. **Run multi-query** — call `memory_search` per angle, with **2–4 tokens per query**.
4. **Merge results** — if all are empty, retry once with a single key proper noun.

## Examples

**T1** “We changed to keep iCloud downloads before, right?”
- ❌ `memory_search("user preference root-cause config first suggestion keep iCloud downloads")`
- ✅ `memory_search("iCloud download setting")` + `memory_search("problem-solving preference")`

**T1** “Didn’t we plan to migrate to a better structure first?”
- ❌ `memory_search("better structure migration FTS path title RRF exact tie-break")`
- ✅ `memory_search("FTS structure migration")` + `memory_search("RRF tie-break design")`

**T2** “Let’s start Paddle payment integration.”
- ❌ no `memory_search`
- ✅ `memory_search("Paddle payment")` + `memory_search("payment integration decision")`

**T3** “OpenClaw search quality is still poor.”
- ❌ `memory_search("OpenClaw search quality is still poor")`
- ✅ `memory_search("OpenClaw search")` + `memory_search("search quality tuning")`

**T1+T3** “What happened after switching to bge-m3?”
- ❌ `memory_search("what happened after switching to bge-m3")`
- ✅ `memory_search("bge-m3 migration result")` + `memory_search("embedding model change")`

**T2** “Set up the new project documentation structure.”
- ❌ no `memory_search`
- ✅ `memory_search("documentation structure preference")` + `memory_search("project template")`
