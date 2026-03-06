# Ralph Loop

## Acknowledgments

This skill is inspired by and improves upon:

1. **Ralph Loop** by @jordyvandomselaar  
   https://github.com/openclaw/skills/blob/main/skills/jordyvandomselaar/ralph-loop/SKILL.md

2. **Coding Agent** by @steipete  
   https://github.com/openclaw/skills/blob/main/skills/steipete/coding-agent/SKILL.md

## Key Improvement

**Solved the hanging issue** with coding agents in ralph-loop: The original pure background bash mode couldn't provide TTY for interactive CLIs (OpenCode, Codex, Claude Code), causing processes to hang.

**Solution**: Uses OpenClaw's **exec + process mode** to provide a real TTY environment with background monitoring and real-time log access.

---

## Introduction

Ralph Loop is a skill that guides **OpenClaw agents** to execute Ralph Wiggum playbook workflows using the `exec` and `process` tools. The agent orchestrates AI coding agent sessions, dividing software development into two phases:

1. **PLANNING**: Analyze requirements, create implementation plan, no code writing
2. **BUILDING**: Implement features according to plan, run tests, commit code

## How This Works

**For OpenClaw Agents**: This skill teaches you how to use the `exec` and `process` tools to orchestrate Ralph Loops.

**For Users**: You ask your OpenClaw agent to "create a Ralph Loop" and it will:
- Use its `exec` tool to launch coding agents (OpenCode, Codex, etc.)
- Use its `process` tool to monitor progress
- Check completion conditions by reading files
- Report progress back to you

**You don't run scripts directly** - your OpenClaw agent handles everything using its tool capabilities.

## Core Features

### ✅ Agent Tool Integration
- Uses OpenClaw's `exec` tool for launching coding agents
- Uses OpenClaw's `process` tool for monitoring and control
- Proper TTY support via `pty: true` parameter

### ✅ Interactive CLI Support
- Provides real terminal environment for OpenCode, Codex, Claude Code, Goose
- Solves hanging issues that occur without proper TTY
- Background execution with real-time monitoring

### ✅ Flexible Workflow
- Supports PLANNING, BUILDING, BOTH modes
- Configurable iteration counts and completion conditions
- Automatic task completion detection

### ✅ Safety Safeguards
- Supports sandbox environments (docker/e2b/fly)
- Working directory isolation
- Git repository validation

## Quick Start

### For Users

Simply ask your OpenClaw agent:

```
"Create a ralph loop for me using OpenCode to implement user authentication"
```

Your agent will:
1. Gather requirements and preferences
2. Create necessary files (PROMPT.md, AGENTS.md, IMPLEMENTATION_PLAN.md)
3. Use exec tool to launch the coding agent
4. Monitor progress with process tool
5. Report results to you

### For OpenClaw Agents

When a user requests a Ralph Loop:

1. **Gather configuration:**
   - CLI choice (opencode, codex, claude, goose, etc.)
   - Model selection
   - Mode (PLANNING/BUILDING/BOTH)
   - Max iterations

2. **Setup files:**
   - Create PROMPT.md with task instructions
   - Create AGENTS.md with test commands
   - Create IMPLEMENTATION_PLAN.md

3. **Execute loop using tools:**
   ```
   exec tool:
   - command: "opencode run --model X \"$(cat PROMPT.md)\""
   - workdir: project_path
   - background: true
   - pty: true
   - timeout: 3600
   ```

4. **Monitor with process tool:**
   ```
   process tool:
   - action: "poll" (check status)
   - action: "log" (view output)
   - action: "kill" (cleanup)
   ```

5. **Check completion:**
   - Read IMPLEMENTATION_PLAN.md
   - Look for "STATUS: COMPLETE"

## How OpenClaw Agents Use This Skill

### Step-by-Step Agent Workflow

**1. User Request:**
```
User: "Set up a Ralph Loop to build a REST API"
```

**2. Agent Gathers Info:**
- Which coding CLI? (OpenCode, Codex, Claude, Goose)
- Which model?
- PLANNING or BUILDING or BOTH?
- How many max iterations?

**3. Agent Creates Files:**
- Write PROMPT.md with detailed instructions
- Write AGENTS.md with test commands
- Initialize IMPLEMENTATION_PLAN.md

**4. Agent Uses exec Tool:**
```
Call exec tool with:
{
  command: "opencode run --model github-copilot/claude-opus-4.5 \"$(cat PROMPT.md)\"",
  workdir: "/path/to/project",
  background: true,
  pty: true,
  timeout: 3600,
  yieldMs: 60000
}

Response contains: sessionId: "abc123"
```

**5. Agent Monitors with process Tool:**
```
Every 10-30 seconds:

Call process tool:
{
  action: "poll",
  sessionId: "abc123"
}
→ Returns: {state: "running"}

Call process tool:
{
  action: "log",
  sessionId: "abc123",
  offset: -30
}
→ Returns recent output
```

**6. Agent Checks Completion:**
```
Read IMPLEMENTATION_PLAN.md
Search for: "STATUS: COMPLETE" or "STATUS: PLANNING_COMPLETE"

If found: Success! Move to next phase or finish
If not found and under max iterations: Start next iteration
If max iterations reached: Report to user
```

**7. Agent Cleans Up:**
```
Call process tool:
{
  action: "kill",
  sessionId: "abc123"
}
```

## Workflow Details

### PLANNING Phase

Goal: Create a clear implementation plan, **without writing code**

1. Analyze requirements documents (`specs/*.md`)
2. Study existing codebase
3. Break down tasks into small steps
4. Record in `IMPLEMENTATION_PLAN.md`
5. Mark complete: `STATUS: PLANNING_COMPLETE`

**Prompt Template Example**:
```markdown
You are running a Ralph PLANNING loop for this goal: Implement user authentication.

Read specs/* and the current codebase. Only update IMPLEMENTATION_PLAN.md.

Rules:
- Do not implement any code
- Do not commit
- Create prioritized task list
- Identify risks and dependencies
- Write down questions if unclear

Completion:
When plan is ready, add: STATUS: PLANNING_COMPLETE
```

### BUILDING Phase

Goal: Implement features according to plan, ensure quality

1. Select next task from `IMPLEMENTATION_PLAN.md`
2. Investigate relevant code
3. Implement feature
4. Run test commands from `AGENTS.md` (backpressure)
5. Update implementation plan status
6. Record learnings in `AGENTS.md`
7. Commit code
8. Mark when all done: `STATUS: COMPLETE`

**Prompt Template Example**:
```markdown
You are running a Ralph BUILDING loop for this goal: Implement user authentication.

Context:
- specs/auth.md: Authentication requirements
- IMPLEMENTATION_PLAN.md: Task list
- AGENTS.md: Test commands and operational guide

Tasks:
1) Select the most important incomplete task
2) Investigate relevant code
3) Implement feature
4) Run backpressure commands from AGENTS.md (tests, lint)
5) Update IMPLEMENTATION_PLAN.md to mark task complete
6) Update AGENTS.md with today's learnings
7) Commit code with clear commit message

Completion:
When all tasks complete, add: STATUS: COMPLETE
```

## Supported CLI Tools

| Tool | Type | TTY Required | Command Template |
|------|------|-------------|-----------------|
| **OpenCode** | Interactive | ✅ Required | `opencode run --model <MODEL> "$(cat PROMPT.md)"` |
| **Codex** | Interactive | ✅ Required | `codex exec --model <MODEL> "$(cat PROMPT.md)"` |
| **Claude Code** | Interactive | ✅ Required | `claude "$(cat PROMPT.md)"` |
| **Pi** | Interactive | ✅ Required | `pi --provider <PROVIDER> --model <MODEL> -p "$(cat PROMPT.md)"` |
| **Goose** | Interactive | ✅ Required | `goose run "$(cat PROMPT.md)"` |
| **aider** | File-based | ❌ Not needed | `aider --message "$(cat PROMPT.md)"` |

## Configuration Options

### Required Configuration

- **CLI_CMD**: AI coding tool command to use
- **MODEL**: AI model (e.g., `github-copilot/claude-opus-4.5`)
- **MODE**: Run mode (`PLANNING` / `BUILDING` / `BOTH`)

### Optional Configuration

- **MAX_PLANNING_ITERS**: Maximum planning phase iterations (default: 5)
- **MAX_BUILDING_ITERS**: Maximum building phase iterations (default: 10)
- **TIMEOUT**: Timeout per iteration in seconds (default: 3600)
- **WORKDIR**: Working directory (default: `$PWD`)
- **PLAN_SENTINEL**: Completion marker regex (default: `STATUS:\s*(PLANNING_)?COMPLETE`)

### Auto-Approval Flags (Use with Caution!)

Some CLIs support auto-approval of operations, but come with risks:

- **Codex**: `--full-auto` (sandboxed), `--yolo` (⚠️ no sandbox)
- **Claude**: `--dangerously-skip-permissions` (⚠️ skips permission checks)

**Recommendations**:
- Use auto-approval in controlled environments
- Prefer sandboxes (docker, e2b, fly)
- Limit cloud service credential permissions

## Monitoring and Control (For Users)

While your agent is running a Ralph Loop, you can ask it to:

### Check Status
```
"What's the status of the Ralph Loop?"
```
Agent will use process tool to poll and show current state.

### View Progress
```
"Show me the recent output"
```
Agent will use process tool with action: "log" to display recent activity.

### Stop the Loop
```
"Stop the Ralph Loop"
```
Agent will use process tool with action: "kill" to terminate the session.

### Check What's Been Completed
```
"What tasks are done?"
```
Agent will read IMPLEMENTATION_PLAN.md and report progress.

## Troubleshooting

### Problem: OpenCode/Codex Hangs

**Cause**: Interactive CLIs need real TTY environment

**Solution**: Agent must use exec tool with `pty: true` parameter

**For users**: If your agent reports hanging, say: "Make sure you're using pty: true in the exec tool"

### Problem: Can't See What's Happening

**Solution**: Ask your agent:
- "Show me the logs"
- "What's the current status?"
- "Display recent output"

Agent will use process tool to retrieve information.

### Problem: Loop Takes Too Long

**Solution**: Ask your agent:
- "What iteration are we on?"
- "Stop this and let's try with fewer iterations"
- "Can we simplify the task?"

### Problem: Agent Reports Session Won't Start

**Check with agent**:
- Is the project in a Git repository?
- Is the coding CLI installed?
- Are the command strings correct?

## Best Practices

### For Users

1. **Start Small**: First time? Try 2-3 iterations to see how it works
2. **Clear Requirements**: Provide detailed specs in `specs/*.md` files
3. **Stay Engaged**: Check in periodically, don't just "fire and forget"
4. **Trust Your Agent**: It knows how to use the exec and process tools correctly

### For OpenClaw Agents

1. **Always Use pty: true**: For interactive CLIs (OpenCode, Codex, Claude, Goose)
2. **Set Reasonable Timeouts**: Default 3600s, adjust based on task complexity
3. **Monitor Regularly**: Poll every 10-30 seconds, not too frequently
4. **Check Completion**: Always read IMPLEMENTATION_PLAN.md after each iteration
5. **Report Progress**: Keep user informed of current iteration and status
6. **Save Logs**: Store output for debugging if things go wrong
7. **Workdir Isolation**: Use workdir parameter to limit file access scope

## Security Considerations

### For Agents: Sandbox Environments

When using auto-approval flags, prefer sandboxed execution:

**Codex with sandbox:**
```
exec tool with:
  command: "codex exec --sandbox docker --full-auto \"$(cat PROMPT.md)\""
```

**Available sandboxes:**
- Docker (local isolation)
- E2B (cloud sandbox)
- Fly.io (temporary containers)

### Auto-Approval Flags (Use Cautiously)

- **Codex**: `--full-auto` (sandboxed) or `--yolo` (⚠️ no sandbox)
- **Claude**: `--dangerously-skip-permissions` (⚠️ skips checks)

**Agent should warn user** when using auto-approval without sandbox.

### Credential Management

- Use read-only or limited permission API keys
- Don't include secrets in PROMPT.md
- Use environment variables

### Workdir Isolation

Agent should set workdir parameter to limit file access:
```
exec tool with:
  workdir: "/path/to/specific/project"
```

## Escape Hatches

If things go wrong:

### For Users

**Stop immediately:**
```
"Stop the Ralph Loop now"
"Kill the current session"
```

**Rollback changes:**
```
"Undo the last 3 commits"
"Reset to the previous state"
```

### For Agents

**Kill session:**
```
process tool:
  action: "kill"
  sessionId: <session_id>
```

**Help user rollback:**
```
exec tool:
  command: "git reset --hard HEAD~N"
```

## License

MIT License

## Contributing

Welcome to submit issues and improvement suggestions!

If you improve this skill, please consider sharing to Clawhub.

## Related Resources

- [OpenClaw Documentation](https://openclaw.com/docs)
- [Original Ralph Loop](https://github.com/openclaw/skills/blob/main/skills/jordyvandomselaar/ralph-loop/SKILL.md)
- [Coding Agent](https://github.com/openclaw/skills/blob/main/skills/steipete/coding-agent/SKILL.md)
- [Ralph Wiggum Playbook](https://ralphwiggum.dev)
