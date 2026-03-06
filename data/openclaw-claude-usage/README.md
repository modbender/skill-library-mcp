# claude-usage

Check your Claude Max subscription usage limits via the Claude Code CLI.

## What It Does

This skill launches the Claude Code CLI interactively, runs the `/usage` command, and extracts your current subscription usage metrics including:

- **Current session usage**: percentage used and reset time
- **Current week (all models)**: percentage used and reset date
- **Current week (Sonnet only)**: percentage used (if available)

Perfect for monitoring your Claude API quota without leaving your agent workflow.

## Requirements

- **Claude Code CLI** must be installed and authenticated
  - Install: `npm install -g @anthropic-ai/claude-code` or `brew install anthropic-ai/tap/claude`
  - Authenticate: `claude auth login`
- **Claude Max subscription** (the skill checks Max plan usage)
- **expect** must be installed (available on macOS via `/usr/bin/expect`)

## Installation

### As a standalone skill:

```bash
cd ~/.openclaw/workspace/skills
git clone https://github.com/openclaw-community/openclaw-skill-claude-usage.git claude-usage
```

## Usage

Ask your agent:
- "What's my Claude usage?"
- "How much Claude quota do I have left?"
- "Check my Claude Max subscription limits"
- Or send: `/claude_usage`

The agent will:
1. Launch Claude Code CLI using `expect` script automation
2. Execute the `/usage` command automatically
3. Parse the output and strip ANSI codes
4. Return your usage metrics in a readable format

## Example Output

```
Current session: 21% used (Resets 5:59pm PST)
Current week (all models): 28% used (Resets Feb 21 at 6am PST)
Current week (Sonnet only): 29% used (Resets Feb 21 at 7am PST)
Extra usage: $50 free available
```

## Scope & Boundaries

**What this skill handles:**
- Reading Claude Max plan usage from Claude Code CLI
- Parsing and formatting usage metrics for user

**What this skill does NOT handle:**
- Modifying subscription plans or billing
- Enabling/disabling extra usage
- API credit management (separate from Max plan)
- Checking usage for other accounts

**Where it ends:**
- Delivers formatted usage metrics to user
- Does not take any action on the account

## Files

- **SKILL.md** - Main skill documentation with detailed procedure
- **skill.yml** - Skill metadata and configuration
- **tests/test-triggers.json** - Example triggers for testing
- **scripts/** - Executable scripts (placeholder)
- **references/** - Reference documentation (placeholder)

## License

MIT License - See [LICENSE](LICENSE) for details
