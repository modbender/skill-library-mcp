---
name: reminder-engine
description: "Create, list, cancel, and snooze reminders using OpenClaw cron jobs (one-shot or recurring). Use when a user asks things like: 'remind me in 20 minutes', 'remind me tomorrow at 9', 'every weekday at 10:30', 'list my reminders', 'cancel reminder', or 'snooze this'. This skill focuses on safe scheduling (timezone-correct), confirmation before creating jobs, and clean reminder text that will read well when it fires."
---

# Reminder Engine

Turn natural-language reminders into OpenClaw `cron` jobs.

## Workflow

### 1) Parse intent
Classify the request:
- **One-shot**: “in 20 minutes”, “tomorrow at 9”, “on March 1st at 10:00”
- **Recurring**: “every day at 9”, “every weekday at 10:30”, “every Monday”, “every 2 hours”
- **Management**: “list reminders”, “cancel X”, “disable/enable”, “snooze X”

Extract:
- reminder text (what should be said when it fires)
- delivery channel context (current chat unless user specifies otherwise)
- timezone (default to the runtime timezone unless user specifies)

### 2) Confirm schedule (always)
Before creating/updating/removing jobs, echo back:
- the computed schedule in human form (and timezone)
- whether it’s one-shot or recurring
- the exact reminder message text

If the user’s wording is ambiguous (“next Friday”, “in the morning”), ask a single clarifying question.

### 3) Create the cron job (reminders)
Use the **cron tool**.

Rules:
- Prefer `schedule.kind="at"` for one-shots.
- Prefer `schedule.kind="cron"` for recurring reminders (use `tz` when possible).
- Use `sessionTarget="main"` and `payload.kind="systemEvent"`.
- Write payload text like a reminder: start with “Reminder:” (especially if the reminder is set far in advance).
- Include light context if it helps (“Reminder: submit the invoice (you said you need this for the client call)”).

### 4) List / cancel / snooze
- **List**: use `cron.list`, show jobId + next run + name/summary.
- **Cancel**: `cron.remove(jobId)` (prefer cancelling by exact jobId; if user provides text, search list and confirm).
- **Snooze**: implement as cancel+recreate (one-shot) or a one-shot override reminder.

## Reminder text quality
- Keep it short and action-oriented.
- Avoid secrets.
- If the reminder is for a public channel, warn the user.

## Safety
- Never create spammy recurring reminders without explicit confirmation.
- Never “broadcast” reminders to multiple targets unless explicitly requested.
- Never include access keys/tokens in reminder payloads.

## Examples (what good looks like)

User: “remind me in 20 minutes to stretch”
- Create one-shot `at` job.
- Payload text: `Reminder: stretch.`

User: “every weekday at 10:30 remind me to stand up”
- Create recurring `cron` job in local timezone.
- Payload text: `Reminder: stand up (weekday standup alarm).`

User: “list my reminders”
- List jobs; show ids so the user can say “cancel <id>”.

User: “cancel the stand up reminder”
- List matching jobs, ask which one if multiple, then remove.
