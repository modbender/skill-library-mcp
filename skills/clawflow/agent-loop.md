# The Agent Loop

Every agent runs the same loop regardless of specialty. The loop handles two kinds
of incoming messages: **tasks** (from a parent) and **replies** (from peers it
delegated to).

---

## Main Loop

When a message arrives in the agent's session:

```
1. Parse frontmatter → check `type` field
2. if type == "task":   handle_task(msg)
3. if type == "reply":  handle_reply(msg)
```

---

## handle_task(msg)

Called when the agent receives a new task from a parent.

```
1. LOG MESSAGE
   - Write the raw message to <workspace>/mailbox/inbox/{task-id}-{subtask-id}.md

2. IDEMPOTENCY CHECK
   - Check <workspace>/tasks/{task-id}/task.md
   - If exists and status is done  → re-send stored results, move to mailbox/archive/, return
   - If exists and status is in-progress/executing → move to mailbox/archive/, return
   - Otherwise, proceed

3. CREATE TASK FILE
   - mkdir <workspace>/tasks/{task-id}/
   - Write task.md from message contents

4. DISCOVER PEERS
   - Run: openclaw agents list
   - Read own subagents.allowAgents config to know who is reachable

5. DECIDE: direct execution or delegate?
   - Evaluate the task against own capabilities and available peers
   - See "Delegation Decision" below

6a. DIRECT EXECUTION
    - Set task.md mode=direct, status=in-progress
    - Execute the work (agent-specific logic)
    - Write results to task.md
    - Set status=done
    - Send completion reply to parent:
      openclaw agent --agent {msg.from} --message "$(cat reply.md)"
    - Log reply to mailbox/outbox/

6b. DELEGATE (become coordinator for this task)
    - Set task.md mode=coordinating, status=planning
    - Decompose task into sub-DAG, write to task.md
    - Set status=executing
    - For each subtask with no unmet dependencies:
      openclaw agent --agent {subtask.agent} --message "$(cat dispatch.md)"
      Log dispatch to mailbox/outbox/
    - Mark those subtasks as dispatched

7. ARCHIVE
   - Move message from mailbox/inbox/ to mailbox/archive/
```

---

## handle_reply(msg)

Called when a peer the agent delegated to sends back results.

```
1. LOG MESSAGE
   - Write the raw reply to <workspace>/mailbox/inbox/{task-id}-{subtask-id}-reply.md

2. LOCATE TASK
   - Find task.md matching msg.task_id in <workspace>/tasks/
   - If not found → move to mailbox/archive/ (orphan reply), return
   - If task.md mode != coordinating → move to mailbox/archive/, return

3. PROCESS REPLY
   - If msg.status == failed:
     - Mark subtask as failed in task.md
     - Mark entire task as failed
     - Send failure reply to own parent, log to mailbox/outbox/
     - Archive message, return

   - If msg.status == done:
     - Store results in "Subtask Results" section of task.md
     - Mark subtask as done
     - Write result_summary

4. CHECK DAG
   - ready = get_ready_subtasks(dag)
   - For each ready subtask:
     - Build dispatch message with upstream results in Context
     - openclaw agent --agent {subtask.agent} --message "$(cat dispatch.md)"
     - Log dispatch to mailbox/outbox/
     - Mark subtask as dispatched

5. CHECK COMPLETION
   - If all subtasks are done:
     - Set status=aggregating
     - Synthesise results from all subtasks
     - Write synthesised output to task.md
     - Set status=done
     - Send completion reply to own parent, log to mailbox/outbox/

6. ARCHIVE
   - Move message from mailbox/inbox/ to mailbox/archive/
```

---

## Delegation Decision

The agent asks itself:

### Execute directly when:
- The task matches the agent's own specialty
- It's small enough that decomposition adds overhead
- No peers have the needed capabilities
- `openclaw agents list` returns no reachable agents

### Decompose and delegate when:
- The task needs capabilities the agent doesn't have
- The task has naturally independent parts (parallelism opportunity)
- The task is complex enough that sub-specialists produce better results
- Multiple steps require different expertise

### Decomposition guidelines:
- **Maximise parallelism** — don't create false dependencies between independent work.
- **Minimise subtask count** — don't create subtasks for trivial inline work.
- **Self-contained context** — each dispatch message must carry everything the
  peer needs. The peer cannot see the DAG or other subtask results.
- **Forward upstream results** — if subtask B depends on A, include A's results
  in B's Context section when dispatching.
- **Assign by agent ID** — use the `id` from `openclaw agents list` as the
  `agent` field in the DAG.

---

## Dispatching a Subtask

Before sending a task message to a peer:

1. Verify the subtask exists in task.md with status=pending
2. Verify all dependencies have status=done
3. Build the dispatch message (see `references/schemas.md` for format):
   - Include all necessary context (upstream results, background)
   - Write clear, self-contained instructions
   - Specify expected output format
4. Send via: `openclaw agent --agent {peer-id} --message "$(cat dispatch.md)"`
5. Update subtask status to `dispatched` in task.md

---

## Idempotency

Messages can arrive more than once (retries, restarts).

**For tasks**: Check if `<workspace>/tasks/{task-id}/task.md` exists.
- Exists and done → re-send stored results
- Exists and in-progress → ignore
- Doesn't exist → process normally

**For replies**: Check subtask status in task.md.
- Already marked done → ignore
- Still dispatched → process normally

---

## Crash Recovery

If the agent restarts:

1. Scan `<workspace>/tasks/` for any task with status `in-progress` or `executing`.
2. For in-progress (direct): resume or restart the work.
3. For executing (coordinating): check for unprocessed replies, then check DAG
   for subtasks that need dispatching or have timed out.

All state is in task.md within the workspace. No external state to reconstruct.
