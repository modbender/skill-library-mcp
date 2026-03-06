---
name: Message
slug: message
version: 1.0.0
description: Communicate across channels without social disasters, with escalation rules, tone calibration, and platform-aware formatting.
metadata: {"clawdbot":{"emoji":"💬","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to send messages on their behalf. Agent must avoid social mistakes that humans wouldn't make: wrong tone, wrong channel, wrong timing, auto-committing to things.

## Quick Reference

| Topic | File |
|-------|------|
| Platform formatting | `platforms.md` |
| Tone calibration | `tone.md` |
| Escalation matrix | `escalation.md` |

## Core Rules

### 1. Never Auto-Commit
- Timelines, pricing, legal terms, availability → draft for human, never send
- "We can deliver by Friday" from AI = career damage
- Money confirmations require explicit per-transaction approval
- When uncertain about commitment level → ask first

### 2. Escalate High-Stakes
Draft for human review, never auto-send:
- Investors, board, press, lawyers
- Client complaints, anything with "urgent", "legal", "disappointed"
- Condolences, relationship issues, conflict
- First message to new important contact

### 3. Match the Human's Style
- Read their last 5 messages before drafting
- Don't add phrases they never use ("Hope you're doing well!")
- Don't use emojis they avoid
- Real humans send "ok", AI sends paragraphs → match their brevity

### 4. Channel Selection Follows Urgency
| Urgency | Channel |
|---------|---------|
| Production down | Call, then Slack |
| Same-day needed | Slack/Teams DM |
| This week | Email |
| FYI only | Email with no action needed |
- NEVER email for urgent issues
- NEVER Slack for formal client communication

### 5. Timing Is Social Signal
- Instant replies reveal automation
- 3 AM recipient time → schedule for morning
- Email = hours acceptable. Slack DM = expect <1hr response

### 6. Context Awareness Prevents Disasters
- Check you're in the RIGHT chat before sending
- Don't introduce yourself to someone you've messaged 50 times
- Group chats: lurking is normal, replying to everything is weird
- Wrong group = social suicide → when unsure, ASK

## Common Traps

- Copying boss on complaint email → escalates when de-escalation needed
- Reply-all with "thanks" → 50 people interrupted
- Forwarding thread with internal comments visible → trust destroyed
- Sending at 11 PM "just to get it off my plate" → signals poor boundaries
- Using client's first name before they used yours → presumptuous
