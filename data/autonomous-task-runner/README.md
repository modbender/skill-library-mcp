# task-runner

**Version:** 2.0.0 | **Tier:** general | **Owner:** main agent

A persistent, daemon-style task queue for OpenClaw agents. Tell the agent what you need done — once, or across multiple days — and it will queue your tasks, execute them in the background via subagents, and notify you as each one completes. The queue never closes. You can keep adding tasks forever.

---

## The Core Idea

**Old design:** User sends tasks → agent runs them → done. ❌

**New design:** User sends tasks → tasks go into a queue → dispatcher wakes up periodically → tasks execute in background → user gets notified. ✅

The agent is always ready for your next task, even if the last one hasn't finished yet.

---

## Two Operating Modes

### Mode 1: INTAKE
Triggered when you send a message with tasks. The agent:
1. Parses your message into structured task objects
2. Assigns IDs (T-01, T-02, ...)
3. Appends them to the persistent queue file
4. Confirms: "Added T-07: [description]. Queue now has 3 pending tasks."
5. Done. The dispatcher will execute them.

### Mode 2: DISPATCHER
Triggered every heartbeat (~every 15–20 min) and by a cron job (every 15 min). The agent:
1. Reads the queue
2. If nothing pending/running → silent (HEARTBEAT_OK)
3. If pending tasks → spawns subagents to execute them (up to 2 at a time)
4. Checks running tasks for completion → notifies you when done or blocked

---

## Example: Tasks Added Over Multiple Days

### Monday morning
You send:
```
I need you to:
1. Research the top 5 open-source LLM frameworks and summarize pros/cons
2. Create a markdown comparison table at ~/reports/llm-frameworks.md
```

Agent responds:
```
📋 Added 2 tasks to queue:
• T-01: Research top 5 open-source LLM frameworks
• T-02: Create LLM framework comparison table at ~/reports/llm-frameworks.md

Queue now has 2 pending tasks. Dispatcher will pick these up shortly.
```

Later that day (after dispatcher runs):
```
✅ T-01 done — Researched 5 LLM frameworks: Ollama, LM Studio, llama.cpp, vLLM, Hugging Face TGI.
Deliverable: summary saved for T-02 input.

✅ T-02 done — Comparison table created at ~/reports/llm-frameworks.md (5 frameworks, 8 criteria).
```

---

### Tuesday afternoon
You send:
```
task: check if the llm-frameworks.md file I asked for actually got created
```

Agent (INTAKE):
```
Added T-03: Verify ~/reports/llm-frameworks.md was created. Queue now has 1 pending task.
```

Later:
```
✅ T-03 done — File confirmed: ~/reports/llm-frameworks.md exists, 2.1KB, created 2026-02-17.
```

---

### Wednesday evening
You send:
```
Add task: post a summary of the LLM framework research to #ai-team channel
```

Agent (INTAKE):
```
Added T-04: Post LLM framework summary to #ai-team channel. Queue now has 1 pending task.
```

Later:
```
🚫 T-04 blocked after 3 attempts

What was tried:
- Strategy 1: message tool → channel #ai-team not found in configured channels
- Strategy 2: search for channel by partial name → no match
- Strategy 3: list available channels → #ai-team does not exist

Why it's blocked:
The channel #ai-team is not configured in the agent's messaging tools.

To unblock:
1. Verify the channel name (may be #ai-research or #ai-discussion)
2. Reply "retry T-04" with the correct channel name: "retry T-04 use channel #ai-research"

Reply "retry T-04" once ready.
```

---

### Thursday morning
You send:
```
retry T-04
```

Agent (INTAKE):
```
⏳ T-04 reset to pending. Queue now has 1 pending task.
```

Later:
```
✅ T-04 done — Summary posted to #ai-research channel.
```

---

## Checking Your Queue

At any time:
```
show tasks
```
or
```
what's in my task queue?
```

Agent responds:
```
📋 Task Queue — 4 total (0 pending, 0 running, 4 done, 0 blocked)

ID    Status    Description
T-01  ✅ done   Research top 5 LLM frameworks
T-02  ✅ done   Create LLM framework comparison table
T-03  ✅ done   Verify llm-frameworks.md was created
T-04  ✅ done   Post summary to #ai-research
```

---

## Queue File

All tasks live in one persistent file:
```
~/.openclaw/tasks/task-queue.json
```

It accumulates over time. Done and blocked tasks older than 7 days are automatically archived to:
```
~/.openclaw/tasks/archive/YYYY-MM.json
```

Tasks are never deleted — they're archived so you always have a record.

---

## Configuration

Add to `TOOLS.md`:
```
## Task Runner
TASK_RUNNER_DIR=~/.openclaw/tasks/
TASK_RUNNER_MAX_CONCURRENT=2
TASK_RUNNER_MAX_RETRIES=3
TASK_RUNNER_ARCHIVE_DAYS=7
```

| Setting | Default | Description |
|---------|---------|-------------|
| `TASK_RUNNER_DIR` | `~/.openclaw/tasks/` | Queue file location |
| `TASK_RUNNER_MAX_CONCURRENT` | `2` | Max simultaneous task subagents |
| `TASK_RUNNER_MAX_RETRIES` | `3` | Retries before marking blocked |
| `TASK_RUNNER_ARCHIVE_DAYS` | `7` | Days to keep done/blocked tasks in main queue |

---

## Task Lifecycle

```
pending → running → done ✅
                  ↘ blocked 🚫  (after maxRetries)
           ↘ skipped ⏭️  (on user request)
           
blocked → pending  (after user says "retry T-NN")
```

---

## Supported Task Types

| Type | Examples | Primary Strategy |
|------|---------|-----------------|
| info-lookup | "find X", "research Y", "what is Z" | `web_search` |
| file-creation | "create a file", "write a report" | `write` tool |
| code-execution | "run this script", "install X", "check if Y is running" | `exec` tool |
| agent-delegation | "have a sub-agent research X", "delegate Y" | subagent spawn |
| reminder-scheduling | "remind me at 3pm", "set a weekly check" | cron tool |
| messaging | "send message to X", "post to #channel" | `message` tool |
| unknown | Ambiguous tasks | `web_search` → re-classify → ask |

---

## Heartbeat Setup

The dispatcher runs automatically on every heartbeat. To enable, add to `HEARTBEAT.md`:

```markdown
## Task Runner Dispatcher
Read ${TASK_RUNNER_DIR}/task-queue.json.
If pending or running tasks exist: run DISPATCHER mode (task-runner skill).
If nothing pending: HEARTBEAT_OK.
```

A backup cron job also runs every 15 minutes:
```
cron: every 15 min → systemEvent: "TASK_RUNNER_DISPATCH: check queue and run pending tasks"
```

---

## References

- `SKILL.md` — Full skill specification (two-mode workflow, all templates)
- `references/queue-schema.md` — Queue JSON format (complete field reference)
- `references/task-types.md` — Task type catalog and strategy selection guide
- `references/verification-guide.md` — Verification logic per task type
- `tests/test-triggers.json` — Trigger test cases
