# Bot Messaging Capabilities (Checklist)

> Note: Confirm exact method names and payloads in the official Zalo Bot Platform docs.

## Core outbound
- Send text messages
- Send images or files (within size limits)
- Send rich/structured messages if supported
- Show typing/acknowledge states if supported

## Inbound handling
- Receive user text messages
- Receive attachments
- Receive postback or button events (if supported)

## User and conversation
- Fetch user profile metadata (if permitted)
- Track conversation context per user
- Respect opt-in / pairing requirements

## Moderation and safety
- Reject unsupported content types
- Throttle outbound messages
- Filter or sanitize user input
