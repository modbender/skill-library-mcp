---
name: ralph-loop
description: Guide OpenClaw agents to execute Ralph Wiggum loops using exec and process tools. Agent orchestrates coding agents (Codex, Claude Code, OpenCode, Goose) with proper TTY support via pty:true. Plans/builds code via PROMPT.md + AGENTS.md, SPECS and IMPLEMENTATION_PLAN.md. Includes PLANNING vs BUILDING modes, backpressure, sandboxing, and completion conditions. Users request loops, agents execute using tools.
version: 1.1.0
author: OpenClaw Community
keywords: [ralph-loop, ai-agent, coding-agent, pty, tty, automation, loop, opencode, codex, claude, goose, exec-tool, process-tool]
license: MIT
---

# Ralph Loop

## Overview
This skill guides **OpenClaw agents** to execute Ralph Loop workflows using the `exec` and `process` tools. The agent orchestrates AI coding agent sessions following the Ralph playbook flow:

1) **Define Requirements** → JTBD → Focus Topics → `specs/*.md`
2) **PLANNING Loop** → Create/update `IMPLEMENTATION_PLAN.md` (do not implement)
3) **BUILDING Loop** → Implement tasks, run tests (backpressure), update plan, commit

The loop persists context via `PROMPT.md` + `AGENTS.md` (loaded each iteration) and the plan/specs on disk.

## How This Skill Works

This skill generates instructions for **OpenClaw agents** to execute Ralph Loops using the `exec` and `process` tools.

- The agent calls `exec` tool with the coding agent command
- Uses `pty: true` to provide TTY for interactive CLIs
- Uses `background: true` for monitoring capabilities
- Uses `process` tool to monitor progress and detect completion

**Important**: Users don't run these scripts directly - the OpenClaw agent executes them using its tool capabilities.

---

## TTY Requirements

Some coding agents **require a real terminal (TTY)** to work properly, or they will hang:

**Interactive CLIs (need TTY)**:
- OpenCode, Codex, Claude Code, Pi, Goose

**Non-interactive CLIs (file-based)**:
- aider, custom scripts

**Solution**: Use **exec + process mode** for interactive CLIs, simple loops for file-based tools.

---

## Agent Tool Usage Patterns

### Interactive CLIs (Recommended Pattern)

For OpenCode, Codex, Claude Code, Pi, and Goose - these require TTY support:

**When I (the agent) receive a Ralph Loop request, I will:**

1. **Use exec tool** to launch the coding agent:
   ```
   exec tool with parameters:
   - command: "opencode run --model <MODEL> \"$(cat PROMPT.md)\""
   - workdir: <project_path>
   - background: true
   - pty: true
   - yieldMs: 60000
   - timeout: 3600
   ```

2. **Capture session ID** from exec tool response

3. **Use process tool** to monitor:
   ```
   process tool with:
   - action: "poll"
   - sessionId: <captured_session_id>
   
   process tool with:
   - action: "log"
   - sessionId: <captured_session_id>
   - offset: -30  (for recent output)
   ```

4. **Check completion** by reading `IMPLEMENTATION_PLAN.md` for sentinel text

5. **Clean up** with process kill if needed:
   ```
   process tool with:
   - action: "kill"
   - sessionId: <session_id>
   ```

**Benefits**: TTY support, real-time logs, timeout handling, parallel sessions, workdir isolation

---

## Agent Workflow

### 1) Gather Inputs

**Required**:
- Goal / JTBD
- CLI (`opencode`, `codex`, `claude`, `goose`, `pi`, other)
- Mode (`PLANNING`, `BUILDING`, or `BOTH`)
- Max iterations (default: PLANNING=5, BUILDING=10)

**Optional**:
- Completion sentinel (default: `STATUS: COMPLETE` in `IMPLEMENTATION_PLAN.md`)
- Working directory (default: `$PWD`)
- Timeout per iteration (default: 3600s)
- Sandbox choice
- Auto-approval flags (`--full-auto`, `--yolo`, `--dangerously-skip-permissions`)

**Auto-detect**:
- If CLI in interactive list → use exec tool with pty: true
- Extract model flag from CLI requirements

### 2) Requirements → Specs (Optional)

If requirements are unclear:
- Break JTBD into focus topics
- Draft `specs/<topic>.md` for each
- Keep specs short and testable

### 3) PROMPT.md + AGENTS.md

**PROMPT.md** references:
- `specs/*.md`
- `IMPLEMENTATION_PLAN.md`
- Relevant project files

**AGENTS.md** includes:
- Test commands (backpressure)
- Build/run instructions
- Operational learnings

### 4) Prompt Templates

**PLANNING Prompt** (no implementation):
```
You are running a Ralph PLANNING loop for this goal: <goal>.

Read specs/* and the current codebase. Only update IMPLEMENTATION_PLAN.md.

Rules:
- Do not implement
- Do not commit
- Create a prioritized task list
- Write down questions if unclear

Completion:
When plan is ready, add: STATUS: PLANNING_COMPLETE
```

**BUILDING Prompt**:
```
You are running a Ralph BUILDING loop for this goal: <goal>.

Context: specs/*, IMPLEMENTATION_PLAN.md, AGENTS.md

Tasks:
1) Pick the most important task
2) Investigate code
3) Implement
4) Run backpressure commands from AGENTS.md
5) Update IMPLEMENTATION_PLAN.md
6) Update AGENTS.md with learnings
7) Commit with clear message

Completion:
When all done, add: STATUS: COMPLETE
```

### 5) CLI Command Reference

The agent constructs command strings using these patterns:

| CLI | Command String Pattern |
|-----|----------------------|
| **OpenCode** | `opencode run --model <MODEL> "$(cat PROMPT.md)"` |
| **Codex** | `codex exec <FLAGS> "$(cat PROMPT.md)"` (requires git) |
| **Claude Code** | `claude <FLAGS> "$(cat PROMPT.md)"` |
| **Pi** | `pi --provider <PROVIDER> --model <MODEL> -p "$(cat PROMPT.md)"` |
| **Goose** | `goose run "$(cat PROMPT.md)"` |

Common flags:
- Codex: `--full-auto`, `--yolo`, `--model <model>`
- Claude: `--dangerously-skip-permissions`

---

## Detailed Agent Tool Usage Examples

### Example 1: OpenCode Ralph Loop

**Agent executes this sequence:**

```
Step 1: Launch OpenCode with exec tool
{
  command: "opencode run --model github-copilot/claude-opus-4.5 \"$(cat PROMPT.md)\"",
  workdir: "/path/to/project",
  background: true,
  pty: true,
  timeout: 3600,
  yieldMs: 60000
}

Step 2: Capture session ID from response
sessionId: "abc123"

Step 3: Monitor with process tool every 10-30 seconds
{
  action: "poll",
  sessionId: "abc123"
}

Step 4: Check recent logs
{
  action: "log",
  sessionId: "abc123",
  offset: -30
}

Step 5: Read IMPLEMENTATION_PLAN.md to check for completion
- Look for: "STATUS: COMPLETE" or "STATUS: PLANNING_COMPLETE"

Step 6: If complete or timeout, cleanup
{
  action: "kill",
  sessionId: "abc123"
}
```

### Example 2: Codex with Full Auto

**Agent tool calls:**

```
exec tool:
{
  command: "codex exec --full-auto --model anthropic/claude-opus-4 \"$(cat PROMPT.md)\"",
  workdir: "/path/to/project",
  background: true,
  pty: true,
  timeout: 3600
}

# Then monitor with process tool as above
```

---

## Completion Detection

Use flexible regex to match variations:

```bash
grep -Eq "STATUS:?\s*(PLANNING_)?COMPLETE" IMPLEMENTATION_PLAN.md
```

**Matches**:
- `STATUS: COMPLETE`
- `STATUS:COMPLETE`
- `STATUS: PLANNING_COMPLETE`
- `## Status: PLANNING_COMPLETE`

---

## Safety & Safeguards

### Auto-Approval Flags (Risky!)
- Codex: `--full-auto` (sandboxed, auto-approve) or `--yolo` (no sandbox!)
- Claude: `--dangerously-skip-permissions`
- **Recommendation**: Use sandboxes (docker/e2b/fly) and limited credentials

### Escape Hatches
- Stop: `Ctrl+C`
- Kill session: process tool with action: "kill"
- Rollback: `git reset --hard HEAD~N`

### Best Practices
1. **Start small**: Test with 1-2 iterations first
2. **Workdir isolation**: Prevent reading unrelated files
3. **Set timeouts**: Default 1h may not fit all tasks
4. **Monitor actively**: Check logs, don't terminate prematurely
5. **Requirements first**: Clear specs before building
6. **Backpressure early**: Add tests from the start

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| OpenCode hangs | Ensure agent uses exec tool with pty: true |
| Session won't start | Check CLI path, git repo, command syntax |
| Completion not detected | Verify sentinel format in IMPLEMENTATION_PLAN.md |
| Process timeout | Agent should increase timeout parameter or simplify tasks |
| Parallel conflicts | Agent should use git worktrees for isolation |
| Can't see progress | Agent should use process tool with action: "log" |

---

## License

MIT

## Credits

This skill builds upon work by:
- **@jordyvandomselaar** - Original Ralph Loop concept and workflow design
- **@steipete** - Coding agent patterns and exec/process tool usage with pty support

Key improvement: Uses OpenClaw's `exec` tool with `pty: true` to provide TTY for interactive CLIs, solving the hanging issue that occurs with simple background bash execution.
