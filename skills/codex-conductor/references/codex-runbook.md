# Coding-Agent Runbook (PTY + Background)

This orchestrator MUST delegate implementation tasks to a coding agent.
Do not hand-code feature work directly when the skill is active.

Supported agents:
- `codex`
- `claude`
- `opencode`
- `pi`

## First Rule

At skill start, ask:
1) Which coding agent should run tasks?
2) Which fallback agent should be used if primary fails?

## Launch Patterns

### Codex
```bash
codex exec --full-auto "<gate task prompt>"
```

### Claude
```bash
claude "<gate task prompt>"
```

### OpenCode
```bash
opencode run "<gate task prompt>"
```

### Pi
```bash
pi -p "<gate task prompt>"
```

OpenClaw execution recommendation:
- `pty:true` for interactive CLIs
- `background:true` for long-running work
- `workdir:<project-root>`

## Required Orchestration Loop

1. Generate gate prompt (`generate_gate_prompt.py`).
2. Execute selected coding agent with that prompt (`agent_exec.py` or equivalent).
3. Require coding agent to update docs immediately after task completion:
   - docs/tasks.md
   - docs/progress.md
   - docs/change-log.md
   - docs/traceability.md
   - docs/test-results.md
   - docs/agent-handoff.md
4. OpenClaw agent runs verification itself:
   - CLI checks in terminal
   - Browser/manual checks for web journeys
5. If validation fails:
   - summarize issue clearly with command/flow + output
   - re-spawn coding agent with fix prompt (same task/spec)
   - require docs updates again
   - re-test
6. Only then update gate status.

## Manual Review Responsibility

Even in autonomous mode, the OpenClaw agent performs manual verification itself:
- Web/UI flows: run in browser tools, test critical journeys.
- CLI flows: run required commands in terminal and inspect outputs.

If checks fail, send concrete failure details to coding agent, request fix, and retest.

## Completion Wake Pattern

For long runs, require coding agent wake messages to include task + verification handoff.

"When fully done, run:
openclaw gateway wake --text 'Done: <gate> | task: <summary> | handoff: see docs/agent-handoff.md for CLI+Browser checks' --mode now"
