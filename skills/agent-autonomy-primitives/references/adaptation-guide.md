# Adaptation Guide

How to wire ClawVault primitives into different agent setups.

## Adoption Strategy: Start Minimal

Don't adopt all five primitives at once. Start with what solves your biggest pain:

| Pain Point | Start With | Add Later |
|-----------|-----------|-----------|
| Agent forgets everything | Typed memory (decisions, lessons) | Projects, tasks |
| Agent can't self-direct | Task primitives + heartbeat | Template customization |
| No visibility into agent work | Tasks + Obsidian Bases | Projects, wiki-links |
| Multiple agents duplicate work | Shared vault + projects | Task ownership, templates |

## OpenClaw Agents

OpenClaw agents have built-in heartbeat support. Wire primitives into `HEARTBEAT.md`:

```markdown
## Task-Driven Autonomy
Every heartbeat:
1. `clawvault task list --owner <name> --status open`
2. Sort by priority + due
3. Pick top task, execute, mark done
4. Create new tasks for discovered work
```

**OpenClaw hooks** (in `skills/clawvault/hooks/`) auto-checkpoint on session end and detect context death on startup. These complement task primitives by ensuring progress isn't lost.

**Cron jobs** for isolated task execution:
```
Schedule: every 30 minutes
Payload: "Check your task queue. Pick the highest priority open task owned by you. Execute it. Report what you did."
Session: isolated (doesn't pollute main session context)
```

## LangChain / LangGraph Agents

Wrap ClawVault CLI calls in tool functions:

```python
import subprocess
import json

def list_tasks(owner: str) -> str:
    result = subprocess.run(
        ["clawvault", "task", "list", "--owner", owner, "--status", "open", "--json"],
        capture_output=True, text=True,
        env={**os.environ, "CLAWVAULT_PATH": "/path/to/vault"}
    )
    return result.stdout

def complete_task(slug: str, reason: str) -> str:
    result = subprocess.run(
        ["clawvault", "task", "done", slug, "--reason", reason],
        capture_output=True, text=True,
        env={**os.environ, "CLAWVAULT_PATH": "/path/to/vault"}
    )
    return result.stdout
```

Add these as tools to your agent's tool set. The agent calls them like any other tool.

## CrewAI / AutoGen

Same pattern — wrap CLI in tool functions. The vault is framework-agnostic because it's just files.

For CrewAI specifically, map ClawVault projects to CrewAI tasks:
- CrewAI `Task` = ClawVault project (high-level goal)
- CrewAI agent actions = ClawVault tasks (specific steps)

## Custom Agent Loops

If you have a custom loop, add three integration points:

```
1. ON WAKE:
   - Read recent memory: clawvault context "current focus"
   - Check task queue: clawvault task list --owner <name> --status open

2. DURING EXECUTION:
   - Update task status: clawvault task update <slug> --status in-progress
   - Store discoveries: clawvault remember lesson/decision/fact "..."
   - Create follow-ups: clawvault task add "..." --priority <p>

3. ON COMPLETION:
   - Mark done: clawvault task done <slug> --reason "..."
   - Checkpoint: clawvault checkpoint --working-on "..."
```

## Multi-Agent Collaboration

Multiple agents sharing a vault need ownership conventions:

1. **Set `CLAWVAULT_PATH`** to the same directory for all agents
2. **Use `--owner`** on every task to prevent conflicts
3. **Convention:** agents only pick up tasks owned by them (or unowned)
4. **Handoffs:** change owner to transfer work: `clawvault task update <slug> --owner other-agent`

Example — two agents sharing work:
```bash
# Agent A creates a task for Agent B
clawvault task add "Review PR #42" --owner agent-b --project shared-project --priority high

# Agent B picks it up during heartbeat
clawvault task list --owner agent-b --status open
clawvault task update review-pr-42 --status in-progress
# ... does the review ...
clawvault task done review-pr-42 --reason "Approved, 2 minor comments"
clawvault remember lesson "PR #42 had a race condition in webhook handler" --content "Always use mutex for shared state"
```

Both agents benefit from the lesson. Neither needed a message bus.

## Migrating from Other Memory Systems

### From vector databases (Mem0, Zep, Pinecone)
Export memories as text → categorize by type → store with `clawvault remember <type>`. The filesystem approach consistently outperforms vector-only retrieval (74% vs 68.5% on LoCoMo benchmark).

### From plain text files
If you already have markdown notes, run `clawvault init` in the same directory. ClawVault works alongside existing files. Gradually move content into typed directories.

### From Notion / Linear / Jira
Export tasks as CSV/JSON → write a script that calls `clawvault task add` for each. Map status fields to ClawVault's `open/in-progress/blocked/done`.

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAWVAULT_PATH` | Vault location (required if not running from vault dir) |
| `CLAWVAULT_COMPRESSION_PROVIDER` | LLM for observation compression (default: gemini) |
| `CLAWVAULT_COMPRESSION_MODEL` | Model name for compression |

Set in your agent's environment or shell config.
