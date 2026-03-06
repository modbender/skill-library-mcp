---
name: slack-actions
summary: Control Slack messaging, reactions, pins, and member information using Clawdbot.
description: Enables authenticated interaction with Slack for sending, editing, deleting, reacting to, and managing messages and pins via a secure bot token.
tags: ["slack","automation","collaboration","productivity","chatops"]
version: 1.2.0
author: Rayen Kamta / GEEKSDOBYTE LLC / GEEKSDOBYTE.COM
---
# Slack Actions Skill

## Overview

The **Slack Actions Skill** enables Clawdbot to securely interact with Slack channels and direct messages using a Bot OAuth token.

This skill allows agents to:

- Send, edit, and delete messages
- Add and list reactions
- Pin and unpin messages
- Read recent channel history
- Retrieve member information
- List workspace emojis

All actions are executed using the permissions granted to the configured bot account.

---

## Purpose & Capability

This skill enables authenticated Slack operations using a Bot OAuth token supplied through the `SLACK_BOT_TOKEN` environment variable.

With valid credentials, the skill can:

- Manage messages and reactions
- Maintain pinned references
- Retrieve basic user metadata
- Support lightweight workflow automation

The skill operates strictly within the authorization scope of the configured Slack bot.

---

## Authentication & Configuration

### Required Environment Variable

This skill requires a Slack Bot User OAuth token.

Before use, configure:

```

SLACK_BOT_TOKEN

````

Example:

```bash
export SLACK_BOT_TOKEN="xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxx"
````

Or in `.env` format:

```
SLACK_BOT_TOKEN=xoxb-xxxxxxxxxxxx-xxxxxxxxxxxx-xxxxxxxxxxxx
```

### Token Requirements

The token must include the following OAuth scopes:

* `chat:write`
* `channels:read`
* `channels:history`
* `reactions:write`
* `pins:write`
* `users:read`
* `emoji:read`

Additional scopes may be required depending on workspace policies.

### Credential Storage

* Tokens must be stored only in environment variables
* Tokens must never be hardcoded
* Tokens must never be logged
* Tokens must not be exposed in outputs

If `SLACK_BOT_TOKEN` is missing, invalid, or revoked, this skill must not execute.

---

## Initial Setup

To configure this skill:

1. Create a Slack App in your workspace
2. Enable Bot Token authentication
3. Assign required OAuth scopes
4. Install the app to the workspace
5. Copy the Bot User OAuth token
6. Store the token in `SLACK_BOT_TOKEN`
7. Restart the agent

After setup, the skill becomes available for execution.

---

## Credential Constraints

* Only Bot User tokens (`xoxb-`) are supported
* User tokens (`xoxp-`) are not permitted
* Tokens must belong to a single workspace
* Cross-workspace tokens are unsupported
* Tokens must be rotated periodically
* Tokens must comply with organizational security policies

Unauthorized credential usage is prohibited.

---

## When to Use This Skill

Activate this skill when the user requests:

* Sending messages to Slack
* Reacting to messages
* Editing or deleting content
* Pinning or unpinning messages
* Reading recent messages
* Looking up users
* Viewing emojis

Example triggers:

> “Send this to #engineering.”
> “React with a checkmark.”
> “Pin that message.”
> “Who is U123?”

---

## Required Inputs

### Message Targeting

* `channelId` — Slack channel ID (ex: `C1234567890`)
* `messageId` — Slack timestamp (ex: `1712023032.1234`)

### Reactions

* `emoji` — Unicode emoji or `:name:` format

### Sending Messages

* `to` — `channel:<id>` or `user:<id>`
* `content` — Message text

Message context may contain reusable fields such as `channel` and `slack message id`.

---

## Supported Action Groups

| Group      | Status  | Description                       |
| ---------- | ------- | --------------------------------- |
| reactions  | Enabled | Add and list reactions            |
| messages   | Enabled | Send, edit, delete, read messages |
| pins       | Enabled | Manage pinned items               |
| memberInfo | Enabled | Retrieve user profiles            |
| emojiList  | Enabled | List custom emojis                |

---

## Available Actions

### React to a Message

```json
{
  "action": "react",
  "channelId": "C123",
  "messageId": "1712023032.1234",
  "emoji": "✅"
}
```

---

### List Reactions

```json
{
  "action": "reactions",
  "channelId": "C123",
  "messageId": "1712023032.1234"
}
```

---

### Send a Message

```json
{
  "action": "sendMessage",
  "to": "channel:C123",
  "content": "Hello from Clawdbot"
}
```

---

### Edit a Message

```json
{
  "action": "editMessage",
  "channelId": "C123",
  "messageId": "1712023032.1234",
  "content": "Updated text"
}
```

---

### Delete a Message

```json
{
  "action": "deleteMessage",
  "channelId": "C123",
  "messageId": "1712023032.1234"
}
```

---

### Read Recent Messages

```json
{
  "action": "readMessages",
  "channelId": "C123",
  "limit": 20
}
```

---

### Pin a Message

```json
{
  "action": "pinMessage",
  "channelId": "C123",
  "messageId": "1712023032.1234"
}
```

---

### Unpin a Message

```json
{
  "action": "unpinMessage",
  "channelId": "C123",
  "messageId": "1712023032.1234"
}
```

---

### List Pinned Items

```json
{
  "action": "listPins",
  "channelId": "C123"
}
```

---

### Get Member Information

```json
{
  "action": "memberInfo",
  "userId": "U123"
}
```

---

### List Workspace Emojis

```json
{
  "action": "emojiList"
}
```

---

## Behavioral Rules

* Confirm IDs before destructive actions
* Never delete messages without explicit user approval
* Prefer reactions over messages for acknowledgments
* Validate inputs before execution
* Never expose credentials

---

## Usage Examples

### Mark Task Complete

```json
{
  "action": "react",
  "channelId": "C123",
  "messageId": "1712023032.1234",
  "emoji": "✅"
}
```

---

### Post Status Update

```json
{
  "action": "sendMessage",
  "to": "channel:C456",
  "content": "Deployment completed successfully."
}
```

---

### Save Important Message

```json
{
  "action": "pinMessage",
  "channelId": "C123",
  "messageId": "1712023032.1234"
}
```

---

## Instruction Scope

This skill is limited to Slack workspace operations authorized by the configured bot token.

It does NOT:

* Create Slack applications
* Modify workspace settings
* Manage billing
* Bypass permissions
* Escalate privileges

All operations respect Slack API constraints.

---

## Compliance

This skill follows Slack API Terms of Service and OAuth security guidelines.

Users are responsible for obtaining organizational approval prior to deployment.

---

## Best Practices

* Use reactions for lightweight workflows
* Pin long-term references
* Keep messages concise
* Avoid bulk destructive actions
* Rotate credentials regularly

---

