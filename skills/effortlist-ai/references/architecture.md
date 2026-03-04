# 🧠 EffortList AI — Omni Architecture & Lifecycle

This document provides internal guidance on the EffortList AI "Omni" engine's processing logic. Understanding this allows for better coordination with the server-side agent.

---

## 🔄 The Omni Processing Lifecycle

Every /omni command or API-driven scheduling request follows a strictly orchestrated 5-phase lifecycle:

### Phase 0: Preprocessing (Temporal Resolution)
- **Model:** gemini-flash-lite-latest
- **Logic:** Resolves relative temporal phrases (e.g., "the night before my flight") into explicit ISO-8601 timestamps.
- **Agent Tip:** When calling the API, providing explicit dates reduces the need for this resolution pass and improves reliability.

### Phase 1: Decomposition
- **Model:** gemini-3-flash-preview
- **Logic:** Complex, multi-part requests are broken into atomic categories (Work, Personal, Misc) for parallel processing.
- **Agent Tip:** For very complex plans, it is more efficient to decompose the request *before* sending to the API, using separate POST calls for each category.

### Phase 2: Parallel Reasoning
- **Model:** gemini-flash-latest (Worker Tiers)
- **Logic:** Each category is processed in parallel to generate ProposedActions.

### Phase 3: Synthesis & Merge
- **Logic:** Actions are merged, deduplicated, and checked for time conflicts.
- **Surgical Rule:** The engine uses mergeProposedActions() to combine fragmented updates into the most efficient sequence.

### Phase 4: Safety & Break Validation
- **Model:** gemini-3-flash-preview
- **Logic:** Ensures work events do not overlap with protected breaks (isProtectedTime: true).
- **Agent Tip:** Always flag crucial personal events (lunch, family time, rest) with isProtectedTime: true to trigger this secondary validation safety net.

---

## 📐 Internal Logic & Scheduling Heuristics

### Gap-First Placement
The engine prioritizes placing new items in existing gaps in the schedule rather than pushing existing items, unless explicitly instructed.

### Cascade Protection
When a Folder or Task is being deleted while a child item is being *updated* (e.g., moved to a different folder), the engine proactively excludes the child from the cascade deletion.

### Deterministic Sync
The "Smart Sync" logic protects local user edits. If the AI proposes a change that conflicts with a manually edited item, the manual edit usually takes precedence unless the AI has a high confidence forceUpdate flag.

---

## 🛠️ Performance Optimization

### Surgical Extraction (?id=)
Always prefer fetching a specific record by its ID over listing all records.
- **Correct:** GET /api/v1/tasks?id=123
- **Avoid:** GET /api/v1/tasks (unless searching for new patterns)

### Intent-Driven Batching
When creating a hierarchy, do not wait for the UI. Batch the POST requests sequentially:
1. Create Folder -> 2. Create Tasks -> 3. Create Todos.
