---
name: planning-with-files
version: "5.0.0-tricore"
description: Structured task planning and execution system based on the TriCore architecture. Integrates the 8-layer agent architecture, ReAct, Reflexion, and Plan-Execute-Plan. Completely abolishes scattered plan/findings files in the root directory, unifying workflow and memory management via the deterministic tools/memctl.py.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - default_api:exec
hooks:
  PreToolUse:
    - matcher: "Write|Edit|Bash|Read|Glob|Grep"
      hooks:
        - type: command
          command: "cat memory/state/WORKING.md 2>/dev/null | grep -A 20 '## Active Tasks' || true"
  PostToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "echo '[planning-with-files] Tool executed. Remember to use memctl.py (work_upsert/capture/kb_append) to persist state if a phase or task is completed.'"
---

# Planning with Files (TriCore Edition)

This is a structured task planning system based on the **TriCore** architecture. This skill retains the **cognitive architectures** of ReAct (Reasoning-Action Loop), Reflexion (Self-Reflection), and PEP (Plan-Execute-Plan), but has completely migrated its **storage and execution engine** to the deterministic `tools/memctl.py`.

⚠️ **MAJOR ARCHITECTURAL CHANGE**:
It is absolutely **FORBIDDEN** to create `task_plan.md`, `findings.md`, `progress.md`, or `reflection.md` in the project root directory! All states and memory must be routed to the `memory/` directory via `memctl.py`.

---

## Core Architecture Mapping (Mapping to TriCore)

| Traditional Concept | TriCore Equivalent Implementation | Tool to Use |
|---|---|---|
| `task_plan.md` | The `## Active Tasks` block in `memory/state/WORKING.md` | `python3 tools/memctl.py work_upsert --title "..." --goal "..."` |
| `progress.md` | Task's `ProgressLog` or daily log `memory/daily/*.md` | `python3 tools/memctl.py capture "note"` |
| `findings.md` | Fact base `memory/kb/facts.md` | `python3 tools/memctl.py kb_append facts "..."` |
| `reflection.md` | Decision/Playbook base `memory/kb/decisions.md` (or playbooks.md) | `python3 tools/memctl.py kb_append playbooks "..."` |

---

## Workflow: Plan-Execute-Plan + ReAct + Reflexion

For complex tasks, follow this lifecycle:

### 1. Initial Planning (Planner)
Before starting any complex task, first establish a task card in WORKING.md:
```bash
python3 tools/memctl.py work_upsert --task_id "T$(date +%Y%m%d-%H%M)" --title "Implement new feature X" --goal "Complete user authentication module" --done_when "All unit tests pass and API returns normally"
```

### 2. Execution & ReAct Loop (Executor & ReAct)
1. **Thought**: Decide the next step based on `WORKING.md`.
2. **Action**: Call tools to execute code writing or information searching.
3. **Observation**: Get the returned results of the tools.
4. **Record**: Whenever progress is made or an obstacle is encountered, log it:
   ```bash
   python3 tools/memctl.py capture "Completed writing auth middleware, currently stuck on token validation logic"
   ```
5. **Knowledge Accumulation**: If an important fact is discovered, store it in the knowledge base:
   ```bash
   python3 tools/memctl.py kb_append facts "The JWT library version used by the project is v4, signature algorithm must be RS256"
   ```

### 3. Monitor & Revise (Monitor & Reviser)
If you find that the original plan does not work during execution (e.g., a third-party API is not supported), update the task state and plan:
```bash
# Re-call upsert to update the goal or completion criteria
python3 tools/memctl.py work_upsert --task_id "T20260226-0000" --title "Implement new feature X" --goal "Use OAuth2 to replace the original JWT solution" --done_when "OAuth2 flow is successful"
```

### 4. Task Completion & Self-Reflection (Reflexion)
After the task is completed, reflect and extract the experience as a Playbook or Decision, then archive the task:
```bash
# 1. Write experience into long-term memory
python3 tools/memctl.py kb_append playbooks "When handling Auth in this system: 1. Always use RS256. 2. Token expiration time cannot exceed 1 hour."
# 2. Mark task as done
python3 tools/memctl.py work_done T20260226-0000
```

---

## Critical Rules

### 1. The 3-Strike Error Protocol
- **Attempt 1**: Analyze the error, identify the root cause, and apply a targeted fix.
- **Attempt 2**: Same error? Change the method/library. **NEVER repeat the exact same failing action**.
- **Attempt 3**: Rethink assumptions, search for solutions, update the plan in `WORKING.md`.
- **After 3 Failures**: Write the error log to `memory/daily/` and ask the user for help.

### 2. Code-First Deterministic Updates
It is forbidden to manually modify `WORKING.md` or `MEMORY.md` using tools like `edit`. You must always use the `python3 tools/memctl.py` script to ensure deterministic formatting and structure.

### 3. Memory Search First
When you need to recall previous solutions or context, you must prioritize using `memory_search` for semantic retrieval, rather than directly reading the entire file (QMD mode is forbidden).

---

## When to Use This Skill
- Multi-step complex engineering tasks (>3 steps)
- Research-oriented projects
- Long-term tasks requiring cross-session context retention
- *Note: For simple single-turn Q&A or minor single-file tweaks, handle them directly without creating a full Task card.*