---
name: slack-thread
description: Read and summarize Slack channel history and thread conversations. Use when receiving a Slack link (https://...slack.com/archives/...), or when asked to view channel/thread messages, summarize conversations, or check recent messages in a channel.
---

# Slack Thread Reader

Script for fetching Slack channel history and thread replies.

## Script Location

`scripts/slack-thread.sh` (entry point) → `scripts/slack-thread.py` (main logic)

## Usage

### Read Thread
```bash
scripts/slack-thread.sh https://your-workspace.slack.com/archives/CHANNEL/pTIMESTAMP
scripts/slack-thread.sh <channel-id> <thread-ts>
```

### Read Channel History
```bash
scripts/slack-thread.sh https://your-workspace.slack.com/archives/CHANNEL
scripts/slack-thread.sh <channel-id>
scripts/slack-thread.sh <channel-id> --limit 30
```

### Channel History with Thread Replies (Full)
```bash
scripts/slack-thread.sh <channel-id> --with-threads
```

### Limit Thread Replies (Optional)
```bash
scripts/slack-thread.sh <channel-id> --with-threads --thread-limit 5
```

## Workflow

1. When given a Slack link or channel ID, use this script to fetch the conversation history.
2. **⚠️ If the link type and the user's request don't match, always ask for clarification.**
   - Link format: `/archives/CHANNEL` = channel, `/archives/CHANNEL/pTIMESTAMP` = thread
   - Example: If the user provides a thread link but says "get the channel history" → **"The link you provided points to a specific thread. Did you want the thread content or the entire channel history?"**
   - People make mistakes. If the link and the request don't match, ask instead of guessing.
3. **When asked to summarize channel history**: Ask the user "Should I include thread replies?" and set the `--with-threads` flag accordingly.
4. Summarize or pass through the fetched content as-is.

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--limit N` | Number of channel history messages | 50 |
| `--with-threads` | Include thread replies inline | off |
| `--thread-limit N` | Max replies per thread (0=all) | 0 (all) |

## Output Elements

| Element | Format | Example |
|---------|--------|---------|
| Timestamp | ISO 8601 (seconds) | `[2026-02-11T17:45:56]` |
| Sender | Real name | `John Doe:` |
| Mentions | `@name` resolved | `@Jane Smith` |
| Emoji reactions | Emoji + reactor names | `[:thumbsup: John,Jane]` |
| Attachments | 📎 filename (type) | `📎 image.png (image/png)` |
| Thread reply count | 💬N | `💬13` |
| Thread replies (inline) | ├ └ tree | with `--with-threads` |

## Notes

- The bot must be a member of the target channel. If you get a `channel_not_found` error, instruct the user to run `/invite @botname` in the channel.
- Without `--with-threads`, channel history won't include thread conversations. Always confirm whether to include threads when summarizing.
