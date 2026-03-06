---
name: cursor-agent
version: 3.0.2
description: "Use Cursor Agent for coding tasks via two paths: (1) Local CLI — run Cursor Agent directly from terminal for fast, general-purpose coding in any project; (2) VS Code Node — control a remote Cursor/VS Code IDE through OpenClaw Node protocol for targeted project work with full IDE intelligence. Prefer CLI for speed; use Node when you need IDE features (diagnostics, references, debugging)."
metadata:
  {
    "openclaw": {
      "emoji": "🖥️",
      "requires": { "anyBins": ["agent", "cursor-agent"] }
    },
  }
---

# Cursor Agent Skill

Two ways to use Cursor Agent from OpenClaw, for different scenarios.

## Related

- **[OpenClaw Node for VS Code](https://marketplace.visualstudio.com/items?itemName=xiaoyaner.openclaw-node-vscode)** — VS Code/Cursor extension that enables the Node path (install this first for Path 2)
- **[vscode-node](https://clawhub.ai/xiaoyaner0201/vscode-node)** — Standalone skill for the Node path only (if you don't need Cursor CLI)
- **Source**: [github.com/xiaoyaner-home/openclaw-vscode](https://github.com/xiaoyaner-home/openclaw-vscode)

## Path Selection

| Scenario | Path | Why |
|----------|------|-----|
| Quick coding task, bug fix, refactor | **CLI** | Fast, no setup, works anywhere |
| Generate code, review PR, write tests | **CLI** | Non-interactive `-p` mode is perfect |
| Fix type errors using real diagnostics | **Node** | `diagnostics.get` shows actual TS/lint errors |
| Navigate definitions/references first | **Node** | `lang.definition`, `lang.references` |
| Run project tests and iterate | **Node** | `test.run` + `test.results` loop |
| Debug with breakpoints | **Node** | Full debug protocol |
| Targeted changes to a specific project | **Node** | IDE workspace context is precise |

**Default: CLI.** Use Node only when you specifically need IDE intelligence.

---

## Path 1: CLI (Local Cursor Agent)

### Prerequisites

```bash
# Install
curl https://cursor.com/install -fsS | bash

# Login
agent login

# Verify
agent --version
```

### Modes

| Mode | Flag | Use Case |
|------|------|----------|
| **Agent** | (default) | Full coding — reads, writes, runs commands |
| **Plan** | `--plan` or `--mode=plan` | Design approach first, then choose local or cloud execution |
| **Ask** | `--mode=ask` | Read-only codebase exploration, no edits |

### Interactive Mode

```bash
# Start interactive session
agent

# Start with prompt
agent "refactor the auth module to use JWT tokens"

# Start in plan mode
agent --plan "design a caching layer for the API"

# Start in ask mode
agent --mode=ask "explain how the auth middleware works"
```

### Non-Interactive Mode (Automation)

```bash
# One-shot task (prints result, exits)
agent -p "find and fix all unused imports in src/"

# With specific model
agent -p "review this code for security issues" --model gpt-5.2

# JSON output for parsing
agent -p "list all TODO comments" --output-format json

# Streaming JSON (real-time)
agent -p "run tests and report" --output-format stream-json --stream-partial-output

# Force mode (auto-apply changes, no confirmation)
agent -p "fix all linting errors" --force
```

### Cloud Agent Handoff

Push work to Cursor's cloud to continue running while you're away:

```bash
# Start directly in cloud
agent -c "refactor the auth module and add comprehensive tests"

# Mid-conversation: prepend & to send to cloud
& refactor the auth module and add comprehensive tests
```

Pick up at [cursor.com/agents](https://cursor.com/agents).

### Session Management

```bash
agent ls              # List previous conversations
agent resume          # Resume most recent
agent --continue      # Continue previous session
agent --resume="id"   # Resume specific conversation
```

### Slash Commands (Interactive)

| Command | Action |
|---------|--------|
| `/plan` | Switch to Plan mode / view current plan |
| `/ask` | Switch to Ask mode |
| `/models` | Switch AI model |
| `/compress` | Summarize conversation, free context |
| `/rules` | Create/edit rules |
| `/commands` | Create/edit custom commands |
| `/mcp enable <name>` | Enable MCP server |
| `/mcp disable <name>` | Disable MCP server |
| `/sandbox` | Configure sandbox mode |
| `/max-mode [on\|off]` | Toggle Max Mode |
| `/resume` | Resume previous conversation |

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Shift+Tab` | Rotate modes (Agent → Plan → Ask) |
| `Shift+Enter` | Insert newline (multi-line prompt) |
| `Ctrl+R` | Review changes (`i` for instructions, arrows to navigate) |
| `Ctrl+D` | Exit (double-press for safety) |
| `ArrowUp` | Cycle previous messages |

### Context & Rules

The CLI automatically loads:
- `.cursor/rules` directory
- `AGENTS.md` at project root
- `CLAUDE.md` at project root
- MCP servers from `mcp.json`

Use `@filename` or `@directory/` in interactive mode to include context.

### ⚠️ Using CLI from OpenClaw (PTY Required)

Cursor CLI is an interactive TUI — it needs a real terminal. Use `pty:true`:

```bash
# ✅ Correct — with PTY
exec pty:true command:"agent -p 'Your task'" workdir:/path/to/project

# ✅ Background for longer tasks
exec pty:true background:true command:"agent -p 'Build REST API'" workdir:/path/to/project

# ❌ Wrong — will hang
exec command:"agent -p 'Your task'"
```

**For long tasks, use background + poll:**

```bash
# Start
exec pty:true background:true workdir:~/project command:"agent -p 'Add comprehensive tests for the auth module' --force"

# Check progress
process action:log sessionId:XXX

# Check if done
process action:poll sessionId:XXX
```

### Sandbox Controls

```bash
# Start with sandbox enabled
agent --sandbox enabled

# Start with sandbox disabled
agent --sandbox disabled

# Configure interactively
/sandbox
```

Sandbox supports granular network access controls — define which domains the agent can reach.

---

## Path 2: VS Code / Cursor Node

Remote-control a Cursor/VS Code IDE through the OpenClaw Node protocol. The IDE must have the `openclaw-node-vscode` extension installed and connected.

### Prerequisites

- Extension installed: [VS Code Marketplace](https://marketplace.visualstudio.com/items?itemName=xiaoyaner.openclaw-node-vscode)
- Node visible in `nodes status`
- Extension status bar shows 🟢

### Invocation Pattern

```
nodes invoke --node "<name>" --invokeCommand "<cmd>" --invokeParamsJson '{"key":"val"}'
```

### Timeout Guide

| Operation | invokeTimeoutMs | Notes |
|-----------|----------------|-------|
| File/editor/lang | 15000 | Fast IDE operations |
| Git | 30000 | May involve disk I/O |
| Test | 60000 | Depends on test suite |
| Agent plan/ask | 180000 | AI thinking time |
| Agent run | 300000 | Full coding task |

### Command Reference

| Category | Prefix | Key Commands |
|----------|--------|-------------|
| **File** | `vscode.file.*` | read, write, edit, delete |
| **Directory** | `vscode.dir.*` | list |
| **Language** | `vscode.lang.*` | definition, references, hover, symbols, rename, codeActions, format |
| **Editor** | `vscode.editor.*` | context, openFiles, selections |
| **Diagnostics** | `vscode.diagnostics.*` | get (errors/warnings) |
| **Git** | `vscode.git.*` | status, diff, log, blame, stage, unstage, commit, stash |
| **Test** | `vscode.test.*` | list, run, results |
| **Debug** | `vscode.debug.*` | launch, stop, breakpoint, evaluate, stackTrace, variables, status |
| **Agent** | `vscode.agent.*` | status, run, setup |
| **Workspace** | `vscode.workspace.*` | info |

### Quick Examples

```bash
# Read a file
nodes invoke --node "my-cursor" --invokeCommand "vscode.file.read" \
  --invokeParamsJson '{"path":"src/main.ts"}'

# Get diagnostics (real type errors!)
nodes invoke --node "my-cursor" --invokeCommand "vscode.diagnostics.get"

# Go to definition
nodes invoke --node "my-cursor" --invokeCommand "vscode.lang.definition" \
  --invokeParamsJson '{"path":"src/main.ts","line":10,"character":5}'

# Git status + commit
nodes invoke --node "my-cursor" --invokeCommand "vscode.git.status"
nodes invoke --node "my-cursor" --invokeCommand "vscode.git.stage" \
  --invokeParamsJson '{"paths":["src/main.ts"]}'
nodes invoke --node "my-cursor" --invokeCommand "vscode.git.commit" \
  --invokeParamsJson '{"message":"fix: resolve type error"}'

# Delegate to Cursor Agent (through IDE)
nodes invoke --node "my-cursor" --invokeCommand "vscode.agent.run" \
  --invokeParamsJson '{"prompt":"Add error handling to all API endpoints","mode":"plan"}' \
  --invokeTimeoutMs 180000
```

### Node Workflow: Fix → Verify → Commit

The real power of Node path — a closed loop with IDE intelligence:

```
1. diagnostics.get           → Find real errors
2. vscode.agent.run (fix)    → Let Cursor Agent fix them
3. diagnostics.get           → Verify errors resolved
4. test.run                  → Run tests
5. test.results              → Check results
6. git.diff                  → Review changes
7. git.stage + git.commit    → Ship it
```

No tmux, no TTY hacks — all through VS Code API.

---

## Combined Workflow Example

Use CLI for broad tasks, switch to Node for precision:

```
1. CLI: agent -p "implement user authentication module" --force
   → Generates the initial code quickly

2. Node: vscode.diagnostics.get
   → Reveals 3 type errors the CLI missed

3. Node: vscode.agent.run '{"prompt":"fix these type errors: ..."}'
   → Fixes with full IDE context

4. Node: vscode.test.run
   → Runs test suite

5. Node: vscode.git.stage + vscode.git.commit
   → Clean commit
```

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| CLI hangs | No PTY | Add `pty:true` to exec |
| `node not found` | Extension disconnected | Check VS Code status bar |
| `command not allowed` | Gateway whitelist | Add to `gateway.nodes.allowCommands` |
| `timeout` | Operation too long | Increase `invokeTimeoutMs` |
| `path traversal blocked` | Absolute path used | Use relative paths for Node |

## Security

- **CLI**: Respects sandbox mode, command approval, rules
- **Node**: All paths relative to workspace, Ed25519 device identity, Gateway approval required
- **Both**: No raw shell access by default
