---
name: group-activation
description: Handles joining and leaving group conversations on messaging platforms (WhatsApp, Signal, Telegram, etc.). Use when the owner tags the agent into a group chat to participate for a time-limited window, and when the agent needs to open or close the participation gate for a specific group.
---

# Group Activation

When the owner tags you into a group on any messaging platform, follow this procedure.

## Prerequisites

`channels.<platform>.groupPolicy`, `groupAllowFrom`, and `groups.*.requireMention` are set so that only the owner can wake you in any group. Trigger phrases are defined in `agents.list[main].groupChat.mentionPatterns`. This applies to WhatsApp, Signal, Telegram, and other supported platforms.

## Procedure

**Step 1 — Capture context**

From the inbound message metadata: platform (e.g. `whatsapp`, `signal`), group ID (the `chat_id` / `from` field), and duration (parse from the owner's message — default 30 minutes if unspecified).

**Step 2 — Open the gate**

Patch `channels.<platform>.groups.<group_id>.requireMention` to `false` in `openclaw.json`. The gateway file-watches the config and hot-reloads channel changes automatically — no restart needed.

**Step 3 — Respond naturally**

Say hi, introduce yourself briefly if it's a new group. Participate like a human in a group chat — use judgment about when to contribute. Do not respond to every message.

**Step 4 — Set a closing cron job**

Create a one-shot cron job (`kind: "at"`) for the parsed duration. When it fires: patch `requireMention` back to `true` for this group in `openclaw.json`, then send a brief goodbye to the group. The gateway hot-reloads and the gate closes — no owner action needed.

**Step 5 — Confirm**

Tell the owner the window is open and when it closes: _"Joined! I'll be here for 60 minutes — going quiet at 4:19 PM."_

## Controls

- **Extend:** owner says `@<agent> stay for another X mins` → cancel existing cron, set a new one
- **Close early:** owner says `@<agent> that's enough` / `close` → patch `requireMention: true` immediately, cancel cron, say goodbye

## Notes

- Group ID is in inbound message metadata (`chat_id` / `from` field)
- Config changes hot-reload — no gateway restart or Docker restart needed
- When closing, remove the specific group entry from `groups` or set `requireMention: true` to return to the wildcard default
