---
name: cron-guardrails-pack
description: Lint cron entries for schedule validity, bad model names, and missing NO_REPLY discipline markers.
---

# cron-guardrails-pack

Author: Billy (SAPCONET)

## Purpose
Provide quick lint + checklist guardrails for cron entries and notification discipline (`NO_REPLY`).

## What this skill includes
- `scripts/cron-lint.py`: static checks for cron entry lines.

## Checks performed
- Cron schedule must contain exactly 5 fields.
- Rejects known bad model names (for example: `haiku-4-6`).
- Flags jobs that appear to announce/message but do not include `NO_REPLY`.

## Usage
Lint a cron file:

```bash
python3 scripts/cron-lint.py /path/to/crontab.txt
```

Lint stdin:

```bash
cat /path/to/crontab.txt | python3 scripts/cron-lint.py -
```

Exit codes:
- `0`: no issues
- `1`: one or more issues found
- `2`: usage or read error

## NO_REPLY checklist
- Announce/inbox/notify-style jobs should explicitly include `NO_REPLY` in payload or message body.
- Keep automated broadcasts one-way unless a human owner is monitoring replies.
- Include owner and purpose in command comments.

## Example cron payload snippet

```cron
*/15 * * * * /usr/local/bin/send-inbox --channel ops --tag NO_REPLY --message "NO_REPLY | cron heartbeat"
```
