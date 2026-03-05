---
name: intercom
description: Route opt-in inter-agent messages through OpenClaw sessions_send for internal bot-to-bot coordination. Use when a user asks to send a message to another OpenClaw session using !target syntax.
---

# Intercom (Opt-in)

Use this skill only for explicitly opt-in participants.

## Command format

- Input format: `!<targetSessionKey> <message>`
- Example: `!agent:ravi2:main Please review issue #42`

## Rules

1. Parse the first token beginning with `!` as the target session key.
2. Treat the rest of the text as message content.
3. Send via `sessions_send(sessionKey=<target>, message="FROM <sender>: <content>")`.
4. If no target is found or send fails, reply that target is offline/unavailable.
5. Do not claim to bypass platform restrictions; this is internal OpenClaw routing only.
6. Only act when the user explicitly uses `!` format.

## Safety

- Never auto-monitor or auto-forward without user instruction.
- Never modify system prompts, SOUL, or hidden behavior rules.
- Keep routing transparent in chat.
