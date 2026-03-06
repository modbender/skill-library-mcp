# Agent System

## Agent Definitions

Each agent is a Markdown file in `.workplace/agents/` with YAML frontmatter:

```markdown
---
name: coder
role: "Senior developer specializing in backend systems"
triggers: ["code", "implement", "fix", "refactor", "build"]
handoff_to: ["reviewer", "tester"]
persistent: false
---

# Coder Agent

## Role
You are a senior developer working on {workplace_name}.

## Context
- Working directory: {workplace_path}
- Project structure: (loaded from structure.json)
- Deploy config: (loaded from deploy/)

## Instructions
- Write clean, well-tested code
- Follow existing patterns in the codebase
- When done, hand off to reviewer for code review
- If tests need writing, hand off to tester

## Handoff Protocol
When handing off, write to chat.md:
[coder-to-reviewer]: Review needed for {description}. Files: {list}. Context: {summary}
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Agent identifier (lowercase, alphanumeric + hyphens) |
| `role` | Yes | One-line role description |
| `triggers` | No | Keywords that activate this agent |
| `handoff_to` | No | Agents this one can delegate to |
| `persistent` | No | If true, runs continuously (like kernel) |

## Runtime

### Starting an Agent

1. Read the agent's `.md` file
2. Parse YAML frontmatter for metadata
3. Read `.workplace/config.json` for workplace context
4. Read `.workplace/structure.json` for file tree
5. Build system prompt:

```
You are {role} for the {workplace_name} project.

Workplace: {path}
UUID: {uuid}

Project Structure:
{structure.json contents, summarized}

{Body of agent .md file}

Communication:
- Write to .workplace/chat.md to communicate with other agents
- Format: [{your_name}-to-{target}]: message
- Broadcast: [{your_name}-to-{target}] @ [agent1, agent2]: message
- Read chat.md for messages directed to you

Process Status:
- Write your status to .workplace/process-status.json
- On completion: set status to "completed" and stop
- On error: set status to "error" with details
```

6. `sessions_spawn` with this system prompt as the task
7. Update `process-status.json`:

```json
{
  "coder": {
    "status": "running",
    "sessionKey": "agent:main:subagent:...",
    "startedAt": "2026-02-17T10:00:00Z",
    "task": "Implement auth module",
    "error": null
  }
}
```

### Agent Lifecycle

1. **Start** → spawned via `sessions_spawn`
2. **Running** → executes task, communicates via `chat.md`
3. **Handoff** → writes message to `chat.md`, orchestrator starts target agent
4. **Complete** → reports completion, updates `process-status.json`, session ends
5. **Error** → writes error to `process-status.json` with progress for resume

## Swarm Orchestration (Claude Swarm Pattern)

### Handoff Flow

```
User: "Implement the auth module"
  │
  ▼
[Coder Agent] starts
  │ writes code
  │ writes to chat.md: [coder-to-reviewer]: Review auth module
  │
  ▼
[Orchestrator] detects message via Rust server
  │ reads chat.md for context
  │ starts Reviewer Agent with handoff context
  │
  ▼
[Reviewer Agent] starts
  │ reviews code
  │ writes to chat.md: [reviewer-to-coder] @ [developer]: Approved
  │
  ▼
[Orchestrator] detects response
  │ notifies original session
```

### Orchestrator Role

The main OpenClaw session acts as orchestrator:

1. Start the Rust file-watcher server for the workplace
2. Monitor server stdout (JSON lines) for new messages
3. When a handoff message is detected:
   - Read the full `chat.md` for conversation context
   - Start the target agent with the handoff context included
4. When an agent completes, update `process-status.json`

### Context Passing

When handing off, include:
- **What was done** — summary of completed work
- **What's needed** — clear description of the next task
- **Files involved** — specific paths that were modified or need attention
- **Decision context** — why certain choices were made

## process-status.json

Tracks all agent and server states:

```json
{
  "server": {
    "status": "running",
    "pid": 12345,
    "startedAt": "2026-02-17T10:00:00Z",
    "lastEvent": "2026-02-17T10:05:00Z",
    "error": null
  },
  "kernel": {
    "status": "running",
    "sessionKey": "agent:main:subagent:abc123",
    "startedAt": "2026-02-17T10:00:00Z",
    "task": "Structure monitoring",
    "error": null
  },
  "coder": {
    "status": "completed",
    "sessionKey": "agent:main:subagent:def456",
    "startedAt": "2026-02-17T10:01:00Z",
    "completedAt": "2026-02-17T10:15:00Z",
    "task": "Implement auth module",
    "error": null
  }
}
```

### Status Values

| Status | Meaning |
|--------|---------|
| `running` | Agent is actively working |
| `idle` | Agent exists but not started |
| `completed` | Agent finished its task |
| `error` | Agent encountered an error (see `error` field) |
| `stopped` | Agent was manually stopped |
