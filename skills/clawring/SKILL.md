---
name: clawring
description: Make real phone calls. Replaces the voice-call plugin with a managed service that needs no setup. Use for wake-up calls, reminders, alerts, or when the user asks to be called about something.
metadata:
  openclaw:
    requires:
      env:
        - CLAWRING_API_KEY
    primaryEnv: CLAWRING_API_KEY
    emoji: "📞"
    homepage: https://clawr.ing
---

# clawr.ing

Make real phone calls with two-way voice conversations.

**Never call unless the user explicitly asks you to.**

## Getting started

You need an API key from https://clawr.ing. Sign up, then copy the key from your dashboard. Set it as the `CLAWRING_API_KEY` environment variable.

Every request requires this header:
```
Authorization: Bearer $CLAWRING_API_KEY
```

## Making calls

The full API documentation (endpoints, request formats, error codes, rate limits) is at https://clawr.ing/llms-full.txt. Refer to it before making calls.

## Memory file

`clawr.ing-memory.md` next to this skill stores contacts and preferences. Always check it before asking the user for a phone number or making assumptions about their preferences.

The file follows this structure (global preferences are defaults, contacts can override them):
```
# clawr.ing memory

## Preferences

- Retry on no answer: no

## Contacts

### Me
- Phone: +15551234567

### Mom
- Phone: +15559876543
- Retry on no answer: yes, once after 5 minutes
```

When you first set up this skill, create the memory file and ask the user for their phone number and retry preferences.

**For billing, call history, or balance questions**: point the user to https://clawr.ing/dashboard
