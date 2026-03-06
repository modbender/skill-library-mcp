---
name: opencode
description: "OpenCode AI - AI-driven code editor/IDE (CLI/TUI version of Cursor/Windsurf). Use when: (1) AI-assisted coding tasks, (2) Code refactoring with AI, (3) GitHub PR review/fixes, (4) Multi-file edits requiring context, (5) Running AI agents on codebases. NOT for: simple one-line edits (use edit tool), reading files (use read tool)."
metadata:
  {
    "openclaw": { "emoji": "🤖", "requires": { "bins": ["opencode"] } },
  }
---

# OpenCode AI - AI Code Editor

OpenCode is an **AI-native code editor** that runs in your terminal. Think of it as Cursor or Windsurf, but as a CLI/TUI tool.

**Version**: 1.2.10 (Homebrew)
**Platform**: macOS Darwin x64

## Prerequisites

**CRITICAL**: OpenCode requires `sysctl` to detect system architecture. Ensure `/usr/sbin` is in your PATH:

```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

If missing, OpenCode will fail with:
```
Executable not found in $PATH: "sysctl"
```

Add this to `~/.zshrc` permanently:
```bash
echo 'export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## When to Use OpenCode

✅ **Use for:**
- Complex refactoring across multiple files
- AI-assisted feature implementation
- GitHub PR review and automated fixes
- Exploring and understanding unfamiliar codebases
- Running multi-step coding tasks with context
- Session-based coding (continue previous work)

❌ **Don't use for:**
- Simple one-line edits (use `edit` tool)
- Reading file contents (use `read` tool)
- Non-coding tasks

---

## Core Operations (TUI Slash Commands)

When running OpenCode in **TUI mode** (`opencode`), you can use these slash commands to control the AI workflow:

### /sessions - Session Management
```
/sessions
```
- Opens session selector
- Choose to continue an existing session
- Create a new session (with user approval)
- Recommended: Select existing session for current project

### /agents - Agent (Mode) Control
```
/agents
```
Available agents:
- **plan** - Planning mode (analyze and design)
- **build** - Build mode (implement and code)
- **explore** - Exploration mode (understand codebase)
- **general** - General assistance

**Best Practice**: Always select **plan** first, then switch to **build** after approval.

### /models - Model Selection
```
/models
```
- Opens model selector
- Filter by provider (OpenAI, Anthropic, Google, Z.AI, etc.)
- Select preferred model for the task
- If authentication required, follow the login link provided

### Agent Workflow

#### Plan Agent Behavior
- Ask OpenCode to analyze the task
- Request a clear step-by-step plan
- Allow OpenCode to ask clarification questions
- Review the plan carefully
- If plan is incomplete, ask for revision
- **Do not allow code generation in Plan mode**

#### Build Agent Behavior
- Switch to Build using `/agents`
- Ask OpenCode to implement the approved plan
- If OpenCode asks questions, switch back to Plan
- Answer and confirm the plan, then switch back to Build

#### Plan → Build Loop
1. Select **plan** agent with `/agents`
2. Describe the task
3. Review and approve the plan
4. Switch to **build** agent with `/agents`
5. Implement the plan
6. Repeat until satisfied

**Key Rules**:
- Never skip Plan
- Never answer questions in Build mode (switch to Plan first)
- Always show slash commands explicitly in output

### Other Useful Commands
- **/title** - Change session title
- **/summary** - Generate session summary
- **/compaction** - Compact conversation history

---

## Core Commands

### 1. Quick Tasks (One-Shot)

```bash
# Run a single AI command on a project
opencode run "Add input validation to the login form"

# With specific directory
opencode run --dir ~/path/to/project "Refactor this code to use async/await"

# With specific model
opencode run -m openai/gpt-4o "Optimize the database queries"

# Attach files for context
opencode run -f src/auth.js -f src/database.js "Fix the authentication bug"

# Continue last session
opencode run --continue

# Continue specific session
opencode run --session abc123 --fork
```

### 2. Interactive TUI Mode

```bash
# Start TUI in current directory
opencode

# Start TUI in specific project
opencode ~/path/to/project

# Start with specific model
opencode -m anthropic/claude-sonnet-4
```

### 3. Authentication

```bash
# List configured providers
opencode auth list

# Login to a provider (e.g., OpenCode, OpenAI, Anthropic)
opencode auth login [url]

# Logout
opencode auth logout
```

### 4. Model Management

```bash
# List all available models
opencode models

# List models for specific provider
opencode models openai

# List with cost metadata
opencode models --verbose

# Refresh model cache
opencode models --refresh
```

### 5. Session Management

```bash
# List all sessions
opencode session list

# Delete a session
opencode session delete <sessionID>

# Export session data
opencode export [sessionID]

# Import session from file
opencode import <file>
```

### 6. GitHub Integration

```bash
# Fetch and checkout a PR, then run OpenCode
opencode pr 123

# Manage GitHub agent
opencode github --help
```

### 7. MCP Servers (Model Context Protocol)

```bash
# List MCP servers
opencode mcp list

# Add an MCP server
opencode mcp add

# Authenticate with OAuth MCP server
opencode mcp auth [name]

# Debug OAuth connection
opencode mcp debug <name>
```

### 8. Agent Management

```bash
# List all agents
opencode agent list

# Create a new agent
opencode agent create
```

### 9. Server Mode

```bash
# Start headless server
opencode serve

# Start server and open web interface
opencode web

# Start ACP (Agent Client Protocol) server
opencode acp
```

### 10. Statistics

```bash
# Show token usage and costs
opencode stats
```

---

## Key Options (Global)

| Option | Description |
|--------|-------------|
| `-m, --model` | Model to use (format: `provider/model`) |
| `-c, --continue` | Continue last session |
| `-s, --session` | Continue specific session |
| `--fork` | Fork session when continuing |
| `--agent` | Use specific agent |
| `--dir` | Directory to run in |
| `--format` | Output format: `default` or `json` |
| `--thinking` | Show thinking blocks |
| `--variant` | Model reasoning effort (`high`, `max`, `minimal`) |

---

## Common Patterns

### Pattern 1: Refactor Code

```bash
opencode run "Refactor this function to be more readable and add error handling"
```

### Pattern 2: Add Features

```bash
opencode run "Add a new API endpoint for user registration with email verification"
```

### Pattern 3: Fix Bugs

```bash
opencode run -f error.log -f src/auth.js "Fix the authentication bug described in the error log"
```

### Pattern 4: Review Code

```bash
opencode run "Review this code for security vulnerabilities and suggest improvements"
```

### Pattern 5: GitHub PR Workflow

```bash
# Auto-fix a PR
opencode pr 123
```

### Pattern 6: Continue Previous Work

```bash
# Continue last session
opencode run --continue

# Fork and continue (keeps original intact)
opencode run --continue --fork
```

---

## Session-Based Work

OpenCode maintains **sessions** that preserve context across runs:

```bash
# Start a new session
opencode run "Implement user authentication"

# Continue it later
opencode run --continue

# Or continue a specific session
opencode run --session session-abc123
```

### Session Lifecycle

1. **Create**: Run `opencode run "prompt"` or `opencode`
2. **Continue**: Use `--continue` or `--session <id>`
3. **Fork**: Use `--fork` to branch from a session
4. **Export**: Save session data as JSON
5. **Delete**: Remove old sessions

---

## Model Selection

### Format

```
provider/model
```

Examples:
- `openai/gpt-4o`
- `anthropic/claude-sonnet-4`
- `opencode/gpt-4o`
- `google/gemini-2.5-pro`

### List Available Models

```bash
# All models
opencode models

# Provider-specific
opencode models openai
opencode models anthropic
```

### Model Variants (Reasoning Effort)

Some models support reasoning effort levels:

```bash
opencode run --variant high "Solve this complex algorithm problem"
opencode run --variant max "Architect a distributed system"
opencode run --variant minimal "Quick code review"
```

---

## JSON Mode (For Automation)

Use `--format json` for machine-readable output:

```bash
opencode run --format json "Refactor this code" | jq .
```

Useful for:
- CI/CD integration
- Scripting
- Parsing results programmatically

---

## Web Interface

For a GUI experience:

```bash
# Start server + open browser
opencode web

# Custom port
opencode web --port 8080

# Custom hostname
opencode web --hostname 0.0.0.0
```

---

## Troubleshooting

### "sysctl not found" Error

**Problem**: OpenCode can't find `sysctl` command
**Solution**:
```bash
export PATH="/usr/sbin:/usr/bin:/sbin:/bin:$PATH"
```

Add to `~/.zshrc` to make permanent.

### "Failed to change directory" Error

**Problem**: OpenCode treats arguments as directory paths
**Solution**: Use flags like `--version`, `--help`, or `run` explicitly:
```bash
# Wrong
opencode version

# Right
opencode --version
```

### OpenCode hangs or freezes

**Problem**: Interactive TUI waiting for input
**Solution**: Press `Ctrl+C` to exit, or use `run` mode for non-interactive tasks.

### Permission issues

**Problem**: Can't write to files
**Solution**: Ensure file/directory permissions allow your user to write:
```bash
chmod +w ./path/to/file
```

---

## Integration with OpenClaw

### Use via exec tool

```bash
# For simple tasks
bash command:"opencode run 'Add error handling'"

# For longer tasks (background)
bash background:true command:"opencode run 'Refactor entire codebase'"
```

### Check current sessions

```bash
bash command:"opencode session list"
```

### View stats

```bash
bash command:"opencode stats"
```

---

## Tips & Best Practices

1. **Be specific**: Clear prompts produce better results
2. **Use files**: Attach relevant files with `-f` for context
3. **Iterate**: Use `--continue` to build on previous work
4. **Fork experiments**: Use `--fork` to try variations safely
5. **Choose models wisely**: Different models excel at different tasks
6. **Monitor costs**: Use `opencode stats` to track token usage
7. **Leverage sessions**: Sessions maintain context across interactions

---

## Comparison to Other Tools

| Feature | OpenCode | Cursor | Windsurf | Claude Code |
|---------|----------|--------|----------|-------------|
| Interface | CLI/TUI | GUI | GUI | CLI |
| Terminal-native | ✅ | ❌ | ❌ | ✅ |
| Session management | ✅ | ✅ | ✅ | ✅ |
| GitHub PR integration | ✅ | ✅ | ✅ | ✅ |
| Model support | Multi | Multi | Multi | Anthropic |
| MCP support | ✅ | ❌ | ❌ | ❌ |

**Choose OpenCode when**:
- You prefer terminal workflows
- Need CI/CD integration
- Want headless/server mode
- Require MCP protocol support

---

## Documentation & Resources

- **Version**: `opencode --version`
- **Help**: `opencode --help` or `opencode <command> --help`
- **Models**: `opencode models --verbose`
- **Sessions**: `opencode session list`

---

*Last updated: 2026-02-25*
