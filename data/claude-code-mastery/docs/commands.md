# Claude Code Command Reference

## CLI Commands

### Starting Sessions

| Command | Description |
|---------|-------------|
| `claude` | Start interactive REPL |
| `claude "query"` | Start REPL with initial prompt |
| `claude -p "query"` | Headless mode: query and exit |
| `claude -c` | Continue most recent conversation |
| `claude -r` | Resume picker (interactive) |
| `claude -r "session-name"` | Resume specific session |
| `claude --from-pr 123` | Resume sessions linked to PR |

### Piping and Integration

| Pattern | Description |
|---------|-------------|
| `cat file \| claude -p "query"` | Process piped content |
| `claude -p "query" --output-format json` | Structured output |
| `claude -p "query" --output-format stream-json` | Real-time streaming |

## CLI Flags

### Essential Flags

| Flag | Description |
|------|-------------|
| `-c, --continue` | Continue most recent conversation |
| `-r, --resume [value]` | Resume by session ID/name or show picker |
| `-p, --print` | Headless mode (non-interactive) |
| `--model <model>` | Set model: `sonnet`, `opus`, or full name |
| `--verbose` | Show full turn-by-turn output |
| `-v, --version` | Output version number |

### Context & System Prompts

| Flag | Description |
|------|-------------|
| `--system-prompt <prompt>` | Replace entire system prompt |
| `--append-system-prompt <prompt>` | Add to default system prompt |
| `--system-prompt-file <path>` | Load system prompt from file |
| `--add-dir <directories...>` | Additional directories to access |

### Permissions & Safety

| Flag | Description |
|------|-------------|
| `--permission-mode <mode>` | `default`, `plan`, `acceptEdits`, `bypassPermissions` |
| `--allowedTools <tools...>` | Tools that execute without permission |
| `--disallowedTools <tools...>` | Tools to deny |
| `--dangerously-skip-permissions` | Bypass all permission checks |

### Agents & Subagents

| Flag | Description |
|------|-------------|
| `--agent <agent>` | Specify agent for session |
| `--agents <json>` | Define custom subagents dynamically |

Example custom agent:
```bash
claude --agents '{
  "code-reviewer": {
    "description": "Expert code reviewer",
    "prompt": "You are a senior code reviewer. Focus on quality and security.",
    "tools": ["Read", "Grep", "Glob", "Bash"],
    "model": "sonnet"
  }
}'
```

### MCP Configuration

| Flag | Description |
|------|-------------|
| `--mcp-config <configs...>` | Load MCP servers from JSON |
| `--strict-mcp-config` | Only use servers from --mcp-config |

### Output Formatting

| Flag | Description |
|------|-------------|
| `--output-format <format>` | `text`, `json`, `stream-json` |
| `--json-schema <schema>` | Validate output against JSON Schema |
| `--max-turns <n>` | Limit agentic turns (headless mode) |
| `--max-budget-usd <amount>` | Maximum spend limit |

### Integration

| Flag | Description |
|------|-------------|
| `--chrome` | Enable Chrome browser integration |
| `--no-chrome` | Disable Chrome integration |
| `--ide` | Auto-connect to IDE if available |

## Slash Commands (In-Session)

### Navigation & Control

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/clear` | Clear conversation history |
| `/context` | View current context usage |
| `/compact [focus]` | Compact conversation, optional focus area |
| `/resume` | Switch to different conversation |
| `/rename <name>` | Give session a descriptive name |
| `/rewind` | Open checkpoint rewind menu |

### Configuration

| Command | Description |
|---------|-------------|
| `/config` | Interactive configuration |
| `/permissions` | Configure permission rules |
| `/login` | Login or switch accounts |
| `/logout` | Log out of current account |
| `/hooks` | Configure lifecycle hooks |

### Tools & Extensions

| Command | Description |
|---------|-------------|
| `/mcp` | Manage MCP servers |
| `/chrome` | Toggle Chrome integration |
| `/init` | Generate CLAUDE.md for project |

### Information

| Command | Description |
|---------|-------------|
| `/usage` | Check rate limits |
| `/stats` | View usage statistics (activity graph) |
| `/cost` | Show session cost information |

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Esc` | Stop current action |
| `Esc Esc` | Open rewind menu |
| `Shift+Tab` | Cycle permission modes |
| `Ctrl+O` | Toggle verbose mode |
| `Option/Alt+T` | Toggle extended thinking |
| `Tab` → `←/→` | Refresh rate limit display |

## MCP Subcommands

```bash
claude mcp add <name> <command> [args...]     # Add stdio server
claude mcp add --transport http <name> <url>  # Add HTTP server
claude mcp add-json <name> <json>             # Add with JSON config
claude mcp list                               # List configured servers
claude mcp get <name>                         # Get server details
claude mcp remove <name>                      # Remove a server
claude mcp add-from-claude-desktop            # Import from Claude Desktop
claude mcp reset-project-choices              # Reset approved servers
claude mcp serve                              # Start Claude Code MCP server
```

## Plugin Subcommands

```bash
claude plugin list              # List installed plugins
claude plugin install <name>    # Install a plugin
claude plugin remove <name>     # Remove a plugin
```

## Other Subcommands

```bash
claude doctor         # Check auto-updater health
claude update         # Check for and install updates
claude setup-token    # Set up authentication token
claude install [target]  # Install specific version
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | API key for authentication |
| `MAX_THINKING_TOKENS` | Limit thinking budget |
| `DISABLE_AUTOUPDATER` | Set to "1" to disable auto-updates |
| `ENABLE_TOOL_SEARCH` | "true" for lazy-load MCP tools |
| `SLASH_COMMAND_TOOL_CHAR_BUDGET` | Skill description limit |
