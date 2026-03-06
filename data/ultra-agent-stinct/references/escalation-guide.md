# Escalation Guide: Self-Handle vs Spawn a Coding Agent

## Do It Yourself (Direct Tools)

Use `read`/`edit`/`exec` directly when:
- Single file fix (one bug, one function)
- Quick script writing (<100 lines)
- Running tests and reading output
- Git status/diff/commit
- Reading error logs
- Config file changes
- Installing packages (`npm install`, `pip install`)

**Advantages:** Faster, less overhead, keeps context in your session.

## Spawn a Coding Agent (Heavy Tasks)

If you have a coding agent CLI installed (e.g. Claude Code, Codex, Aider), spawn it for heavy tasks:

```
exec pty:true background:true command:"<agent> '<task description>'"
```

Use this when:
- Multi-file refactor (3+ files changing)
- Entire new feature with tests
- Complex debugging needing deep codebase exploration
- Tasks needing extended autonomous coding (>10 tool calls)
- Build/deploy pipelines taking >60 seconds
- When the user explicitly asks you to delegate

**Advantages:** Dedicated context window, autonomous multi-step work, won't bloat your session.

**Common coding agent CLIs:**
- `claude` — Claude Code (Anthropic)
- `codex` — Codex CLI (OpenAI)
- `aider` — Aider (open source)

## Monitoring Spawned Agents

```
process action:list                          # See all sessions
process action:poll sessionId:<id>           # Check if done
process action:log sessionId:<id>            # Read output
process action:submit sessionId:<id> data:"yes"  # Send input
process action:kill sessionId:<id>           # Kill it
```

Keep the user updated: message when it starts, when it finishes, if it fails.

## Never Spawn For

- Reading a single file
- Running one command
- Making a small edit
- Git operations
- Anything you can do in 2-3 tool calls
