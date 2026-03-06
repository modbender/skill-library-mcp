---
name: claude-usage
description: Check Claude Max plan usage limits by launching Claude Code and running /usage. Use when the user asks about Claude plan usage, remaining quota, rate limits, or sends /claude_usage.
---

# Claude Usage

Check Claude Max subscription usage by launching Claude Code interactively.

## Requirements

- `expect` must be installed (available at `/usr/bin/expect` on macOS)
- Claude Code CLI must be installed and authenticated

## Procedure

Use `expect` to automate the interactive TUI (the `/usage` command is a terminal UI, not a simple CLI):

1. Run the expect script to launch Claude Code and execute `/usage`:
   ```bash
   expect -c '
   spawn claude
   expect "Welcome"
   send "/usage\r"
   expect "Show plan usage"
   sleep 1
   send "\r"
   expect "Resets"
   '
   ```

2. Parse the output for these metrics:
   - **Current session**: Look for "Current session" line with percentage and reset time
   - **Current week (all models)**: Look for "Current week (all models)" with percentage and reset date
   - **Current week (Sonnet only)**: Look for "Current week (Sonnet only)" with percentage
   - **Extra usage**: Look for "Extra usage" line

3. Strip ANSI escape codes from output before parsing

4. Format and relay the metrics to the user

## Example Output

The expect script returns something like:
```
Current session     ██████████░░░░░░░░░░░░░░░░░ 21% used    Resets 5:59pm (America/Los_Angeles)

Current week (all models)
████████████████████████░░░░░░░░░░░░░ 28% used    Resets Feb 21 at 6am (America/Los_Angeles)

Current week (Sonnet only)
█████████████████████████░░░░░░░░░░░░ 29% used    Resets Feb 21 at 7am (America/Los_Angeles)

Extra usage
Extra usage not enabled • /extra-usage to enable

$50 free extra usage · /extra-usage to enable
```

## Fallback

If `expect` is not available, fall back to:
1. `claude auth status` - shows subscription type (Max/Pro)
2. `~/.claude/stats-cache.json` - shows local session token counts (limited data)
