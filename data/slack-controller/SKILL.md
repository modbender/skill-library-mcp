---
name: slack-controller
description: Control Slack via Browser Automation to send messages, manage huddles, screen share, set status, and react as the logged-in user.
---

# Slack Controller (Browser Edition)

This skill automates the Slack Web Client (`app.slack.com`) or Desktop App (via Debug Port) using a dedicated automation profile. This allows the agent to send messages, start huddles, share screen, and manage status acting **as you**.

## Prerequisites

1.  **Slack Desktop App** (preferred) or **Google Chrome** installed.
2.  **Permissions**: Terminal/Cursor must have **Screen Recording** and **Accessibility** permissions in macOS System Settings.
3.  **Login**: You must log in manually once in the automation window/profile if prompted.

## Usage

### Via OpenClaw Chat
> "Message Adeel saying hello"
> "Start a huddle with Adeel and share my screen"
> "Set my status to In a Meeting for 1 hour"
> "Search for 'quarterly report'"

### Via CLI (Manual)

**Messaging:**
```bash
node ~/.cursor/skills/slack-controller/dist/index.js --action=sendMessage --target="adeel" --message="Hello there"
```

**Huddle & Screen Share:**
```bash
node ~/.cursor/skills/slack-controller/dist/index.js --action=startHuddleAndScreenShare --target="general"
```

**Leave Huddle:**
```bash
node ~/.cursor/skills/slack-controller/dist/index.js --action=leaveHuddle --target="general"
```

**Status:**
```bash
node ~/.cursor/skills/slack-controller/dist/index.js --action=setStatus --statusEmoji=":coffee:" --statusText="Lunch"
```

**Search:**
```bash
node ~/.cursor/skills/slack-controller/dist/index.js --action=search --target="project updates"
```

## Actions

- `sendMessage`: Send a text message to a user or channel.
- `openChat`: Just open the conversation window physically.
- `sendHuddleInvite`: Toggle the huddle (standard join).
- `startHuddleAndScreenShare`: Join huddle, wait for UI, and click "Share screen" -> "Entire screen".
- `leaveHuddle`: Leave the current huddle.
- `setStatus`: Set custom status emoji and text.
- `setPresence`: Toggle Active/Away.
- `pauseNotifications`: Snooze notifications.
- `uploadFile`: Upload a local file to a chat.
- `addReaction`: React to the latest message in a chat.
- `search`: Perform a global search and return results.
