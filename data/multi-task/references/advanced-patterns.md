# Advanced Patterns for Multi-Task Orchestration

## Table of Contents

1. [Dependency Handling](#dependency-handling)
2. [Dynamic Batch Sizing](#dynamic-batch-sizing)
3. [Conditional Dispatch](#conditional-dispatch)
4. [Result Aggregation Patterns](#result-aggregation-patterns)
5. [Error Recovery Strategies](#error-recovery-strategies)

---

## Dependency Handling

Most batch tasks are fully independent, but sometimes tasks have partial dependencies. Here are the patterns for handling them.

### Linear Chain

Tasks must execute in sequence: A → B → C

**When this happens:** Each task's output feeds into the next task's input (e.g., extract → transform → load).

**Strategy:** Don't use multi-task for the chain itself. Instead, treat the chain as a single work unit. If you have multiple independent chains, parallelize across chains:

```
Chain 1: A1 → B1 → C1  (single subagent handles the whole chain)
Chain 2: A2 → B2 → C2  (another subagent, runs in parallel with Chain 1)
Chain 3: A3 → B3 → C3  (another subagent, runs in parallel)
```

### Fan-Out / Fan-In

One task produces output that multiple downstream tasks consume, then results merge:

```
        ┌→ B1 ─┐
A ──────┼→ B2 ──┼──→ C (merge)
        └→ B3 ─┘
```

**Strategy:** Execute in phases:
1. **Phase 1:** Run task A (single subagent)
2. **Phase 2:** Read A's output, then dispatch B1, B2, B3 in parallel (include A's output in each prompt)
3. **Phase 3:** Collect all B results, run merge task C

### Partial Dependencies

Some tasks are independent, others depend on specific predecessors:

```
A ──→ C
B ──→ D
A,B → E (needs both A and B)
```

**Strategy:** Build a dependency graph and dispatch in topological order:
1. **Wave 1:** Dispatch A and B in parallel (no dependencies)
2. **Wave 2:** Once A completes, dispatch C. Once B completes, dispatch D. Once both A and B complete, dispatch E.

**Implementation:** Track completion status and dispatch new tasks as their dependencies resolve:
```
pending = {C: [A], D: [B], E: [A, B]}
completed = set()

# After each task completes, check what's now unblocked:
completed.add("A")
for task, deps in pending.items():
    if all(d in completed for d in deps):
        dispatch(task)  # C and potentially E if B is also done
```

---

## Dynamic Batch Sizing

The default wave size of 8-10 works well for most scenarios, but you can adjust based on:

### Task Complexity

| Task type | Suggested wave size | Reason |
|---|---|---|
| Simple file rename/copy | 15-20 | Low resource usage per task |
| Text extraction/parsing | 8-10 | Moderate processing |
| Document generation (DOCX, PDF) | 6-8 | Higher resource usage, more tools |
| Code generation with tests | 4-6 | Complex, may need many tool calls |
| Image generation/processing | 3-5 | Resource-intensive |

### Adaptive Sizing

Start with the default wave size. After the first wave completes:
- If all tasks completed quickly with no errors → increase wave size by 2-3
- If some tasks failed or timed out → decrease wave size by 2-3
- If tasks are taking very long → keep size but add background execution

---

## Conditional Dispatch

Sometimes the operation for each work unit depends on the unit's characteristics.

### Type-Based Routing

When a folder contains mixed file types:

```
/input/
├── report.pdf      → use /pdf skill
├── data.xlsx       → use /xlsx skill
├── summary.docx    → use /docx skill
├── notes.csv       → use /xlsx skill
└── slides.pptx     → use /pptx skill
```

**Strategy:** During the ANALYZE step, group files by type. Each subagent gets a prompt tailored to its file type with the appropriate skill recommendation.

### Content-Based Routing

When the operation depends on file content (e.g., "translate files that are in Chinese, summarize files that are in English"):

**Strategy:** Run a quick pre-scan phase:
1. Dispatch lightweight subagents to classify each file
2. Collect classifications
3. Group by classification and dispatch processing tasks with appropriate instructions

---

## Result Aggregation Patterns

### Simple Collection

Each task produces one output file. Merge step is just listing them:
```
Results:
- task-001/output.md
- task-002/output.md
- ...
```

### Concatenation

Tasks produce text that should be combined into one document:
1. Each subagent writes to `task-NNN/output.md`
2. After all complete, concatenate in task-ID order:
   ```python
   combined = []
   for i in sorted(task_dirs):
       combined.append(read(f"{i}/output.md"))
   write("combined.md", "\n\n---\n\n".join(combined))
   ```

### Structured Merge

Tasks produce structured data (JSON, CSV rows) that should be merged:
1. Each subagent writes a JSON fragment or CSV rows
2. After all complete, merge into a single structured file
3. Handle deduplication if needed

### Report Generation

Tasks produce individual analyses that feed into an aggregate report:
1. Dispatch all analysis tasks in parallel
2. Collect all individual reports
3. Dispatch a final "synthesis" subagent that reads all reports and produces a summary

---

## Error Recovery Strategies

### Automatic Retry

When a task fails, analyze the error type:

| Error type | Retry? | Action before retry |
|---|---|---|
| File not found | No | Check path, fix prompt, retry once |
| Timeout | Yes | Retry with simpler instructions or smaller input |
| Tool error | Yes | Retry — may be transient |
| Wrong output format | No | Fix prompt template, retry once |
| Dependency missing | No | Install dependency first, then retry |

### Partial Results Recovery

If a task partially completed before failing:
1. Check the output directory for any files produced
2. If partial output is usable, note it and don't reprocess the completed portion
3. Construct a retry prompt that continues from where it left off

### Batch-Level Recovery

If an entire wave fails (e.g., shared dependency issue):
1. Fix the root cause
2. Re-dispatch only the failed tasks, not the entire batch
3. Keep successful results from previous waves

### Graceful Degradation

For non-critical batch operations, consider a threshold:
- If >80% of tasks succeed, report partial success and list failures
- If <80% succeed, pause and ask the user whether to continue or fix the underlying issue
