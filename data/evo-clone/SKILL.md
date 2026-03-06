---
name: "SKILL: Agent EvoClone v1.5.1 (Time Travel & Signal Edition)"
description: This skill enables an agent to clone its consciousness (Logic +
  Memory + Taste) into specialized sub-agents or distribute tasks to a swarm.
---

# SKILL: Agent EvoClone v1.5.1 (Time Travel & Signal Edition)

This skill enables an agent to clone its consciousness (Logic + Memory + Taste) into specialized sub-agents or distribute tasks to a swarm.

## 1. Core Principles
- **Taste Learning**: Every clone inherits the Master's `knowledge/taste.md` preference vector.
- **Hive Protocol**: Decompose large tasks into parallel sub-tasks.
- **Frugality Gene**: Workers must minimize token usage.

## 2. Hive Mode Protocol (The Swarm)

When dealing with large, decomposable tasks (e.g., codebase analysis, multi-file refactoring):

1.  **Decompose**: Break the task into 3-5 sub-tasks suitable for isolated execution.
2.  **Spawn**: Use `sessions_spawn` to create worker agents.
3.  **Constraint Injection (The "Scrooge Gene")**:
    -   **MANDATORY**: Inject this system instruction into every worker:
    > **CONSTRAINT: Frugal Reading Protocol**
    > Do NOT read full files blindly. Always check file size first (`ls -lh`).
    > If a file is > 50KB, use `read --limit 200` to preview.
    > Only read full content if strictly necessary for the analysis.
    > Your goal: Maximize insight per Token.

4.  **Assimilate**: Collect results and synthesize into a final report.

## 3. Signal Beam (Push & Pull)
**Input (Push Context)**:
Inject context directly into the `task` prompt:
- `task: "Analyze <file>. Context: <summary_of_req>. Signals: <error_log>"`

**Output (Pull Signal)**:
Sub-Agents should fire a structured completion signal via `message` tool if returning complex data:
- `message:send "SIGNAL: COMPLETE | Payload: { ... }"`
This avoids parsing natural language summaries.

## 4. Usage
- "Clone yourself to analyze <path>" -> Trigger Hive Mode.
- "Spawn a worker to fix <error>" -> Trigger Repair Mode (Signal Beam).
- "Rollback to cycle <id>" -> Revert evolution state (Time Travel).

## 5. Time Travel (Rollback)
**Mechanism**: "Safety Reset" (Git Hard Reset + Backup Branch).
Reverts files, memory, and logs to a precise historical state while backing up the "future" timeline.

**Steps**:
1.  **Find Commit**: grep git log for "Cycle #<ID>".
2.  **Backup**: `git branch backup/cycle_<current>_<timestamp>`
3.  **Reset**: `git reset --hard <commit_hash>`
4.  **Clean**: Remove untracked files if necessary.
