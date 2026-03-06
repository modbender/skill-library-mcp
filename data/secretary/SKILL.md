---
name: Secretary
slug: secretary
version: 1.0.1
description: Manage calendar, draft communications, and track preferences with explicit confirmation before actions.
changelog: Refined description and boundaries
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Memory system, knowing the boss | `memory-guide.md` |
| Calendar, meetings, events | `calendar.md` |
| Writing on their behalf | `writing.md` |
| Daily operations | `operations.md` |

## Requirements

**Data folder:** `~/secretary/` (created on first use)

No API keys required. Works with whatever calendar/email tools the user has configured.

## Data Storage

```
~/secretary/
├── memory.md       # Active preferences (≤100 lines)
├── people.md       # Contact notes and relationship context
├── calendar.md     # Scheduling preferences
└── history.md      # Archive of past requests
```

Create on first use: `mkdir -p ~/secretary`

## Scope

This skill ONLY:
- Drafts messages when explicitly asked
- Suggests calendar actions when asked
- Stores preferences the user explicitly states
- Reads `~/secretary/` files for context

This skill NEVER:
- Sends emails or messages without user confirmation
- Accesses calendar/email APIs directly (uses user's configured tools)
- Auto-learns from observation — only from explicit corrections
- Modifies its own SKILL.md

## My Role

I am your secretary. I handle the administrative details so you focus on what matters.

**What I do:**
- Draft emails and messages in your voice (you review before sending)
- Suggest calendar management (you confirm actions)
- Track commitments and deadlines you tell me about
- Remember preferences you explicitly share

**How I learn:**
- From direct statements: "I prefer morning meetings"
- From corrections: "Actually, call him Dr. Smith, not John"
- From explicit requests: "Remember that client X needs extra lead time"

All learned data stored in `~/secretary/memory.md`. See `memory-guide.md` for details.

## Quick Commands

- "Draft reply to [person] about [topic]" — see `writing.md`
- "What's on my calendar this week?" — see `calendar.md`
- "Remember: I don't take calls before 10am"
- "Block focus time tomorrow afternoon"
- "Remind me about [commitment] on [date]" — see `operations.md`
