---
name: claude-usage
description: Check Claude Code / Claude Max usage limits. Run when user asks about usage, limits, quota, or how much Claude capacity is left.
homepage: https://github.com/aligurelli/clawd
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["claude"], "pty": true }
      }
  }
---

# Claude Usage Checker

Launches the Claude CLI interactively (PTY) and reads the `/usage` output to report your Claude Code / Claude Max quota.

## Prerequisites
- **Claude CLI** must be installed (`npm i -g @anthropic-ai/claude-code`) and logged in
- If running `claude` shows "Missing API key", the user must log in manually first: open a terminal, run `claude`, and complete the browser login flow
- Requires an interactive PTY — the agent will launch a local process and read its output (quota info only)

## Steps

1. Launch `claude` with PTY
2. Wait for the welcome screen (poll until it appears)
3. Send `/usage` + Enter
4. Read the output (poll until usage data appears)
5. Close with Escape then `/exit`
6. Report the results

## Commands

```bash
# Launch claude with PTY
exec pty=true command="claude"

# Wait and check log
process action=poll sessionId=XXX timeout=5000

# Send /usage
process action=send-keys sessionId=XXX literal="/usage"
process action=send-keys sessionId=XXX keys=["Enter"]

# Read output
process action=poll sessionId=XXX timeout=5000

# Exit
process action=send-keys sessionId=XXX keys=["Escape"]
process action=send-keys sessionId=XXX literal="/exit"
process action=send-keys sessionId=XXX keys=["Enter"]
```

## Notes
- If you see "Missing API key" → tell the user to log in; browser-based login won't work headlessly
- Allow a few seconds between polls — Claude CLI starts slowly
- "Current week" = weekly reset, not daily

## Output Format

Report in a table:

| | Usage | Resets |
|---|---|---|
| **Current session** | X% used | today at HH:MM (timezone) |
| **Weekly (all models)** | X% used | HH:MM (timezone) |
| **Weekly (Sonnet only)** | X% used | HH:MM (timezone) |
| **Extra usage** | X% used / $X of $Y spent | date (timezone) |

Always show reset times. The CLI displays them as "Resets Xpm" — convert to HH:MM format.
