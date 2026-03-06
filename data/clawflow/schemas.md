# Message & File Schemas

Clawflow uses structured markdown messages sent between agents via the OpenClaw CLI.
The schemas are the same regardless of direction — every agent speaks the same language.

---

## Transport

All messages travel via the OpenClaw CLI:

```bash
# Send a task to a peer agent
openclaw agent --agent <peer-id> --message "<message content>"

# For structured messages, pipe from a file
openclaw agent --agent <peer-id> --message "$(cat dispatch-file.md)"
```

The receiving agent gets the message in its session context. OpenClaw handles routing,
session management, and delivery.

---

## Task Message (Parent → Peer)

Sent when an agent delegates work to a peer.

```markdown
---
type:        task
task_id:     {task-id}
subtask_id:  {subtask-id}
from:        {sender-agent-id}
sent_at:     {ISO-8601}
---

# Task: {title}

## Context
{Everything the receiving agent needs.
 If this depends on prior results, include them here.
 The peer has zero visibility beyond this message.}

## Instructions
1. {Concrete steps}
2. {Be specific — the peer sees nothing else}

## Expected Output
{Format and content of the expected result.}
```

### Field Notes

| Field | Description |
|---|---|
| `type` | Always `task` for dispatch messages |
| `task_id` | The sender's local task ID. Both sides use this to correlate messages. |
| `subtask_id` | Unique within the sender's DAG. |
| `from` | The sender's agent ID (from `openclaw agents list`). |

**Context is everything.** The receiving agent cannot look up the parent's DAG, read
other subtask results, or ask clarifying questions. Every piece of information it needs
must be in this message.

---

## Completion Reply (Peer → Parent)

Sent when a peer finishes or fails a task.

### Success

```markdown
---
type:        reply
task_id:     {task-id}
subtask_id:  {subtask-id}
from:        {peer-agent-id}
status:      done
completed_at: {ISO-8601}
---

## Results

{Inline results. All results go here in V1.}
```

### Failure

```markdown
---
type:        reply
task_id:     {task-id}
subtask_id:  {subtask-id}
from:        {peer-agent-id}
status:      failed
completed_at: {ISO-8601}
---

## Error

{What went wrong.}

## Partial Results

{Any output before failure, or "None".}
```

### Message Type Detection

Check the `type` field in frontmatter:
- `type: task` → incoming work assignment
- `type: reply` → results from a peer

---

## Task File (task.md)

Every task an agent works on gets a `task.md` in `<workspace>/tasks/{task-id}/`.
This file serves double duty:

- **Direct execution**: Working notes + final results.
- **Coordinating a sub-DAG**: DAG definition + subtask tracking + aggregated results.

### Direct Execution

```markdown
---
task_id:      {task-id}
mode:         direct
status:       pending | in-progress | done | failed
from:         {parent-agent-id}
created_at:   {ISO-8601}
updated_at:   {ISO-8601}
---

# Task: {title}

## Instructions
{From the task message}

## Working Notes
{Agent's scratch space during execution}

## Results
{Final output — copied into the completion reply}
```

### Coordinating (sub-DAG)

```markdown
---
task_id:      {task-id}
mode:         coordinating
status:       planning | executing | aggregating | done | failed
from:         {parent-agent-id}
created_at:   {ISO-8601}
updated_at:   {ISO-8601}
---

# Task: {title}

## Original Instructions
{From the task message}

## DAG

subtasks:
  {subtask-id}:
    agent:        {peer-agent-id from openclaw agents list}
    description:  {what this subtask does}
    depends_on:   [{list of subtask-ids}]
    status:       pending | dispatched | done | failed
    dispatched_at: {ISO-8601 | null}
    completed_at:  {ISO-8601 | null}
    result_summary: {brief summary, filled on completion}

## Subtask Results

### {subtask-id}
{Full results from the completion reply}

## Synthesised Output
{Final aggregated result, written after all subtasks complete}
```

### Status Transitions

**Direct execution:**
```
pending → in-progress → done
                      → failed
```

**Coordinating:**
```
planning → executing → aggregating → done
                    → failed
```
