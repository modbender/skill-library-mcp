# Coordinating

When an agent decides to decompose a task rather than execute it directly, it
temporarily takes on a coordinating role. This document covers the coordination-specific
logic.

---

## Entering Coordination Mode

After deciding to delegate in `handle_task`:

1. Set `task.md` mode to `coordinating`, status to `planning`.
2. Discover peers: `openclaw agents list` (filtered by `subagents.allowAgents`).
3. Analyse the task and decompose it into subtasks.
4. Write the DAG to `task.md`.
5. Set status to `executing`.
6. Dispatch all initially ready subtasks (those with no dependencies).

---

## Building the DAG

### Step 1: Identify the pieces

Read the task instructions and ask:
- What are the distinct units of work?
- Which units need different capabilities?
- Which units can run in parallel?
- Which units depend on outputs from other units?

### Step 2: Assign agents

For each unit of work, find the best-matching agent from `openclaw agents list`.
Match based on what you know about each agent's configuration — their workspace,
model, identity, and any capability notes in their `IDENTITY.md` or `SOUL.md`.

If no agent matches a piece of work, the coordinating agent can either:
- Handle that piece itself (hybrid: coordinate some, execute some)
- Fail the task (if it truly can't do the work)

### Step 3: Define dependencies

Draw the dependency graph:
- A subtask lists the IDs of subtasks it depends on.
- `depends_on: []` means it can start immediately.
- Avoid unnecessary sequential chains — maximise parallelism.

### Step 4: Write to task.md

```yaml
subtasks:
  extract-data:
    agent:       data-extractor
    description: Pull Q3 numbers from the CSV
    depends_on:  []
    status:      pending
  extract-feedback:
    agent:       data-extractor
    description: Extract customer feedback themes
    depends_on:  []
    status:      pending
  analyse:
    agent:       analyst
    description: Correlate sales trends with feedback themes
    depends_on:  [extract-data, extract-feedback]
    status:      pending
  write-report:
    agent:       writer
    description: Draft executive summary
    depends_on:  [analyse]
    status:      pending
```

`extract-data` and `extract-feedback` run in parallel. `analyse` waits for both.
`write-report` waits for `analyse`. Agent IDs match `openclaw agents list` output.

---

## Hybrid Execution

An agent can coordinate *and* execute within the same task:

- Delegate `extract-data` and `extract-feedback` to peers.
- When both complete, do the analysis itself (direct execution).
- Delegate `write-report` to another peer.

Model this in the DAG with `agent: self`:

```yaml
  analyse:
    agent:       self
    description: Correlate sales trends with feedback themes
    depends_on:  [extract-data, extract-feedback]
    status:      pending
```

When `analyse` becomes ready, the agent executes the work inline instead of
dispatching via `openclaw agent`.

---

## Passing Context Downstream

The most common coordination mistake: sending a subtask without enough context.

**Rules:**
- The peer sees *only* the task message. Nothing else.
- If subtask B depends on subtask A, B's dispatch message **must include A's results**
  in the Context section.
- Background information the agent received from *its* parent should be forwarded
  if relevant.
- When in doubt, include more context rather than less.

**Example:** Dispatching `analyse` after `extract-data` and `extract-feedback` are done:

```markdown
## Context
You are analysing Q3 performance for Acme Corp.

### Sales Data (from extract-data)
| Region | Q3 Revenue | Q2 Revenue | Change |
|--------|-----------|-----------|--------|
| North  | $2.1M     | $1.8M     | +17%   |
| South  | $1.4M     | $1.5M     | -7%    |

### Customer Feedback Themes (from extract-feedback)
1. Shipping speed (mentioned 340 times, 78% positive)
2. Product quality (mentioned 210 times, 91% positive)
3. Pricing (mentioned 180 times, 45% negative)

## Instructions
1. Identify correlations between sales trends and feedback themes
2. Flag regions where negative feedback aligns with revenue decline
3. Return findings as a structured analysis
```

---

## Synthesis

After all subtasks complete, the coordinating agent synthesises results.

1. Read all subtask results from task.md.
2. Combine into a coherent output that answers the original task.
3. Add structure, draw connections, resolve contradictions — don't just concatenate.
4. Write to the "Synthesised Output" section.
5. Use this as the body of the completion reply to the parent.

**Keep it proportional.** Match the Expected Output from the original task message.

---

## Recursive Coordination

A peer that receives a subtask might itself decompose and coordinate. This is
invisible to the parent:

- Parent dispatches subtask to Peer B via `openclaw agent --agent B`.
- Peer B decides to delegate to Peers D and E.
- D and E execute and reply to B.
- B synthesises and replies to Parent.
- Parent sees one reply from B. It doesn't know B delegated.

Each level of the tree is self-contained. The protocol is the same at every level.

**Depth limit:** V1 doesn't enforce a max recursion depth. 2-3 levels is typical.
