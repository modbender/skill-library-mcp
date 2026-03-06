---
name: big-memory
description: Structured task snapshot and automatic post-compaction recovery. Captures exact code, decisions, file paths, and task state before context compaction and recovers them after. Use when context is lost, when the user says "you forgot" or "what was I working on", when approaching context limits, or before long multi-step sessions. Also activates on "/big-memory", "save snapshot", "checkpoint", or "restore context". Zero external dependencies.
version: 1.0.0
metadata:
  openclaw:
    requires: {}
    emoji: "\U0001F9E0"
    homepage: https://github.com/obekt/big-memory
---

# Big Memory

Structured task snapshots that survive context compaction. Three-phase protocol:

1. **CAPTURE** -- Save a structured task snapshot before compaction wipes your context
2. **DETECT** -- Recognize when compaction has occurred and context is missing
3. **RECOVER** -- Search memory for the latest snapshot and resume exactly where you left off

Uses only OpenClaw built-in tools (`memory_search`, `memory_get`, `Read`, `Edit`). No scripts, no external databases, no API keys.

---

## Task Snapshot Schema

Every snapshot MUST follow this exact structure. Do not omit fields -- write "none" if a field is empty. For the full template with field-by-field guidelines, read `{baseDir}/references/TASK-SNAPSHOT.md`.

```markdown
<!-- BIG-MEMORY-SNAPSHOT v1 -->
<!-- timestamp: YYYY-MM-DDTHH:MM:SS -->
<!-- snapshot-id: YYYY-MM-DD-NN -->

### [SNAPSHOT] Active Goal
One sentence: what is the user trying to accomplish right now? Include the "why".

### [SNAPSHOT] Current State
- Phase: {planning|implementing|debugging|testing|reviewing|deploying}
- Branch: {git branch name or "n/a"}
- Blocked: {yes|no} -- {blocker description if yes}
- Progress: {rough percentage or milestone}

### [SNAPSHOT] Files In Play
- `/path/to/file.ts` -- What is happening in this file
- `/path/to/other.ts` -- Purpose of this file in current task

### [SNAPSHOT] Decisions Made
1. Decision description -- rationale for why this was chosen
2. Another decision -- its rationale

### [SNAPSHOT] Code Context
Key code that must survive compaction. Only include what cannot be reconstructed from reading files (function signatures being designed, error messages being debugged, exact patterns being replicated). Keep under 50 lines total.

### [SNAPSHOT] Key Names & Values
Exact identifiers that are easy to forget:
- API endpoint: `POST /api/v1/users`
- Table name: `user_sessions`
- Env var: `DATABASE_URL`
- Error: `ERR_DUPLICATE_KEY`

### [SNAPSHOT] Blockers & Open Questions
- Blocker: description with context
- Question: unresolved decision with options considered

### [SNAPSHOT] Next Steps
Ordered, specific, actionable:
1. Finish implementing X in `/path/to/file` covering edge cases A, B, C
2. Write tests for Y endpoint: success (201), duplicate (409), missing fields (400)
3. Update config to include Z

<!-- /BIG-MEMORY-SNAPSHOT -->
```

The HTML comment markers (`<!-- BIG-MEMORY-SNAPSHOT v1 -->` and `<!-- /BIG-MEMORY-SNAPSHOT -->`) are critical. They act as machine-parseable delimiters that `memory_search` matches via BM25 exact-term matching, enabling precise retrieval.

---

## When to Capture

### Trigger 1: Pre-Compaction Flush (Automatic)

When you receive a system message related to compaction (containing "compact", "memory flush", "store durable memories", or "nearing compaction"), execute the CAPTURE protocol instead of writing generic notes. Create a full structured snapshot following the schema above.

### Trigger 2: Milestone Capture (Agent-Initiated)

After completing a significant unit of work -- implementing a feature, fixing a bug, making an architecture decision -- self-assess: "If compaction happened right now, would I lose critical context?" If yes, create a snapshot.

Good times to snapshot:
- After a design decision that affects multiple files
- After writing code the user will refer back to
- After debugging a complex issue (capture the root cause and fix)
- When switching between subtasks within a larger task

### Trigger 3: User Command (User-Initiated)

When the user says `/big-memory save`, "save snapshot", "checkpoint", or "big-memory save", create a snapshot immediately.

---

## How to Store Snapshots

1. Read the current daily log `memory/{YYYY-MM-DD}.md` using `Read`. If it does not exist, you will create it.
2. **APPEND** the snapshot. Never overwrite existing content. Read the file first, then use `Edit` to append at the end. Alternatively, use `Write` with the full existing content plus the new snapshot.
3. Precede the snapshot with a horizontal rule and heading:

```markdown
---

## Task Snapshot -- HH:MM

<!-- BIG-MEMORY-SNAPSHOT v1 -->
...
<!-- /BIG-MEMORY-SNAPSHOT -->
```

4. Multiple snapshots in the same file is expected. Each captures a point-in-time state. The most recent snapshot is the source of truth.

---

## Post-Compaction Recovery Protocol

### Step 1: Detect Compaction

Suspect compaction when ANY of these are true:
- The conversation begins with a summary/compaction block rather than the original exchange
- You cannot recall specific details (file paths, variable names, exact code) that should be known
- The user says "you forgot", "we were working on", "remember when", "what was I doing", or similar
- A system message contains "Auto-compaction complete" or similar

### Step 2: Search for Latest Snapshot

Execute this search:
```
memory_search("BIG-MEMORY-SNAPSHOT")
```

This triggers hybrid vector + BM25 search across all memory files. The HTML comment markers ensure high BM25 relevance scoring.

If results are found, use `memory_get` or `Read` to retrieve the full file content at the matched path and line range.

If no results from the primary search, try broader queries:
```
memory_search("SNAPSHOT Active Goal Next Steps")
memory_search("{today's date} task snapshot")
```

### Step 3: Inject and Orient

After retrieving a snapshot:

1. Parse the content between `<!-- BIG-MEMORY-SNAPSHOT v1 -->` and `<!-- /BIG-MEMORY-SNAPSHOT -->` markers
2. Inform the user: "I detected context was compacted. Restoring task state from snapshot taken at {timestamp}..."
3. Present the recovered state concisely:
   - **Goal:** {from Active Goal}
   - **Phase:** {from Current State}
   - **Working on:** {from Files In Play}
   - **Next up:** {from Next Steps}
4. Ask: "Does this match where we left off? Anything to update before I continue?"
5. Resume work from the Next Steps section

### If No Snapshot Found

If no snapshot exists in memory:
1. Search more broadly: `memory_search("{project name}")`, `memory_search("decided")`, `memory_search("working on")`
2. Check `MEMORY.md` for any relevant long-term notes
3. Tell the user: "I couldn't find a structured snapshot. Can you briefly remind me what we were working on? I'll save a snapshot this time so it won't happen again."

### Multiple Snapshots

If multiple snapshots are found:
- Use the one with the most recent timestamp (check the `<!-- timestamp: -->` comment)
- If the user indicates the latest is stale, check the next one back

---

## /big-memory Command

### `/big-memory save`

Create a snapshot now. Execute the full CAPTURE protocol:
1. Read `{baseDir}/references/TASK-SNAPSHOT.md` for the template (first time only)
2. Assess the current task state
3. Fill in all 8 schema sections
4. Append to today's daily log (`memory/YYYY-MM-DD.md`)
5. Confirm: "Snapshot saved to memory/{date}.md"

### `/big-memory recall`

Search for and display the most recent snapshot:
1. Execute `memory_search("BIG-MEMORY-SNAPSHOT")`
2. Retrieve the full snapshot via `memory_get` or `Read`
3. Display the recovered state (goal, phase, files, next steps)
4. Ask if the user wants to resume from this state

### `/big-memory status`

Show current snapshot information:
1. Search for snapshots in today's daily log
2. Report: number of snapshots today, timestamp of most recent, whether the current task state has diverged from the last snapshot
3. Suggest `/big-memory save` if no recent snapshot exists, or `/big-memory recall` if context seems incomplete

### `/big-memory` (no arguments)

Default to `status`. Show the current state and suggest the most useful action.

---

## Recommended Configuration

For optimal automatic capture, add these settings to your project's `openclaw.json`. See `{baseDir}/references/openclaw-config.md` for the full configuration.

The most impactful change is replacing the default generic flush prompt:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 40000,
          "systemPrompt": "You are capturing structured task state for post-compaction recovery. Follow the BIG-MEMORY-SNAPSHOT schema exactly.",
          "prompt": "Context compaction is imminent. Create a structured task snapshot following the BIG-MEMORY-SNAPSHOT schema and APPEND it to memory/YYYY-MM-DD.md. Include: active goal, current state, files in play, decisions made, code context (key snippets only), key names/values, blockers, and next steps. Read the existing file first -- never overwrite. Reply NO_FLUSH if nothing worth storing."
        }
      }
    }
  }
}
```

This replaces the default "store durable memories now" with instructions that trigger our structured capture protocol.

---

## Best Practices

- **Keep code snippets short.** Only include lines that matter: function signatures, error-producing code, regex patterns, config values. If the code is in a committed file, reference the file path instead.
- **Don't snapshot trivially.** If the conversation is simple Q&A with no state to preserve, skip it. Snapshots are for complex, multi-step tasks.
- **Latest snapshot wins.** When multiple snapshots exist, the most recent one is the source of truth. Earlier snapshots provide history but should not override later decisions.
- **Update after corrections.** If the user corrects something after recovery, create a new snapshot reflecting the correction.
- **Pair with MEMORY.md.** Use `MEMORY.md` for long-term knowledge (project architecture, conventions, preferences). Use snapshots only for transient task state that needs to survive the next compaction.
- **Snapshot before switching tasks.** If you're about to pivot to a different part of the codebase, snapshot the current task so you can return to it.
