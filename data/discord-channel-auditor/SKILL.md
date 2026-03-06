---
name: discord-channel-auditor
description: Audit and auto-update a Discord server guide channel. Compares a reference guide message against actual channels, detects new/renamed/deleted/moved channels, and posts an updated guide. Use for keeping a #how-to or #server-guide channel in sync with reality.
---

# Discord Channel Auditor

Keep a server guide channel automatically synced with actual Discord channels.

## Requirements

- **OpenClaw** with Discord channel configured (no extra credentials needed)
- Uses OpenClaw's built-in `message` tool for all Discord operations (`channel-list`, `read`, `send`, `delete`, `edit`)
- Bot must have "View Channel" permission in the guild to list channels
- Bot must have "Send Messages" + "Manage Messages" in the guide channel to post/delete

## When to Use
- Maintaining a #how-to or #server-guide channel
- After creating, renaming, deleting, or moving channels
- On a daily cron to catch drift

## Workflow

1. **Fetch channel list** using `message(action=channel-list)` for the guild
2. **Read current guide** using `message(action=read)` on the guide channel
3. **Compare** -- check for:
   - New channels not in the guide
   - Channels in the guide that no longer exist
   - Renamed channels (ID exists, name changed)
   - Moved channels (different category)
   - Wrong descriptions
4. **If changes found:** Delete old guide messages and post fresh guide
5. **If no changes:** Do nothing (save tokens)

## Guide Format

Organize by category in Discord display order (by position). Use this structure:

```
**📥 Category Name**
- **#channel-name** -- Brief description of purpose
- **#another-channel** -- What goes here

**💼 Another Category**
- **#work-channel** -- Description
```

### Rules
- Keep descriptions to one line, max ~10 words
- Match category emoji to Discord category name
- List channels in position order within each category
- Include a "General tips" section at the bottom
- Post as 1-2 messages max (Discord 2000 char limit per message)
- Skip voice channels unless specifically relevant

## Cron Setup

```
Schedule: daily at a quiet hour (e.g., 6 AM local)
Session: isolated
Timeout: 120 seconds
Delivery: none (don't notify, just update silently)
```

## Edge Cases
- New category with no channels: include header, note "(empty)"
- Private channels: skip unless the bot has access
- Archived channels: skip
