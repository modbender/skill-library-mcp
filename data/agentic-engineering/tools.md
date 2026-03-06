# Tool Selection — Agentic Engineering

## Philosophy: Less is More

Every tool has a context cost. Most aren't worth it.

```
"I removed my last MCP since Claude would spin up Playwright 
unasked when it could simply read the code — which is faster 
and pollutes the context less." — steipete
```

## CLIs Beat MCPs

Agents already know common CLIs. No context cost.

| Task | Tool | Config |
|------|------|--------|
| Git ops | `gh` | None needed |
| Logs | `vercel`, `axiom` | One line in AGENTS.md |
| Database | `psql` | Connection example |
| Deploy | `vercel`, `fly` | None needed |

One line is enough: "logs: use vercel cli"

## Skip These

| Category | Why |
|----------|-----|
| RAG systems | Models are good at searching code already |
| Complex MCPs | Context pollution, unpredictable behavior |
| Subagent frameworks | Use separate terminals instead |
| Custom orchestration | Just run parallel agents manually |

## Recommended Stack

### Terminal
- **Ghostty** — Fast, stable, no memory bloat
- **iTerm2** — Good alternative, split panes
- **tmux** — For background tasks

### Coding Agents
- **Codex CLI** — Fast, efficient context use, queues messages
- **Claude Code** — Good for certain tasks, more verbose

### Editor
- **VS Code** — For browsing code, not writing
- **Cursor** — Tab completion if you still type code

### Reviews
- **GPT-5 Pro** — Plan review before big changes
- **chatgpt.com** — Second opinion on architecture

## tmux for Background Tasks

When agent starts a dev server or long test:
```
"Run via tmux"
```

Agent knows tmux. Server runs in background. No stuck terminal.

## Voice Input

**Wispr Flow** — Voice to text with semantic correction.

Great for:
- Long prompts while thinking
- Brainstorming sessions
- Hands-free steering

## Browser Debugging

**chrome-devtools-mcp** — Only MCP worth using.

When needed:
- Debug runtime issues
- Verify UI changes
- Test auth flows

Most of the time: just ask agent to read the code.

## Cost Management

Subscriptions beat API calls:
```
4x OpenAI subs + 1x Anthropic ≈ $1k/month
Equivalent API usage ≈ $5-10k/month
```

Unlimited tokens at subscription rate is the deal.

## What Not to Build

The AI tool market is crowded. Don't build:
- Another Claude Code wrapper
- Yet another worktree manager
- AI orchestration frameworks

Focus on your actual product. Tools are commoditizing fast.
