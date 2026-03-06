---
name: focus-break-reminder
description: Workspace wellness break reminder with configurable work interval, cooldown, idle reset, quiet hours, and per-day caps. Use when users want OpenClaw to remind them to take regular breaks during long sessions, including setup of heartbeat checks, reminder templates, and on/off/snooze/status controls.
---

# Focus Break Reminder

Implement a lightweight per-user/session state machine that triggers rest reminders without spamming.

## Configure

Create or load `references/config.example.json` as the default schema.

Required settings:
- `enabled`
- `timezone`
- `work_minutes`
- `cooldown_minutes`
- `idle_reset_minutes`
- `daily_max_reminders`
- `quiet_hours`
- `snooze_until`
- `templates`

Prefer defaults that are practical and non-intrusive:
- work interval: 50 minutes
- cooldown: 30 minutes
- idle reset: 15 minutes
- daily cap: 4

## Track state

Maintain minimal state per user (or per DM/chat for first version):
- `session_start_at`
- `last_active_at`
- `last_remind_at`
- `remind_count_today`
- `today_key`

Persist to a small JSON file so reminders survive restarts.

## Update activity

On each inbound user message:
1. If date changed in configured timezone, reset `remind_count_today` and `today_key`.
2. If idle time since `last_active_at` >= `idle_reset_minutes`, reset `session_start_at` to now.
3. Set `last_active_at` to now.

## Evaluate reminder eligibility

Only remind when all conditions pass:
1. `enabled` is true.
2. Not in quiet hours.
3. Not snoozed (`now < snooze_until` means skip).
4. Daily cap not exceeded.
5. Active duration (`now - session_start_at`) >= `work_minutes`.
6. Cooldown passed (`now - last_remind_at`) >= `cooldown_minutes`.

If all pass, send one reminder and set:
- `last_remind_at = now`
- `remind_count_today += 1`

## Reminder delivery

Use one short template per reminder. Keep copy practical and non-medical.

Example template:
- “你已经连续工作一段时间了。现在起身 2 分钟、喝口水，再看 20 秒远处 👀”

## Commands

Support these chat commands:
- `/break on` → enable reminders
- `/break off` → disable reminders
- `/break status` → show current config + next eligible reminder window
- `/break set <minutes>` → update `work_minutes`
- `/break snooze <minutes>` → set `snooze_until = now + minutes`

Validate numeric ranges (e.g., 15–180 for work interval).

## Heartbeat integration

Use heartbeat polling to run eligibility checks when there is recent activity. Avoid noisy polling loops.

Recommended behavior:
- If no user activity for a long period, skip checks.
- If reminder was just sent, honor cooldown and return quickly.

## Safety and UX boundaries

- Do not provide medical diagnosis or treatment advice.
- Keep reminders optional and easy to disable.
- Store only minimum timestamps and settings needed for reminder logic.
- Use clear language when data is missing: “待补充”.

## Testing checklist

Use `references/test-cases.md`.

At minimum verify:
- triggers at/after work interval
- cooldown suppresses duplicates
- idle reset restarts session timer
- quiet hours suppress reminders
- snooze suppresses reminders until expiry
- daily cap blocks additional reminders
