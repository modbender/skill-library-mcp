# Out-of-band delivery (recommended)

Problem: if an isolated cron job returns a long text payload, OpenClaw often records it into the main session transcript (as a `System: Cron:` injection). Over time this bloats the interactive context and can trigger compaction or context overflow.

Goal: keep the user notifications, but avoid inflating the interactive session transcript.

## Pattern

Inside the isolated cron worker:
1) Send the message to the user using the platform tool (Telegram/Discord/Slack/etc.)
2) Output exactly `NO_REPLY`

This makes the cron run "silent" from the perspective of the main session transcript, while still delivering the content to the user.

## Practical guidance

- Keep user-facing messages short enough to be readable.
- If you need details, write them to a file first (e.g., `memory/...json`) and send a link/path + a short summary.

## Bonus

Pair this with a memory layer (e.g., openclaw-mem) to retrieve state on demand.
