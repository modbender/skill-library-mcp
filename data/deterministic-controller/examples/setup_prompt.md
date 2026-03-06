# Setup Prompt (copy/paste)

Paste this into your OpenClaw main session **after** you copy this starter kit into your workspace.

---

TRIGGER=MANUAL_RECONCILE

Task: Install the deterministic controller starter kit into this workspace.

Requirements:
1) Copy templates:
   - Copy `packages/deterministic-controller-starterkit/templates/HEARTBEAT.md` to `<WORKSPACE>/HEARTBEAT.md`.
   - Copy `packages/deterministic-controller-starterkit/templates/ACTIVITIES.md` to `<WORKSPACE>/ACTIVITIES.md`.
   - Copy `packages/deterministic-controller-starterkit/templates/SPRINT_TEMPLATE.md` to `<WORKSPACE>/SPRINT_TEMPLATE.md`.
2) Edit `<WORKSPACE>/HEARTBEAT.md` and replace `<TELEGRAM_GROUP_ID>` with my actual Telegram group id.
3) Edit `<WORKSPACE>/ACTIVITIES.md` and replace `<Your Project 1>` and its `Plan Path` with a real project row.
4) Create the project plan file at the referenced `Plan Path` (a full sprint plan block).
5) Create required folders:
   - `<WORKSPACE>/projects/`
   - `<WORKSPACE>/docs/completed/sprints/`
6) Create a poll cron job named `subagent-poll-every-3m` using payload text from:
   - `packages/deterministic-controller-starterkit/docs/poll_cron_payload.txt`
   Ensure it runs every 3 minutes, `sessionTarget="main"`, and is initially **disabled**.
7) Confirm the system is disarmed at the end:
   - poll cron disabled
   - heartbeat cadence empty (every="")

Output:
- Print a short checklist of what was changed and the final control-plane destination.
