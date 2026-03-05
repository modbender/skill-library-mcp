---
name: snail-mail
description: A slow-channel inbox for leaving your operator important messages. Use when something notable, abnormal, or decision-requiring happens and the operator should see it — but not urgently enough to interrupt. Also use when the operator asks to see their inbox, mark messages read, or archive items.
---

# Operator Inbox

A "slow channel" between you and your operator. Not every event deserves a ping. The inbox captures what matters and presents it beautifully when they're ready to look.

## Setup

On first use, the inbox file is created automatically at `{workspace}/inbox/messages.json`.

## When to Write to the Inbox

Write an inbox entry when something is **notable enough that your operator would want to know, but not urgent enough to interrupt them.**

### Write when:
- **Needs decision** — something only a human can resolve (payment, approval, policy)
- **Abnormal** — errors, failures, unexpected patterns, security events
- **Interesting** — notable engagement, media mentions, milestones, opportunities
- **FYI** — context that might matter later but needs no action now

### Do NOT write when:
- Routine success ("cron ran fine", "heartbeat OK")
- Something you already told them in chat
- Trivial events with no lasting significance
- Duplicate of something already in the inbox

### Priority levels:
- `urgent` — needs attention within hours (prefix title with `[URGENT]`)
- `important` — should see today (prefix title with `[IMPORTANT]`)
- `normal` — whenever they check (no prefix)

### Writing good entries:
- **Title:** Short, scannable. Include the WHO or WHAT. ("@bigaccount (500K) mentioned us", not "Social media event")
- **Message:** 1-3 sentences. What happened, why it matters, what (if anything) needs doing. Include links/handles when relevant.

## CLI Usage

```bash
# Add entry
node {skill}/scripts/inbox.js add "Title" "Description of what happened"

# Add with priority
node {skill}/scripts/inbox.js add "[URGENT] Server disk 95%" "Only 2GB remaining on /dev/sda1"

# List unread
node {skill}/scripts/inbox.js list

# List all (including read)
node {skill}/scripts/inbox.js list all

# List archived
node {skill}/scripts/inbox.js list archived

# Mark one read
node {skill}/scripts/inbox.js read <id>

# Mark all read
node {skill}/scripts/inbox.js read-all

# Archive one
node {skill}/scripts/inbox.js archive <id>

# Archive all read
node {skill}/scripts/inbox.js archive-read

# Render for chat (auto-detects channel)
node {skill}/scripts/inbox.js render [unread|all|archived]

# Render as HTML (force)
node {skill}/scripts/inbox.js render --html

# Render as markdown (force)
node {skill}/scripts/inbox.js render --md

# Render as plain text (force)
node {skill}/scripts/inbox.js render --text
```

## Presenting the Inbox

When the operator asks to see their inbox (or says "inbox", "messages", "check inbox"), run:

```bash
node {skill}/scripts/inbox.js render [unread|all|archived] [--html|--md|--text]
```

Choose format based on channel:
- **Telegram, webchat** → `--html`
- **Discord, Slack** → `--md`
- **SMS, plain** → `--text`

Send the output as your reply. Do not add commentary unless they ask.

## Heartbeat Integration

During heartbeats, check for unread urgent/important items:

```bash
node {skill}/scripts/inbox.js list unread --json
```

If urgent items exist, surface them proactively. Otherwise stay quiet.

## Storage

Messages stored in `{workspace}/inbox/messages.json`. Single-writer (the agent), so no locking needed. Writes use atomic rename (write .tmp → rename) to prevent corruption.
