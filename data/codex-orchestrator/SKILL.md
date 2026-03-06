---
name: codex-orchestrator
description: Monitor, control, and orchestrate background Codex sessions. Use this skill to track progress, handle interruptions, and ensure task completion for long-running coding tasks.
---

# Codex Orchestrator

This skill provides a workflow for supervising the Codex coding agent running in background processes.

## Workflow

### 1. Start (Launch)
Always launch Codex in a background PTY session to maintain interactivity without blocking the main agent.

```bash
bash pty:true workdir:<target_dir> background:true command:"codex exec --full-auto '<PROMPT>'"
```
*   Store the returned `sessionId`.
*   If `sessionId` is lost, find it via `process action:list`.

### 2. Monitor (Watch)
Check progress regularly (e.g., via cron or manual check).

```bash
# Get last 2KB of logs to see current status
process action:log sessionId:<id> limit:2000
```

**Signs of life:**
*   Spinner animations or progress bars updating.
*   "Working...", "Thinking...", "Running...".
*   File edits (`Edit ...`).

**Signs of blockage:**
*   Interactive prompts (e.g., "Select directory", "Approve change [y/n]").
*   No log output for >5 minutes (process might be hung or waiting for hidden input).

### 3. Intervene (Control)
If Codex is stuck at a prompt:

```bash
# Send 'y' and Enter
process action:submit sessionId:<id> data:"y"

# Send just Enter (default choice)
process action:submit sessionId:<id> data:""
```

If Codex is looping or hallucinating:
```bash
# Kill the session
process action:kill sessionId:<id>
```

### 4. Report (Notify)
When a significant milestone is reached or the task is done:
1.  Summarize the work done (files changed, tests passed).
2.  Notify the user.

## Standard Operating Procedures (SOPs)

### "The Stuck Agent" Protocol
1.  **Diagnose**: Run `process action:log sessionId:<id> limit:500`.
2.  **Analyze**: Is it asking a question? Is it downloading?
3.  **Action**:
    *   If asking: Provide answer via `submit`.
    *   If downloading (slow): Wait.
    *   If silent >10m: Send a "poke" (e.g. `submit data:"\n"` to refresh prompt) or kill/resume.

### "The Resume" Protocol
If a session died or was killed:
1.  Run `codex resume --last` or `codex resume <session_id>` in a new background process.
2.  Verify it picked up the context.

## Logs & Artifacts
*   Codex logs are ephemeral in the PTY buffer.
*   For persistent logs, instruct Codex to write to a file: `codex exec "task..." > codex.log 2>&1` (Note: buffering may delay output).
*   Better: Use `process action:log` to snapshot the buffer periodically.
