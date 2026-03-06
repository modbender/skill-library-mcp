# OpenClaw Integration

Complete setup and usage guide for integrating the Mulch Self Improver skill with OpenClaw. For features, benefits, and pain points (qualification), see [QUALIFICATION.md](../QUALIFICATION.md).

## Overview

OpenClaw uses workspace-based prompt injection combined with event-driven hooks. Context is injected from workspace files at session start, and hooks can trigger on lifecycle events.

## Workspace Structure

```
~/.openclaw/                      
├── workspace/                   # Working directory
│   ├── AGENTS.md               # Multi-agent coordination patterns
│   ├── SOUL.md                 # Behavioral guidelines and personality
│   ├── TOOLS.md                # Tool capabilities and gotchas
│   ├── MEMORY.md               # Long-term memory (main session only)
│   └── memory/                 # Daily memory files
│       └── YYYY-MM-DD.md
├── skills/                      # Installed skills
│   └── <skill-name>/
│       └── SKILL.md
└── hooks/                       # Custom hooks
    └── <hook-name>/
        ├── HOOK.md
        └── handler.ts
```

## Quick Setup

### 1. Install the Skill

```bash
clawdhub install self-improving-agent
```

Or copy manually:

```bash
cp -r self-improving-agent ~/.openclaw/skills/
```

### 2. Install the Hook (Optional)

Copy the hook to OpenClaw's hooks directory:

```bash
cp -r hooks/openclaw ~/.openclaw/hooks/self-improvement
```

Enable the hook:

```bash
openclaw hooks enable self-improvement
```

### 3. Use Mulch for Learnings

This skill uses [Mulch](https://github.com/jayminwest/mulch) as the learning store (no `.learnings/`). In each project or workspace where you want expertise to accumulate:

```bash
mulch init
mulch add api
mulch add database
# add domains as needed
```

At session start run `mulch prime`. Record with `mulch record <domain> --type failure|convention|decision|pattern|guide`. See SKILL.md for full workflow.

## Injected Prompt Files

### AGENTS.md

Purpose: Multi-agent workflows and delegation patterns.

```markdown
# Agent Coordination

## Delegation Rules
- Use explore agent for open-ended codebase questions
- Spawn sub-agents for long-running tasks
- Use sessions_send for cross-session communication

## Session Handoff
When delegating to another session:
1. Provide full context in the handoff message
2. Include relevant file paths
3. Specify expected output format
```

### SOUL.md

Purpose: Behavioral guidelines and communication style.

```markdown
# Behavioral Guidelines

## Communication Style
- Be direct and concise
- Avoid unnecessary caveats and disclaimers
- Use technical language appropriate to context

## Error Handling
- Admit mistakes promptly
- Provide corrected information immediately
- Log significant errors to learnings
```

### TOOLS.md

Purpose: Tool capabilities, integration gotchas, local configuration.

```markdown
# Tool Knowledge

## Self-Improvement (Mulch)
Run `mulch prime` at session start; record with `mulch record <domain> --type ...`. Promote proven patterns to SOUL.md, AGENTS.md, TOOLS.md.

## Local Tools
- Document tool-specific gotchas here
- Note authentication requirements
- Track integration quirks
```

## Learning Workflow (Mulch)

### Capturing Learnings

1. **In-session**: `mulch record <domain> --type failure|convention|decision|pattern|guide` as appropriate
2. **Cross-session**: Promote proven patterns to workspace files (SOUL.md, AGENTS.md, TOOLS.md)

### Promotion Decision Tree

```
Is the learning project-specific?
├── Yes → Keep in .mulch/ (mulch record)
└── No → Is it behavioral/style-related?
    ├── Yes → Promote to SOUL.md
    └── No → Is it tool-related?
        ├── Yes → Promote to TOOLS.md
        └── No → Promote to AGENTS.md (workflow)
```

### Promotion Format Examples

**From learning:**
> Git push to GitHub fails without auth configured - triggers desktop prompt

**To TOOLS.md:**
```markdown
## Git
- Don't push without confirming auth is configured
- Use `gh auth status` to check GitHub CLI auth
```

## Inter-Agent Communication

OpenClaw provides tools for cross-session communication:

### sessions_list

View active and recent sessions:
```
sessions_list(activeMinutes=30, messageLimit=3)
```

### sessions_history

Read transcript from another session:
```
sessions_history(sessionKey="session-id", limit=50)
```

### sessions_send

Send message to another session:
```
sessions_send(sessionKey="session-id", message="Learning: API requires X-Custom-Header")
```

### sessions_spawn

Spawn a background sub-agent:
```
sessions_spawn(task="Research X and report back", label="research")
```

## Available Hook Events

| Event | When It Fires |
|-------|---------------|
| `agent:bootstrap` | Before workspace files inject |
| `command:new` | When `/new` command issued |
| `command:reset` | When `/reset` command issued |
| `command:stop` | When `/stop` command issued |
| `gateway:startup` | When gateway starts |

## Detection Triggers

### Standard Triggers
- User corrections ("No, that's wrong...")
- Command failures (non-zero exit codes)
- API errors
- Knowledge gaps

### OpenClaw-Specific Triggers

| Trigger | Action |
|---------|--------|
| Tool call error | Log to TOOLS.md with tool name |
| Session handoff confusion | Log to AGENTS.md with delegation pattern |
| Model behavior surprise | Log to SOUL.md with expected vs actual |
| Skill issue | Record with mulch or report upstream |

## Verification

Check hook is registered:

```bash
openclaw hooks list
```

Check skill is loaded:

```bash
openclaw status
```

## Troubleshooting

### Hook not firing

1. Ensure hooks enabled in config
2. Restart gateway after config changes
3. Check gateway logs for errors

### Expertise not persisting

1. Ensure project has `mulch init` and `mulch add <domain>` run
2. Run from the directory that contains `.mulch/`
3. Use `mulch status` to verify; check file permissions on `.mulch/expertise/`

### Skill not loading

1. Check skill is in skills directory
2. Verify SKILL.md has correct frontmatter
3. Run `openclaw status` to see loaded skills
