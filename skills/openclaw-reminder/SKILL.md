---
name: reminder
description: Create one-time reminder tasks using OpenClaw cron. User specifies reminder time and task content in natural language via Discord, and the task result will be sent back through Discord.
metadata:
  {
    "openclaw": {
      "emoji": "⏰",
      "user-invocable": true,
      "requires": { "bins": ["openclaw"], "tools": ["session_status"] }
    }
  }
---

# Reminder Skill

Create one-time reminder tasks using OpenClaw cron.

## Usage

When user says "remind me to XXX in 30 seconds" or "remind me at 3pm", I create a cron job that executes the task and returns the result when the time comes.

## Parameter Configuration

### Fixed Parameters

- `--session main` - Use main session to inherit Discord context
- `--system-event` - System event payload for main session
- `--channel discord` - Discord channel
- `--announce` - Send result directly to Discord
- `--delete-after-run` - Delete task after execution

### Dynamic Parameters (from current session context)

Use `session_status` tool to get current session's deliveryContext:

- `--agent` - Get from `deliveryContext.accountId` (e.g., `machu`)
- `--to` - Get from `deliveryContext.to` (e.g., `channel:1476104553148452958`)

How to get:
```bash
# Get current session info
session_status
# Output contains deliveryContext:
# {
#   "channel": "discord",
#   "to": "channel:1476104553148452958",
#   "accountId": "machu"
# }
```

## Time Parsing

Parse user input time, support:

- Relative time: `30 seconds`, `1 minute`, `30 minutes`, `2 hours`, `1 day`
- Absolute time: `3pm`, `9am today`, `12pm tomorrow`

Convert to ISO 8601 format for cron.

## Usage Example

User says "remind me to check weather in 30 seconds":

```bash
# 1. Get current session's deliveryContext
session_status
# Assume output:
# {
#   "deliveryContext": {
#     "channel": "discord",
#     "to": "channel:1476104553148452958",
#     "accountId": "machu"
#   }
# }

# 2. Calculate time 30 seconds later
date -u -d "+30 seconds" +"%Y-%m-%dT%H:%M:%SZ"
# Result: 2026-02-26T13:30:00Z

# 3. Create cron job (using main session + system-event)
openclaw cron add \
  --name "reminder-weather" \
  --at "2026-02-26T13:30:00Z" \
  --session main \
  --system-event "Check Beijing weather" \
  --agent machu \
  --announce \
  --channel discord \
  --to "channel:1476104553148452958" \
  --delete-after-run
```

## Task Content (SECURITY)

User-specified task content must be sanitized before passing to cron:

1. **Validation Method**: REJECT dangerous patterns (not escape)
   
   The script rejects any input containing:
   - Command substitution: `$()`, backticks `` ` ``
   - Shell metacharacters: `;`, `|`, `&`, `>`, `<`
   - Double quotes: `"` (breaks CLI quoting)
   - Newlines: `\n` (can inject multiple commands)
   - Dangerous command prefixes: `sudo`, `rm`, `wget`, `curl`, `bash`, etc.

2. **Sanitization Script**:
   Use `scripts/sanitize-message.sh` to validate input:
   ```bash
   ./scripts/sanitize-message.sh "user's task content"
   # Exit code 0 = safe, non-zero = rejected
   ```

3. **If rejected**: Tell user the task contains invalid characters and ask them to rephrase without: $() ` ; | & > < " or dangerous commands.

## Confirmation Reply

After creating the task, reply to user to confirm:
- "OK, will remind you in X minutes/to do XXX"
- Don't tell user the specific cron command

## Notes

1. Time must be in the future, not the past
2. Task content should be concise and clear
3. If time exceeds 48 hours, suggest using calendar
4. Always use `--session main` + `--system-event` for reliable Discord delivery
5. Validate task content with sanitize-message.sh before creating job
